from . import main
from flask import render_template,redirect,url_for,request,session,flash, current_app
from flask_login import login_required,current_user
from ..models import User,Blog
from .forms import writeBlog_form,Search_form
from .. import db, cache


@main.route('/')
@cache.cached( timeout =50)
def index():
    blogs = Blog.query.order_by(Blog.id.desc())[0:2]
    # print(type(blogs))
    return render_template('index.html',blogs=blogs)


@main.route('/mypage')
@login_required
def mypage():
    return 'only verified'

@main.route('/blog',methods=['GET','POST'])
@login_required
def write_blog():
    form = writeBlog_form()
    if form.validate_on_submit():
        new_blog = Blog(
            title=form.title.data,
            description=form.description.data,
            slug=form.slug.data,
            author=current_user
        )
        db.session.add(new_blog)
        db.session.commit()

        current_app.search_engine.ingest_text(
            text=form.description.data,
            metadata={
                "title": form.title.data,
                "slug": form.slug.data,
                "id": new_blog.id
            }
        )

        return redirect(url_for('main.write_blog'))
    return render_template('write_blog.html',form = form) 


@main.route('/posts/<int:id>')
def newpost(id):
    blog = Blog.query.filter_by(id=id).first()
    if blog:
        return render_template('single_post.html',blog = blog)
    else:
        return f"some error occured"

@main.route('/posts/edit/<int:id>',methods=['GET','POST'])
@login_required
def editpost(id):
    blog = Blog.query.get_or_404(id)
    if blog.author != current_user:
        flash('u don\'t have access to edit this post')
        return redirect(url_for('main.newpost',id=id))
    form = writeBlog_form(obj=blog)
    # or you can just copy paste values of blog into form
    if form.validate_on_submit():
        # blog.title=form.title.data
        # blog.slug=form.slug.data
        # blog.description = form.description.data
        form.populate_obj(blog) #this way i can directly populate blog object with form details
        db.session.commit()
        return redirect(url_for('main.newpost',id=id))
    return render_template('edit_post.html',blog = blog,form=form)

@main.route('/posts/delete/<int:id>')
@login_required
def deletePost(id):
    blog_to_delete = Blog.query.get_or_404(id)
    if blog_to_delete.author !=current_user:
        flash("u dont have access to delete this post")
        return redirect(url_for('main.newpost',id=id))
    try:
        db.session.delete(blog_to_delete)
        db.session.commit()
        flash("Blog deleted successfully",'warning')
        return redirect(url_for('.posts'))
    except:
        return f"some problem occured i think"  




# @main.route("/deleteit")
# def deleteit():
#     User.query.delete()
#     db.session.commit()
#     return "done"



# for search-bar to get searchform we initialized in context processor so its avail everywhere now with search_form name  
@main.app_context_processor
def pass_formto_searchbar():
    form = Search_form()
    return dict(search_form=form)


@main.route("/search" ,methods =["GET","POST"])
def search():
    form = Search_form()
    if form.validate_on_submit():
        session['query']= form.search.data
        return redirect(url_for('.search'))
    query_text = session.pop('query', None)
    if not query_text:
        return redirect(url_for('main.index'))
    
    results = current_app.search_engine.search(query_text, top_k=5)
    return render_template('search.html', form=form, results=results, query=query_text)
    # blogs = Blog.query
    # blogs = blogs.filter(Blog.description.like('%'+description+'%'))
    # blogs = blogs.order_by(Blog.title).all()
    # return render_template('search.html',form =form,blogs=blogs)










##mayank
@main.route('/dashboard')
@login_required
def dashboard():
    # Filter directly by the database column 'author_id' matching the logged-in user's ID
    user_blogs = Blog.query.filter_by(author_id=current_user.id).order_by(Blog.id.desc()).all()
    
    return render_template('dashboard.html', blogs=user_blogs)


@main.route('/posts')
def posts():
    # 1. Grab the page number from the URL (default to 1 if it doesn't exist)
    page = request.args.get('page', 1, type=int)
    
    # 2. Use .paginate() instead of .all()
    # per_page=4 sets the limit. error_out=False prevents crashing if a user types ?page=1000
    # I also added .desc() so your newest posts show up first!
    blogs = Blog.query.order_by(Blog.id.desc()).paginate(page=page, per_page=4, error_out=False)
    
    return render_template('show_posts.html', blogs=blogs)