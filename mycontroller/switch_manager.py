from pox.core import core

log = core.getLogger()


class SwitchManager(object):

    def __init__(self):

        self.connections = {}

    def add_switch(
        self,
        connection
    ):

        self.connections[
            connection.dpid
        ] = connection

        log.info(
            "Registered switch %s",
            connection.dpid
        )

    def remove_switch(
        self,
        dpid
    ):

        self.connections.pop(
            dpid,
            None
        )

        log.info(
            "Removed switch %s",
            dpid
        )

    def get_connection(
        self,
        dpid
    ):

        return self.connections.get(
            dpid
        )

    def all_switches(
        self
    ):

        return self.connections.keys()