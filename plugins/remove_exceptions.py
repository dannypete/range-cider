import ipaddress
import logging

SCRIPT_NAME = "remove-exceptions"

logger = logging.getLogger(__name__)


def handle_remove_exceptions(ranges, exceptions, args):
    removed = list(ipaddress.collapse_addresses(remove_exceptions_from_ranges(ranges, exceptions)))

    if args.expanded:
        res = []
        for rem in removed:
            res.extend(map(str, list(rem)))
        out = "\n".join(res)

    else:
        out = "\n".join(map(str, removed))

    return out

def remove_exceptions_from_ranges(ranges, exceptions):
    res = []
    for range in ranges:
        res.extend(remove_exceptions_from_range(range, exceptions))

    return res

def remove_exceptions_from_range(range, exceptions):
    if len(exceptions) == 0:
        logger.debug(f"Done removing exceptions from {range}.")
        return [range]

    exception = exceptions[0]
    removal_result = remove_exception_from_range(range, exception)

    # an exeption was removed which eliminated the entire range
    if len(removal_result) == 0:
        logger.debug(f"Removal of {exception} from {range} resulted in the range being deleted.")
        return []

    # one or more ranges were returned; either:
    #   an exception was removed, leaving one or more ranges left over
    #   the range had no exception removed, leaving the starting range intact
    # in either case, we need to remove the remaining exceptions from this range
    logger.debug(f"Removal of {exception} from {range} resulted in the range becoming {removal_result}.")
    return remove_exceptions_from_ranges(removal_result, exceptions[1:])

def remove_exception_from_range(range, exception):
    # logger.debug(f"Removing exception {exception} from range {range}.")

    range_min, range_max = ipaddress.ip_address(range[0]), ipaddress.ip_address(range[-1])
    exception_min, exception_max = ipaddress.ip_address(exception[0]), ipaddress.ip_address(exception[-1])

    # logger.debug(f"rmin = {range_min},  rmax = {range_max}")
    # logger.debug(f"emin = {exception_min},  emax = {exception_max}")

    if exception_max < range_min or exception_min > range_max:
        return [range]

    if (exception_min == range_min and exception_max == range_max) or \
            (exception_min < range_min and exception_max == range_max) or \
            (exception_min == range_min and range_max < exception_max) or \
            (exception_min < range_min and range_max < exception_max):
        return []

    elif (range_min < exception_min and exception_max == range_max) or \
            (range_min < exception_min and range_max < exception_max):
        return list(ipaddress.summarize_address_range(range_min, max(range_min, exception_min - 1)))

    elif (exception_min == range_min and exception_max < range_max) or \
            (exception_min < range_min and exception_max < range_max):
        return list(ipaddress.summarize_address_range(min(exception_max + 1, range_max), range_max))

    elif (range_min < exception_min and exception_max < range_max):
        return list(ipaddress.summarize_address_range(range_min, max(range_min, exception_min - 1))) + \
               list(ipaddress.summarize_address_range(min(exception_max + 1, range_max), range_max))

    else: 
        logger.error(f"Encountered unhandled area: range {range}, trying to remove {exception}")


def add_parser_configuration(subparser):
    remove_exceptions_subparser = subparser.add_parser(
        SCRIPT_NAME, help="Remove exceptions from ranges")
    remove_exceptions_subparser.set_defaults(handler=handle_remove_exceptions)
    remove_exceptions_subparser.set_defaults(parser=SCRIPT_NAME)

    remove_exceptions_subparser.add_argument(
        "--expanded", help="Output a single IP per line", required=False, action="store_true", default=False)
