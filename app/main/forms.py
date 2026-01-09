from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField,SubmitField
from wtforms.validators import DataRequired,Length 




class writeBlog_form(FlaskForm):
    title= StringField('title',validators=[DataRequired(),Length(max=100)])
    description=TextAreaField('description',validators=[DataRequired(),Length(min=30,max=1000)])
    submit=SubmitField('submit')