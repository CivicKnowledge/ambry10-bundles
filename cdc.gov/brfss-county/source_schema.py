# -*- coding: utf-8 -*-

""" Helper to create sources_schema.csv. """

import os
import re

import requests
import unicodecsv

FILE_DIR = os.path.abspath(os.path.dirname(__file__))
HELPERS_DIR = os.path.join(FILE_DIR, 'helpers')


class Column(object):
    """ Represents column specification. """
    def __init__(self, start, variable, width, position):
        self.start = int(start)  # start position of the variable value
        self.variable = variable  # name of the variable
        self.width = int(width)  # width of the variable value
        self.position = position  # position of the column
        self.type = None  # Will be populated from outside.

    def __repr__(self):
        return '{}({})'.format(self.variable, self.type)


class SourceSchemaBuilder(object):

    def __init__(self):
        self._columns = []

    def get_columns(self):
        """ Downloads codebook and converts it to list of Column elements. """
        print('Downloading codebook. Please wait...')
        url = 'http://www.cdc.gov/brfss/smart/2012/CNTY12_SASOUT.SAS'
        response = requests.get(url)
        assert response.status_code == 200
        sas_file = os.path.join(HELPERS_DIR, 'CNTY12_SASOUT.SAS')
        with open(sas_file, 'wb') as f:
            f.write(response.content)

        # parse and create list of columns
        print('Converting codebook...')
        self._columns = []
        inside = False

        rep = re.compile(r'([^\s]+)\s+\$?([^\s]+)')
        position = 1

        with open(sas_file) as f:
            for line in f.readlines():

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
                        self._columns.append(Column(start, var, width, position))
                        position += 1
        assert len(self._columns) == 138

    def add_types(self):
        """ Adds type to each column.

        Args:
            columns (list of Column):

        Note:
            I have no idea how primary developer got types. And I have no idea how to get types
            from brfss site. So code here copyes types from primary developer schema file.
            URL of the old schema file: https://github.com/CivicKnowledge/pre-10-bundles/blob/master/national-bundles/cdc.gov/brfss-county/meta/schema.csv

        Returns:
            list of Column

        """
        print('Populating types...')
        column_to_type_map = {}
        with open(os.path.join(HELPERS_DIR, 'old_schema.csv')) as f:
            reader = unicodecsv.DictReader(f)
            for i, row in enumerate(reader):
                column_to_type_map[row['column']] = row['type']

        for column in self._columns:
            variable = column.variable.lower().rstrip('_')
            column.type = column_to_type_map[variable]

    def dump(self):
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
        sources_schema_file = os.path.join(FILE_DIR, 'source_schema.csv')

        with open(sources_schema_file, 'wb') as csvfile:
            writer = unicodecsv.writer(csvfile)
            writer.writerow(header)

            sorted_by_position = sorted(self._columns, key=lambda c: c.position)
            for column in sorted_by_position:
                # Do not allow dupes.
                source_header = column.variable
                dest_header = column.variable
                if column.type == 'INTEGER':
                    datatype = 'int'
                elif column.type == 'INTEGER64':
                    datatype = 'long'
                elif column.type == 'VARCHAR':
                    datatype = 'str'
                elif column.type == 'REAL':
                    datatype = 'float'
                else:
                    raise Exception('Do not know how to convert {} type.'.format(column.type))

                valuetype = ''
                size = ''
                summary = ''
                description = ''
                writer.writerow([
                    'brfss_county', column.position, source_header, dest_header, datatype, valuetype,
                    column.start, column.width, size, summary, description])


def create_source_schema():
    builder = SourceSchemaBuilder()
    builder.get_columns()
    builder.add_types()
    builder.dump()


if __name__ == '__main__':
    create_source_schema()
    print('Done.')
