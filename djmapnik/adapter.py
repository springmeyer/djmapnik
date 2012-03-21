# django
from django.contrib.gis.gdal import SpatialReference
#from django.contrib.gis.db.models.fields import GeometryField

# mapnik
import mapnik

# djmapnik
from djmapnik import utils

def get_base_params(using=None):
    from django.conf import settings
    if hasattr(settings,'DATABASES'):
        db = settings.DATABASES.get(using) or settings.DATABASES['default']
        if not db.get('ENGINE') == 'django.contrib.gis.db.backends.postgis':
            raise NotImplementedError('Only the postgis backend is supported at this time')
        return {
            'dbname':db['NAME'], 'user':db['USER'], 'password':db['PASSWORD'],
            'host':db['HOST'],'port':db['PORT'],
            }
    else:
        if not 'postgresql' in settings.DATABASE_ENGINE:
            raise NotImplementedError('Only postgresql/postgis is supported at this time')
        return {
            'dbname':settings.DATABASE_NAME, 'user':settings.DATABASE_USER, 
            'password':settings.DATABASE_PASSWORD, 'host':settings.DATABASE_HOST,
            'port':settings.DATABASE_PORT,
            }


def qs_to_map(qs,styles=[],srs='+init=epsg:900913',buffer_size=128):
    m = mapnik.Map(256,256,srs)
    if buffer_size:
        m.buffer_size = buffer_size
    m.background = mapnik.Color('transparent')
    adapter = PostgisLayer(qs,styles=styles)
    lyr = adapter.to_mapnik()
    for s in styles:
        m.append_style(s['name'],s['obj'])
    m.layers.append(lyr)
    return m


class LayerAdapter:
    def __init__(self,queryset,name=None,styles=[],field_name=None,use_proj4_literal=False,persist_connection=True):
        self.qs = queryset
        assert hasattr(self.qs,'query'), '%s must be a queryset and have a .query attribute' % self.qs
        self.name = name
        self.styles = styles
        self.field_name = field_name
        self.use_proj4_literal = use_proj4_literal
        self.persist_connection = persist_connection
        if self.field_name:
            self.geometry_field = self.qs.query.get_meta().get_field(field_name)
        else:
            self.geometry_field = self.qs.query._geo_field()

    def show(self,width=400,height=300,filename=None,app=None):
        lyr = self.to_mapnik()
        sty = self.get_default_style()
        return utils.show(lyr,sty,width=width,height=height)

    def get_default_style(self):
        # todo - mapnik should be able to report geometry type in the future
        geometry_type = self.geometry_field.geom_type.lower()
        return utils.get_default_style(geometry_type)
        
    def to_mapnik(self,settings=None):
        ds = self.get_mapnik_ds(settings=settings)
        if self.name:
            lyr = mapnik.Layer(self.name)
        else:
            lyr = mapnik.Layer('name')

        lyr.datasource = ds
        if self.use_proj4_literal:
            lyr.srs = SpatialReference(self.geometry_field.srid).proj4
        else:
            lyr.srs = '+init=epsg:%s' % self.geometry_field.srid
        if self.styles:
            for s in self.styles:
                lyr.styles.append(s['name'])
        return lyr

    def get_mapnik_ds(self,**kwargs):
        raise NotImplementedError('Do not use this class directly, use a subclass')


class MemoryLayer(LayerAdapter):
    "Build up a mapnik.MemoryDatasource"

    def get_mapnik_ds(self,**kwargs):
        """Pull features from a Django queryset into a Mapnik MemoryDatasource.
        """
        if not self.geometry_field:
            raise ValueError('Geometry field not found')

        import itertools
        ids = itertools.count(0)
        assert hasattr(mapnik,'MemoryDatasource'), "mapnik.MemoryDatasource requires >= mapnik 2.1"
        ds = mapnik.MemoryDatasource()
        # todo - how to get subset of columns requested from the queryset?
        field_names = self.qs.query.get_meta().get_all_field_names()
        field_names.remove(self.geometry_field.name)
        if hasattr(mapnik,'Context'):
            context = mapnik.Context()
            for fld in field_names:
                context.push(fld)
        for i in self.qs.iterator():
            feature = None
            if hasattr(mapnik,'Context'):
                feature = mapnik.Feature(context,ids.next())
            else:
                feature = mapnik.Feature(ids.next())
            feature.add_geometries_from_wkb(str(getattr(i,self.geometry_field.name).wkb))
            for fld in field_names:
                feature[fld] = getattr(i,fld)
            ds.add_feature(feature)
        return ds

class PostgisLayer(LayerAdapter):

    def get_mapnik_ds(self,**kwargs):
        if not self.geometry_field:
            raise ValueError('Geometry field not found')
        if kwargs.get('settings'):
            params_ = kwargs.get('settings').copy()
        else:
            if hasattr(self.qs,'_db'):
                # we use qs._db here instead of qs.db because it
                # evaluates to None if using default db
                params_ = get_base_params(using=self.qs._db)
            else:
                params_ = get_base_params()
        subquery = self._as_mapnik_sql(**kwargs)
        sub_low = subquery.lower()
        # requires >= Mapnik 0.7.0
        if 'where' in sub_low or sub_low.count('from') > 1:
            params_['extent_from_subquery'] = True
        else:
            params_['extent_from_subquery'] = False
        params_['table'] = str(subquery)
        params_['geometry_field'] = str(self.geometry_field.name)
        params_['srid'] = int(self.geometry_field.srid)
        params_['persist_connection'] = self.persist_connection
        ds = mapnik.PostGIS(**params_)
        ds.subquery = subquery
        return ds

    def _as_mapnik_sql(self,**kwargs):
        """Transform the raw SQL from a Django queryset into a Mapnik subquery.
        """
        # running multidb available in django 1.2
        if hasattr(self.qs.query,'get_compiler'):
           compiler = self.qs.query.get_compiler(self.qs.db)
           sql, args = compiler.as_sql()
           gqn = compiler.connection.ops.geo_quote_name
        else:
           sql, args = self.qs.query.as_sql()
           from django.contrib.gis.db.backends.util import gqn
        #if qs.query.has_where
        if args:
           sql = sql % tuple([str(i) if hasattr(i,'ewkb') else gqn(i) for i in args])
        return """(%s) as django_table""" % sql

