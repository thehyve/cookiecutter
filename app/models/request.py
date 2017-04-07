from .. import db


class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    study_id = db.Column(db.Integer)


class RequestVariable(db.Model):
    __tablename__ = 'request_variables'
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer)
    variable_id = db.Column(db.Integer)


class RequestFieldAnswer(db.Model):
    __tablename__ = 'request_field_answer'
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer)
    variable_id = db.Column(db.Integer)
    answer = db.Column(db.Text)


class RequestProcess(db.Model):
    __tablename__ = 'request_processes'
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.Integer, unique=True)


class ProcessStep(db.Model):
    __tablename__ = 'process_steps'
    id = db.Column(db.Integer, primary_key=True)
    request_process_id = db.Column(db.Integer)
    name = db.Column(db.String(64))
    description = db.Column(db.Text)
    final = db.Column(db.Boolean)
    approves = db.Column(db.Boolean)
    denies = db.Column(db.Boolean)


class RequestField(db.Model):
    __tablename__ = 'request_fields'
    id = db.Column(db.Integer, primary_key=True)
    process_id = db.Column(db.Integer)
    name = db.Column(db.String(64))
    mandatory = db.Column(db.Boolean)
