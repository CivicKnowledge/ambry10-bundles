# -*- coding: utf-8 -*-
# Ambry Bundle Library File
# Use this file for code that may be imported into other bundles

from datetime import datetime
import time

from bs4 import BeautifulSoup
import requests

API_URL = 'http://www.abc.ca.gov/datport/AHCityRep.asp'

DATE_FORMAT = '%m-%d-%Y'

HEADER = [
    'License Number', 'Status', 'License Type', 'Orig. Iss. Date',
    'Expir Date', 'Primary Owner', 'Premises Addr.', 'Tract', 'Business Name',
    'Mailing Address', 'Geo Code']

CITIES = [
    'CARLSBAD',
    'CHULA VISTA',
    'CORONADO',
    'DEL MAR',
    'EL CAJON',
    'ENCINITAS',
    'ESCONDIDO',
    'IMPERIAL BEACH',
    'LA MESA',
    'LEMON GROVE',
    'NATIONAL CITY',
    'OCEANSIDE',
    'POWAY',
    'SAN DIEGO',
    'SAN MARCOS',
    'SANTEE',
    'SOLANA BEACH',
    'VISTA',
]


class AlcoholLicensesDataGenerator(object):

    def __init__(self, bundle, source=None):
        self._bundle = bundle
        self._source = source

        '''
        if source:
            self.year = int(source.time)
            self.space = source.space
        else:
            self.year = 2010
            self.space = 'CA'
        '''

    def __iter__(self):
        """ Generates header and rows with data of all cities. """

        header = None

        # partition = self.partitions.find_or_new(table='licenses', time=str(datetime.date.today().year))
        # header = [c.name for c in partition.table.columns]
        # target_cities = self.metadata.meta.target_cities

        for city in CITIES[0:1]:
            self._bundle.log('Downloading `{}` city page'.format(city))
            cache_state, page = self._download_page(city, report_type='p_Retail')
            if cache_state == 'new':
                # Why do we need to sleep?
                time.sleep(5)
            else:
                self._bundel.log('Page was cached')

            self._bundle.log('Parsing {} city page'.format(city))
            bf = BeautifulSoup(page)

            tr_elems = bf.select('tr.report_column')
            # FIXME: assert self._contains_header(tr_elems[0])

            if not header:
                header = HEADER
                self._bundle.debug('Generate header: {}'.format(header))
                yield header

            for i, tr_elem in enumerate(tr_elems[1:]):
                row = self._retrieve_row(tr_elem)
                self._bundle.debug('{} row of {} city retrieved as {}'.format(i, city, row))

                if row:
                    new_row = self._convert_row(row)
                    self._bundle.debug(
                        'Row conversion:\n  city: {},\n  row_index: {},\n  old_row: {},\n  new_row: {}'
                        .format(city, i, row, new_row))
                    yield new_row

            # with partition.database.inserter(partition.table, cache_size=0) as ins:
            #    for row in table:
            #        ins.insert(dict(zip(header, row)))

    def _download_page(self, city_name, report_type=None):
        """Download and cache a page, or return a cached version if it is less than a month old. """

        # partition = self.partitions.find_or_new(table='page_cache')

        #
        # Look in the cache for the page.
        #

        # from sqlalchemy.sql import text
        # s = text(""" SELECT date, page FROM page_cache WHERE city = :city_name
        #         AND report_type = :report_type
        #         AND date > date('now','-1 month')
        #         ORDER BY date desc
        #         """)

        # row = partition.database.connection.execute(s,
        #                                             city_name=city_name,
        #                                             report_type=report_type
        #                                            ).first()

        # if row:
        #    return 'cached', row[1]

        #
        # Not found, get it from the web.
        #

        payload = {
            'q_CityLOV': city_name,
            'RPTYPE': report_type,
            'SUBMIT1': 'Continue'
        }

        response = requests.post(API_URL, data=payload)
        assert response.status_code == 200, \
            'Download error: status_code: {}, text: {}'.format(response.status_code, response.text)

        ''' FIXME: cache the downloaded page.

        with partition.database.inserter() as ins:
            row = {
                'date': datetime.datetime.now(),
                'city': city_name,
                'license_type': '01',
                'report_type': report_type,
                'page': r.text
            }
            ins.insert(row)
        '''

        return 'new', response.text

    def _retrieve_row(self, tr_elem):
        """ Converts tr_elem to list of strings.

        Args:
            tr_elem (FIXME:):

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
# Following code should not be used by other bundles. I created it only for testing
# while developing the generator.
#


def _test():

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
