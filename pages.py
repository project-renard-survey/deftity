# deftity - a tool for interaction architect
#
# Copyright (C) 2011 Matti Katila
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


# Written by Matti J. Katila, 2011

import cairo
import pango
import pangocairo

import actions
import tool
import util

"""The page component drawn on screen.

Paper size of A4 is 210 x 297 mm. Cairo wants pixel size and the
resolution is 1 pixel = 1/72 inch, where inch is 2.54 cm.
1 inch = 25.4 mm
1 pixel = 1/72 inch = 25.4/72 mm
1 mm = 1/(25.4/72) pixel
210 x 297 mm = 595.2755 x 841.889 pixels
"""

SIZE_TITLE = 64
SIZE_HEADER = 32
SIZE_TEXT = 12


A4_SIZE = ( 1./(25.4/72)*297., 1./(25.4/72)*210. )


class Page(tool.Component):
    def __init__(self):
        self.wh = A4_SIZE
        self.xy = [ 0,0 ]
        self.actions = []
        self.data = {}
    def xywh(self):
        return ( self.xy[0], self.xy[1], self.wh[0], self.wh[1])
    def pos(self, x,y):
        self.xy = [x, y]

    def is_close(self,x0,y0):
        x,y,w,h = self.xywh()
        return x-70 < x0 < x+w+70 and \
               y-70 < y0 < y+h+70

    def draw(self, c, active):
        x,y,w,h = self.xywh()
        for act in self.actions:
            xx,yy = act.x, act.y
            act.draw(c, x+xx, y+yy, active)

    def draw_frame(self, c, tc, label, mx, my):
        x,y,w,h = self.xywh()
        c.new_path()
        c.rectangle(x,y,w,h)
        c.close_path()
        if self in tc.selected_comps:
            c.set_source_rgb(1,0,0)
        else:
            c.set_source_rgb(0,0,0)
        c.stroke()
        util.write(c, label, x,y-10, 40)

        if self.is_close(mx,my):
            c.new_path()
            c.rectangle(x,y,w,h)
            c.close_path()
            c.set_source(cairo.SolidPattern(.8,.9,1, .2))
            c.fill_preserve()

    def mouse_released(self, tc, mx, my):
        x,y,w,h = self.xywh()
        x = mx - x
        y = my - y
        for act in self.actions:
            if act.is_hit(x, y):
                act.mouse_released(tc, x,y)

        if tc.arrow in [tool.ToolContext.ARROW_START,
                        tool.ToolContext.ARROW_END]:
            if tc.arrow_comps == []:
                tc.set_arrow(self)
            elif isinstance(tc.arrow_comps[0], tool.Start) \
                 or isinstance(tc.arrow_comps[0], Page):
                tc.set_arrow(self)


    def save_data(self):
        ret = tool.Component.save_data(self)
        ret['data'] = self.data
        print self.data
        return ret
    def get_data(self): return self.data
       



class TitlePage(Page):
    def __init__(self):
        Page.__init__(self)
        self.data = { 'title': '', 'subtitle': ''}
        x,y,w,h = self.xywh()
        wlim = w
        self.actions.append(actions.TextfieldAct( \
            'Title:', x, h/2-32., wlim, 64, 'title', self.get_data))
        self.actions.append(actions.TextfieldAct( \
            'SubTitle:', x, h/2+40., wlim, 38, 'subtitle', self.get_data))
    def draw(self, c, tc, mx, my):
        Page.draw_frame(self, c, tc, 'Title page', mx, my)

        Page.draw(self, c, self.is_close(mx,my))

class ChangeLogPage(Page):
    def __init__(self):
        Page.__init__(self)
        self.data = { 'titlerow': ['Version', 'Description'],
                      'row1': ['0.1', 'Foo']}
        x,y,w,h = self.xywh()
        wlim = w/2
    def draw(self, c, tc, mx, my):
        Page.draw_frame(self, c, tc, 'Changelog page', mx, my)
        x,y,w,h = self.xywh()
        util.write_center(c, 'Changelog', x, w, y+2*SIZE_HEADER, SIZE_HEADER)
        
        Page.draw(self, c, self.is_close(mx,my))

class DescriptionPage(Page):
    def __init__(self):
        Page.__init__(self)
        self.data = { 'title': 'Project golas',
                      'text': 'some text'}
        x,y,w,h = self.xywh()
        wlim = w
        self.actions.append(actions.TextfieldAct( \
            'Title:', 0, SIZE_HEADER, wlim, SIZE_HEADER, 
            'title', self.get_data))
        self.actions.append(actions.TextareaAct( \
            'Text:', w/20, 3*SIZE_HEADER, 
            w*18/20, h-3*SIZE_HEADER, SIZE_TEXT, 'text', self.get_data))

    def draw(self, c, tc, mx, my):
        Page.draw_frame(self, c, tc, 'Description page', mx, my)
        x,y,w,h = self.xywh()
        Page.draw(self, c, self.is_close(mx,my))


class EmptyPage(Page):
    def __init__(self):
        Page.__init__(self)
    def draw(self, c, tc, mx, my):
        Page.draw_frame(self, c, tc, 'Page', mx, my)
