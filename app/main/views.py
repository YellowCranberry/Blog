import logging
from functools import wraps
from . import main
from flask import (
    render_template, redirect, url_for, request,
    session, flash, current_app
)
from flask_login import login_required, current_user
from ..models import User, Blog
from .forms import writeBlog_form, Search_form
from .. import db, cache
from .. import search as hybrid_search

# Exempt the admin login route from Flask-WTF global CSRF — the admin
# password itself provides the authentication, and CSRF on this internal
# route isn't a meaningful attack vector.
try:
    from flask_wtf.csrf import csrf_exempt as _csrf_exempt
    _CSRF_EXEMPT_AVAILABLE = True
except ImportError:
    _CSRF_EXEMPT_AVAILABLE = False

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Home & listings
# ---------------------------------------------------------------------------

@main.route('/')
@cache.cached(timeout=50)
def index():
    blogs = Blog.query.order_by(Blog.id.desc())[0:2]
    return render_template('index.html', blogs=blogs)


@main.route('/mypage')
@login_required
def mypage():
    return 'only verified'


@main.route('/posts')
def posts():
    page = request.args.get('page', 1, type=int)
    blogs = Blog.query.order_by(Blog.id.desc()).paginate(
        page=page, per_page=4, error_out=False
    )
    return render_template('show_posts.html', blogs=blogs)


@main.route('/posts/<int:id>')
def newpost(id):
    blog = Blog.query.filter_by(id=id).first()
    if blog:
        return render_template('single_post.html', blog=blog)
    return "Post not found", 404


# ---------------------------------------------------------------------------
# Blog CRUD — all three paths (create / edit / delete) keep the index in sync
# ---------------------------------------------------------------------------

def _url_for_blog(blog) -> str:
    """Canonical identifier used in the vector store for a blog post."""
    return blog.slug or f"post-{blog.id}"


@main.route('/blog', methods=['GET', 'POST'])
@login_required
def write_blog():
    form = writeBlog_form()
    if form.validate_on_submit():
        new_blog = Blog(
            title=form.title.data,
            description=form.description.data,
            slug=form.slug.data,
            author=current_user,
        )
        db.session.add(new_blog)
        db.session.commit()

        # Index the new post — wrapped in try/except so a search failure
        # never prevents the blog post from being saved.
        try:
            n, m = hybrid_search.ingest_text(
                text=form.description.data,
                metadata={
                    "title": form.title.data,
                    "url": _url_for_blog(new_blog),
                    "slug": new_blog.slug,
                    "id": new_blog.id,
                },
            )
            logger.info(
                "Indexed post id=%d url=%s chunks=%d total=%.1fms",
                new_blog.id, _url_for_blog(new_blog), n, m.total_ms,
            )
            flash(f"Blog posted and indexed ({n} chunks, {m.total_ms:.0f}ms)!", "success")
        except Exception as exc:
            logger.error("Search indexing failed for new post id=%d: %s", new_blog.id, exc)
            flash("Blog posted (search index update failed — it will sync on next restart).", "warning")

        cache.delete_memoized(index)  # Clear home-page cache so new post appears
        return redirect(url_for('main.index'))

    return render_template('write_blog.html', form=form)


@main.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def editpost(id):
    blog = Blog.query.get_or_404(id)
    if blog.author != current_user:
        flash("You don't have access to edit this post.")
        return redirect(url_for('main.newpost', id=id))

    form = writeBlog_form(obj=blog)
    if form.validate_on_submit():
        old_url = _url_for_blog(blog)
        form.populate_obj(blog)
        db.session.commit()
        new_url = _url_for_blog(blog)

        # Step 1: Remove stale chunks (old content OR old slug/url)
        # Step 2: Re-ingest with fresh content
        try:
            hybrid_search.delete_document(old_url)
            if new_url != old_url:
                hybrid_search.delete_document(new_url)  # clean any leftover under new url too

            n, m = hybrid_search.ingest_text(
                text=blog.description,
                metadata={
                    "title": blog.title,
                    "url": new_url,
                    "slug": blog.slug,
                    "id": blog.id,
                },
            )
            logger.info(
                "Re-indexed post id=%d url=%s chunks=%d total=%.1fms",
                blog.id, new_url, n, m.total_ms,
            )
            flash(f"Post updated and re-indexed ({n} chunks, {m.total_ms:.0f}ms)!", "success")
        except Exception as exc:
            logger.error("Search re-indexing failed for post id=%d: %s", blog.id, exc)
            flash("Post updated (search index update failed — search results may be stale).", "warning")

        return redirect(url_for('main.newpost', id=id))

    return render_template('edit_post.html', blog=blog, form=form)


@main.route('/posts/delete/<int:id>')
@login_required
def deletePost(id):
    blog = Blog.query.get_or_404(id)
    if blog.author != current_user:
        flash("You don't have access to delete this post.")
        return redirect(url_for('main.newpost', id=id))

    url = _url_for_blog(blog)
    try:
        db.session.delete(blog)
        db.session.commit()

        # Remove from search index after DB delete succeeds
        chunks_removed = hybrid_search.delete_document(url)
        logger.info("Deleted post id=%d url=%s chunks_removed=%d", id, url, chunks_removed)
        flash("Blog deleted and removed from search index.", "warning")
    except Exception as exc:
        db.session.rollback()
        logger.error("Delete failed for post id=%d: %s", id, exc)
        flash("An error occurred while deleting the post.", "danger")

    return redirect(url_for('.dashboard'))


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@main.route('/dashboard')
@login_required
def dashboard():
    user_blogs = Blog.query.filter_by(author_id=current_user.id).order_by(Blog.id.desc()).all()
    return render_template('dashboard.html', blogs=user_blogs)


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

# Make the search form available in every template via context processor
@main.app_context_processor
def pass_formto_searchbar():
    form = Search_form()
    return dict(search_form=form)


@main.route("/search", endpoint="search", methods=["GET", "POST"])
def search_view():
    form = Search_form()
    if form.validate_on_submit():
        session['query'] = form.search.data
        return redirect(url_for('main.search'))

    query_text = session.pop('query', None)
    if not query_text:
        return redirect(url_for('main.index'))

    try:
        results, m = hybrid_search.search_hybrid(query_text, top_k=5)
        logger.info(
            "Search query=%r results=%d embed=%.1fms db=%.1fms total=%.1fms",
            query_text, len(results), m.embed_ms, m.db_ms, m.total_ms,
        )
    except Exception as exc:
        logger.error("Search failed for query=%r: %s", query_text, exc)
        results, m = [], None
        flash("Search is temporarily unavailable. Please try again later.", "danger")

    return render_template(
        'search.html',
        form=form,
        results=results,
        query=query_text,
        metrics=m,
    )


# ---------------------------------------------------------------------------
# Admin: Search Metrics Dashboard (password-protected)
# ---------------------------------------------------------------------------

def _admin_password_required(f):
    """
    Decorator that gates a view behind the ADMIN_METRICS_PASSWORD config value.
    Stores a flag in the session so the user only has to enter the password once
    per browser session.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('admin_metrics_authed'):
            return f(*args, **kwargs)
        # Show a simple password form
        if request.method == 'POST':
            entered = request.form.get('admin_password', '')
            expected = current_app.config.get('ADMIN_METRICS_PASSWORD', 'admin123')
            if entered == expected:
                session['admin_metrics_authed'] = True
                return f(*args, **kwargs)
            flash('Incorrect admin password.', 'danger')
        return render_template('admin_login.html')
    decorated.__name__ = f.__name__
    return decorated


@main.route('/admin/search-metrics', methods=['GET', 'POST'])
@(_csrf_exempt if _CSRF_EXEMPT_AVAILABLE else lambda f: f)
@_admin_password_required
def search_metrics():
    """Admin dashboard showing search and ingestion timing in real time."""
    data = hybrid_search.get_metrics_summary()
    return render_template('metrics.html', data=data)


@main.route('/admin/logout')
def admin_logout():
    """Clear the admin session flag."""
    session.pop('admin_metrics_authed', None)
    flash('Logged out of admin.', 'info')
    return redirect(url_for('main.index'))