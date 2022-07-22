import logging


SCRIPT_NAME = "live-host-breakdown"

logger = logging.getLogger(__name__)


def handle_breakdown(ranges, exceptions, args):
    if exceptions:
        logger.warn(
            "Received exceptions, but this plugin does not use exceptions")

    if args.ipv6:
        logger.exception("Not implemented")
        return ""

    else:  # ipv4
        summary = _handle_breakdown_ipv4(ranges, args.prefix_summary_bits)
        return _format_summary_ipv4(summary)


def _handle_breakdown_ipv4(ranges, prefix_summary_len):
    if prefix_summary_len is None:
        prefix_summary_len = 24
    elif prefix_summary_len < 0 or prefix_summary_len > 32:
        logger.exception(
            "Please choose a prefix summary bit length between 0 and 32")
    logger.debug(f"Breaking down IPs into /{prefix_summary_len}")

    summary_dict = {}
    for network in ranges:

        if network.prefixlen < prefix_summary_len:
            logger.debug(f"Calculating the /{prefix_summary_len} subnets that comprise the range {network}")
            child_nets = _get_child_nets_ipv4(network, prefix_summary_len)
            for cn in child_nets:
                str_cn = cn
                if str_cn in summary_dict:
                    logger.exception(
                        f"Child net {str_cn} of {str(network)} already defined in summary dict?")
                summary_dict[str_cn] = cn.num_addresses

        elif network.prefixlen > prefix_summary_len:
            logger.debug(f"Calculating the /{prefix_summary_len} supernet that the range {network} belongs to")
            parent_net = _get_parent_net_ipv4(network, prefix_summary_len)
            str_pn = parent_net
            if str_pn in summary_dict:
                summary_dict[str_pn] += network.num_addresses
            else:
                summary_dict[str_pn] = network.num_addresses

        else:  # network.prefixlen == prefix_summary_len
            logger.debug(f"Range {network} is already a /{prefix_summary_len}. Leaving it as-is")
            str_n = network
            if str_n in summary_dict:
                logger.exception(f"{str_n} already defined in summary dict?")
            summary_dict[str_n] = network.num_addresses

    return summary_dict


def _get_child_nets_ipv4(network, target_prefix):
    diff = target_prefix - network.prefixlen
    if diff <= 0:
        logger.error(f"Diff is less than 0? It's {diff} for range {str(network)}")
        return network
    return network.subnets(prefixlen_diff=diff)


def _get_parent_net_ipv4(network, target_prefix):
    diff = network.prefixlen - target_prefix
    if diff <= 0:
        logger.error(f"Diff is less than 0? It's {diff} for range {str(network)}")
        return network        
    return network.supernet(prefixlen_diff=diff)


def _format_summary_ipv4(summary_dict):
    keys = sorted(summary_dict.keys())
    res = ""
    for key in keys:
        res += f"{str(key): >18}: {summary_dict[key]: >6} live hosts\n"
    res += "\n"
    res += f"{sum(summary_dict.values())} Total Live IP Addresses\n"
    return res


def add_parser_configuration(subparser):
    remove_exceptions_subparser = subparser.add_parser(
        SCRIPT_NAME, help="Print breakdown of live hosts")
    remove_exceptions_subparser.set_defaults(handler=handle_breakdown)
    remove_exceptions_subparser.set_defaults(parser=SCRIPT_NAME)

    remove_exceptions_subparser.add_argument(
        "--prefix-summary-bits", help="The bit count to summarize live hosts into networks by (default=24, for /24)", type=int)
    # remove_exceptions_subparser.add_argument(
    #     "--sort-field", help="Sort output by field", choices=["ip", "count"], type=str, default="ip" 
    # )
    # remove_exceptions_subparser.add_argument(
    #     "--sort-dir", help="Sort output firection", choices=["asc", "desc"], type=str, default="asc"
    # )
