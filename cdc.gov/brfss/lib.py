# -*- coding: utf-8 -*-
# Ambry Bundle Library File
# Use this file for code that may be imported into other bundles



import os
import subprocess

from bs4 import BeautifulSoup
import requests
import unicodecsv





class BRFSSColumn(object):
    """ Represents column specification. """
    def __init__(self, start, variable, width, position):
        self.start = int(start)  # start position of the variable value
        self.variable = variable  # name of the variable
        self.width = int(width)  # width of the variable value
        self.position = position  # position of the column


def create_source_schema(bundle):
   
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











def yield_text(bundle):
    import io
    from lxml import etree
    xml_file =  convert_xml(bundle)
    
    with io.open(xml_file, encoding='latin1') as f:
        parser = etree.XMLParser(ns_clean=True, recover = True)
        tree   = etree.parse(f, parser)
        
    for r in tree.findall('.//text'):
        yield r.text

def get_codebook_data(bundle):
    import io
    
    xml_file =  convert_xml(bundle)
    
    bundle.log("Processing XML file: {}".format(xml_file))
    
    with io.open(xml_file, encoding='latin1') as f:
        bf = BeautifulSoup(f.read())

    # first get specs from llcp_varlayout_13_onecolumn.html
    specs = get_specs(bundle)

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

    

    for text_elem in bf.select('text'):
    
        var_name = text_elem.text.encode('ascii','ignore').strip()
    
        print var_name
      
        if var_name.replace('SAS Variable Name: ','') in specs:
      
            print var_name
      
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




if __name__ == '__main__':
    create_source_schema()
