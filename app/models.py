from app.extensions import db
from datetime import datetime,timezone
from werkzeug.security import check_password_hash,generate_password_hash 



class User(db.Model):
    __tablename__='users'
    id = db.Column(db.Integer,primary_key=True)
    username =db.Column(db.String(100),unique=True,nullable=False)
    email = db.Column(db.String(),unique=True,index=True,nullable = False)
    password_hash = db.Column(db.String(),nullable=False)
    date_added = db.Column(db.DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
   
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
        



class BlogData(db.Model):
    __tablename__='blog'
    id = db.Column(db.Integer,primary_key=True)
    title =db.Column(db.String(100),nullable=False)
    description =db.Column(db.String(),nullable=False)
    date_added = db.Column(db.DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))
