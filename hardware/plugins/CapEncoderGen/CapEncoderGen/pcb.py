import pcbnew



class PCB(object):
    def __init__(self):
        self.board = pcbnew.GetBoard()

    def remove_all_zones(self):
        # Avoid mutating the list while iterating it.
        all_zones = list(self.board.Zones())
        for z in all_zones:
            self.board.Remove(z)

    def add_zone(self, net, layer, points):

        # Fixme: Use FromMM for unit conversion!!!

        if len(points) < 3:
            raise ValueError("there must be at least three points")

        net_id = self.find_or_create_net(net)
        layer_id = self.board.GetLayerID(layer)

        p1 = pcbnew.wxPoint(int(points[0][0] * 1e6), int(points[0][1] * 1e6))
        zone = self.board.AddArea(None, net_id, layer_id, p1, pcbnew.ZONE_FILL_MODE_POLYGONS)
        
        sps = zone.Outline()
        for p in points[1:]:
            sps.Append(int(p[0] * 1e6), int(p[1] * 1e6))

    def find_or_create_net(self, net):
        net_map = self.board.GetNetsByName()
        if net_map.has_key(net):
            net_info = net_map[net]
        else:
            net_info = pcbnew.NETINFO_ITEM(self.board, net)
            self.board.Add(net_info)

        return net_info.GetNetCode()
