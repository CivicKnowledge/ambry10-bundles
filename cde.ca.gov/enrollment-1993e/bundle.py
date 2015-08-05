import ambry.bundle 


class Bundle(ambry.bundle.Bundle):
    pass

from ambry.etl.pipeline import Modify

class  LookupCDS(Modify):

    def process_body(self, row):

        # Eventually, we'll get a dataset for the county, district and school numbers 
        # and map all of the unset values for county, district and school. 

        return row