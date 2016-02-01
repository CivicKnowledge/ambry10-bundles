# -*- coding: utf-8 -*-
import os
import subprocess

from bs4 import BeautifulSoup
import requests
import unicodecsv

""" Helper for convert CODEBOOK13_LLCP.pdf and llcp_varlayout_13_onecolumn.html to sources_schema.csv. """

FILE_DIR = os.path.abspath(os.path.dirname(__file__))

# _PSU is alias for SEQNO, IDATE is alias for year, month, date. Should skip both.
VARIABLES_TO_SKIP = ('_PSU', 'IDATE')

# Columns listed here exist in the html but not in pdf.
COLUMNS_TO_SKIP = (
    '2259-_FRTLT1',
    '2260-_VEGLT1',
)


class BRFSSColumn(object):
    """ Represents column specification. """
    def __init__(self, start, variable, width, position):
        self.start = int(start)  # start position of the variable value
        self.variable = variable  # name of the variable
        self.width = int(width)  # width of the variable value
        self.position = position  # position of the column


def _ensure_pdf_converted():
    """ Finds xml of the converted pdf. If not found, downloads pdf and converts to xml. """
    pdf_file = os.path.join(FILE_DIR, 'CODEBOOK13_LLCP.pdf')
    xml_file = os.path.join(FILE_DIR, 'CODEBOOK13_LLCP.xml')

    def download(pdf_path):
        print('Downloading codebook. Please wait...')
        url = 'http://www.cdc.gov/brfss/annual_data/2013/pdf/CODEBOOK13_LLCP.pdf'
        response = requests.get(url)
        assert response.status_code == 200
        with open(pdf_path, 'wb') as f:
            f.write(response.content)

    def convert(pdf_path, xml_path):
        print('Converting codebook to xml. Please wait...')
        call_args = ['pdftohtml', pdf_file, xml_file, '-xml']
        process = subprocess.Popen(call_args)
        if process.wait() != 0:
            print('Errors while converting pdf to xml.')

    if os.path.exists(xml_file):
        pass
    elif os.path.exists(pdf_file):
        # downloaded but not converted.
        convert(pdf_file, xml_file)
    else:
        # no converted, no downloaded
        download(pdf_file)
        convert(pdf_file, xml_file)


def create_source_schema():
    _ensure_pdf_converted()

    sources_schema_file = os.path.join(FILE_DIR, 'source_schema.csv')
    header = [
        'table',
        'position',
        'source_header',
        'dest_header',
        'datatype',
        'valuetype',
        'start',
        'width',
        'size',
        'summary',
        'description'
    ]

    with open(sources_schema_file, 'wb') as csvfile:
        writer = unicodecsv.writer(csvfile)
        writer.writerow(header)

        visited = []
        sorted_by_position = sorted(_get_codebook_data().items(), key=lambda tpl: tpl[1]['position'])
        for var_name, var_spec in sorted_by_position:
            # Do not allow dupes.
            assert var_name not in visited
            visited.append(var_name)
            source_header = var_name
            dest_header = var_name
            if var_spec['type'] == 'Num':
                datatype = 'float'
            elif var_spec['type'] == 'Char':
                datatype = 'str'
            else:
                raise Exception('Do not know how to convert {} type.'.format(var_spec['type']))

            valuetype = ''
            size = ''
            summary = ''
            description = var_spec['description']
            try:
                writer.writerow([
                    'brfss2013', var_spec['position'], source_header, dest_header, datatype, valuetype,
                    var_spec['start'], var_spec['width'], size, summary, description])
            except Exception as exc:
                import pdb; pdb.set_trace()


def _get_codebook_data():
    xml_file = os.path.join(FILE_DIR, 'CODEBOOK13_LLCP.xml')
    with open(xml_file) as f:
        bf = BeautifulSoup(f.read())

    # first get specs from llcp_varlayout_13_onecolumn.html
    specs = _get_specs()

    # now extend types obtained from CODEBOOK13_LLCP.pdf
    visited_columns = {}
    updated = set([])

    MANUAL_FIXES = {
        # There are really complicated vars, so it's easier to add them by hands.
        'BLOODCHO': {
            'type': 'Num',
            'start': 95,
            'end': 95,
            'position': specs['BLOODCHO']['position'],
            'width': 1,
            'description': 'Blood cholesterol is a fatty substance found '
                           'in the blood. Have you EVER had your blood cholesterol checked?'
        },
        'PSATEST1': {
            'type': 'Num',
            'start': 404,
            'end': 404,
            'position': specs['PSATEST1']['position'],
            'width': 1,
            'description': 'Have you EVER HAD a PSA test?'
        },
        'CARERCVD': {
            'type': 'Num',
            'start': 344,
            'end': 344,
            'position': specs['CARERCVD']['position'],
            'width': 1,
            'description': 'In general, how satisfied are you with the health '
                           'care you received? Would you say'
        }
    }

    for page_elem in bf.select('page'):
        for text_elem in page_elem.select('text'):
            if text_elem.text.strip() in specs:
                var_name = text_elem.text.strip()

                if var_name in VARIABLES_TO_SKIP:
                    continue

                if var_name in MANUAL_FIXES:
                    specs[var_name] = MANUAL_FIXES[var_name]
                    updated.add(var_name)
                    continue

                var_type = None
                description = None
                start_column = None
                end_column = None
                # look for variable type and columns in the previous siblings.
                for prev_elem in [x for x in text_elem.previous_siblings if x != '\n']:
                    if prev_elem.text.strip() == 'Type:':
                        var_type = prev_elem.next_sibling.next_sibling.text.strip()
                    if prev_elem.text.strip() == 'Column:':
                        column = prev_elem.next_sibling.next_sibling.text.strip()
                        if '-' in column:
                            start_column, end_column = column.split('-')
                            start_column = int(start_column)
                            end_column = int(end_column)
                        else:
                            start_column = end_column = int(column)
                    if var_type and start_column and end_column:
                        break

                if '{}-{}'.format(start_column, var_name) in COLUMNS_TO_SKIP:
                    continue

                if column in visited_columns and visited_columns[column]['var_name'] != var_name:
                    raise Exception(
                        '`{}` column already visited with `{}` variable. Requires manual resolve.'
                        .format(column, visited_columns[column]['var_name']))
                # Some descriptions are hard to obtain. Set them manually.
                DESCRIPTIONS = {
                    'CTELNUM1': 'Is this (phone number)?',
                    '_PRACE1': 'Preferred race category',
                    '_AGE80': 'Imputed Age value collapsed above 80',
                }
                description = DESCRIPTIONS.get(var_name, None)

                # look for the first description in the next siblings.
                if not description:
                    for next_elem in [x for x in text_elem.next_siblings if x != '\n']:
                        if next_elem.text.strip() == 'Description:':
                            description = next_elem.next_sibling.next_sibling.text.strip()
                            break

                assert start_column
                assert end_column
                assert description, 'No description found for `{}` variable.'.format(var_name)
                if var_type not in ('Num', 'Char'):
                    raise Exception(
                        'Invalid type `{}` found in `{}` var. Find real value and add manual resolve.'
                        .format(var_type, var_name))

                # Variables listed here may have description less then 8.
                SHORT_DESCRIPTION = [
                ]

                NO_SPACE_DESCRIPTION = {
                    'DROCDY3_': 'Drink-occasions-per-day',
                }

                if var_name not in SHORT_DESCRIPTION and len(description) < 8:
                    raise Exception(
                        'Fishily short description `{}` for `{}` variable. Add to exclude list if it is correct.'
                        .format(description, var_name))

                if var_name not in NO_SPACE_DESCRIPTION and ' ' not in description.strip():
                    raise Exception(
                        '`{}` description of `{}` variable does not have any spaces. Add to exclude list if it is correct.'
                        .format(var_name, description))

                if start_column != specs[var_name]['start']:
                    raise Exception('start column mismatch for {} variable'.format(var_name))
                if end_column != specs[var_name]['start'] + specs[var_name]['width'] - 1:
                    raise Exception('end column mismatch for {} variable'.format(var_name))
                current = {
                    'type': var_type,
                    'description': description,
                    'end': int(end_column),
                }
                if var_name not in updated:
                    visited_columns[column] = {'var_name': var_name}
                    specs[var_name].update(current)
                    updated.add(var_name)

    # some validation of the obtained data.
    assert len(specs) == len(updated), \
        'Not all columns updated: specs amount = {}, updated amount = {}' \
        .format(len(specs), len(updated))

    # Some manual checks.
    assert specs['STRFREQ_']['start'] == 2312
    assert specs['STRFREQ_']['end'] == 2316
    assert specs['STRFREQ_']['type'] == 'Num'
    assert specs['STRFREQ_']['description'] == 'Strength Activity Frequency per Week'
    return specs


def _get_specs():
    """ Returns list with column specs. """

    url = 'http://www.cdc.gov/brfss/annual_data/2013/llcp_varlayout_13_onecolumn.html'
    response = requests.get(url)
    assert response.status_code == 200, \
        'Download error: status_code: {}, text: {}'.format(response.status_code, response.text)

    bf = BeautifulSoup(response.text)
    tables = bf.select('table')
    assert len(tables) == 1
    table = tables[0]
    specs = {}
    position = 1

    for i, tr in enumerate(table.select('tr')):
        if i == 0:
            assert 'Is header'
            continue
        row = [' '.join(x.strings) for x in tr.select('td')]
        assert len(row), 3
        start, var_name, width = row
        position = position
        if var_name in VARIABLES_TO_SKIP:
            continue
        if '{}-{}'.format(start, var_name) in COLUMNS_TO_SKIP:
            continue

        assert var_name not in specs
        specs[var_name] = {
            'start': int(start),
            'width': int(width),
            'position': position}
        position += 1
    return specs


if __name__ == '__main__':
    create_source_schema()
