#!/usr/bin/env python
"""Based on gtk+/test/testcairo.c
"""

from __future__ import division
import math

import cairo
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import geometry
import pcb

copper_pours = []
traces = []

class CopperPour:
    def __init__(self, layer=0, net="0"):
        self.layer = layer
        self.net = net
        self.vertices = []

class Trace:
    def __init__(self, layer=0, net="0"):
        self.layer = layer
        self.net = net
        self.vertices = []

def compute_geometry():
    global copper_pours
    global traces

    stator = geometry.StatorComponent(30, 61.4, 100)
    stator_pcb = pcb.pcb_from_component(stator, add_connector=True)
    stator_pcb.to_file('stator')    

    rotor = geometry.RotorComponent(30, 61.4, 100)
    rotor_pcb = pcb.pcb_from_component(rotor, flip=True)
    rotor_pcb.to_file('rotor')

def draw_copper_pours(ctx):
    for p in copper_pours:
        set_layer_color(ctx, p.layer)

        vs = p.vertices
        ctx.move_to(vs[0][0], vs[0][1])
        for v in vs[1:]:
            ctx.line_to(v[0], v[1])
        ctx.close_path()
        ctx.fill()

def draw_traces(ctx):
    for t in traces:
        set_layer_color(ctx, t.layer)

        vs = t.vertices
        ctx.move_to(vs[0][0], vs[0][1])
        for v in vs[1:]:
            ctx.line_to(v[0], v[1])        
        ctx.stroke()

def set_layer_color(ctx, layer):
    layer_colors = [
        [0.75, 0.0, 0.0],
        [0.0, 0.0, 1.0]
    ]

    c = layer_colors[layer]
    ctx.set_source_rgb(c[0], c[1], c[2])

def oval_path(ctx, xc, yc, xr, yr):
    ctx.save()

    ctx.translate(xc, yc)
    ctx.scale(1.0, yr / xr)
    ctx.move_to(xr, 0.0)
    ctx.arc(0, 0, xr, 0, 2 * math.pi)
    ctx.close_path()

    ctx.restore()

def set_window(ctx, width, height, radius):
    xc = width / 2
    yc = height / 2

    scale = float(min(width, height)) / (2.0 * radius)

    ctx.translate(xc, yc)
    ctx.scale(scale, scale)
    ctx.set_line_width(1 / scale)

def draw(ctx, width, height):
    # Fill context with black
    ctx.rectangle(0, 0, width, height)
    ctx.set_source_rgb(0.0, 0.0, 0.0)
    ctx.fill()

    # Transform the context to fit the bounds
    set_window(ctx, width, height, 110)
    
    ctx.set_source_rgb(1, 1, 1)    
    ctx.set_operator(cairo.OPERATOR_ADD)

    # Draw the board outlines
    oval_path(ctx, 0, 0, 45, 45)
    ctx.stroke()
    oval_path(ctx, 0, 0, 105, 105)
    ctx.stroke()

    draw_copper_pours(ctx)
    draw_traces(ctx)

def draw_event(drawingarea, ctx):
    alloc = drawingarea.get_allocation()
    draw(ctx, alloc.width, alloc.height)
    return False

def main():
    compute_geometry()

    # win = Gtk.Window()
    # win.connect('destroy', Gtk.main_quit)
    # win.set_title('Capactive PCB')
    # win.set_default_size(400, 400)

    # drawingarea = Gtk.DrawingArea()
    # win.add(drawingarea)
    # drawingarea.connect('draw', draw_event)

    # win.show_all()
    # Gtk.main()


if __name__ == '__main__':
    main()
