import ambry.bundle 


class Bundle(ambry.bundle.Bundle):
    pass


    def dl(self):

        for i, source in enumerate(self.sources):
            print i, source.name, source.url
            
            for row in source.fetch().source_pipe():
                print row
      