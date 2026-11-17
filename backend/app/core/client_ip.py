"""The real client IP behind trusted reverse proxies.

Forwarding headers are only believed when the request arrives from a trusted proxy
(FORWARDED_ALLOW_IPS); otherwise anyone could fake them. X-Forwarded-For is read right to
left, skipping trusted proxies, so values a client prepends itself are never used.

Uvicorn (`--proxy-headers`) may already have replaced the peer address with the client's;
that address is then untrusted and returned as is, so both layers agree.
"""

import ipaddress
from collections.abc import Sequence

IPNetwork = ipaddress.IPv4Network | ipaddress.IPv6Network


def _parse(value: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    try:
        return ipaddress.ip_address(value.strip())
    except ValueError:
        return None


def _is_trusted(value: str, trusted: Sequence[IPNetwork] | None) -> bool:
    if trusted is None:  # "*"
        return True
    address = _parse(value)
    return address is not None and any(address in network for network in trusted)


def client_ip(
    peer: str | None,
    forwarded_for: str | None,
    real_ip: str | None,
    trusted: Sequence[IPNetwork] | None,
) -> str | None:
    """Best-known client IP. `trusted=None` trusts every peer ("*")."""
    if peer is None or not _is_trusted(peer, trusted):
        return peer

    if forwarded_for:
        hops = [hop.strip() for hop in forwarded_for.split(",") if _parse(hop)]
        for hop in reversed(hops):
            if not _is_trusted(hop, trusted):
                return hop
        if hops:  # every hop is a trusted proxy: the first one is the client
            return hops[0]

    if real_ip and _parse(real_ip):
        return real_ip.strip()
    return peer
