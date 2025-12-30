from flask import Flask
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

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

#run
if __name__=="__main__":
    app.run(debug=True)