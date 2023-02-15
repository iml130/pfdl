# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Functions defined here set attributes for drawing the petri net."""

# standard libraries
import threading
from pathlib import Path

# 3rd party lib
import snakes.plugins

snakes.plugins.load(["labels", "gv"], "snakes.nets", "nets")

draw_lock = threading.Lock()


"""Constants that are used in the drawer functions"""
NODE_SEP_VALUE = 5

PLACE_SHAPE = "circle"
PLACE_LABEL = ""

TRANSITION_SHAPE = "rect"
TRANSITION_FILL_COLOR = "black"
TRANSITION_WIDTH = 1
TRANSITION_HEIGHT = 0.1
TRANSITION_LABEL = ""

INHIBITOR_ARC_ARROW_HEAD = "odot"

LAYOUT_METHOD = "dot"


def draw_graph(graph, attr):
    """Set attributes for drawing the net."""
    attr["nodesep"] = NODE_SEP_VALUE


def draw_place(place, attr):
    """Set attributes for drawing places."""
    if place.label("name") != "":
        attr["xlabel"] = place.label("name")
    else:
        attr["xlabel"] = place.name

    if 1 in place:
        attr["label"] = "&bull;"
    else:
        attr["label"] = PLACE_LABEL
    attr["shape"] = PLACE_SHAPE


def draw_transition(trans, attr):
    """Set attributes for drawing transitions."""

    attr["label"] = TRANSITION_LABEL
    attr["shape"] = TRANSITION_SHAPE
    attr["height"] = TRANSITION_HEIGHT
    attr["width"] = TRANSITION_WIDTH
    attr["fillcolor"] = TRANSITION_FILL_COLOR


def draw_arcs(arc, attr):
    """Set attributes for drawing arcs."""
    if isinstance(arc, snakes.nets.Inhibitor):
        attr["arrowhead"] = INHIBITOR_ARC_ARROW_HEAD
    attr["label"] = ""


def draw_petri_net(net, file_path, file_ending=".png"):
    """Calls the draw method form the Snakes module on the given PetriNet."""
    with draw_lock:
        Path("./temp").mkdir(parents=True, exist_ok=True)
        net.draw(
            file_path + file_ending,
            LAYOUT_METHOD,
            graph_attr=draw_graph,
            arc_attr=draw_arcs,
            place_attr=draw_place,
            trans_attr=draw_transition,
        )
