import logging

SCRIPT_NAME = "info"

logger = logging.getLogger(__name__)


def handle_info(args):
    pass


def add_parser_configuration(subparser):
    info_subparser = subparser.add_parser(
        SCRIPT_NAME, help="Print information about ranges.")
    info_subparser.set_defaults(handler=handle_info)
    info_subparser.set_defaults(parser=SCRIPT_NAME)
