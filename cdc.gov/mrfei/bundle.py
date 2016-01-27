# -*- coding: utf-8 -*-
import ambry.bundle


class Bundle(ambry.bundle.Bundle):

    def parse_tiger_tract(self, v):
        from geoid.census import Tract

        if isinstance(v, (float, int)):
            v = '{:0>11}'.format(int(v))
        

        return Tract.parse(v)