# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains the PetriNetLogic class."""

# standard libraries
import json
from typing import Dict

# 3rd party packages
from nets import PetriNet, Value

# local sources
from pfdl_scheduler.petri_net.drawer import draw_petri_net
from pfdl_scheduler.petri_net.generator import PetriNetGenerator
from pfdl_scheduler.scheduling.event import START_PRODUCTION_TASK, SET_PLACE, SERVICE_FINISHED
from pfdl_scheduler.scheduling.event import Event


class PetriNetLogic:
    """Provides methods for interacting with the generated petri nets for scheduling.

    Scheduling of the production process with the help of the
    generated petri nets is done in this class.

    Attributes:
        petri_net_generator:  A reference to the PetriNetGenerator.
        petri_net: A reference to the generated petri net.
        draw_net: Indiciating whether the net should be drawn.
        transition_dict: A reference to the dict in the generator which maps the uuids to callbacks.
    """

    def __init__(
        self, petri_net_generator: PetriNetGenerator, draw_net: bool = True, file_name: str = ""
    ) -> None:
        """Initialize the object.

        Args:
            petri_net_generator: A reference to the PetriNetGenerator.
            draw_net: Indiciating whether the net should be drawn.
        """
        self.petri_net_generator: PetriNetGenerator = petri_net_generator
        self.petri_net: PetriNet = petri_net_generator.net
        self.draw_net: bool = draw_net
        self.transition_dict: Dict = self.petri_net_generator.transition_dict
        self.file_name = file_name

    def draw_petri_net(self) -> None:
        """Saves the given petri net in the current working directory.

        If the `draw_net` flag is set, this method will save the petri net in a "temp" folder
        inside the root folder of the project. The petri net is saved as an image and as a dot
        file to allow further processing. The dot file also contains the "call_tree", a tree
        structure that describes the call hierarchy of PFDL tasks.

        Args:
            name: The name of the image.
            petri_net: The petri net instance that should be drawn.
        """

        file_path = "./temp/" + self.file_name

        if self.draw_net:
            draw_petri_net(self.petri_net, file_path)
            draw_petri_net(self.petri_net, file_path, ".dot")
            with open(file_path + ".dot", "a") as file:
                file.write("\ncall_tree:")
                file.write(json.dumps(self.petri_net_generator.tree.toJSON(), indent=4))

    def evaluate_petri_net(self) -> None:
        """Triggers the evaluation of the petri net and its tokens.

        This method tries to fire every transition successively until no transition
        can be fired anymore. If a transition is fired, the whole loop starts again, as
        a new petri net state could allow past transitions to be fired now.
        Each method call also calls the `draw_petri_net` method.
        """
        index = 0

        transitions = list(self.petri_net._trans)
        while index < len(transitions):
            transition_uuid = transitions[index]

            if self.petri_net.transition(transition_uuid).enabled(Value(1)):
                if transition_uuid in self.transition_dict:
                    callbacks = self.transition_dict[transition_uuid]
                    temp = None

                    for callback in callbacks:
                        # parallel loop functionality stop evaluation
                        if callback.func.__name__ == "on_parallel_loop_started":
                            temp = callback
                            callbacks.remove(temp)

                    if temp:
                        # execute other callbacks first before handling parallel loop functionality
                        for callback in list(callbacks):
                            callback()
                            callbacks.remove(callback)
                        temp()
                        return
                    else:
                        self.petri_net.transition(transition_uuid).fire(Value(1))

                        for callback in callbacks:
                            callback()
                else:
                    self.petri_net.transition(transition_uuid).fire(Value(1))

                index = 0
            else:
                index = index + 1

        self.draw_petri_net()

    def fire_event(self, event: Event) -> bool:
        """Adds a token to the corresponding place of the event in the petri net.

        Args:
            event: The Event object that is fired.

        Returns:
            True if the given event could be resolved into an existing place in the petri net.
        """

        name_in_petri_net = ""
        if event.event_type == START_PRODUCTION_TASK:
            name_in_petri_net = self.petri_net_generator.task_started_uuid
        elif event.event_type == SET_PLACE:
            name_in_petri_net = event.data["place_uuid"]
        elif event.event_type == SERVICE_FINISHED:
            name_in_petri_net = self.petri_net_generator.place_dict[event.data["service_uuid"]]

        if self.petri_net.has_place(name_in_petri_net):
            self.petri_net.place(name_in_petri_net).add(1)
            self.draw_petri_net()
            self.evaluate_petri_net()
            return True

        return False
