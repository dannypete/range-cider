import ipaddress
import logging

SCRIPT_NAME = "remove-exceptions"

logger = logging.getLogger(__name__)


def handle_remove_exceptions(args):
    ranges_txt = open(args.ranges).read().split()
    rangesnws = list(
        map(lambda x: ipaddress.IPv4Network(x, strict=False), ranges_txt))

    excpt_txt = open(args.exceptions).read().split()
    excptnws = list(
        map(lambda x: ipaddress.IPv4Network(x, strict=False), excpt_txt))

    # TODO don't read into memory; be smarter using IPAddress's existing functions
    range_hosts = []
    for rnge in rangesnws:
        range_hosts.extend(list(rnge))

    excpt_hosts = []
    for ecpt in excptnws:
        excpt_hosts.extend(list(ecpt))

    for excpt_host in excpt_hosts:
        if excpt_host in range_hosts:
            range_hosts.remove(excpt_host)

    if not args.expanded:
        range_hosts = list(ipaddress.collapse_addresses(range_hosts))

    print("\n".join(map(str, sorted(range_hosts))))

    if args.output:
        open(args.output, "w").write("\n".join(map(str, range_hosts)))


def add_parser_configuration(subparser):
    remove_exceptions_subparser = subparser.add_parser(
        SCRIPT_NAME, help="Remove exceptions from ranges")
    remove_exceptions_subparser.set_defaults(handler=handle_remove_exceptions)
    remove_exceptions_subparser.set_defaults(parser=SCRIPT_NAME)

    remove_exceptions_subparser.add_argument(
        "-e", "--exceptions", help="Exceptions file path", required=True, type=str)
    remove_exceptions_subparser.add_argument(
        "--expanded", help="Output a single IP per line", required=False, action="store_true", default=False)
