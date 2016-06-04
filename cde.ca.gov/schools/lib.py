# -*- coding: utf-8 -*-
# Ambry Bundle Library File
# Use this file for code that may be imported into other bundles

class GenerateDistricts(object):

    def __init__(self, bundle, source=None):
        self.bundle = bundle
        pass

    def __iter__(self):

        from ambry import get_library
        import censuslib.dataframe
        import pandas as pd

        # The district NCES codes aren't in the district file, although they are in the school file. 
        schools = self.bundle.partition(table='schools').analysis.dataframe()
        schools['cd_code'] = schools.cdscode.apply(lambda cdscode: cdscode[:7])

        nces_districts = schools[schools.statustype=='Active'][['ncesdist', 'cd_code']].drop_duplicates()

        # The actual districts file
        ca_districts = self.bundle.partition(table='districts').analysis.dataframe()[
            ['cd_code', 'county_sos','county_fips','county_gvid','county','district']]

        #assert len(nces_districts) == len(ca_districts)

        # Combine the codes from the school file with the district file
        cd_code_districts = ca_districts.set_index('cd_code').join(nces_districts.set_index('cd_code')).reset_index()
        
        ##
        ## Join the California state districts list with the Census districts list
        ###

        from geoid.acs import AcsGeoid
        from geoid.civick import GVid
        dist_pred = lambda row: row.state ==6


        def mk_cd_code(nces):
            return '06{:05d}'.format(nces)

        # Combine the three partitions for school districts in the census, and extract the NCES code
        
        elem = self.bundle.dep('elementary').analysis.dataframe(dist_pred)[['geoid', 'name']].copy()
        elem['nces'] = elem.geoid.apply(lambda geoid: mk_cd_code(AcsGeoid.parse(geoid).sdelm) )
        
        second = self.bundle.dep('secondary').analysis.dataframe(dist_pred)[['geoid', 'name']].copy()
        second['nces'] = second.geoid.apply(lambda geoid: mk_cd_code(AcsGeoid.parse(geoid).sdsec) )
        
        unified = self.bundle.dep('unified').analysis.dataframe(dist_pred)[['geoid', 'name']].copy()
        unified['nces'] = unified.geoid.apply(lambda geoid: mk_cd_code(AcsGeoid.parse(geoid).sduni) )

        # Add a GVID
        census_districts = pd.concat([elem, second, unified], axis=0)
        census_districts['gvid'] = census_districts.geoid.apply(lambda geoid: AcsGeoid.parse(geoid).convert(GVid) )

        # Do the join
        districts = cd_code_districts.set_index('ncesdist').join(census_districts.drop_duplicates().set_index('nces')).reset_index()
        districts.columns = ['ncesdist'] + list(districts.columns)[1:]

        # These are different sizes, don't know why. The de-duplicated census file is smaller than the 
        # list from California, probably because many of the districts are smaller than the reporting limits. 
        # NOTE: Becase join is a left join, (a) it must be joined in the order above ( cd_code_districts, the larger list, 
        # is the base ) and (b) the joined 'districts' dataframe will have some missing geoids. 
        # The missing geoids appears to be primarily for County offices of education and districts in small counties. 
        # >>> print len(census_districts), len(census_districts.drop_duplicates()), len(cd_code_districts), len(districts)
        # >>> 1976 988 1098 1098
        
        districts.gvid.fillna(value='', inplace = True)
        districts.geoid.fillna(value='', inplace = True)
        districts.name.fillna(value='', inplace = True)
        districts.ncesdist.fillna(value=0, inplace = True)
        
        df = districts.reset_index()

        yield ['id'] + list(df.columns)

        for index, row in df.iterrows():

            yield [index] + list(row)
        