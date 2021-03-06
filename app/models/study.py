from .. import db


class Study(db.Model):
    __tablename__ = 'studies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    patients = db.Column(db.Integer)
    variables = db.Column(db.Integer)


class Variable(db.Model):
    __tablename__ = 'variables'
    id = db.Column(db.Integer, primary_key=True)
    study_id = db.Column(db.Integer)
    path = db.Column(db.String(256))
    code = db.Column(db.String(64))
    label = db.Column(db.String(64))
    type = db.Column(db.String(64))
    in_minimal_set = db.Column(db.Boolean)  # if it is selected by default
    is_selected = False


class Codebook(db.Model):
    __tablename__ = 'codebooks'
    id = db.Column(db.Integer, primary_key=True)
    attachment_id = db.Column(db.Integer)
    study_id = db.Column(db.Integer)


class Attachment(db.Model):
    __tablename__ = 'attachments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    uuid = db.Column(db.String(4096))
    owner = db.Column(db.Integer, db.ForeignKey("users.id"))
    study_id = db.Column(db.Integer, db.ForeignKey("studies.id"))  # only one of the two can be set at the same time
    request_id = db.Column(db.Integer, db.ForeignKey("requests.id"))
