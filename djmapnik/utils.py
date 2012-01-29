# std lib
import os
import tempfile
import platform
from subprocess import Popen, PIPE

# mapnik
try:
    import mapnik2 as mapnik
except:
    import mapnik

def call(cmd,fail=False):
    try:
        response = Popen(cmd.split(' '),stdin=PIPE, stdout=PIPE, stderr=PIPE)
        cm = response.communicate()
        return cm[0]
    except Exception, e:
        if fail:
            raise SystemExit(e)
        else:
            return None
    
def open_image(filename, app=None):
    if os.name == 'nt':
        if app:
            raise SystemExit('Overriding default image viewer not supported on Win32')
        call('start %s' % filename.replace('/','\\'))
    elif platform.uname()[0] == 'Linux':
        if app:
            call('%s %s' % (app, filename))
        else:
            try:
                cmd = 'xdg-open %s' % self.image
                Popen(cmd.split(' '))
            except OSError:
                try:
                    cmd = 'gthumb %s' % self.image
                    Popen(cmd.split(' '))
                except OSError:
                    cmd = 'display %s' % self.image
                    Popen(cmd.split(' '))
    elif platform.uname()[0] == 'Darwin':
        if app:
            call('open %s -a %s' % (filename, app))
        else:
            call('open %s' % filename)

def get_default_style(geometry_type):
    """ Ultra simple default style for quick setup or debugging. 
    """
    style, rule = mapnik.Style(), mapnik.Rule()
    gtype = geometry_type.lower()
    if 'poly' in gtype:
        rule.symbols.append(mapnik.PolygonSymbolizer(mapnik.Color('steelblue')))
        rule.symbols.append(mapnik.LineSymbolizer(mapnik.Color('steelblue'),.5))
    elif 'line' in gtype:
        rule.symbols.append(mapnik.LineSymbolizer(mapnik.Color('steelblue'),1.5))
    else:
        point = mapnik.PointSymbolizer()
        point.allow_overlap = True
        rule.symbols.append(point)
    style.rules.append(rule)
    return style

def show(lyr,sty,width=400,height=300,filename=None,app=None):
    m = mapnik.Map(width,height,lyr.srs)
    m.background = mapnik.Color('transparent')
    lyr.styles.append('style')
    m.append_style('style',sty)
    m.layers.append(lyr)
    m.zoom_all()
    if not filename:
        (handle, filename) = tempfile.mkstemp('.png', 'django-map-')
        os.close(handle)
    mapnik.render_to_file(m,str(filename))
    open_image(str(filename))
    return m