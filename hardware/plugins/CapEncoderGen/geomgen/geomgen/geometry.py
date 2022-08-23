import math
from scipy.optimize import minimize

ROTOR_INSET = 2
STAGE_INSET = 1
STAGE_SPACING = 0.5
BUS_PITCH = 0.75

class Component:
    def __init__(self, inner_radial_diameter, outer_radial_diameter, box_dimension):
        self.inner_radial_diameter = inner_radial_diameter
        self.outer_radial_diameter = outer_radial_diameter
        self.box_dimension = box_dimension

        self.signals = list()
        
        self.edge_cuts = Graphics()
        self.masks = Graphics()
        self.silks = Graphics()
        self.holes = list()

        stage_ir = self.outer_radial_diameter / 2 + STAGE_INSET
        stage_or = self.box_dimension / 2 - STAGE_INSET - ROTOR_INSET

        self.ann = self.compute_annuli(stage_ir, stage_or, STAGE_SPACING)

    def build_stages(self, options):
        self.stages = [
            Stage(4, 4, 36, 12, self.ann[1][0], self.ann[1][1], options[0]),
            Stage(4, 2, 36, 36, self.ann[2][0], self.ann[2][1], options[1]),
            Stage(4, 2, 35, 35, self.ann[0][0], self.ann[0][1], options[2])
        ]

    def build_masks(self):
        rx = self.box_dimension / 2 + 1
        ry = self.box_dimension / 2 + 1

        self.masks.polygons += [GraphicPolygon([
            [-rx, -ry],
            [ rx, -ry],
            [ rx,  ry],
            [-rx,  ry]
        ])]    

    def compute_annuli(self, ri, ro, rsp):
        S = ro - ri - 2 * rsp

        def objective(x):
            return -x[0]
        def constraint(x):
            drs = compute_drs(x[0])
            return S - drs[0] - drs[1] - drs[2]
        def compute_drs(dr1):
            r1 = ri
            A = (r1 + dr1) ** 2 - r1 ** 2
            r2 = r1 + dr1 + rsp
            dr2 = math.sqrt(r2 ** 2 + A) - r2
            r3 = r2 + dr2 + rsp
            dr3 = math.sqrt(r3 ** 2 + A) - r3
            return (dr1, dr2, dr3)
        def compute_ranges(drs):
            r1 = ri
            r2 = r1 + drs[0] + rsp
            r3 = r2 + drs[1] + rsp
            return ((r1, r1 + drs[0]), (r2, r2 + drs[1]), (r3, r3 + drs[2]))

        x0 = [0]
        bounds = [(0, S)]
        constraints = [{'type': 'eq', 'fun': constraint}]
        sol = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        drs = compute_drs(sol.x[0])
        return compute_ranges(drs)

    def add_layer(self, layer, signal_names):
        for l, sn in zip(layer.groups, signal_names):
            self.signals.append(ComponentSignal(sn, l.arc, l.electrodes, l.vias))

class StatorComponent(Component):
    def __init__(self, inner_radial_diameter, outer_radial_diameter, box_dimension):
        super(StatorComponent, self).__init__(inner_radial_diameter, outer_radial_diameter, box_dimension)

        stage_options = [
            StageOptions(True, True, False, False),
            StageOptions(True, False, False, False),
            StageOptions(True, False, True, False)
        ]

        self.build_stages(stage_options)

        self.add_layer(self.stages[0].input_layer, ['S+', 'C+', 'S-', 'C-'])
        self.add_layer(self.stages[1].output_layer, ['O+', 'O-'])
        self.add_layer(self.stages[2].output_layer, ['I+', 'I-'])

        self.build_edge_cuts()
        self.build_masks()
        self.build_silks()

    def build_edge_cuts(self):
        r1 = self.box_dimension / 2
        r2 = 4

        x = 2 * math.sqrt(r1 * r2)
        y1 = r1 - r2
        y2 = r1

        for angle in range(0, 360, 90):
            negative_arc = GraphicArc(rot([x, y1], angle), rot([x, y2], angle), -45)
            positive_arc = GraphicArc(rot([y1, x], angle), rot([y2, x], angle), 45)

            negative_line = GraphicLine(rot([0, r1], angle), rot([x, y2], angle))
            positive_line = GraphicLine(rot([r1, 0], angle), rot([y2, x], angle))
            mid_line = GraphicLine(negative_arc.end(), positive_arc.end())

            self.edge_cuts.arcs += [
                negative_arc,
                positive_arc
            ]

            self.edge_cuts.lines += [
                negative_line,
                positive_line,
                mid_line
            ]

            self.holes += [
                MountingHole(rot([x, y1], angle)),
                MountingHole(rot([y1, x], angle))
            ]

        self.edge_cuts.circles += [
            GraphicCircle([0, 0], self.outer_radial_diameter / 2)
        ]

    def build_silks(self):
        self.silks.circles += [
            GraphicCircle([0, 0], self.box_dimension / 2 - ROTOR_INSET)
        ]

class RotorComponent(Component):
    def __init__(self, inner_radial_diameter, outer_radial_diameter, box_dimension):
        super(RotorComponent, self).__init__(inner_radial_diameter, outer_radial_diameter, box_dimension)

        stage_options = [
            StageOptions(False, False, True, True),
            StageOptions(False, False, True, False),
            StageOptions(False, True, False, False)
        ]

        self.build_stages(stage_options)    

        self.add_layer(self.stages[0].output_layer, ['UO1', 'UO2', 'UO3', 'UO4'])
        self.add_layer(self.stages[1].input_layer, ['UO1', 'UO2', 'UO3', 'UO4'])
        self.add_layer(self.stages[2].input_layer, ['UO4', 'UO3', 'UO2', 'UO1'])

        self.build_edge_cuts()
        self.build_masks()
        self.build_silks()

    def build_edge_cuts(self):
        self.edge_cuts.circles += [
            GraphicCircle([0, 0], self.box_dimension / 2 - ROTOR_INSET),
            GraphicCircle([0, 0], self.inner_radial_diameter / 2)
        ]

        self.holes += [
            MountingHole(rot([22, 0], angle)) for angle in range(0, 360, 60)
        ]

    def build_silks(self):
        self.silks.circles += [
            GraphicCircle([0, 0], self.outer_radial_diameter / 2)
        ]

class ComponentSignal:
    def __init__(self, name, arc, electrodes, vias):
        self.name = name
        self.arc = arc
        self.electrodes = electrodes
        self.vias = vias

class StageOptions:
    def __init__(self,
                 clip_induction,
                 invert_bus,
                 start_butt,
                 end_butt):
        self.clip_induction = clip_induction
        self.invert_bus = invert_bus
        self.start_butt = start_butt
        self.end_butt = end_butt

class Stage:
    def __init__(self,               
                 input_count,
                 output_count,          
                 excitation_periods,
                 induction_periods,
                 inner_radius,
                 outer_radius,
                 options):
        excitation_count = input_count * excitation_periods
        induction_count = output_count * induction_periods

        excitation_angle = 360 / float(excitation_count)
        induction_pitch_angle = 360 / float(induction_count)
        induction_width_angle = 2 * excitation_angle

        def build_excitation_electrode(sector):
            return ExcitationElectrode(sector)

        self.input_layer = self.__build_layer(
            build_excitation_electrode,
            input_count,
            excitation_periods,
            excitation_angle,
            excitation_angle,
            inner_radius,
            outer_radius,
            BUS_PITCH,
            options.invert_bus,
            options.start_butt,
            options.end_butt)

        def build_induction_electrode(sector):
            return InductionElectrode(sector, 0.025 if options.clip_induction else 0)

        self.output_layer = self.__build_layer(
            build_induction_electrode,
            output_count,
            induction_periods,
            induction_pitch_angle,
            induction_width_angle,
            inner_radius,
            outer_radius,
            BUS_PITCH,
            options.invert_bus,
            options.start_butt,
            options.end_butt)

    def __build_layer(self,
                      electrode_builder,
                      channel_count,
                      period_count,
                      pitch_angle,
                      width_angle,
                      inner_radius,
                      outer_radius,
                      bus_pitch,
                      invert_bus,
                      start_butt,
                      end_butt):
        center_radius = (inner_radius + outer_radius) / 2

        bus_width = bus_pitch * (channel_count - 1)

        electrode_count = channel_count * period_count
        start_butt_angle = 45
        end_butt_angle = pitch_angle * (electrode_count - 1) + 45

        groups = []
        for ch in range(channel_count):      
            center_angles = [pitch_angle * (ch + channel_count * p) + 45 for p in range(period_count)]

            if not invert_bus:
                bus_lower_radius = center_radius - bus_width / 2
                bus_radius = bus_lower_radius + ch * bus_pitch
            else:
                bus_upper_radius = center_radius + bus_width / 2
                bus_radius = bus_upper_radius - ch * bus_pitch

            if not start_butt:
                start_angle = center_angles[0]
            else:
                start_angle = start_butt_angle

            if not end_butt:
                end_angle = center_angles[-1]
            else:
                end_angle = end_butt_angle

            arc = Arc(bus_radius, start_angle, end_angle)
            vias = [Via(bus_radius, ca) for ca in center_angles]

            electrodes = [
                electrode_builder(
                    AnnularSector(
                        inner_radius,
                        outer_radius,
                        ca - width_angle / 2,
                        ca + width_angle / 2)
                    ) for ca in center_angles]

            group = ElectrodeGroup(arc, electrodes, vias)
            groups.append(group)

        return Layer(groups)

class Layer:
    def __init__(self, groups):
        self.groups = groups

class ElectrodeGroup:
    def __init__(self, arc, electrodes, vias):
        self.arc = arc
        self.electrodes = electrodes
        self.vias = vias

class Electrode:
    def __init__(self, sector):
        self.sector = sector

    def to_polygon():
        raise NotImplementedError

class ExcitationElectrode(Electrode):
    def __init__(self, sector):
        super(ExcitationElectrode, self).__init__(sector)

    def to_polygon(self):
        radius = self.sector.center_radius()
        delta_radius = self.sector.radial_length() / 2

        start_angle = self.sector.start_angle
        end_angle = self.sector.end_angle

        width_fraction = 0.5
        base_theta = 0.5 * width_fraction * (end_angle - start_angle) + start_angle
        width_angle = width_fraction * (end_angle - start_angle)

        vertices = []

        n = 2

        for i in range(0, n + 1):
            f = i / float(n)
            r = radius + delta_radius
            theta = base_theta + f * width_angle
            vertices.append(from_polar(r, theta))

        for i in range(0, n + 1):
            f = 1.0 - i / float(n)
            r = radius - delta_radius
            theta = base_theta + f * width_angle
            vertices.append(from_polar(r, theta))

        return vertices

class InductionElectrode(Electrode):
    def __init__(self, sector, cutoff):
        super(InductionElectrode, self).__init__(sector)
        self.cutoff = cutoff

    def to_polygon(self):
        radius = self.sector.center_radius()
        delta_radius = self.sector.radial_length() / 2

        start_angle = self.sector.start_angle
        end_angle = self.sector.end_angle

        base_theta = start_angle
        width_angle = end_angle - start_angle

        vertices = []

        for i in range(0, 12):
            f = i / 11.0
            fa = (1 - 2 * self.cutoff) * f + self.cutoff
            r = radius + delta_radius * math.sin(math.pi * fa)
            theta = base_theta + fa * width_angle
            vertices.append(from_polar(r, theta))

        for i in range(0, 12):
            f = 1.0 - i / 11.0
            fa = (1 - 2 * self.cutoff) * f + self.cutoff
            r = radius - delta_radius * math.sin(math.pi * fa)
            theta = base_theta + fa * width_angle
            vertices.append(from_polar(r, theta))

        return vertices

class Arc:
    def __init__(self, radius, start_angle, end_angle):
        self.radius = radius
        self.start_angle = start_angle
        self.end_angle = end_angle

    def to_polygon(self):
        vertices = []
        for i in range(361):
            f = i / 360
            theta = self.start_angle + f * (self.end_angle - self.start_angle)
            vertices.append(from_polar(self.radius, theta))
        return vertices

class Via:
    def __init__(self, radius, angle):
        self.radius = radius
        self.angle = angle

    def to_vertex(self):
        return from_polar(self.radius, self.angle)

class Graphics:
    def __init__(self):
        self.lines = []
        self.circles = []
        self.arcs = []
        self.polygons = []

class GraphicLine:
    def __init__(self, start, end):
        self.start = start
        self.end = end

class GraphicCircle:
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

class GraphicArc:
    def __init__(self, center, start, angle):
        self.center = center
        self.start = start
        self.angle = angle

    def end(self):
        dx = self.start[0] - self.center[0]
        dy = self.start[1] - self.center[1]
        theta = math.pi / 180.0 * self.angle
        s, c = math.sin(theta), math.cos(theta)
        ex = c * dx - s * dy + self.center[0]
        ey = s * dx + c * dy + self.center[1]
        return (ex, ey)

class GraphicPolygon:
    def __init__(self, vertices):
        self.vertices = vertices

class MountingHole:
    def __init__(self, center):
        self.center = center

class AnnularSector:
    def __init__(self, inner_radius, outer_radius, start_angle, end_angle):
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.start_angle = start_angle
        self.end_angle = end_angle

    def radial_length(self):
        return self.outer_radius - self.inner_radius

    def angular_length(self):
        return self.end_angle - self.start_angle

    def center_radius(self):
        return (self.inner_radius + self.outer_radius) / 2

    def center_angle(self):
        return (self.start_angle + self.end_angle) / 2

    def center_arc_length(self):
        return 2 * math.pi * self.center_radius() * (self.angular_length() / 360.0)

def from_polar(r, theta):
    theta_rad = math.pi / 180.0 * theta
    x = r * math.cos(theta_rad)
    y = r * math.sin(theta_rad)
    return (x, y)

def rot(p, angle):
    theta = math.pi / 180.0 * angle
    s, c = math.sin(theta), math.cos(theta)
    ex = c * p[0] - s * p[1]
    ey = s * p[0] + c * p[1]
    return (ex, ey)
