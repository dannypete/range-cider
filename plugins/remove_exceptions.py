import ipaddress
import logging

SCRIPT_NAME = "remove-exceptions"

logger = logging.getLogger(__name__)


def handle_remove_exceptions(ranges, exceptions, args):
    rangesnws = list(
        map(lambda x: ipaddress.IPv4Network(x, strict=False), ranges))

    excptnws = list(
        map(lambda x: ipaddress.IPv4Network(x, strict=False), exceptions))

    # TODO don't read into memory; be smarter using IPAddress's existing functions
    range_hosts = set()
    for rnge in rangesnws:
        range_hosts = range_hosts.union(set(rnge))
    range_hosts = sorted(range_hosts)

    excpt_hosts = set()
    for ecpt in excptnws:
        excpt_hosts = excpt_hosts.union(set(ecpt))
    excpt_hosts = sorted(excpt_hosts)

    for excpt_host in excpt_hosts:
        if excpt_host in range_hosts:
            range_hosts.remove(excpt_host)
            logger.debug(f"Removing {str(excpt_host)} from ranges.")

    if not args.expanded:
        range_hosts = list(ipaddress.collapse_addresses(range_hosts))

    result = "\n".join(map(str, range_hosts))
    return result


def add_parser_configuration(subparser):
    remove_exceptions_subparser = subparser.add_parser(
        SCRIPT_NAME, help="Remove exceptions from ranges")
    remove_exceptions_subparser.set_defaults(handler=handle_remove_exceptions)
    remove_exceptions_subparser.set_defaults(parser=SCRIPT_NAME)

    remove_exceptions_subparser.add_argument(
        "--expanded", help="Output a single IP per line", required=False, action="store_true", default=False)
