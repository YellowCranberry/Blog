from . import db
from datetime import datetime,timezone
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin

class User(UserMixin,db.Model):
    __tablename__='users'
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(),unique=True,index=True,nullable = False)
    username =db.Column(db.String(100),unique=True,nullable=False)
    hashed_password = db.Column(db.String(),nullable=False)    
    date_added = db.Column(db.DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))
    posts = db.relationship('Blog', backref='author')
    #now i can get useremail using author.email
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.hashed_password = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.hashed_password, password)


class Blog(db.Model):
    __tablename__='blogs'
    id = db.Column(db.Integer,primary_key=True)
    title =db.Column(db.String(100),nullable=False)
    description =db.Column(db.String(255),nullable=False)
    slug = db.Column(db.String(100))
    date_added = db.Column(db.DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))
    #foriegn key to link to users
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))



    