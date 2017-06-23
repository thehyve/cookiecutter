from urllib.parse import quote
import requests as rq
from pandas import DataFrame
from . import db
from .models import Study, Variable

CONCEPT_SEP = '\\'
STUDY_NODE_INDEX = 3  # index of the study node in the full concept path


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
        patients = get_patients(new_study.name, token, transmart_url)
        new_study.patients = len(patients)
        new_study.variables = len(variables)
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


def get_patients(study, token, transmart_url):
    call = "{0}/studies/{1}/subjects".format(transmart_url, study)
    headers = get_auth_headers(token)
    response = rq.get(call, headers=headers)
    patients = response.json()["subjects"]
    return patients


def _get_observations(token, transmart_url, study, concept_path):
    """
    Given full concept path (as returned from tm 1.2 rest-api /concepts) return dict
    of patient_id : value
    :param token: 
    :param transmart_url: 
    :param study: 
    :param concept_path: 
    :return: 
    """
    obs = {}
    concept_path = _get_relative_concept_path(concept_path)
    call = "{0}/studies/{1}/concepts/{2}/observations".format(transmart_url, study, concept_path)
    headers = get_auth_headers(token)
    response = rq.get(call, headers=headers)
    for observation in response.json():
        patient_id = observation['subject']['id']
        obs[patient_id] = observation['value']
    return obs


def get_observations(token, transmart_url, study, concept_paths):
    """
    Given an iterable of concept paths (as returned from tm 1.2 rest-api /concepts) return dict
    of concept_path : dict(patient_id:value) 
    :param token: 
    :param transmart_url: 
    :param study: 
    :param concept_paths: 
    :return: 
    """
    obs = {concept: _get_observations(token, transmart_url, study, concept) for concept in concept_paths}
    return obs


def observations_to_tsv(obs):
    df = DataFrame(obs)
    return df.to_csv(sep='\t')  # TODO: might choke on really big exports


def _get_relative_concept_path(full_concept_path):
    sp = full_concept_path.split(CONCEPT_SEP)
    sp = sp[STUDY_NODE_INDEX:-1]
    relative_concept_path = "/".join(sp)
    return quote(relative_concept_path)
