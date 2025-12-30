from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,TextAreaField,SubmitField
from wtforms.validators import DataRequired,Length



class User_registration_form(FlaskForm):
    name = StringField('Username',validators=[DataRequired(),Length(max=100)])
    email = StringField('Email',validators=[DataRequired()])
    password = PasswordField('password',validators=[DataRequired(),Length(min=7,max=23)])
    submit = SubmitField('Submit')



class Blog(FlaskForm):
    id=None
    title= StringField('title',validators=[DataRequired(),Length(max=100)])
    description=TextAreaField('description',validators=[DataRequired(),Length(min=30,max=1000)])
    tags=None
    submit=SubmitField('submit')