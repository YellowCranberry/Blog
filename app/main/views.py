from . import main
from ..helpers.decorators import login_required
from flask import render_template,session



@main.route('/')
def home():
    username = session.get('user')   # will be None if not logged in
    return render_template('home.html',username=username)



# @main.route('/Create_blog',methods=['GET','POST'])
# def Create_blog():
#     my_blog = Blog()
#     if my_blog.validate_on_submit():
#         items_to_add=[BlogData(title=my_blog.title.data,description=my_blog.description.data)]
#         db.session.add_all(items_to_add)
#         db.session.commit()
        
#         return redirect(url_for('Create_blog'))
#     return render_template('Create_blog.html',form=my_blog)