import requests as rq
from . import db
from .models import Study, Variable


def sync(username, password, transmart_url, uses_post=False):
    """Creates new studies and syncs their variables"""
    token = authenticate(username, password, transmart_url, uses_post)
    if not token:
        raise ValueError("Provided username password pair is not recognized in given transmart url")
    studies = get_studies(token, transmart_url)
    existing_studies = [s.name for s in Study.query.all()]
    new_studies = []
    for study in studies:
        if study not in existing_studies:
            new_study = Study()
            new_study.name = study
            db.session.add(new_study)
            new_studies.append(new_study)
    db.session.commit()
    for new_study in new_studies:
        variables = get_variables(new_study.name, token, transmart_url)
        for variable in variables:
            variable.study_id = new_study.id
            db.session.add(variable)
    db.session.commit()


def authenticate(username, password, transmart_url, uses_post=False):
    url = """{0}/oauth/token?grant_type=password&client_id=glowingbear-js&client_secret=&username={1}&password={2}""".format(
        transmart_url, username, password)
    headers = {'Accept': 'application/json'}
    if uses_post:
        response = rq.post(url, headers=headers)
    else:
        response = rq.get(url, headers=headers)
    if response.ok:
        return response.json()['access_token']
    else:
        return None


def get_variables(study, token, transmart_url):
    """Retrieve all concepts from given transmart and then filter for leafs"""
    variables_call = "{0}/studies/{1}/concepts".format(transmart_url, study)
    headers = get_auth_headers(token)
    response = rq.get(variables_call, headers=headers)
    result = response.json()['ontology_terms']
    variables = []
    for concept in result:
        new_var = Variable()
        new_var.path = concept['fullName']
        new_var.code = concept['name']
        new_var.type = concept['type']
        variables.append(new_var)
    return variables


def get_auth_headers(token):
    return {'Accept': 'application/json', 'Authorization': "Bearer {0}".format(token)}


def get_studies(token, transmart_url):
    call = "{0}/studies".format(transmart_url)
    headers = get_auth_headers(token)
    response = rq.get(call, headers=headers)
    studies = response.json()['studies']
    studies = [s['id'] for s in studies]
    return studies


def get_patients(token, transmart_url):
    pass


def get_observations(token, transmart_url, concept_paths):
    pass

