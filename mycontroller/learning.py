from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.recoco import Timer

log = core.getLogger()

DEFAULT_STATS_INTERVAL = 15
DEFAULT_IDLE_TIMEOUT = 30


class FlowDatabase(object):

    def __init__(self, stats_interval):

        self.stats_interval = stats_interval
        self.flows = {}

    def update(
        self,
        flow_key,
        match,
        packet_count,
        byte_count,
        duration
    ):

        previous = self.flows.get(flow_key)

        if previous is None:

            packet_delta = packet_count
            byte_delta = byte_count
            idle_polls = 0

        else:

            packet_delta = (
                packet_count -
                previous["packets"]
            )

            byte_delta = (
                byte_count -
                previous["bytes"]
            )

            if packet_delta == 0:
                idle_polls = (
                    previous["idle_polls"] + 1
                )
            else:
                idle_polls = 0

        self.flows[flow_key] = {
            "match": match,
            "packets": packet_count,
            "bytes": byte_count,
            "duration": duration,
            "packet_delta": packet_delta,
            "byte_delta": byte_delta,
            "idle_polls": idle_polls
        }

    def remove(self, flow_key):

        self.flows.pop(
            flow_key,
            None
        )

    def get(self, flow_key):

        return self.flows.get(flow_key)

    def keys(self):

        return list(self.flows.keys())

    def active_flow_count(self):

        return len(self.flows)

    def busiest_flow(self):

        if not self.flows:
            return None

        busiest = max(
            self.flows.items(),
            key=lambda item: item[1]["byte_delta"]
        )

        if busiest[1]["byte_delta"] == 0:
            return None

        return busiest

    def get_idle_flows(
        self,
        idle_timeout
    ):

        idle_limit = (
            idle_timeout //
            self.stats_interval
        )

        idle = []

        for flow_key, stats in self.flows.items():

            if (
                stats["idle_polls"] >=
                idle_limit
            ):
                idle.append(flow_key)

        return idle




class LearningEngine(object):

    def __init__(self, connection, topology):

        self.connection = connection
        self.topology = topology

        self.mac_to_port = {}

        self.installed_flows = set()

        self.stats_interval = DEFAULT_STATS_INTERVAL

        self.idle_timeout = DEFAULT_IDLE_TIMEOUT

        self.flow_db = FlowDatabase(
            self.stats_interval
        )

        connection.addListeners(self)

        Timer(
            self.stats_interval,
            self.request_flow_stats,
            recurring=True
        )

        log.info(
            "Switch %s connected",
            connection.dpid
        )

    def request_flow_stats(self):

        msg = of.ofp_stats_request(
            body=of.ofp_flow_stats_request()
        )

        self.connection.send(msg)

        log.debug(
            "Requested flow statistics"
        )

    def _handle_FlowStatsReceived(
        self,
        event
    ):

        current_flows = set()

        log.info("")
        log.info("=" * 110)

        log.info(
            "%-20s %-20s %8s %8s %10s %10s %8s",
            "Source MAC",
            "Destination MAC",
            "Packets",
            "ΔPkts",
            "Bytes",
            "ΔBytes",
            "Age"
        )

        log.info("-" * 110)

        for stat in event.stats:

            if stat.priority == 0:
                continue

            flow_key = (
                str(stat.match.dl_src),
                str(stat.match.dl_dst)
            )

            current_flows.add(
                flow_key
            )

            self.flow_db.update(
                flow_key,
                stat.match,
                stat.packet_count,
                stat.byte_count,
                stat.duration_sec
            )

            stats = self.flow_db.get(
                flow_key
            )

            log.info(
                "%-20s %-20s %8d %8d %10d %10d %8d",
                flow_key[0],
                flow_key[1],
                stats["packets"],
                stats["packet_delta"],
                stats["bytes"],
                stats["byte_delta"],
                stats["duration"]
            )

        removed = []

        for flow_key in self.flow_db.keys():

            if flow_key not in current_flows:

                removed.append(
                    flow_key
                )

        for flow_key in removed:

            self.flow_db.remove(
                flow_key
            )

        log.info("-" * 110)

        log.info(
            "Active flows : %d",
            self.flow_db.active_flow_count()
        )

        busiest = self.flow_db.busiest_flow()

        if busiest:

            (src, dst), stats = busiest

            log.info(
                "Busiest flow : %s -> %s (%d bytes)",
                src,
                dst,
                stats["byte_delta"]
            )

        else:

            log.info(
                "No active traffic since last poll"
            )

        idle_flows = list(
            self.flow_db.get_idle_flows(
                self.idle_timeout
            )
        )

        log.info("=" * 110)

        for flow_key in idle_flows:

            self.remove_flow(
                flow_key
            )

    def install_flow(
        self,
        event,
        packet,
        out_port
    ):

        flow_key = (
            str(packet.src),
            str(packet.dst)
        )

        if flow_key in self.installed_flows:

            log.info(
                "Flow already installed %s -> %s",
                packet.src,
                packet.dst
            )

            msg = of.ofp_packet_out()

            msg.data = event.ofp

            msg.actions.append(
                of.ofp_action_output(
                    port=out_port
                )
            )

            self.connection.send(msg)

            return

        msg = of.ofp_flow_mod()

        msg.match = of.ofp_match.from_packet(
            packet,
            event.port
        )

        msg.actions.append(
            of.ofp_action_output(
                port=out_port
            )
        )

        msg.data = event.ofp

        self.connection.send(msg)

        self.installed_flows.add(
            flow_key
        )

        log.info(
            "Installed NEW flow %s -> %s (port %d -> %d)",
            packet.src,
            packet.dst,
            event.port,
            out_port
        )

    def remove_flow(
        self,
        flow_key
    ):

        stats = self.flow_db.get(
            flow_key
        )

        if stats is None:
            return False

        msg = of.ofp_flow_mod()

        msg.command = of.OFPFC_DELETE

        msg.match = stats["match"]

        self.connection.send(msg)

        self.installed_flows.discard(
            flow_key
        )

        self.flow_db.remove(
            flow_key
        )

        log.info(
            "Deleted idle flow %s -> %s (idle %d seconds)",
            flow_key[0],
            flow_key[1],
            self.idle_timeout
        )

        return True

    def _handle_PacketIn(
        self,
        event
    ):

        packet = event.parsed

        if not packet.parsed:

            log.warning(
                "Ignoring incomplete packet"
            )

            return

        if packet.type == 0x86DD:
            return

        src = packet.src
        dst = packet.dst
        in_port = event.port

        self.mac_to_port[src] = in_port

        log.info(
            "Packet: %s -> %s type=%s in_port=%d",
            src,
            dst,
            packet.type,
            in_port
        )

        if dst not in self.mac_to_port:

            log.info(
                "Unknown destination %s, flooding",
                dst
            )

            msg = of.ofp_packet_out()

            msg.data = event.ofp

            msg.actions.append(
                of.ofp_action_output(
                    port=of.OFPP_FLOOD
                )
            )

            self.connection.send(msg)

            return

        out_port = self.mac_to_port[dst]

        if out_port == in_port:
            return

        self.install_flow(
            event,
            packet,
            out_port
        )