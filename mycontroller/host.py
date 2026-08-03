from pox.core import core

log = core.getLogger()


class Host(object):

    def __init__(
        self,
        mac,
        switch,
        port
    ):

        self.mac = mac

        self.switch = switch

        self.port = port


class HostDatabase(object):

    def __init__(self):

        self.hosts = {}

    def learn(
        self,
        mac,
        switch,
        port
    ):

        changed = False

        host = self.hosts.get(
            mac
        )

        if host is None:

            self.hosts[mac] = Host(
                mac,
                switch,
                port
            )

            changed = True

        else:

            if (
                host.switch != switch
                or
                host.port != port
            ):

                host.switch = switch

                host.port = port

                changed = True

        if changed:

            log.info(
                "Host %s -> Switch %s Port %s",
                mac,
                switch,
                port
            )

        return changed

    def get(
        self,
        mac
    ):

        return self.hosts.get(
            mac
        )

    def print_hosts(
        self
    ):

        log.info("")

        log.info("=" * 70)

        log.info("Host Database")

        log.info("=" * 70)

        for mac in sorted(
            self.hosts
        ):

            host = self.hosts[mac]

            log.info(
                "%-18s -> Switch %s Port %s",
                mac,
                host.switch,
                host.port
            )

        log.info("=" * 70)