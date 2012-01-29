import os
from django.db import connection
from django.contrib.gis.db.models import GeoManager
from django.contrib.gis.db.models.sql import GeoQuery
from django.contrib.gis.db.models.query import GeoQuerySet
from timeit import time

from djmapnik.adapter import PostgisLayer

class MapnikQuerySet(GeoQuerySet):
    def __init__(self, model=None, query=None, using=None):
        super(MapnikQuerySet, self).__init__(model=model, query=query, using=using)
        try:
            self.query = query or GeoQuery(self.model)
        except TypeError: # pre django 1.2
            self.query = query or GeoQuery(self.model,connection)        

    def show(self,**kwargs):
        timeit = kwargs.get('timeit')
        if timeit:
            start = time.time()
        # todo - we should check for postgis support, and otherwise
        # use the MemoryDatasource
        lyr_adapter = PostgisLayer(self)
        lyr_adapter.show(**kwargs)
        if timeit:
            elapsed = (time.time() - start)/60
            print 'render time: %s seconds' % elapsed 
        
class MapnikManager(GeoManager):

    def get_query_set(self):
        qs = MapnikQuerySet(model=self.model)
        if self._db is not None:
            qs = qs.using(self._db)
        return qs
            
    def show(self,**kwargs):
        return self.get_query_set().show(**kwargs)
    