from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField,SubmitField
from wtforms.validators import DataRequired,Length 
from flask_ckeditor import CKEditorField



class writeBlog_form(FlaskForm):
    title= StringField('title',validators=[DataRequired(),Length(max=100)])
    description=CKEditorField('description',validators=[DataRequired(),Length(min=30,max=1000)])
    slug = StringField('slug',validators=[Length(max=100)])
    submit=SubmitField('submit')

class Search_form(FlaskForm):
    search = StringField('search',validators=[DataRequired()])
    submit = SubmitField('submit')
    