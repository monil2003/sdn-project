from pox.core import core
from .controller import SDNController

log = core.getLogger()


def start_switch(event):
    log.info("Switch connected")

    SDNController(event.connection)


def launch():
    core.openflow.addListenerByName(
        "ConnectionUp",
        start_switch
    )
