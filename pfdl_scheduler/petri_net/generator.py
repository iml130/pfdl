# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains the PetriNetGenerator class."""

# standard libraries
from typing import Any, Callable, Dict, List, OrderedDict, Tuple
import uuid
import functools

# 3rd party packages
from snakes import plugins
from pfdl_scheduler.api.service_api import ServiceAPI
from pfdl_scheduler.api.task_api import TaskAPI

# local sources
from pfdl_scheduler.model.process import Process
from pfdl_scheduler.model.task import Task
from pfdl_scheduler.model.service import Service
from pfdl_scheduler.model.task_call import TaskCall
from pfdl_scheduler.model.parallel import Parallel
from pfdl_scheduler.model.counting_loop import CountingLoop
from pfdl_scheduler.model.while_loop import WhileLoop
from pfdl_scheduler.model.condition import Condition

from pfdl_scheduler.petri_net.drawer import draw_petri_net
from pfdl_scheduler.petri_net.callbacks import PetriNetCallbacks

plugins.load(["labels", "gv"], "snakes.nets", "nets")
from nets import PetriNet, Place, Transition, Value


class PetriNetGenerator:
    """Generates a Petri Net from a given Process object which corresponds to a PFDL file.

    Attributes:
        path_for_image: The path where the image of the generated Petri Net is saved.
        net: The snakes Petri Net instance.
        tasks: A dict representing the Tasks of the given Process object.
        transition_dict: A dict for mapping the UUIDs of the Transitions to their behavior.
        place_dict: A dict for mapping the service id to the place name.
        task_started_id: The id of the 'Task started' place.
        callbacks: A PetriNetCallbacks instance representing functions called while execution.
        generate_test_ids: A boolean indicating if test ids (counting from 0) should be generated.
        used_in_extension: A boolean indicating if the Generator is used within the extension.
    """

    def __init__(
        self,
        path_for_image: str = "",
        used_in_extension: bool = False,
        generate_test_ids: bool = False,
        draw_net: bool = True,
    ) -> None:
        """Initialize the object.

        Args:
            path_for_image: The path where the image of the generated Petri Net is saved.
            used_in_extension: A boolean indicating if the Generator is used within the extension.
            generate_test_ids: A boolean indicating if test ids (counting from 0) should be generated.
            draw_net: A boolean indicating if the petri net should be drawn.
        """

        if used_in_extension:
            self.path_for_image: str = "../media/petri_net"
        elif path_for_image == "":
            self.path_for_image: str = "temp/petri_net"
        else:
            self.path_for_image: str = path_for_image + "/temp/petri_net"

        self.net: PetriNet = PetriNet("petri_net")
        self.draw_net: bool = draw_net
        self.tasks: Dict[str, Task] = None
        self.transition_dict: OrderedDict = OrderedDict()
        self.place_dict: Dict = {}
        self.task_started_id: str = ""
        self.callbacks: PetriNetCallbacks = PetriNetCallbacks()
        self.generate_test_ids: bool = generate_test_ids
        self.used_in_extension: bool = used_in_extension

    def add_callback(self, transition_id: str, callback_function: Callable, *args: Any) -> None:
        """Registers the given callback function in the transition_dict.

        If the transition the transition_id refers to is fired, the callback function
        will be called with the given arguments inside the PetriNetLogic class.

        Args:
            transition_id: The UUID of the transition where the callback is called if fired.
            callback_function: The callback function which should be called.
            *args: Arguments with which the callback function is called.
        """
        if not self.used_in_extension:
            callback = functools.partial(callback_function, *args)
            if transition_id not in self.transition_dict:
                self.transition_dict[transition_id] = []

            self.transition_dict[transition_id].append(callback)

    def generate_petri_net(self, process: Process) -> PetriNet:
        """Generates a Petri Net from the given Process object.

        Starts from the 'productionTask' and iterates over his statements.
        For each statement type like Condition or TaskCall a Petri Net component
        is generated. All components get connected at the end.

        Returns:
            A PetriNet instance representing the generated net.
        """
        self.tasks = process.tasks
        for task in process.tasks.values():
            if task.name == "productionTask":
                task_context = TaskAPI(task, None)
                if self.generate_test_ids:
                    task_context.uuid = "0"

                self.task_started_id = create_place(task.name + "_started", self.net)
                connection_id = create_transition("", "", self.net)

                self.add_callback(connection_id, self.callbacks.task_started, task_context)

                self.net.add_input(self.task_started_id, connection_id, Value(1))
                self.task_finished_id = create_place(task.name + "_finished", self.net)

                second_connection_id = create_transition("", "", self.net)

                self.generate_statements(
                    task_context, task.statements, connection_id, second_connection_id
                )
                self.net.add_output(self.task_finished_id, second_connection_id, Value(1))

                self.add_callback(second_connection_id, self.callbacks.task_finished, task_context)

        if self.draw_net:
            if self.used_in_extension:
                draw_petri_net(self.net, self.path_for_image, ".dot")
            else:
                draw_petri_net(self.net, self.path_for_image, ".png")
        return self.net

    def generate_statements(
        self,
        task_context: TaskAPI,
        statements: List,
        first_connection_id: str,
        last_connection_id: str,
        in_loop: bool = False,
    ) -> List[str]:
        """Generate Petri Net components for each statement in the given Task

        Iterate over the statements of the given Tasks and generate the corresponding
        Petri Net components. Connect the individual components with each other via a
        transition.

        Returns:
            The ids of the last connections (transitions).
        """
        current_connection_id = ""
        previous_connection_id = first_connection_id

        connection_ids = []
        for i, statement in enumerate(statements):
            multiple_statements = len(statements) > 1

            # only create a transition when there is more than 1 statement
            # and we are not in the last iteration
            if multiple_statements:
                if i < len(statements) - 1:
                    current_connection_id = create_transition("connection", "", self.net)
                else:
                    current_connection_id = last_connection_id
            else:
                previous_connection_id = first_connection_id
                current_connection_id = last_connection_id

            args = (statement, task_context, previous_connection_id, current_connection_id, in_loop)

            if isinstance(statement, Service):
                connection_ids = [self.generate_service(*args)]
            elif isinstance(statement, TaskCall):
                connection_ids = self.generate_task_call(*args)
            elif isinstance(statement, Parallel):
                connection_ids = [self.generate_parallel(*args)]
            elif isinstance(statement, CountingLoop):
                connection_ids = [self.generate_counting_loop(*args)]
            elif isinstance(statement, WhileLoop):
                connection_ids = [self.generate_while_loop(*args)]
            else:
                connection_ids = self.generate_condition(*args)

            previous_connection_id = current_connection_id

        return connection_ids

    def generate_service(
        self,
        service: Service,
        task_context: TaskAPI,
        first_transition_id: str,
        second_transition_id: str,
        in_loop: bool = False,
    ) -> str:
        """Generate the Petri Net components for a Service Call.

        Returns:
            The id of the last transition of the Service petri net component.
        """
        service_api = ServiceAPI(service, task_context, in_loop=in_loop)

        service_started_id = create_place(service.name + " started", self.net)

        service_finished_id = create_place(service.name + " finished", self.net)
        self.place_dict[service_api.uuid] = service_finished_id

        service_done_id = create_place(service.name + " done", self.net)
        service_done_transition_id = create_transition("service_done", "", self.net)

        self.add_callback(first_transition_id, self.callbacks.service_started, service_api)
        self.add_callback(service_done_transition_id, self.callbacks.service_finished, service_api)

        self.net.add_input(service_started_id, service_done_transition_id, Value(1))
        self.net.add_input(service_finished_id, service_done_transition_id, Value(1))
        self.net.add_output(service_done_id, service_done_transition_id, Value(1))

        self.net.add_output(service_started_id, first_transition_id, Value(1))
        self.net.add_input(service_done_id, second_transition_id, Value(1))

        return service_done_transition_id

    def generate_task_call(
        self,
        task_call: TaskCall,
        task_context: TaskAPI,
        first_transition_id: str,
        second_transition_id: str,
        in_loop: bool = False,
    ) -> List[str]:
        """Generate the Petri Net components for a Task Call.

        Returns:
            The ids of the last transitions of the TaskCall petri net component.
        """
        called_task = self.tasks[task_call.name]
        new_task_context = TaskAPI(called_task, task_context, task_call=task_call, in_loop=in_loop)

        # Order for callbacks important: Task starts before statement and finishes after
        self.add_callback(first_transition_id, self.callbacks.task_started, new_task_context)
        last_connection_ids = self.generate_statements(
            new_task_context,
            called_task.statements,
            first_transition_id,
            second_transition_id,
            in_loop,
        )

        for last_connection_id in last_connection_ids:
            self.add_callback(last_connection_id, self.callbacks.task_finished, new_task_context)

        return last_connection_ids

    def generate_parallel(
        self,
        parallel: Parallel,
        task_context: TaskAPI,
        first_transition_id: str,
        second_transition_id: str,
        in_loop: bool = False,
    ) -> str:
        """Generate the Petri Net components for a Parallel statement.

        Returns:
            The id of the last transition of the Parallel petri net component.
        """

        sync_id = create_transition("", "", self.net)
        parallel_finished_id = create_place("Parallel finished", self.net)

        for task_call in parallel.task_calls:
            self.generate_task_call(task_call, task_context, first_transition_id, sync_id, in_loop)

        self.net.add_output(parallel_finished_id, sync_id, Value(1))
        self.net.add_input(parallel_finished_id, second_transition_id, Value(1))
        return sync_id

    def generate_condition(
        self,
        condition: Condition,
        task_context: TaskAPI,
        first_transition_id: str,
        second_transition_id: str,
        in_loop: bool = False,
    ) -> List[str]:
        """Generate Petri Net components for the Condition statement.

        Returns:
            The ids of the last transitions of the Condition petri net component.
        """
        passed_id = create_place("Passed", self.net)
        failed_id = create_place("Failed", self.net)

        expression_id = create_place("If " + self.parse_expression(condition.expression), self.net)

        first_passed_transition_id = create_transition("", "", self.net)
        first_failed_transition_id = create_transition("", "", self.net)

        self.net.add_input(expression_id, first_passed_transition_id, Value(1))
        self.net.add_input(expression_id, first_failed_transition_id, Value(1))

        self.net.add_input(passed_id, first_passed_transition_id, Value(1))
        self.net.add_input(failed_id, first_failed_transition_id, Value(1))

        finished_id = create_place("Condition_Finished", self.net)

        second_passed_transition_id = create_transition("", "", self.net)
        self.net.add_output(finished_id, second_passed_transition_id, Value(1))

        self.generate_statements(
            task_context,
            condition.passed_stmts,
            first_passed_transition_id,
            second_passed_transition_id,
            in_loop,
        )

        self.net.add_output(expression_id, first_transition_id, Value(1))
        self.net.add_input(finished_id, second_transition_id, Value(1))

        args = (condition, passed_id, failed_id, task_context)
        self.add_callback(first_transition_id, self.callbacks.condition_started, *args)

        if condition.failed_stmts:
            second_failed_transition_id = create_transition("", "", self.net)
            self.generate_statements(
                task_context,
                condition.failed_stmts,
                first_failed_transition_id,
                second_failed_transition_id,
                in_loop,
            )

            self.net.add_output(finished_id, second_failed_transition_id, Value(1))
            return [second_passed_transition_id, second_failed_transition_id]
        else:
            self.net.add_output(finished_id, first_failed_transition_id, Value(1))
            return [second_passed_transition_id, first_failed_transition_id]

    def generate_counting_loop(
        self,
        loop: CountingLoop,
        task_context: TaskAPI,
        first_transition_id: str,
        second_transition_id: str,
        in_loop: bool = False,
    ) -> str:
        """Generates the Petri Net components for a Couting Loop.

        Returns:
            The id of the last transition of the CountingLoop petri net component.
        """
        if loop.parallel:
            return self.generate_parallel_loop(
                loop, task_context, first_transition_id, second_transition_id
            )

        loop_id = create_place("Loop", self.net)

        loop_text = "Loop"

        loop_statements_id = create_place(loop_text, self.net)
        loop_finished_id = create_place("Number of Steps Done", self.net)

        condition_passed_transition_id = create_transition("", "", self.net)
        condition_failed_transition_id = create_transition("", "", self.net)
        iteration_step_done_transition_id = create_transition("", "", self.net)

        self.net.add_input(loop_id, condition_passed_transition_id, Value(1))
        self.net.add_input(loop_statements_id, condition_passed_transition_id, Value(1))
        self.net.add_input(loop_id, condition_failed_transition_id, Value(1))
        self.net.add_input(loop_finished_id, condition_failed_transition_id, Value(1))
        self.net.add_output(loop_id, iteration_step_done_transition_id, Value(1))

        loop_done_id = create_place("Loop Done", self.net)
        self.generate_statements(
            task_context,
            loop.statements,
            condition_passed_transition_id,
            iteration_step_done_transition_id,
            True,
        )

        self.net.add_output(loop_done_id, condition_failed_transition_id, Value(1))
        self.net.add_output(loop_id, first_transition_id, Value(1))
        self.net.add_input(loop_done_id, second_transition_id, Value(1))

        args = (loop, loop_statements_id, loop_finished_id, task_context)
        self.add_callback(first_transition_id, self.callbacks.counting_loop_started, *args)
        self.add_callback(
            iteration_step_done_transition_id, self.callbacks.counting_loop_started, *args
        )

        return condition_failed_transition_id

    def generate_parallel_loop(
        self,
        loop: CountingLoop,
        task_context: TaskAPI,
        first_transition_id: str,
        second_transition_id: str,
    ) -> str:
        """Generates the static petri net components for a ParallelLoop.

        This method will generate a placeholder for the ParallelLoop. The real amount
        of parallel startet Tasks is only known at runtime.

        Returns:
            The id of the last transition of the ParallelLoop petri net component.
        """
        parallel_loop_started = create_place(
            "Start " + loop.statements[0].name + " in parallel", self.net
        )

        self.net.add_output(parallel_loop_started, first_transition_id, Value(1))
        self.net.add_input(parallel_loop_started, second_transition_id, Value(1))

        args = (
            loop,
            task_context,
            loop.statements[0],
            parallel_loop_started,
            first_transition_id,
            second_transition_id,
        )
        self.add_callback(first_transition_id, self.callbacks.parallel_loop_started, *args)
        return second_transition_id

    def remove_place_on_runtime(self, place_id: str) -> None:
        """Removes a place from the petri net at runtime.

        Args:
            place_id: The id as stringg of the task which should be removed from the net.
        """
        self.net.remove_place(place_id)
        if self.draw_net:
            draw_petri_net(self.net, self.path_for_image)

    def generate_empty_parallel_loop(
        self, first_transition_id: str, second_transition_id: str
    ) -> None:
        empty_loop_place = create_place("Exeute 0 tasks", self.net)
        self.net.add_output(empty_loop_place, first_transition_id, Value(1))
        self.net.add_input(empty_loop_place, second_transition_id, Value(1))

    def generate_while_loop(
        self,
        loop: CountingLoop,
        task_context: TaskAPI,
        first_transition_id: str,
        second_transition_id: str,
        in_loop: bool = False,
    ) -> str:
        """Generate the Petri Net components for a While Loop.

        Returns:
            The id of the last transition of the WhileLoop petri net component.
        """
        loop_id = create_place("Loop", self.net)

        loop_text = "Loop"

        loop_statements_id = create_place(loop_text, self.net)
        loop_finished_id = create_place("Number of Steps Done", self.net)

        condition_passed_transition_id = create_transition("", "", self.net)
        condition_failed_transition_id = create_transition("", "", self.net)
        iteration_step_done_transition_id = create_transition("", "", self.net)

        self.net.add_input(loop_id, condition_passed_transition_id, Value(1))
        self.net.add_input(loop_statements_id, condition_passed_transition_id, Value(1))
        self.net.add_input(loop_id, condition_failed_transition_id, Value(1))
        self.net.add_input(loop_finished_id, condition_failed_transition_id, Value(1))
        self.net.add_output(loop_id, iteration_step_done_transition_id, Value(1))

        loop_done_id = create_place("Loop Done", self.net)
        self.generate_statements(
            task_context,
            loop.statements,
            condition_passed_transition_id,
            iteration_step_done_transition_id,
            True,
        )

        self.net.add_output(loop_id, first_transition_id, Value(1))
        self.net.add_input(loop_done_id, second_transition_id, Value(1))

        args = (loop, loop_statements_id, loop_finished_id, task_context)
        self.add_callback(first_transition_id, self.callbacks.while_loop_started, *args)
        self.add_callback(
            iteration_step_done_transition_id, self.callbacks.while_loop_started, *args
        )

        self.net.add_output(loop_done_id, condition_failed_transition_id, Value(1))

        return condition_failed_transition_id

    def parse_expression(self, expression: Dict) -> str:
        """Parses the given expression to a printable format.

        Returns:
            The content of the expression as a formatted string.
        """
        if isinstance(expression, (str, int, float, bool)):
            return str(expression)
        if isinstance(expression, list):
            list_string = ""
            for element in expression:
                if list_string != "":
                    list_string = list_string + "." + element
                else:
                    list_string = element
            return list_string
        if len(expression) == 2:
            return "!" + self.parse_expression(expression["value"])
        if expression["left"] == "(" and expression["right"] == ")":
            return "(" + self.parse_expression(expression["binOp"]) + ")"

        return (
            self.parse_expression(expression["left"])
            + expression["binOp"]
            + self.parse_expression(expression["right"])
        )


def create_place(name: str, net: PetriNet) -> str:
    """Utility function for creating a place with the snakes module.

    This function is used to add a place with the given name and to add labels for
    scheduling (for example if the place represents an event or if its initialized).

    Args:
        name: A string representing the displayed name of the place.
        net: The petri net instance this place should be added to.

    Returns:
        A UUID as string for the added place.
    """
    place_id = str(uuid.uuid4())
    net.add_place(Place(place_id, []))
    net.place(place_id).label(name=name)
    return place_id


def create_transition(transition_name: str, transition_type: str, net: PetriNet) -> str:
    """Utility function for creating a transition with the snakes module.

    This function is used to add a transition with the given name and to add labels for
    scheduling (currently only the type of the transition).

    Args:
        transition_name: A string representing the displayed name of the transition.
        net: The petri net instance this transition should be added to.

    Returns:
        A UUID as string for the added transition.
    """
    transition_id = str(uuid.uuid4())
    net.add_transition(Transition(transition_id))
    net.transition(transition_id).label(name=transition_name, transitionType=transition_type)
    return transition_id
