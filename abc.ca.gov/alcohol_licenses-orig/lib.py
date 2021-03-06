# -*- coding: utf-8 -*-
# Ambry Bundle Library File
# Use this file for code that may be imported into other bundles
import os

from datetime import datetime, date

from bs4 import BeautifulSoup
import requests

API_URL = 'http://www.abc.ca.gov/datport/AHCityRep.asp'

DATE_FORMAT = '%m-%d-%Y'

HEADER = [
    'License Number', 'Status', 'License Type', 'Orig. Iss. Date',
    'Expir Date', 'Primary Owner', 'Premises Addr.', 'Tract', 'Business Name',
    'Mailing Address', 'Geo Code']

CITIES = [
    'Carlsbad',
    'Chula Vista',
    'Coronado',
    'Del Mar',
    'El Cajon',
    'Encinitas',
    'Escondido',
    'Imperial Beach',
    'La Mesa',
    'Lemon Grove',
    'National City',
    'Oceanside',
    'Poway',
    'San Diego',
    'San Marcos',
    'Santee',
    'Solana Beach',
    'Vista',
]


class AlcoholLicensesDataGenerator(object):

    def __init__(self, bundle, source=None):
        self._bundle = bundle
        self._source = source

    def __iter__(self):
        """ Generates header and rows with data of all cities. """

        header = None

        for city in CITIES:
            self._bundle.log('Getting `{}` city page content'.format(city))
            page = self._download_page(city, report_type='p_Retail')

            if not header:
                header = HEADER
                self._bundle.debug('Generate header: {}'.format(header))
                yield header

            self._bundle.log('Parsing {} city page'.format(city))
            bf = BeautifulSoup(page)

            tr_elems = bf.select('tr.report_column')

            # We are going to skip first row, so ensure it's a header.
            self._assert_contains_header(tr_elems[0])
            for i, tr_elem in enumerate(tr_elems[1:]):
                row = self._retrieve_row(tr_elem)
                self._bundle.debug('{} row of {} city retrieved as {}'.format(i, city, row))

                if row:
                    new_row = self._convert_row(row)
                    self._bundle.debug(
                        'Row conversion:\n  city: {},\n  row_index: {},\n  old_row: {},\n  new_row: {}'
                        .format(city, i, row, new_row))
                    yield new_row

    def _assert_contains_header(self, tr_elem):
        header = []
        for th_elem in tr_elem.select('th'):
            header.append(' '.join(th_elem.strings).strip())
        assert header[1].lower() == HEADER[0].lower(), \
            'Header mismatch: expected: {}, downloaded: {}'.format(HEADER[1], header[1])
        assert header[2].lower() == HEADER[1].lower(), \
            'Header mismatch: expected: {}, downloaded: {}'.format(HEADER[1], header[2])

    def _download_page(self, city_name, report_type=None):
        """Download and cache a page, or return a cached version if it is less than a month old. """
        # ensure cache directories exist.
        year_month = '{}_{}'.format(date.today().year, date.today().month)
        download_cache = self._bundle.library.download_cache
        if not download_cache.exists('abc.ca.gov'):
            download_cache.makedir('abc.ca.gov')
        if not download_cache.exists('abc.ca.gov/html'):
            download_cache.makedir('abc.ca.gov/html')
        if not download_cache.exists('abc.ca.gov/html/{}'.format(year_month)):
            download_cache.makedir('abc.ca.gov/html/{}'.format(year_month))

        city_html = 'abc.ca.gov/html/{}/{}.html'.format(year_month, city_name)
        page_content = ''
        if not download_cache.exists(city_html):
            self._bundle.log('Downloading `{}` city page'.format(city_name))
            payload = {
                'q_CityLOV': city_name.upper(),
                'RPTYPE': report_type,
                'SUBMIT1': 'Continue'
            }

            response = requests.post(API_URL, data=payload)
            assert response.status_code == 200, \
                'Download error: status_code: {}, text: {}'.format(response.status_code, response.text)

            download_cache.createfile(city_html)
            with download_cache.open(city_html, 'w') as f:
                page_content = response.text
                f.write(response.text)
        else:
            page_content = download_cache.open(city_html, 'r').read()
            self._bundle.log('Returning `{}` city page content from cache'.format(city_name))
        assert page_content
        return page_content

    def _retrieve_row(self, tr_elem):
        """ Converts tr_elem to list of strings.

        Args:
            tr_elem (bs4.element.Tag):

        Returns:
            list of str:
        """
        row = []

        for i, td_elem in enumerate(tr_elem.select('td')):

            if i == 6:
                strings = [s.strip() for s in td_elem.strings]
                if len(strings) > 2:
                    owner = strings.pop(0)
                    tract = strings.pop().split(' ')[-1]
                    address = ', '.join(map(lambda x: x.strip(), strings))

                    row.append(owner)
                    row.append(address)
                    row.append(tract)
            else:
                v = ' '.join(td_elem.strings).strip()
                row.append(v)
        return row

    def _convert_row(self, row):
        new_row = [x for x in row]
        del new_row[0]  # ordinal number
        try:
            new_row[3] = datetime.strptime(new_row[3], DATE_FORMAT).date()
            new_row[4] = datetime.strptime(new_row[4], DATE_FORMAT).date()
            return new_row
        except Exception as e:
            self._bundle.error('Bad row: {}; {}'.format(row, e.message))


#
# Following code should not be used by ambry. I created it only for testing
# while developing the generator.
#
# How to run developer test:
# python lib.py


def _test():

    from fs.opener import fsopendir

    class LibraryLike(object):
        """ Represents minimal library. """
        if not os.path.exists('/tmp/dev_test1k'):
            os.mkdir('/tmp/dev_test1k')
        download_cache = fsopendir('/tmp/dev_test1k')

    class BundleLike(object):
        # simple mock of a bundle for development purposes.
        def log(self, message):
            print('INFO: {}'.format(message))

        def debug(self, message):
            print('DEBUG: {}'.format(message))

        def error(self, message):
            print('ERROR: {}'.format(message))

    source = None

    for i, row in enumerate(AlcoholLicensesDataGenerator(BundleLike(), source=source)):
        if i == 0:
            assert row == HEADER, 'Generated header does not match to expected: {}'.format(row)
        else:
            assert row != HEADER, 'Header returned again. Expecting row.'
            assert len(row) == len(HEADER)
    print('Correct.')

if __name__ == '__main__':
    _test()
