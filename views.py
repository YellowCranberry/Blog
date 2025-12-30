from .__init__ import app,db
from flask import render_template,redirect,url_for,flash,session
from .forms import Blog,User_registration_form
from .models import BlogData,User

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/Create_blog',methods=['GET','POST'])
def Create_blog():
    my_blog = Blog()
    if my_blog.validate_on_submit():
        items_to_add=[BlogData(title=my_blog.title.data,description=my_blog.description.data)]
        db.session.add_all(items_to_add)
        db.session.commit()
        
        return redirect(url_for('Create_blog'))
    return render_template('Create_blog.html',form=my_blog)
    



    

@app.route('/newform',methods=['GET','POST'])
def newform():
    form = User_registration_form()
    if form.validate_on_submit():
        user = User.query.filter_by(email =form.email.data).first()
        if user is None:
            items_to_add =[User(username = form.name.data,email =form.email.data,password=form.password.data)]
            db.session.add_all(items_to_add)
            db.session.commit()
            flash('user registered successfully','success')
        else:
            flash('user already registered','warning')
        return redirect(url_for("newform"))
    return render_template("form.html",form=form)    



@app.route("/register",methods=['GET','POST'])
def register():
    form = User_registration_form()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data,email = form.email.data,password=form.password.data)
            db.session.add(user)
            db.session.commit()    
            session['known']=False
        else:
            session['known']=True
        #now add session so that when reload we go into a get request
        session['name']=form.name.data
        session['email']=form.email.data
        session['pass']=form.password.data
        return redirect(url_for('register'))
    return render_template('registration.html',form=form,name=session.get('name'),email=session.get('email'),password=session.get('pass'),known=session.get('known'))

