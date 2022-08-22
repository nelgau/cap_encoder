import os
import pcbnew

from .pcb import PCB
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
        pcb = PCB()

        pcb.remove_all_zones()

        tmpl = [
            [0, 0],
            [5, 0],
            [5, 5],
            [0, 5]
        ]

        for i in range(0, 10):
            pts = [[p[0] + 20 * i, p[1]] for p in tmpl]
            pcb.add_zone(None, None, pts)
