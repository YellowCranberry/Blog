from flask import Flask,render_template,redirect,session,url_for,flash
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField,TextAreaField
from wtforms.validators import DataRequired,Email,Length,email
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timezone

#creating instances of class
app = Flask(__name__)
moment = Moment(app)
bootstrap = Bootstrap(app)

#configuration
app.config['SECRET_KEY']='hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_data.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #ye kya krta hai ab?

#database
db = SQLAlchemy(app)#isko alag se intialize krna pda 


#classes
class User_registration_form(FlaskForm):
    name = StringField('Username',validators=[DataRequired(),Length(max=100)])
    email = StringField('Email',validators=[DataRequired()])
    password = PasswordField('password',validators=[DataRequired(),Length(min=7,max=23)])
    submit = SubmitField('Submit')

class User(db.Model):
    __tablename__='users'
    id = db.Column(db.Integer,primary_key=True)
    username =db.Column(db.String(100),unique=True,nullable=False)
    email = db.Column(db.String(),unique=True,index=True,nullable = False)
    password = db.Column(db.String(),nullable=False)
    date_added = db.Column(db.DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))

class BlogData(db.Model):
    __tablename__='blog'
    id = db.Column(db.Integer,primary_key=True)
    title =db.Column(db.String(100),nullable=False)
    description =db.Column(db.String(),nullable=False)
    date_added = db.Column(db.DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))

class Blog(FlaskForm):
    id=None
    title= StringField('title',validators=[DataRequired(),Length(max=100)])
    description=TextAreaField('description',validators=[DataRequired(),Length(min=30,max=1000)])
    tags=None
    submit=SubmitField('submit')
    
        

#routes
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



#run
if __name__=="__main__":
    app.run(debug=True)