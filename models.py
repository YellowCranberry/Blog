from .__init__ import db
from datetime import datetime,timezone




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
