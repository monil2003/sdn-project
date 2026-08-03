from pox.core import core

log = core.getLogger()


class Link(object):

    def __init__(
        self,
        src_port,
        dst_port,
        cost=1
    ):

        self.src_port = src_port
        self.dst_port = dst_port
        self.cost = cost


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
            {}
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

            neighbors.pop(
                dpid,
                None
            )

        log.info(
            "Switch %s removed",
            dpid
        )

    def add_link(
        self,
        src_switch,
        src_port,
        dst_switch,
        dst_port
    ):

        self.links.setdefault(
            src_switch,
            {}
        )

        new_link = Link(
            src_port,
            dst_port
        )

        changed = (
            dst_switch not in self.links[src_switch]
            or
            self.links[src_switch][dst_switch].src_port != src_port
            or
            self.links[src_switch][dst_switch].dst_port != dst_port
        )

        self.links[src_switch][dst_switch] = new_link

        if changed:

            log.info(
                "Added link %s:%s -> %s:%s",
                src_switch,
                src_port,
                dst_switch,
                dst_port
            )

        return changed

    def remove_link(
        self,
        src_switch,
        dst_switch
    ):

        if src_switch in self.links:

            self.links[src_switch].pop(
                dst_switch,
                None
            )

    def neighbors(
        self,
        dpid
    ):

        return self.links.get(
            dpid,
            {}
        )

    def get_link(
        self,
        src_switch,
        dst_switch
    ):

        if src_switch not in self.links:
            return None

        return self.links[src_switch].get(
            dst_switch
        )

    def is_edge_port(
        self,
        switch,
        port
    ):

        if switch not in self.links:
            return True

        for link in self.links[switch].values():

            if link.src_port == port:
                return False

        return True

    def print_topology(self):

        log.info("")

        log.info("=" * 80)

        log.info("Current Network Topology")

        log.info("=" * 80)

        for src in sorted(
            self.links
        ):

            if not self.links[src]:

                log.info(
                    "Switch %s -> []",
                    src
                )

                continue

            for dst in sorted(
                self.links[src]
            ):

                link = self.links[src][dst]

                log.info(
                    "%s:%s ---> %s:%s cost=%d",
                    src,
                    link.src_port,
                    dst,
                    link.dst_port,
                    link.cost
                )

        log.info("=" * 80)

    def get_output_port(
        self,
        src_switch,
        dst_switch
    ):

        link = self.get_link(
            src_switch,
            dst_switch
        )

        if link is None:
            return None

        return link.src_port