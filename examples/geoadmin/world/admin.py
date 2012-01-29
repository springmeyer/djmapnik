# admin.py

# This file controls the look and feel of the models within the Admin App
# They appear in the admin app once they are registered at the bottom of 
# this code (same goes for the databrowse app)

from django.conf import settings # needed if we use the GOOGLE_MAPS_API_KEY from settings

# Import the admin site reference from django.contrib.admin
from django.contrib import admin

# Grab the Admin Manager that automaticall initializes an OpenLayers map
# for any geometry field using the in Google Mercator projection with OpenStreetMap basedata
from django.contrib.gis.admin import OSMGeoAdmin, GeoModelAdmin

# Note, another simplier manager that does not reproject the data on OpenStreetMap is available
# with from `django.contrib.gis.admin import GeoModelAdmin`

# Finally, import our model from the working project
# the geographic_admin folder must be on your python path
# for this import to work correctly
from world.models import WorldBorders

# Import the Databrowse app so we can register our models to display via the Databrowse
from django.contrib import databrowse
databrowse.site.register(WorldBorders)

USE_GOOGLE_TERRAIN_TILES = False

class WorldBordersAdmin(OSMGeoAdmin):
    """
    
    The class that determines the display of the WorldBorders model
    within the Admin App.
    
    This class uses some sample options and provides a bunch more in commented
    form below to show the various options GeoDjango provides to customize OpenLayers.
    
    For a look at all the GeoDjango options dive into the source code available at:
    
    http://code.djangoproject.com/browser/django/trunk/django/contrib/gis/admin/options.py
    
    """
    # Standard Django Admin Options
    list_display = ('name','pop2005','region','subregion','geometry',)
    list_editable = ('geometry',)
    search_fields = ('name',)
    list_per_page = 4
    ordering = ('name',)
    list_filter = ('region','subregion',)
    save_as = True
    search_fields = ['name','iso2','iso3','subregion','region']
    list_select_related = True
    fieldsets = (
      ('Country Attributes', {'fields': (('name','pop2005')), 'classes': ('show','extrapretty')}),
      ('Country Codes', {'fields': ('region','subregion','iso2','iso3','un',), 'classes': ('collapse',)}),
      ('Area and Coordinates', {'fields': ('area','lat','lon',), 'classes': ('collapse', 'wide')}),
      ('Editable Map View', {'fields': ('geometry',), 'classes': ('show', 'wide')}),
    )

    if USE_GOOGLE_TERRAIN_TILES:
      map_template = 'gis/admin/google.html'
      extra_js = ['http://openstreetmap.org/openlayers/OpenStreetMap.js', 'http://maps.google.com/maps?file=api&amp;v=2&amp;key=%s' % settings.GOOGLE_MAPS_API_KEY]
    else:
      pass # defaults to OSMGeoAdmin presets of OpenStreetMap tiles

    # Default GeoDjango OpenLayers map options
    # Uncomment and modify as desired
    # To learn more about this jargon visit:
    # www.openlayers.org
    
    #default_lon = 0
    #default_lat = 0
    #default_zoom = 4
    #display_wkt = False
    #display_srid = False
    #extra_js = []
    #num_zoom = 18
    #max_zoom = False
    #min_zoom = False
    #units = False
    #max_resolution = False
    #max_extent = False
    #modifiable = True
    #mouse_position = True
    #scale_text = True
    #layerswitcher = True
    scrollable = False
    #admin_media_prefix = settings.ADMIN_MEDIA_PREFIX
    map_width = 400
    map_height = 325
    #map_srid = 4326
    #map_template = 'gis/admin/openlayers.html'
    #openlayers_url = 'http://openlayers.org/api/2.6/OpenLayers.js'
    #wms_url = 'http://labs.metacarta.com/wms/vmap0'
    #wms_layer = 'basic'
    #wms_name = 'OpenLayers WMS'
    #debug = False
    #widget = OpenLayersWidget

# Finally, with these options set now register the model
# associating the Options with the actual model
admin.site.register(WorldBorders,WorldBordersAdmin)