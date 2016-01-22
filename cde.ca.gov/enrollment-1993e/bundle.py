import ambry.bundle 


class Bundle(ambry.bundle.Bundle):
    pass


    def edit_pipeline(self, pl):
        """The -L option limits each source build to the first 400 rows"""
        from ambry.etl.pipeline import Head
        if self.limited_run:
            pl.first = [Head(400)]
            
        return pl
            