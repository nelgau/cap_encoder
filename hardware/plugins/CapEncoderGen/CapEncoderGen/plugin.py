import os
import json
import time
import pcbnew

from .pcb import PCB
from .geomgen import GeomgenCommand
from .logger import get_logger, log_exception



class CapEncoderGenPlugin(pcbnew.ActionPlugin, object):
    def __init__(self):
        super(CapEncoderGenPlugin, self).__init__()

        self.name = "Generate Capacitive Encoder"
        self.description = "Generate Capacitive Encoder"
        self.category = "Modify PCB"

        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'icon.png')

        self.logger = get_logger()

    @log_exception(reraise=True)
    def Run(self):
        c = GeomgenCommand()
        output = c.run()

        self.logger.info("result: %s", output)

        geom = json.loads(output)

        pcb = PCB()
        pcb.remove_all_zones()

        for z in geom['zones']:
            net = z['net']
            layer = z['layer']
            points = z['points']
            pcb.add_zone(net, layer, points)
