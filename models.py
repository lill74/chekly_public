from setting import db


class Users(db.Model):
    __tablename__  = 'users'
    phone = db.Column(db.String(15), primary_key=True)
    name = db.Column(db.String(10))
    schoolCode = db.Column(db.String(15))
    birthDay = db.Column(db.String(6))
    region = db.Column(db.String(9))
    time = db.Column(db.Integer)

class Errors(db.Model):
    __tablename__ = 'errors'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data = db.Column(db.Text)

class Transactions(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column(db.String(15))
    data = db.Column(db.Text)

class notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data = db.Column(db.Text)