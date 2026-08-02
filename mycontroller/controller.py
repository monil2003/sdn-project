from pox.core import core
from .topology import TopologyManager
from .learning import LearningEngine

log = core.getLogger()


class SDNController(object):

    def __init__(self, connection):

        self.connection = connection

        self.topology = TopologyManager()

        self.topology.add_switch(
            connection.dpid
        )

        self.learning = LearningEngine(
            connection,
            self.topology
        )

        log.info("Controller initialized")
