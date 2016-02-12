# -*- coding: utf-8 -*-
# Ambry Bundle Library File
# Use this file for code that may be imported into other bundles






# -*- coding: utf-8 -*-

""" Helper to create sources_schema.csv. """

import os
import re

import requests
import unicodecsv

#FILE_DIR = os.path.abspath(os.path.dirname(__file__))
#HELPERS_DIR = os.path.join(FILE_DIR, 'helpers')


class Column(object):
    """ Represents column specification. """
    def __init__(self, start, variable, width, position):
        self.start = int(start)  # start position of the variable value
        self.variable = variable  # name of the variable
        self.width = int(width)  # width of the variable value
        self.position = position  # position of the column
        self.type = None  # Will be populated from outside.


    def __repr__(self):
        return '{}({} {} {})'.format(self.variable, self.start, self.width, self.type)


def get_columns(bundle):
    """ Downloads codebook and converts it to list of Column elements. """
    print('Downloading codebook. Please wait...')

    response = requests.get(bundle.source('columnspec').ref)

    inside = False

    rep = re.compile(r'([^\s]+)\s+\$?([^\s]+)')
    position = 1
    columns = []

    for line in response.content.splitlines():

        if line.startswith('INPUT'):
            inside = True
            continue

        if line.startswith('ENDOFREC'):
            break

        if inside:
            m = rep.match(line)
            if m:
                var, span = m.groups()
                if '-' in span:
                    start, end = span.split('-')
                    width = int(end) - int(start) + 1
                else:
                    start = span
                    width = 1
                columns.append(Column(start, var, width, position))
                position += 1
                
    assert len(columns) == 138
    
    return columns

def meta_source_schema(bundle):

    columns = get_columns(bundle)

    bundle.dataset.source_tables[:] = []
    bundle.commit() 
    
    t = bundle.dataset.new_source_table('brfss')
    
    for i,c in enumerate(columns,1):
        t.add_column(source_header=c.variable,
                     dest_header=c.variable.lower(),
                     position=i,
                     datatype=None,
                     description=c.variable,
                     start = c.start,
                     width=c.width
                     )
               
    bundle.build_source_files.sourceschema.objects_to_record()      
    bundle.commit()
        


