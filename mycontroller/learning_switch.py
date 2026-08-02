
from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()


class LearningSwitch(object):
    def __init__(self, connection):
        self.connection = connection

        # MAC Address -> Switch Port
        self.mac_to_port = {}

        connection.addListeners(self)

        log.info("Switch %s connected", connection.dpid)

    def _handle_PacketIn(self, event):
        packet = event.parsed

        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return

        src = packet.src
        dst = packet.dst

        in_port = event.port

        # Learn source MAC
        self.mac_to_port[src] = in_port

        log.info(
           "Packet: %s -> %s  type=%s",
           src,
           dst,
           packet.type
        )

        if dst in self.mac_to_port:

            out_port = self.mac_to_port[dst]

            msg = of.ofp_flow_mod()

            msg.match = of.ofp_match.from_packet(packet, in_port)

            msg.actions.append(
                of.ofp_action_output(port=out_port)
            )
            msg.data = event.ofp

            self.connection.send(msg)

            log.info(
                "Installing flow %s -> %s via port %s",
                src,
                dst,
                out_port
            )

        else:

            msg = of.ofp_packet_out()

            msg.data = event.ofp

            msg.actions.append(
                of.ofp_action_output(
                    port=of.OFPP_FLOOD
                )
            )

            self.connection.send(msg)

            log.info(
                "Flooding packet %s -> %s",
                src,
                dst
            )


def start_switch(event):
    log.info("Controlling %s", event.connection)
    LearningSwitch(event.connection)


def launch():
    core.openflow.addListenerByName(
        "ConnectionUp",
        start_switch
    )
