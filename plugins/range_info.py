import logging

SCRIPT_NAME = "info"

logger = logging.getLogger(__name__)


def handle_info(ranges, exceptions, args):
    logger.warning("Not implemented")


def add_parser_configuration(subparser):
    info_subparser = subparser.add_parser(
        SCRIPT_NAME, help="Print information about ranges (and exceptions, if provided and applicable).")
    info_subparser.set_defaults(handler=handle_info)
    info_subparser.set_defaults(parser=SCRIPT_NAME)

    info_subparser.add_argument(
        "--co", "--check-overlap", help="Check if supplied ranges have any overlap", action="store_true", default=False)
    info_subparser.add_argument(
        "--fl", "--first-last", help="Print first and last IP for each range", action="store_true", default=False)
    info_subparser.add_argument(
        "--rs", "--range-size", help="Print number of IPs per range (with any exceptions removed)", action="store_true", default=False)
    info_subparser.add_argument(
        "--ts", "--total-size", help="Print total number of IPs of all ranges combined (with any exceptions removed)", action="store_true", default=False)
    info_subparser.add_argument("--nb", "--network-broadcast",
                                help="Print network and broadcast addresses for each range", action="store_true", default=False)
    info_subparser.add_argument(
        "--rfc1918", help="Prints whether each range is a private or public IP address according to RFC1918", action="store_true", default=False)
    info_subparser.add_argument(
        "--nm", "--with-netmask", help="Print ranges with their netmasks", action="store_true", default=False)
    info_subparser.add_argument(
        "--hm", "--with-hostmask", help="Print ranges with their hostmasks", action="store_true", default=False)
