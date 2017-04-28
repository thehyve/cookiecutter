"""
Codebooks are expected to be small in size (up to a few thousands lines for the biggest studies).
"""
from . import db
from .models import Study, Variable


SEP='\t'
COLUMNS_NO = 5
IGNORE_EMPTY_LINES = True

def bind_codebook(study, mappings):
    study = Study.query.filter(Study.name == study).first()
    variables = Variable.query.filter(Variable.study_id == study.id).all()
    var_map = {variable.name: variable for variable in variables}
    for variable_code, variable_label in mappings:
        var = var_map[variable_code] # if validation works properly there should never be KeyError here
        var.label = variable_label
    db.session.commit()



def parse_codebook(codebook_file):
    mappings = []
    with open(codebook_file) as infile:
        for line in infile.readlines():
            if not line and IGNORE_EMPTY_LINES:
                continue
            splittage = line.split(SEP)
            mapping = splittage[0], splittage[1]
            mappings.append(mapping)
    return mappings


def validate_codebook(codebook_file):
    invalid_lines = []
    with open(codebook_file) as infile:
        for line_no, line in enumerate(infile.readlines()):
            if not IGNORE_EMPTY_LINES and not line:
                err = line_no, 'Line is empty'
                invalid_lines.append(err)
                continue
            splittage = line.split(SEP)
            if not len(splittage) == COLUMNS_NO:
                err = line_no, "Line contains {0} columns instead of {1}. Columns need to be tab separated".format(len(splittage), COLUMNS_NO)
                invalid_lines.append(err)
    return invalid_lines

