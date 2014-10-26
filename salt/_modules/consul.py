import json

try:
    import requests
except ImportError:
    requests = None


def __virtual__():
    if requests is None:
        return False, ["requests must be installed and importable."]
    return True


def cluster_ready():
    # Determine if we have at least one server
    try:
        resp = requests.get("http://127.0.0.1:8500/v1/agent/members")
        resp.raise_for_status()
    except (requests.HTTPError, requests.ConnectionError):
        return False

    for node in resp.json():
        if node["Tags"]["role"] == "consul":
            break
    else:
        return False

    # We have a server, determine if we have a leader
    try:
        resp = requests.get("http://127.0.0.1:8500/v1/status/leader")
        resp.raise_for_status()
    except (requests.HTTPError, requests.ConnectionError):
        return False

    if resp.json():
        return True
    else:
        return False


def node_exists(name, address, dc=None):
    params = {}
    if dc is not None:
        params["dc"] = dc

    resp = requests.get(
        "http://127.0.0.1:8500/v1/catalog/nodes",
        params=params,
    )
    resp.raise_for_status()

    for node in resp.json():
        if node["Node"] == name and node["Address"] == address:
            return True

    return False


def node_service_exists(node, service_name, port, dc=None):
    params = {}
    if dc is not None:
        params["dc"] = dc

    resp = requests.get(
        "http://127.0.0.1:8500/v1/catalog/node/{}".format(node),
        params=params,
    )
    resp.raise_for_status()

    for service in resp.json()["Services"].values():
        if service["Service"] == service_name and service["Port"] == port:
            return True

    return False


def register_external_service(node, address, datacenter, service, port):
    data = {
        "Datacenter": datacenter,
        "Node": node,
        "Address": address,
        "Service": {
            "Service": service,
            "Port": port,
        }
    }

    resp = requests.put(
        "http://127.0.0.1:8500/v1/catalog/register",
        data=json.dumps(data),
    )
    resp.raise_for_status()
