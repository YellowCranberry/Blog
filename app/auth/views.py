from flask import render_template,redirect,session,url_for,flash
from . import auth
from .forms import LoginForm,RegistrationForm
from ..models import User
from .. import db

@auth.route('/login',methods =['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('user not found','warning')
            return redirect(url_for('auth.register'))
        else:
            if user.verify_password(form.password.data):
                session['known']=True
                session['email']=form.email.data   
                return redirect(url_for('main.index'))
            else:
                session['known']=False
                flash('wrong email or password','warning')
                return redirect(url_for('auth.register'))
    return render_template('login.html',form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Already registered', 'warning')
        else:
            user = User(username=form.username.data, email=form.email.data)
            user.password = form.password.data
            db.session.add(user)
            db.session.commit()
            flash('Registered successfully', 'success')
            return redirect(url_for('auth.login'))

    return render_template('registration.html', form=form)
