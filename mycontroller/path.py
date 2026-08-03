from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import EthAddr


log = core.getLogger()


class PathManager(object):

    def __init__(
        self,
        topology,
        routing,
        host_db,
        switch_manager
    ):

        self.topology = topology
        self.host_db = host_db
        self.routing = routing
        self.switch_manager = switch_manager
        self.installed_paths = {}

    def install_flow(
        self,
        connection,
        src_mac,
        dst_mac,
        out_port
    ):
        msg = of.ofp_flow_mod()

        msg.match.dl_src = EthAddr(src_mac)
        msg.match.dl_dst = EthAddr(dst_mac)

        msg.actions.append(
            of.ofp_action_output(
                port=out_port
            )
        )

        connection.send(msg)

    def install_path(
        self,
        src_mac,
        dst_mac,
        path,
        event
    ):

        key = (
            src_mac,
            dst_mac
        )

        if key in self.installed_paths:
            return

        log.info("")
        log.info("=" * 60)
        log.info(
            "Installing path for %s -> %s",
            src_mac,
            dst_mac
        )

        dst_host = self.host_db.get(dst_mac)

        if dst_host is None:
            return

        self.installed_paths[key] = list(path)

        for i, switch in enumerate(path):

            connection = self.switch_manager.get_connection(
                switch
            )

            if connection is None:
                continue
            if i == len(path) - 1:

                out_port = dst_host.port
            else:

                next_switch = path[i + 1]

                out_port = self.topology.get_output_port(
                    switch,
                    next_switch
                )

            log.info(
                "Switch %s -> output port %s",
                switch,
                out_port
            )

            self.install_flow(
                connection,
                src_mac,
                dst_mac,
                out_port
            )

        first_switch = path[0]

        if self.switch_manager.get_connection(first_switch) == event.connection:
            if len(path) > 1:

                out_port = self.topology.get_output_port(
                    path[0],
                    path[1]
                )
            else:
                out_port = dst_host.port
            self.send_packet(
                event.connection,
                event,
                out_port
            )

        log.info("=" * 60)


    def send_packet(
        self,
        connection,
        event,
        out_port
    ):
        msg = of.ofp_packet_out()
        msg.data = event.ofp
        msg.actions.append(
            of.ofp_action_output(
                port=out_port
            )
        )

        connection.send(msg)

    def has_path(
        self,
        src_mac,
        dst_mac
    ):

        return (
            src_mac,
            dst_mac
        ) in self.installed_paths

    def clear_paths(
        self
    ):

        self.installed_paths.clear()

    def remove_path(
        self,
        src_mac,
        dst_mac
    ):

        key = (
            src_mac,
            dst_mac
        )

        if key not in self.installed_paths:
            return False

        src_host = self.host_db.get(
            src_mac
        )

        dst_host = self.host_db.get(
            dst_mac
        )

        if (
            src_host is None
            or
            dst_host is None
        ):
            return False

        path = self.installed_paths.get(key)

        if path is None:
            return False

        for switch in path:

            connection = self.switch_manager.get_connection(
                switch
            )

            if connection is None:
                continue

            msg = of.ofp_flow_mod()

            msg.command = of.OFPFC_DELETE

            msg.match.dl_src = EthAddr(
                src_mac
            )

            msg.match.dl_dst = EthAddr(
                dst_mac
            )

            connection.send(
                msg
            )

        self.installed_paths.pop(
            key,
            None
        )

        log.info(
            "Removed path %s -> %s",
            src_mac,
            dst_mac
        )

        return True