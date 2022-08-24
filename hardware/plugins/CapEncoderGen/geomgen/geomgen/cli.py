import json

from .geometry import StatorComponent



def test():
    print("""
    {
        "zones": [
            {
                "net": "S+",
                "layer": "F.Cu",
                "points": [
                    [0, 0],
                    [5, 0],
                    [5, 5],
                    [0, 5]
                ]
            }
        ],
        "tracks": [
            {
                "net": "S+",
                "layer": "F.Cu",
                "start": [100, 100],
                "end": [150, 100],
                "width": 0.127
            }
        ],
        "vias": [
            {
                "net": "S+",
                "point": [100, 100],
                "size": 0.6,
                "drill": 0.4
            }
        ]
    }
    """)

def main():
    component = StatorComponent(30, 61.4, 100)


    zones = []


    for s in component.signals:
        net_name = s.name

        # avs = s.arc.to_polygon()
        # for i in range(len(avs) - 1):
        #     segments.append(Segment(start=avs[i], end=avs[i + 1], net=net.code, layer=arc_layer, width=trace_width))

        for e in s.electrodes:
            evs = e.to_polygon()
            zones.append({
                "net": net_name,
                "layer": "F.Cu",
                "points": evs
            })

        # for v in s.vias:
        #     vv = v.to_vertex()
        #     vias.append(Via(at=vv, size=via_size, drill=via_drill, net=net.code))

    geom = {
        "zones": zones,
        "tracks": [],
        "vias": []
    }

    output = json.dumps(geom)
    print(output)

if __name__ == "__main__":
    main()
