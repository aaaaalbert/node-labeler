# node-labeler
A small, stand-alone node labeling service for @EdgeNet-Project.

This program goes and puts labels on EdgeNet nodes so that deployments
can be constructed by filtering for these labels. For a Proof of Concept,
*geographical* labels are used: the Node Labeler

* retrieves the list of nodes currently on the system,
* looks up each IP address in a local GeoIP database, and
* assigns appropriate geo-labels such as `lat`, `lon`, `country` and `city`.

(In later versions, we might have an update scheme for mobile nodes,
or a generic harness to figure out and apply other, non-geo type labels.)


# Work Plan
Before we begin:

* Be reminded of K8s' labeling functionality, see [their docs](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/).
* Let's use the official Python K8s bindings, see [here](https://github.com/kubernetes-client/python).
* From my experience, GeoIP is easy. @SeattleTestbed has a pretty
  straightforward server implementation [here](https://github.com/SeattleTestbed/geoip_server/blob/master/geoip_server.py), so we'll (re)use parts of
  that.

What I plan to do:

1. I'll start with what I hope is a trivial PoC for the Python bindings,
  like listing pods and their properties, and assigning pod labels.
2. Then I'll work my way upwards to "privileged" functions that involve
  *node* labels.
3. Then add GeoIP and
4. see how we can generalize this for other node label types.

What I don't plan to do: Make a full-fledged, self-contained,
auto-everything service out of it (yet).


# What I did

* Set up a local `RUNNABLE` folder for testing.
* Set up a Python3 virtualenv for the dependencies my code will have:
  `virtualenv venv`
* Activate the virtualenve: `source venv/bin/activate`
* Install dependencies (from PyPI this time; perhaps from-source is
  preferable for a fast-moving thing like K8s?)
  * [MaxMind geoip2](https://github.com/maxmind/GeoIP2-python)
  * [Python Kubernetes client](https://github.com/kubernetes-client/python)
```
pip3 install geoip2
pip3 install kubernetes
```
* `python -c 'import kubernetes ; import geoip2' && echo We are good to go!`

There is some example code for the K8S Python bindings; the effort lies
in recognizing and selecting the right ((non-)namespaced etc.) methods:
* https://github.com/kubernetes-client/python/tree/master/examples
* https://github.com/kubernetes-client/python/blob/master/examples/manage_node_labels.py

* We should look for the value of the `kubernetes.io/hostname` label
  and resolve that to an IP address. There are other `address` labels
  (e.g. under the `status` key of a `NodeList` item), but from visual
  inspection they look less reliable (e.g. contain private IPv4 addresses).
* MaxMind GeoLite2 databases are available via [their download page](https://dev.maxmind.com/geoip/geoip2/geolite2/)
  -- note licensing conditions!
  * https://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz
  * https://geolite.maxmind.com/download/geoip/database/GeoLite2-Country.tar.gz
* Let's use the `City` database which maps IP addresses to
  * `location.latitude`, `location.longitude` (geo coordinates),
  * `city.names["en"]` (name of City in English),
  * `country.iso_code` (two-letter ISO country code)
  * `continent.code` (two-letter continent code)
