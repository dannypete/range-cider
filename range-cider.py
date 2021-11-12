import argparse
import ipaddress
import logging
import sys

import plugins.range_info
import plugins.remove_exceptions

logger = logging.getLogger(__name__)


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-r", "--ranges", help="Comma-separated ranges", required=False, type=str)
    parser.add_argument(
        "--rp", "--ranges-path", help="Ranges file path", required=False, type=str)

    parser.add_argument(
        "-e", "--exceptions", help="Comma-separated ranges", required=False, type=str)
    parser.add_argument(
        "--ep", "--exceptions-path", help="Exceptions file path", required=False, type=str)

    parser.add_argument("-v", "--verbose", help="More output",
                        required=False, action="store_true", default=False)
    parser.add_argument("--debug", help="More output (implies --verbose)",
                        required=False, action="store_true", default=False)
    parser.add_argument("--op", "--output-path", help="Output file path",
                        required=False, type=str, default="")
    parser.add_argument("-6", "--ipv6", help="Provided IPs are IPv6, not IPv4",
                        required=False, action="store_true", default=False)

    subparser = parser.add_subparsers(help="Choose an action")

    plugins.range_info.add_parser_configuration(subparser)
    plugins.remove_exceptions.add_parser_configuration(subparser)

    return parser


def parse_ips(ranges, is_ipv6=False) -> list:
    if is_ipv6:
        return list(
            map(lambda x: ipaddress.IPv6Network(x, strict=False), ranges))

    else:
        return list(
            map(lambda x: ipaddress.IPv4Network(x, strict=False), ranges))


if __name__ == '__main__':
    cider_parser = get_parser()
    args = cider_parser.parse_args()

    if args.debug:
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter(
            '[%(levelname)s] %(filename)s:%(lineno)s %(message)s'))
        for n in [__name__, "plugins"]:
            lgr = logging.getLogger(n)
            lgr.setLevel(level=logging.DEBUG)
            lgr.addHandler(h)
        logger.debug(args)
    elif args.verbose:
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
        for n in [__name__, "plugins"]:
            lgr = logging.getLogger(n)
            lgr.setLevel(level=logging.INFO)
            lgr.addHandler(h)

    if not args.ranges and not args.rp:
        cider_parser.print_help()
        logger.error("Please provide ranges to use")
        sys.exit(-1)

    ranges = []
    if args.ranges:
        ranges.extend(args.ranges.split(","))
    if args.rp:
        ranges.extend(open(args.rp).read().split())

    parsed_ranges = parse_ips(ranges, args.ipv6)
    logger.debug(f"Ranges: {' '.join(map(str, ranges))}")

    exceptions = []
    if args.exceptions:
        exceptions.extend(args.exceptions.split(","))
    if args.ep:
        exceptions.extend(open(args.ep).read().split())
    parsed_exceptions = parse_ips(exceptions, args.ipv6)
    logger.debug(f"Exceptions: {' '.join(map(str, exceptions)) or 'None'}")

    if not hasattr(args, "handler"):
        cider_parser.print_help()
        logger.error("Please select a command")
        sys.exit(-1)

    result = args.handler(parsed_ranges, parsed_exceptions, args)

    if args.op:
        open(args.op, "w").write(result)

    print(result)
