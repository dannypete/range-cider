import argparse
import logging
import sys

import plugins.range_info
import plugins.remove_exceptions

logger = logging.getLogger(__name__)


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-r", "--ranges", help="Ranges file path", required=True, type=str)

    parser.add_argument("-v", "--verbose", help="More output",
                        required=False, action="store_true", default=False)
    parser.add_argument("--debug", help="More output (implies --verbose)",
                        required=False, action="store_true", default=False)
    parser.add_argument("-o", "--output", help="Output file path",
                        required=False, type=str, default="")

    subparser = parser.add_subparsers(help="Choose an action")

    plugins.range_info.add_parser_configuration(subparser)
    plugins.remove_exceptions.add_parser_configuration(subparser)

    return parser


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

    if not hasattr(args, "handler"):
        logger.error("Please select a command")
        cider_parser.print_help()
        sys.exit(-1)
    args.handler(args)
