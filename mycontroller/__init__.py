from pox.core import core

from .controller import SDNController
from .topology import TopologyManager
from .host import HostDatabase
from .routing import RoutingManager
from .path import PathManager
from .switch_manager import SwitchManager

log = core.getLogger()

topology = TopologyManager()
host_db = HostDatabase()
routing = RoutingManager(topology)
switch_manager = SwitchManager()
path = PathManager(
    topology,
    routing,
    host_db,
    switch_manager
)


def start_switch(event):

    log.info("Switch connected")

    topology.add_switch(
        event.connection.dpid
    )

    switch_manager.add_switch(
        event.connection
    )

    SDNController(
        event.connection,
        topology,
        routing,
        switch_manager,
        path,
        host_db
    )

    # log.info(
    #     "Topology object %s",
    #     id(topology)
    # )

def launch():

    core.openflow.addListenerByName(
        "ConnectionUp",
        start_switch
    )