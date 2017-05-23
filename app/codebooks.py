"""
Codebooks are expected to be small in size (up to a few thousands lines for the biggest studies).
"""
from os.path import abspath
from tempfile import NamedTemporaryFile
from . import db
from .models import Study, Variable

SEP = '\t'
COLUMNS_NO = 5
IGNORE_EMPTY_LINES = True


def apply_codebook(study, codebook_file):
    mappings = _parse_codebook(codebook_file)
    _bind_codebook(study, mappings)


def _bind_codebook(study, mappings):
    variables = Variable.query.filter(Variable.study_id == study.id).all()
    var_map = {variable.code: variable for variable in variables}
    for variable_code, variable_label in mappings:
        var = var_map[variable_code]  # if validation works properly there should never be KeyError here
        var.label = variable_label
    db.session.commit()


def _parse_codebook(codebook_file):
    mappings = []
    for line in codebook_file.readlines():
        if not line and IGNORE_EMPTY_LINES:
            continue
        splittage = line.split(SEP)
        mapping = splittage[0], splittage[1]
        mappings.append(mapping)
    return mappings


def validate_codebook(codebook_file):
    invalid_lines = []
    for line_no, line in enumerate(codebook_file.readlines()):
        if not IGNORE_EMPTY_LINES and not line:
            err = line_no, 'Line is empty'
            invalid_lines.append(err)
            continue
        splittage = line.split(SEP)
        if not len(splittage) == COLUMNS_NO:
            err = line_no, "Line contains {0} columns instead of {1}. Columns need to be tab separated".format(
                len(splittage), COLUMNS_NO)
            invalid_lines.append(err)
    return invalid_lines


def generate_codebook_template(study):
    variables = Variable.query.filter(Variable.study_id == study.id).all()
    entries = []
    for variable in variables:
        line = []
        line.append(variable.code)
        line.append('REPLACE_WITH_LABEL')
        line.append(variable.type)
        line.append('')
        line.append('NA')
        line = SEP.join(line)
        entries.append(line)
    codebook_text = '\n'.join(entries)
    file_pref = "{0}_codebook_template".format(study.name)
    tmp_file = NamedTemporaryFile(delete=False, mode='w+', prefix=file_pref, suffix='.txt')
    tmp_file.write(codebook_text)
    tmp_file.close()
    return tmp_file.name
