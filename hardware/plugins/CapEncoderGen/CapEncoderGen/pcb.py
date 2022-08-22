import pcbnew



class PCB(object):
    def __init__(self):
        self.board = pcbnew.GetBoard()

    def remove_all_zones(self):
        for z in self.board.Zones():
            self.board.Remove(z)

    def add_zone(self, net, layer, points):
        if len(points) < 3:
            raise ValueError("there must be at least three points")

        p1 = pcbnew.wxPoint(int(points[0][0] * 1e6), int(points[0][1] * 1e6))
        zone = self.board.AddArea(None, 0, pcbnew.F_Cu, p1, pcbnew.ZONE_FILL_MODE_POLYGONS)
        
        sps = zone.Outline()
        for p in points[1:]:
            sps.Append(int(p[0] * 1e6), int(p[1] * 1e6))
