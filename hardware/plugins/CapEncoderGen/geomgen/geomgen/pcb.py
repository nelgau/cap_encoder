from pykicad.pcb import *
from pykicad.module import *

import math
import os

def pcb_from_component(component, flip=False, add_connector=False):
  os.environ['KISYSMOD'] = '/Library/Application Support/kicad/modules'

  pcb = Pcb()

  trace_clearance = 0.127
  trace_width = 0.127
  via_size = 0.6
  via_drill = 0.3

  setup = Setup(
    trace_clearance=trace_clearance,
    trace_min=trace_width,
    via_min_size=via_size,
    via_min_drill=via_drill,    

    # Check these!
    pad_to_mask_clearance=0.051,
    solder_mask_min_width=0.25
  )

  layers = [
    Layer('F.Cu'),
    Layer('B.Cu'),
    Layer('Edge.Cuts', type='user')
  ]

  for layer in ['Mask', 'Paste', 'SilkS', 'CrtYd', 'Fab']:
      for side in ['B', 'F']:
          layers.append(Layer('%s.%s' % (side, layer), type='user'))

  if not flip:
    arc_layer = 'B.Cu'
    electrode_layer = 'F.Cu'
    mask_layer = 'F.Mask'
  else:
    arc_layer = 'F.Cu'
    electrode_layer = 'B.Cu'
    mask_layer = 'B.Mask'

  nets = []
  net_map = {}

  segments = []
  zones = []
  vias = []

  arcs = []
  lines = []
  circles = []
  polygons = []

  modules = []

  for s in component.signals:
    net_name = s.name
    if net_map.get(net_name) is None:
      net = Net(net_name)
      nets.append(net)
      net_map[net_name] = net

  for s in component.signals:
    net_name = s.name
    net = net_map[net_name]

    avs = s.arc.to_polygon()

    for i in range(len(avs) - 1):
        segments.append(Segment(start=avs[i], end=avs[i + 1], net=net.code, layer=arc_layer, width=trace_width))

    for e in s.electrodes:
        evs = e.to_polygon()
        zones.append(Zone(net=net.code, net_name=net.name, layer=electrode_layer, polygon=evs, filled_polygon=evs, clearance=0.0, min_thickness=0.0254))

    for v in s.vias:
        vv = v.to_vertex()
        vias.append(Via(at=vv, size=via_size, drill=via_drill, net=net.code))

  def add_graphics(graphics, layer):
    for ga in graphics.arcs:
      arcs.append(GrArc(ga.center, ga.start, ga.angle, layer=layer))

    for gl in graphics.lines:
      lines.append(GrLine(gl.start, gl.end, layer=layer))

    for gc in graphics.circles:
      circles.append(GrCircle(gc.center, [gc.center[0] + gc.radius, gc.center[1]], layer=layer))

    for gp in graphics.polygons:
      polygons.append(GrPolygon(gp.vertices, layer=layer))

  add_graphics(component.edge_cuts, 'Edge.Cuts')
  add_graphics(component.masks, mask_layer)
  add_graphics(component.silks, 'F.SilkS')

  for h in component.holes:
    m3_hole = Module.from_library('MountingHole', 'MountingHole_3.2mm_M3')
    for t in m3_hole.texts:
      t.hide = True
    m3_hole.at = h.center
    modules += [m3_hole]

  pcb.setup = setup

  pcb.layers += layers
  pcb.nets += nets

  pcb.segments += segments
  pcb.zones += zones
  pcb.vias += vias

  pcb.arcs += arcs
  pcb.lines += lines 
  pcb.circles += circles
  pcb.polygons += polygons

  if add_connector:
    conn = Module.from_library('Connector_PinHeader_2.54mm', 'PinHeader_2x04_P2.54mm_Vertical')
    for t in conn.texts:
        t.hide = True

    x_offset = 1.5 * 0.1 * 25.4 * math.sin(math.pi / 4)
    y_offset = 1.5

    x = 40 - x_offset - y_offset
    y = 40 + x_offset - y_offset
    conn.at = [x, y]
    conn.rotate(135)

    pad_net_names = ['O-', 'O+', 'I-', 'I+', 'C-', 'S-', 'C+', 'S+']

    for i, name in enumerate(pad_net_names):
      net = net_map[name]
      conn.pads[i].net = net

    modules += [conn]

  pcb.modules += modules

  net_class = NetClass('Default', clearance=trace_clearance, trace_width=trace_width, via_dia=via_size, via_drill=via_drill, nets=[n.name for n in nets])

  pcb.net_classes += [net_class]

  return pcb
