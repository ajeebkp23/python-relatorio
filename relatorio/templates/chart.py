###############################################################################
#
# Copyright (c) 2007, 2008 OpenHex SPRL. (http://openhex.com) All Rights
# Reserved.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more 
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

__metaclass__ = type

from cStringIO import StringIO

import yaml
import genshi
import genshi.output
from genshi.template import Template as GenshiTemplate, NewTextTemplate

import cairo
import pycha
import pycha.pie
import pycha.line
import pycha.bar

PYCHA_TYPE = {'pie': pycha.pie.PieChart,
              'vbar': pycha.bar.VerticalBarChart,
              'hbar': pycha.bar.HorizontalBarChart,
              'line': pycha.line.LineChart,
             }
_encode = genshi.output.encode

class Template(NewTextTemplate):

    def __init__(self, source, filepath=None, filename=None, loader=None,
                 encoding=None, lookup='strict', allow_exec=True):
        if source is None:
            source = open(filepath, 'r').read()
        super(Template, self).__init__(source, filepath, filename, loader,
                                       encoding, lookup, allow_exec)
    def generate(self, *args, **kwargs):
        generated = super(Template, self).generate(*args, **kwargs)
        return PNGStream(generated, PNGSerializer())

    @staticmethod
    def id_function(mimetype):
        if mimetype == 'image/png':
            return 'chart'


class PNGStream(genshi.core.Stream):

    def __init__(self, content_stream, serializer):
        self.events = content_stream
        self.serializer = serializer

    def render(self, method=None, encoding='utf-8', out=None, **kwargs):
        return self.serializer(self.events)

    def serialize(self, method, **kwargs):
        return self.render(method, **kwargs)

    def __or__(self, function):
        return PNGStream(self.events | function, self.serializer)


class PNGSerializer:

    def __init__(self):
        self.text_serializer = genshi.output.TextSerializer()

    def __call__(self, stream):
        img = StringIO()
        yml = StringIO(_encode(self.text_serializer(stream)))
        chart_yaml = yaml.load(yml.read())
        chart_info = chart_yaml['chart']
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, chart_info['width'],
                                     chart_info['height'])
        chart = PYCHA_TYPE[chart_info['type']](surface, chart_yaml['options'])
        chart.addDataset(chart_info['dataset'])
        chart.render()
        surface.write_to_png(img)
        return img
