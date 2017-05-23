import os
from uuid import uuid4
from os.path import join
from .models import Attachment
from . import db

FILESTORE_PATH = '~/.dp_filestore'  # TODO: make configurable


def make_dataset(observations_tsv_str, user, request):
    return register_request_attachment(observations_tsv_str, 'data.txt', user, request, False)


def register_study_attachment(attachment_file_content, original_name, user, study):
    new_attachment = _register_attachment(attachment_file_content, original_name, user)
    new_attachment.study_id = study.id
    db.session.add(new_attachment)
    db.session.commit()
    return new_attachment


def register_request_attachment(attachment_file_content, original_name, user, request, binary_content=True):
    new_attachment = _register_attachment(attachment_file_content, original_name, user, binary_content)
    new_attachment.request_id = request.id
    db.session.add(new_attachment)
    db.session.commit()
    return new_attachment


def _register_attachment(attachment_file_content, original_name, user):
    file_uuid = _deposit_file(attachment_file_content)
    new_attachment = Attachment()
    new_attachment.uuid = file_uuid
    new_attachment.owner = user.id
    new_attachment.name = original_name
    return new_attachment


def _deposit_file(attachment_file_content, binary=True):
    """ Deposit contents of the file into the filestore. 
    Returns uuid identifying it."""
    if binary:
        mode = 'bw'
    else:
        mode = 'w'
    file_uuid = str(uuid4())
    path = join(FILESTORE_PATH, file_uuid)
    with open(path, mode) as outfile:
        outfile.write(attachment_file_content)
    return file_uuid


def remove_file(attachment_id):
    """
    Remove attachment entry and the corresponding file
    :param attachment_id: 
    :return: 
    """
    attachment = Attachment.query.filter(Attachment.id == attachment_id).first()
    corresponding_file = join(FILESTORE_PATH, attachment.uuid)
    os.unlink(corresponding_file)
    db.session.delete(attachment)
    db.session.commit()
