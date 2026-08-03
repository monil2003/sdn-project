from pox.core import core

from pox.lib.packet.ethernet import (
    ethernet
)
from pox.lib.packet import ETHERNET

from pox.lib.packet.lldp import (
    lldp,
    chassis_id,
    port_id,
    ttl,
    system_description,
    end_tlv
)

log = core.getLogger()


class LLDPManager(object):

    def __init__(self):
        pass

    def build_packet(
        self,
        dpid,
        port_no,
        port_addr
    ):

        chassis = chassis_id(
            subtype=chassis_id.SUB_LOCAL
        )

        chassis.id = (
            "dpid:" +
            hex(int(dpid))[2:]
        ).encode()

        port = port_id(
            subtype=port_id.SUB_PORT,
            id=str(port_no)
        )

        ttl_tlv = ttl(
            ttl=120
        )

        sysdesc = system_description()

        sysdesc.payload = (
            "dpid:" +
            hex(int(dpid))[2:]
        ).encode()

        lldp_pkt = lldp()

        lldp_pkt.tlvs.append(
            chassis
        )

        lldp_pkt.tlvs.append(
            port
        )

        lldp_pkt.tlvs.append(
            ttl_tlv
        )

        lldp_pkt.tlvs.append(
            sysdesc
        )

        lldp_pkt.tlvs.append(
            end_tlv()
        )

        eth = ethernet(
            type=ethernet.LLDP_TYPE
        )

        eth.src = port_addr

        eth.dst = ETHERNET.NDP_MULTICAST

        eth.payload = lldp_pkt

        return eth

    def is_lldp(
        self,
        packet
    ):

        return (
            packet.type ==
            ethernet.LLDP_TYPE
        )


    def parse_packet(
        self,
        packet
    ):

        lldp_pkt = packet.payload

        if (
            lldp_pkt is None or
            len(lldp_pkt.tlvs) < 4
        ):
            return None

        chassis = (
            lldp_pkt.tlvs[0]
            .id
            .decode()
        )

        sender_dpid = int(
            chassis.replace(
                "dpid:",
                ""
            ),
            16
        )

        sender_port = int(
            lldp_pkt.tlvs[1].id
        )

        return (
            sender_dpid,
            sender_port
        )