from . import main
from flask import render_template,redirect,url_for,request,session
from flask_login import login_required
from ..models import User,BlogForm
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
        items_to_add = BlogForm(title = form.title.data,description=form.description.data)
        db.session.add(items_to_add)
        db.session.commit()
        return redirect(url_for('main.write_blog'))
    blogs = BlogForm.query.order_by(BlogForm.date_added.desc()).all()
    return render_template('write_blog.html',form = form,blogs = blogs) 