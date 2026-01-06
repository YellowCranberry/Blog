from . import auth
from app.extensions import db
from .forms import Registration_form,Login_form    
from ..models import User
from ..helpers.decorators import login_required
from flask import flash,render_template,url_for,session,redirect,request



@auth.route('/register',methods =['GET','POST'])
def register():
    form = Registration_form()
    # already registered
    # register kr liye fir main page pe le jana hai 
    # session wgera ki bkchodi hogi 
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data)
        if user is None:
            items_to_add = [User(username = form.name.data,email=form.name.data,password_hash =form.password.data)]
            db.session.add_all(items_to_add)
            db.session.commit()
            flash('user registered successfully','success')
        else:
            flash('user already registered','warning')    
        return redirect(url_for('auth.login'))
    return render_template('register.html')


@auth.route('/login',methods=['GET','POST'])
def login():
    form = Login_form()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data)
        if user is not None and user.verify_password(form.password.data):
            session['user']=user.username
            return redirect( url_for('main.home'))
        else:
            flash('invalid username or password','warning')            
        return redirect(url_for('login'))
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    session.clear() 
    return redirect(url_for('main.home'))
