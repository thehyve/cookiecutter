from .. import db


class Transmart(db.Model):
    __tablename__ = 'transmarts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    version = db.Column(db.String(64))
    url = db.Column(db.String(128))
