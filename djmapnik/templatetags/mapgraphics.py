# std lib
import os
from random import random

# django
from django import template
from django.conf import settings
from django.utils.encoding import smart_str, force_unicode
from django.utils.safestring import mark_safe

# djmapnik
from djmapnik.adapter import PostgisLayer
#from djmapnik import utils

# mapnik
try:
    import mapnik2 as mapnik
except:
    import mapnik
    
register = template.Library()

# http://docs.djangoproject.com/en/dev/howto/custom-template-tags/

graphics = os.path.join(settings.MEDIA_ROOT,'mapgraphics')
if not os.path.exists(graphics):
    os.makedirs(graphics)

# TODO:
# sorl thumbnail like configurability
# allow application of styles
# turn into a proper tag

def render(qs,options):
    kwargs = {}
    if options:
        if ';' in options:
            for item in options.split(';'):
                if ':' in item:
                    k,v = item.split(':')
                    kwargs[k] = v

    width = int(kwargs.get('width',600))
    height = int(kwargs.get('height',600))
    #field = kwargs.get('field',None)
    if hasattr(qs,'_meta'):
        # it looks like a model
        qs = qs.objects.all()
    m = mapnik.Map(width,height)
    m.aspect_fix_mode = mapnik.aspect_fix_mode.GROW_CANVAS
    adapter = PostgisLayer(qs)
    lyr = adapter.to_mapnik()
    sty = adapter.get_default_style()
    lyr.styles.append('style')
    m.append_style('style',sty)
    #m.background = mapnik.Color('green')
    m.srs = lyr.srs
    m.layers.append(lyr)
    m.zoom_all()
    #print mapnik.save_map_to_string(m)
    mod = qs.query.get_meta().module_name
    # TODO - need way to properly cache vs. always overwriting...
    name = '%s_%s_%s_%s.png' % (mod,width,height,random())
    map_graphic = os.path.join(graphics,name)
    mapnik.render_to_file(m,str(map_graphic))
    url = os.path.join(settings.MEDIA_URL,'mapgraphics',name)
    return mark_safe(force_unicode('<img src="%s" />' % smart_str(url)))

register.filter(render)
