# Library file for code that is common to meta.py and bundle.py

from ambry.etl.pipeline import Pipe

class  LookupCDS(Modify):

    def process_body(self, row):

        # Eventually, we'll get a dataset for the county, district and school numbers 
        # and map all of the unset values for county, district and school. 

        return row