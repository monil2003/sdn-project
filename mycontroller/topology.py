from pox.core import core

log = core.getLogger()


class TopologyManager(object):

    def __init__(self):

        self.switches = set()

        self.links = {}

    def add_switch(
        self,
        dpid
    ):

        if dpid in self.switches:
            return

        self.switches.add(
            dpid
        )

        self.links.setdefault(
            dpid,
            set()
        )

        log.info(
            "Switch %s added",
            dpid
        )

    def remove_switch(
        self,
        dpid
    ):

        if dpid not in self.switches:
            return

        self.switches.remove(
            dpid
        )

        self.links.pop(
            dpid,
            None
        )

        for neighbors in self.links.values():

            neighbors.discard(
                dpid
            )

        log.info(
            "Switch %s removed",
            dpid
        )

    def add_link(
        self,
        src,
        dst
    ):

        self.links.setdefault(
            src,
            set()
        )

        if dst in self.links[src]:
            return

        self.links[src].add(
            dst
        )

        log.info(
            "Link %s -> %s",
            src,
            dst
        )

    def remove_link(
        self,
        src,
        dst
    ):

        if src in self.links:

            self.links[src].discard(
                dst
            )

    def neighbors(
        self,
        dpid
    ):

        return self.links.get(
            dpid,
            set()
        )

    def print_topology(self):

        log.info("")

        log.info("=" * 60)

        log.info("Current Network Topology")

        log.info("=" * 60)

        for switch in sorted(
            self.switches
        ):

            log.info(
                "Switch %-3s -> %s",
                switch,
                sorted(
                    self.links[switch]
                )
            )

        log.info("=" * 60)
