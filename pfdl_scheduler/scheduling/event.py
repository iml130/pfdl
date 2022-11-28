# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains the Event class."""

# standard libraries
import json
from typing import Dict, Union

# internal events
START_PRODUCTION_TASK = "start_production_task"
SET_PLACE = "loc_started"

# external event types that can be used
SERVICE_FINISHED = "service_finished"


class Event:
    """Data class for controlling the PetriNet instance.

    Currently avaiable Events:
        - Event(event_type="service_finished", data={"service_id": <service_id>})

    Attributes:
        event_type: A string representing the type of the event.
        data: A dict containing the corresponding data of the event type.
    """

    def __init__(self, event_type: str = "", data: Dict = None) -> None:
        self.event_type: str = event_type
        self.data: Dict = data

    def __eq__(self, other: "Event"):
        if not isinstance(other, Event):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.event_type == other.event_type and self.data == other.data

    @classmethod
    def from_json(cls, json_string: str) -> Union[None, "Event"]:
        """Creates an Event instance out of the given JSON string.

        Args:
            json_string: A JSON string desribing the Event.

        Returns:
            The Event which was created from the JSON string. None if the conversion failed.
        """
        json_dict = json.loads(json_string)
        if "event_type" in json_dict and "data" in json_dict:
            return Event(event_type=json_dict["event_type"], data=json_dict["data"])
        else:
            return None
