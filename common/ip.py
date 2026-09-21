from ipware import get_client_ip as _ipware_client_ip


def get_client_ip(request) -> str | None:
    """Proxy arkasında gerçek istemci IP'si (başlık sırası: IPWARE_META_PRECEDENCE_ORDER)."""
    ip, _routable = _ipware_client_ip(request)
    return ip
