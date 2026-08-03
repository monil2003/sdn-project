from pox.core import core

from .learning import LearningEngine

from .lldp import LLDPManager

log = core.getLogger()


class SDNController(object):

    def __init__(
        self,
        connection,
        topology,
        routing,
        switch_manager,
        path,
        host_db
    ):

        self.connection = connection

        self.lldp = LLDPManager()

        self.topology = topology

        self.routing = routing

        self.switch_manager = switch_manager

        self.path = path
        
        self.host_db = host_db

        self.learning = LearningEngine(
            connection,
            topology,
            self.lldp,
            self.routing,
            self.switch_manager,
            self.path,
            self.host_db
        )

        log.info(
            "Controller initialized"
        )