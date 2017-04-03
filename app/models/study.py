from .. import db


class Study(db.Model):
    __tablename__ = 'studies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)


class Variable(db.Model):
    __tablename__ = 'variables'
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(64), unique=True)
    code = db.Column(db.String(64))
    label = db.Column(db.String(64))
    var_type = db.Column(db.String(64))



class Codebook(db.Model):
    __tablename__ = 'codebooks'
    id = db.Column(db.Integer, primary_key=True)
    attachment_id = db.Column(db.Integer)
    study_id = db.Column(db.Integer)


class Attachment(db.Model):
    __tablename__ = 'attachments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    filesystem_path = db.Column(db.String(4096))
