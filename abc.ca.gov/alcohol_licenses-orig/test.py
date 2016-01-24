# -*- coding: utf-8 -*-
# Bundle test code

from ambry.bundle.test import BundleTest
from ambry.bundle.events import after_ingest


class Test(BundleTest):

    @after_ingest
    def test_after_ingest(self):
        self.assertEqual(['licenses'], [t.name for t in self.bundle.dataset.source_tables])
