from . import main
from flask import render_template,redirect,url_for,request,session,flash
from flask_login import login_required
from ..models import User,Blog
from .forms import writeBlog_form
from .. import db

@main.route('/')
def index():

    return render_template('index.html')


@main.route('/mypage')
@login_required
def mypage():
    return 'only verified'

@main.route('/blog',methods=['GET','POST'])
def write_blog():
    form = writeBlog_form()
    if form.validate_on_submit():
        items_to_add = Blog(title = form.title.data,description=form.description.data,slug=form.slug.data)
        db.session.add(items_to_add)
        db.session.commit()
        return redirect(url_for('main.write_blog'))
    blogs = Blog.query.order_by(Blog.date_added.desc()).all()
    return render_template('write_blog.html',form = form,blogs = blogs) 

@main.route('/posts')
def posts():
    blogs = Blog.query.order_by(Blog.id).all()
    return render_template('show_posts.html',blogs = blogs)

@main.route('/posts/<int:id>')
def newpost(id):
    blog = Blog.query.filter_by(id=id).first()
    if blog:
        return render_template('single_post.html',blog = blog)
    else:
        return f"some error occured"

@main.route('/posts/edit/<int:id>',methods=['GET','POST'])
def editpost(id):
    blog = Blog.query.filter_by(id=id).first()
    form = writeBlog_form(obj=blog)
    if form.validate_on_submit():
        # blog.title=form.title.data
        # blog.slug=form.slug.data
        # blog.description = form.description.data
        form.populate_obj(blog) #this way i can directly populate blog object with form details
        db.session.commit()
        return redirect(url_for('main.newpost',id=id))
    return render_template('edit_post.html',blog = blog,form=form)

@main.route('/posts/delete/<int:id>')
def deletePost(id):
    blog_to_delete = Blog.query.get_or_404(id)
    try:
        db.session.delete(blog_to_delete)
        db.session.commit()
        flash("Blog deleted successfully",'warning')
        return redirect(url_for('.posts'))
    except:
        return f"some problem occured i think"