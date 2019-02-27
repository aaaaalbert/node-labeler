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

