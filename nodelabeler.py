"""
nodelabeler.py -- a basic node labeling service for GeoIP data

This program reads in your K8s config, then
* collects all node names on your K8s cluster,
* resolves their hostnames to IP addresses,
* looks up these IPs in a local GeoIP database,
* and assigns K8s node labels containing geographic information to
  each node.

It also prints progress information as it works.

Label values currently includes coordinates (lat, lon), city name,
two-letter country code, and continent.

You can use these labels for selecting nodes to deploy to.

-----

MaxMind GeoLite2 licensing notice:
'''
The GeoLite2 databases are distributed under the Creative Commons
Attribution-ShareAlike 4.0 International License. The attribution
requirement may be met by including the following in all advertising
and documentation mentioning features of or use of this database:

This product includes GeoLite2 data created by MaxMind, available from
<a href="https://www.maxmind.com">https://www.maxmind.com</a>.
'''
"""

# This is the local config; remember to adapt the paths etc. there!
import config

import kubernetes

import geoip2
import geoip2.database

import socket



def _get_name_and_ip(node):
    """
    <Purpose>
        Extract node hostname and look up IP address

    <Arguments>
        A node object as contained in a K8s node list

    <Side Effects>
        Does a DNS lookup of the node name

    <Exceptions>
        Per socket.gethostbyname

    <Returns>
        Node name and IP address as strings
    """
    name = node.metadata.labels["kubernetes.io/hostname"]
    ip = socket.gethostbyname(name)
    return name, ip



def _get_geoip_details(geoip_reader, ip):
    """
    <Purpose>
        Get GeoIP details for an IP address using the supplied DB reader

    <Arguments>
        A GeoIP database reader
        An IP address to look up in the database

    <Side Effects>
        Searches the local GeoIP database

    <Exceptions>
        Per geoip2.database.Reader

    <Returns>
        A dictionary with GeoIP details for the IP address, including
        lat, lon, city name, ISO two-letter country code, continent.
        (The values of the returned dict are massaged to become proper
        K8s label values, see below.)
    """
    # Read the database entry for this IP
    geoip_record = geoip_reader.city(ip)

    # Make properly-formatted K8s values out of lat/lon floats.
    # For latitude, this is a prefix of "n" (North) or "s" (South)
    # for positive and negative values, respectively.
    # For longitudes, the prefix is "e" (East) and "w" (West).
    # Also restrict the lat/lon strings to two decimal points
    # to avoid the usual float/decimal representation issues.
    lat = geoip_record.location.latitude
    lon = geoip_record.location.longitude
    lat_string = ("n" if lat >= 0 else "s") + "%.2f" % abs(lat)
    lon_string = ("e" if lon >= 0 else "w") + "%.2f" % abs(lon)

    # The city string might be empty, account for that;
    # also ensure there is no whitespace in names (e.g. "New_York")
    city = geoip_record.city.names.get("en", "")
    city = city.replace(" ", "_")

    return {
            "lat": lat_string,
            "lon": lon_string,
            "city": city,
            "country_iso": geoip_record.country.iso_code,
            "continent": geoip_record.continent.code,
    }



def main():
    # Read the local K8s config and get us an API client
    kubernetes.config.load_kube_config(config_file=config.kubeconfig)
    k8sclient = kubernetes.client.CoreV1Api()

    # Get node list (dropping other cluster details)
    nodelist = k8sclient.list_node().items

    # Prepare the GeoIP database reader
    geoip_reader = geoip2.database.Reader(config.maxmind_db_file)

    for node in nodelist:
        # Get the node name and IP address
        name, ip = _get_name_and_ip(node)

        print("Processing", name, "at", ip)

        # Get the GeoIP details for this IP
        node_geoip = _get_geoip_details(geoip_reader, ip)

        print("GeoIP for", ip, "is", node_geoip, "\n")

        for key, value in node_geoip.items():
            k8sclient.patch_node(name, {"metadata": {"labels": node_geoip}})


if __name__ == "__main__":
    main()

