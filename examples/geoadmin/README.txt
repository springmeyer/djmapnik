Geoadmin
========

This "geoadmin" app is originally ripped from:

http://code.google.com/p/geodjango-basic-apps/wiki/GeographicAdminQuickStart

to use as a sample for testing djmapnik features. See the above for details
on getting set up with the geoadmin basics.

Currently this sample, as far as djmapnik features, does very little. It just 
shows template tag usage in main page which is not a real world usecase but
rather purely for testing.

The main idea is that the wrappers can be used to create actual Mapnik layer objects,
which you can then use in your app however you like, for example by applying styles,
pushing into a map object, and rendering.

As sugar, this auto-creation of layers also allows you too thing like:

  $ python manage.py shell

  >>> from djmapnik.adapter import PostgisLayer
  >>> from world.models import WorldBorders as W
  >>> PostgisLayer(W.objects.all()).show() # returns map object and opens image in default viewer
  <mapnik._mapnik.Map object at 0x10684d890>

Or, if you have applied the MapnikManager to your model:

  $ python manage.py shell
  >>> from world.models import WorldBorders as W
  >>> W.objects.show()

You can also write scripts to be run from the command line to render maps:

  #!/usr/bin/env python
  
    import os
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
      
    import mapnik
    
    from djmapnik.adapter import PostgisLayer as DjLayer
    #from djmapnik.adapter import MemoryLayer as DjLayer
    
    from world.models import WorldBorders as W
    adapter = DjLayer(W.objects.all())
    lyr = adapter.to_mapnik()
    sty = adapter.get_default_style()
    lyr.styles.append('test')
    m = mapnik.Map(600,400)
    m.append_style('test',sty)
    m.layers.append(lyr)
    m.zoom_all()
    im = mapnik.Image(m.width,m.height)
    mapnik.render(m,im)
    im.save('test.png')

