from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,TextAreaField,SubmitField
from wtforms.validators import DataRequired,Length,EqualTo


class Registration_form(FlaskForm):
    name = StringField('Username',validators=[DataRequired(),Length(max=100)])
    email = StringField('Email',validators=[DataRequired()])
    password = PasswordField('password',validators=[DataRequired(),EqualTo('password2',message='both fields must match'),Length(min=7,max=23)])
    password2 = PasswordField('password',validators=[DataRequired(),Length(min=7,max=23)])
    submit = SubmitField('Submit')

class Login_form(FlaskForm):
    email = StringField('Username',validators=[DataRequired(),Length(max=100)])
    password = PasswordField('password',validators=[DataRequired(),Length(min=7,max=23)])
    submit = SubmitField('Submit')