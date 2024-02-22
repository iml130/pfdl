# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains integration tests to check the marking of the petri net."""

# standard libraries
import json
from sched import scheduler
from typing import List, Union
import unittest

# 3rd party libs
from snakes.nets import Marking, MultiSet
from pfdl_scheduler.api.service_api import ServiceAPI
from pfdl_scheduler.api.task_api import TaskAPI
from pfdl_scheduler.model.struct import Struct

# local sources
from pfdl_scheduler.scheduler import Event, Scheduler

TEST_FILE_FOLDER_PATH = "tests/test_files/scheduling/"
EVENT_FILE_FOLDER_PATH = "tests/test_files/events/"


class TestScheduling(unittest.TestCase):
    """These tests check if the scheduling logic and the interaction with the petri net works.

    It is tested whether the net handles the fired events correctly and the transitions trigger
    the correct callbacks.
    """

    def setUp(self) -> None:
        self.scheduler: Scheduler = None
        self.petri_net = None
        self.events: List[Event] = []
        self.service_started_triggered: List[str] = []
        self.service_finished_triggered: List[str] = []
        self.task_started_triggered: List[str] = []
        self.task_finished_triggered: List[str] = []

    def load_file(self, test_file_name: str) -> None:
        """Loads a file from the given path and parses it if it is a PFDL program."""

        file_path = TEST_FILE_FOLDER_PATH + test_file_name + ".pfdl"
        self.scheduler = Scheduler(file_path, True, False)

    def setup(self, test_case_name: str) -> None:
        self.load_file(test_case_name)

        self.assertFalse(self.scheduler.running)
        self.scheduler.start()
        self.assertTrue(self.scheduler.running)

        self.petri_net = self.scheduler.petri_net_logic.petri_net

    def fire_event(self, event: Event) -> None:
        """Resets the callback attributes to None to check if new callback is triggered"""
        self.service_started_triggered = []
        self.service_finished_triggered = []
        self.task_started_triggered = []
        self.task_finished_triggered = []
        self.scheduler.fire_event(event)

    def token_in_last_place(self) -> bool:
        last_place_marking = {self.scheduler.petri_net_generator.task_finished_id: MultiSet(1)}

        final_marking = Marking(last_place_marking)
        return self.petri_net.get_marking() == final_marking

    def test_simple_task(self) -> None:
        self.setup("simple_task")

        event = Event("service_finished", data={"service_id": "0"})
        self.fire_event(event)

        self.assertTrue(self.token_in_last_place())

    def test_multiple_services(self) -> None:
        self.setup("multiple_services")

        self.fire_event(Event("service_finished", data={"service_id": "0"}))
        self.fire_event(Event("service_finished", data={"service_id": "1"}))

        self.assertTrue(self.token_in_last_place())

    def test_parallel_loop(self) -> None:
        self.setup("parallel_loop")

        # execute 3 tasks in parallel
        access_func = lambda var, context: Struct(attributes={"parts_count": 3})
        self.scheduler.register_variable_access_function(access_func)

        self.fire_event(Event("service_finished", data={"service_id": "0"}))
        self.fire_event(Event("service_finished", data={"service_id": "1"}))
        self.fire_event(Event("service_finished", data={"service_id": "2"}))
        self.fire_event(Event("service_finished", data={"service_id": "3"}))

        self.assertTrue(self.token_in_last_place())

    def test_parallel_tasks(self) -> None:
        self.setup("parallel_tasks")

        self.fire_event(Event("service_finished", data={"service_id": "1"}))
        self.fire_event(Event("service_finished", data={"service_id": "0"}))

        self.assertTrue(self.token_in_last_place())

    def test_service_and_condition(self) -> None:
        # Passed path
        self.setup("service_and_condition")
        access_func = lambda var, context: Struct(attributes={"wetness": 11})
        self.scheduler.register_variable_access_function(access_func)

        self.fire_event(Event("service_finished", data={"service_id": "0"}))
        self.fire_event(Event("service_finished", data={"service_id": "1"}))
        self.fire_event(Event("service_finished", data={"service_id": "2"}))

        self.assertTrue(self.token_in_last_place())

        # Failed path
        self.setup("service_and_condition")
        access_func = lambda var, context: Struct(attributes={"wetness": 3})
        self.scheduler.register_variable_access_function(access_func)

        self.fire_event(Event("service_finished", data={"service_id": "0"}))
        self.fire_event(Event("service_finished", data={"service_id": "1"}))
        self.fire_event(Event("service_finished", data={"service_id": "2"}))
        self.fire_event(Event("service_finished", data={"service_id": "3"}))

        self.assertTrue(self.token_in_last_place())

    def test_task_synchronisation(self) -> None:
        self.setup("task_synchronisation")

        self.fire_event(Event("service_finished", data={"service_id": "1"}))
        self.fire_event(Event("service_finished", data={"service_id": "0"}))
        self.fire_event(Event("service_finished", data={"service_id": "2"}))

        self.assertTrue(self.token_in_last_place())

    def test_counting_loop(self) -> None:
        # service and task ids dont follow number order cause of scheduling logic for loops
        self.setup("task_with_counting_loop")

        # iterate 3 times
        access_func = lambda var, context: Struct(attributes={"parts_count": 3})
        self.scheduler.register_variable_access_function(access_func)

        self.fire_event(Event("service_finished", data={"service_id": "0"}))
        self.fire_event(Event("service_finished", data={"service_id": "1"}))
        self.fire_event(Event("service_finished", data={"service_id": "2"}))
        self.fire_event(Event("service_finished", data={"service_id": "3"}))

        self.assertTrue(self.token_in_last_place())

    def test_while_loop(self) -> None:
        self.setup("task_with_while_loop")
        wetness = 3

        # iterate until wetness > 1 -> 2 times
        access_func = lambda var, context: Struct(attributes={"wetness": wetness})
        self.scheduler.register_variable_access_function(access_func)

        self.fire_event(Event("service_finished", data={"service_id": "0"}))
        wetness = 2

        self.fire_event(Event("service_finished", data={"service_id": "1"}))
        wetness = 1

        self.fire_event(Event("service_finished", data={"service_id": "2"}))

        self.assertTrue(self.token_in_last_place())


if __name__ == "__main__":
    unittest.main()
