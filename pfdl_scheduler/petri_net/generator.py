# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains the PetriNetGenerator class."""

# standard libraries
import copy
from typing import Any, Callable, Dict, List, OrderedDict, Tuple
import uuid
import functools
import json
from pathlib import Path

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

plugins.load(["labels", "gv", "clusters"], "snakes.nets", "nets")

from nets import PetriNet, Place, Transition, Value, Cluster


class Node(object):
    """Represents a type of component relative to its position in the call graph

    Attributes:
        group_uuid: The id of the group of petri net components this node represents
    """

    def __init__(self, group_uuid: str, name="", parent: "Node" = None):
        self.group_uuid: str = group_uuid
        self.name: str = name
        self.children: List[Node] = []
        self.path = []
        if parent:
            parent.add_child(self)
            self.path = copy.deepcopy(parent.path)
            self.path.append(len(parent.children))

    def add_child(self, node: "Node"):
        self.children.append(node)

    def get_path(self) -> List[str]:
        return self.path

    def toJSON(self):
        children_list = []
        for child in self.children:
            child_dict = child.toJSON()
            children_list.append(child_dict)
        json_dict = {"id": self.group_uuid, "name": self.name, "children": children_list}
        return json_dict


class PetriNetGenerator:
    """Generates a Petri Net from a given Process object which corresponds to a PFDL file.

    Attributes:
        path_for_image: The path where the image of the generated Petri Net is saved.
        net: The snakes Petri Net instance.
        tasks: A dict representing the Tasks of the given Process object.
        transition_dict: A dict for mapping the UUIDs of the Transitions to their behavior.
        place_dict: A dict for mapping the service uuid to the place name.
        task_started_uuid: The uuid of the 'Task started' place.
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
        file_name: str = "petri_net",
    ) -> None:
        """Initialize the object.

        Args:
            path_for_image: The path where the image of the generated Petri Net is saved.
            used_in_extension: A boolean indicating if the Generator is used within the extension.
            generate_test_ids: A boolean indicating if test ids (counting from 0) should be generated.
            draw_net: A boolean indicating if the petri net should be drawn.
        """

        if used_in_extension:
            self.path_for_image: str = "../media/" + file_name
        elif path_for_image == "":
            Path("./temp").mkdir(parents=True, exist_ok=True)
            self.path_for_image: str = "temp/" + file_name
        else:
            Path("./temp").mkdir(parents=True, exist_ok=True)
            self.path_for_image: str = path_for_image + "/temp/" + file_name

        self.net: PetriNet = PetriNet("petri_net")
        self.draw_net: bool = draw_net
        self.tasks: Dict[str, Task] = None
        self.transition_dict: OrderedDict = OrderedDict()
        self.place_dict: Dict = {}
        self.task_started_uuid: str = ""
        self.callbacks: PetriNetCallbacks = PetriNetCallbacks()
        self.generate_test_ids: bool = generate_test_ids
        self.used_in_extension: bool = used_in_extension
        self.tree = None
        self.file_name = file_name

    def add_callback(self, transition_uuid: str, callback_function: Callable, *args: Any) -> None:
        """Registers the given callback function in the transition_dict.

        If the transition the transition_uuid refers to is fired, the callback function
        will be called with the given arguments inside the PetriNetLogic class.

        Args:
            transition_uuid: The UUID of the transition where the callback is called if fired.
            callback_function: The callback function which should be called.
            *args: Arguments with which the callback function is called.
        """
        if not self.used_in_extension:
            callback = functools.partial(callback_function, *args)
            if transition_uuid not in self.transition_dict:
                self.transition_dict[transition_uuid] = []

            self.transition_dict[transition_uuid].append(callback)

    def generate_petri_net(self, process: Process) -> PetriNet:
        """Generates a Petri Net from the given Process object.

        Starts from the 'productionTask' and iterates over his statements.
        For each statement type like Condition or TaskCall a Petri Net component
        is generated. All components get connected at the end.

        Returns:
            A PetriNet instance representing the generated net.
        """
        self.tasks = process.tasks
        production_task = process.tasks["productionTask"]
        group_uuid = str(uuid.uuid4())
        self.tree = Node(group_uuid, production_task.name)

        task_context = TaskAPI(production_task, None)
        if self.generate_test_ids:
            task_context.uuid = "0"

        self.task_started_uuid = create_place(
            production_task.name + "_started", self.net, self.tree
        )
        connection_uuid = create_transition("", "", self.net, self.tree)

        self.add_callback(connection_uuid, self.callbacks.task_started, task_context)

        self.net.add_input(self.task_started_uuid, connection_uuid, Value(1))
        self.task_finished_uuid = create_place(
            production_task.name + "_finished", self.net, self.tree
        )

        second_connection_uuid = create_transition("", "", self.net, self.tree)

        self.tree.cluster = Cluster(
            [
                self.task_started_uuid,
                connection_uuid,
                second_connection_uuid,
                self.task_finished_uuid,
            ]
        )
        self.generate_statements(
            task_context,
            production_task.statements,
            connection_uuid,
            second_connection_uuid,
            self.tree,
        )
        self.net.add_output(self.task_finished_uuid, second_connection_uuid, Value(1))

        self.add_callback(second_connection_uuid, self.callbacks.task_finished, task_context)

        if self.draw_net:
            json_string = json.dumps(self.tree.toJSON(), indent=4)
            draw_petri_net(self.net, self.path_for_image, ".dot")
            draw_petri_net(self.net, self.path_for_image, ".png")
            with open(self.path_for_image + ".dot", "a") as file:
                file.write("\ncall_tree:")
                file.write(json_string)

        return self.net

    def generate_statements(
        self,
        task_context: TaskAPI,
        statements: List,
        first_connection_uuid: str,
        last_connection_uuid: str,
        node: Node,
        in_loop: bool = False,
    ) -> List[str]:
        """Generate Petri Net components for each statement in the given Task

        Iterate over the statements of the given Tasks and generate the corresponding
        Petri Net components. Connect the individual components with each other via a
        transition.

        Returns:
            The uuids of the last connections (transitions).
        """
        current_connection_uuid = ""
        previous_connection_uuid = first_connection_uuid

        connection_uuids = []
        for i, statement in enumerate(statements):
            multiple_statements = len(statements) > 1

            # only create a transition when there is more than 1 statement
            # and we are not in the last iteration
            if multiple_statements:
                if i < len(statements) - 1:
                    current_connection_uuid = create_transition("connection", "", self.net, node)
                    # node.cluster.add_child(Cluster(current_connection_uuid))
                else:
                    current_connection_uuid = last_connection_uuid
            else:
                previous_connection_uuid = first_connection_uuid
                current_connection_uuid = last_connection_uuid

            args = (
                statement,
                task_context,
                previous_connection_uuid,
                current_connection_uuid,
                node,
                in_loop,
            )

            if isinstance(statement, Service):
                connection_uuids = [self.generate_service(*args)]
            elif isinstance(statement, TaskCall):
                connection_uuids, new_task_context = self.generate_task_call(*args)
            elif isinstance(statement, Parallel):
                connection_uuids = [self.generate_parallel(*args)]
            elif isinstance(statement, CountingLoop):
                connection_uuids = [self.generate_counting_loop(*args)]
            elif isinstance(statement, WhileLoop):
                connection_uuids = [self.generate_while_loop(*args)]
            elif isinstance(statement, Condition):
                connection_uuids = self.generate_condition(*args)
            else:
                connection_uuids = self.handle_other_statements(*args)

            previous_connection_uuid = current_connection_uuid

        return connection_uuids

    def generate_service(
        self,
        service: Service,
        task_context: TaskAPI,
        first_transition_uuid: str,
        second_transition_uuid: str,
        node: Node,
        in_loop: bool = False,
    ) -> str:
        """Generate the Petri Net components for a Service Call.

        Returns:
            The uuid of the last transition of the Service petri net component.
        """
        group_uuid = str(uuid.uuid4())
        service_node = Node(group_uuid, service.name, node)

        service_api = ServiceAPI(service, task_context, in_loop=in_loop)

        service_started_uuid = create_place(service.name + " started", self.net, service_node)
        service_finished_uuid = create_place(service.name + " finished", self.net, service_node)

        self.place_dict[service_api.uuid] = service_finished_uuid

        service_done_uuid = create_place(service.name + " done", self.net, service_node)
        service_done_transition_uuid = create_transition("service_done", "", self.net, service_node)

        self.add_callback(first_transition_uuid, self.callbacks.service_started, service_api)
        self.add_callback(
            service_done_transition_uuid, self.callbacks.service_finished, service_api
        )

        self.net.add_input(service_started_uuid, service_done_transition_uuid, Value(1))
        self.net.add_input(service_finished_uuid, service_done_transition_uuid, Value(1))
        self.net.add_output(service_done_uuid, service_done_transition_uuid, Value(1))

        self.net.add_output(service_started_uuid, first_transition_uuid, Value(1))
        self.net.add_input(service_done_uuid, second_transition_uuid, Value(1))

        service_node.cluster = Cluster(
            [
                service_started_uuid,
                service_finished_uuid,
                service_done_transition_uuid,
                service_done_uuid,
            ]
        )
        return service_done_transition_uuid

    def generate_task_call(
        self,
        task_call: TaskCall,
        task_context: TaskAPI,
        first_transition_uuid: str,
        second_transition_uuid: str,
        node: Node,
        in_loop: bool = False,
    ) -> List[str]:
        """Generate the Petri Net components for a Task Call.

        Returns:
            The uuids of the last transitions of the TaskCall petri net component.
        """
        called_task = self.tasks[task_call.name]
        new_task_context = TaskAPI(called_task, task_context, task_call=task_call, in_loop=in_loop)

        group_uuid = str(uuid.uuid4())
        task_node = Node(group_uuid, task_call.name, node)

        # Order for callbacks important: Task starts before statement and finishes after
        self.add_callback(first_transition_uuid, self.callbacks.task_started, new_task_context)
        last_connection_uuids = self.generate_statements(
            new_task_context,
            called_task.statements,
            first_transition_uuid,
            second_transition_uuid,
            task_node,
            in_loop,
        )

        for last_connection_uuid in last_connection_uuids:
            self.add_callback(last_connection_uuid, self.callbacks.task_finished, new_task_context)

        return last_connection_uuids, new_task_context

    def generate_parallel(
        self,
        parallel: Parallel,
        task_context: TaskAPI,
        first_transition_uuid: str,
        second_transition_uuid: str,
        node: Node,
        in_loop: bool = False,
    ) -> str:
        """Generate the Petri Net components for a Parallel statement.

        Returns:
            The uuid of the last transition of the Parallel petri net component.
        """

        group_uuid = str(uuid.uuid4())
        parallel_node = Node(group_uuid, "Parallel", node)

        sync_uuid = create_transition("", "", self.net, group_uuid)
        parallel_finished_uuid = create_place("Parallel finished", self.net, parallel_node)

        cluster = Cluster([], Cluster([sync_uuid, parallel_finished_uuid]))
        node.cluster.add_child(cluster)
        parallel_node.cluster = cluster

        for task_call in parallel.task_calls:
            parallel_cluster = Cluster([])
            cluster.add_child(parallel_cluster)
            parallel_node.cluster = parallel_cluster
            self.generate_task_call(
                task_call, task_context, first_transition_uuid, sync_uuid, parallel_node, in_loop
            )

        self.net.add_output(parallel_finished_uuid, sync_uuid, Value(1))
        self.net.add_input(parallel_finished_uuid, second_transition_uuid, Value(1))
        return sync_uuid

    def generate_condition(
        self,
        condition: Condition,
        task_context: TaskAPI,
        first_transition_uuid: str,
        second_transition_uuid: str,
        node: Node,
        in_loop: bool = False,
    ) -> List[str]:
        """Generate Petri Net components for the Condition statement.

        Returns:
            The uuids of the last transitions of the Condition petri net component.
        """
        group_uuid = str(uuid.uuid4())
        condition_node = Node(group_uuid, "Condition", node)

        passed_uuid = create_place("Passed", self.net, condition_node)
        failed_uuid = create_place("Failed", self.net, condition_node)

        expression_uuid = create_place(
            "If " + self.parse_expression(condition.expression),
            self.net,
            condition_node,
        )

        first_passed_transition_uuid = create_transition("", "", self.net, condition_node)
        first_failed_transition_uuid = create_transition("", "", self.net, condition_node)

        self.net.add_input(expression_uuid, first_passed_transition_uuid, Value(1))
        self.net.add_input(expression_uuid, first_failed_transition_uuid, Value(1))

        self.net.add_input(passed_uuid, first_passed_transition_uuid, Value(1))
        self.net.add_input(failed_uuid, first_failed_transition_uuid, Value(1))

        finished_uuid = create_place("Condition_Finished", self.net, condition_node)

        second_passed_transition_uuid = create_transition("", "", self.net, condition_node)
        self.net.add_output(finished_uuid, second_passed_transition_uuid, Value(1))

        cluster = Cluster([passed_uuid, failed_uuid, expression_uuid, finished_uuid])
        node.cluster.add_child(cluster)

        cluster_passed = Cluster([first_passed_transition_uuid, second_passed_transition_uuid])
        cluster_failed = Cluster([first_failed_transition_uuid])
        cluster.add_child(cluster_passed)
        cluster.add_child(cluster_failed)
        condition_node.cluster = cluster_passed

        self.generate_statements(
            task_context,
            condition.passed_stmts,
            first_passed_transition_uuid,
            second_passed_transition_uuid,
            condition_node,
            in_loop,
        )

        self.net.add_output(expression_uuid, first_transition_uuid, Value(1))
        self.net.add_input(finished_uuid, second_transition_uuid, Value(1))

        args = (condition, passed_uuid, failed_uuid, task_context)
        self.add_callback(first_transition_uuid, self.callbacks.condition_started, *args)

        if condition.failed_stmts:
            condition_node.cluster = cluster_failed
            second_failed_transition_uuid = create_transition("", "", self.net, condition_node)
            cluster_failed.add_node(second_failed_transition_uuid)
            self.generate_statements(
                task_context,
                condition.failed_stmts,
                first_failed_transition_uuid,
                second_failed_transition_uuid,
                condition_node,
                in_loop,
            )

            self.net.add_output(finished_uuid, second_failed_transition_uuid, Value(1))
            return [second_passed_transition_uuid, second_failed_transition_uuid]
        else:
            self.net.add_output(finished_uuid, first_failed_transition_uuid, Value(1))
            return [second_passed_transition_uuid, first_failed_transition_uuid]

    def generate_counting_loop(
        self,
        loop: CountingLoop,
        task_context: TaskAPI,
        first_transition_uuid: str,
        second_transition_uuid: str,
        node: Node,
        in_loop: bool = False,
    ) -> str:
        """Generates the Petri Net components for a Couting Loop.

        Returns:
            The uuid of the last transition of the CountingLoop petri net component.
        """
        if loop.parallel:
            return self.generate_parallel_loop(
                loop, task_context, first_transition_uuid, second_transition_uuid, node
            )

        group_uuid = str(uuid.uuid4())
        counting_loop_node = Node(group_uuid, "Counting Loop", node)
        loop_uuid = create_place("Loop", self.net, group_uuid)

        loop_text = "Loop"

        loop_statements_uuid = create_place(loop_text, self.net, counting_loop_node)
        loop_finished_uuid = create_place("Number of Steps Done", self.net, counting_loop_node)

        condition_passed_transition_uuid = create_transition("", "", self.net, counting_loop_node)
        condition_failed_transition_uuid = create_transition("", "", self.net, counting_loop_node)
        iteration_step_done_transition_uuid = create_transition(
            "", "", self.net, counting_loop_node
        )

        self.net.add_input(loop_uuid, condition_passed_transition_uuid, Value(1))
        self.net.add_input(loop_statements_uuid, condition_passed_transition_uuid, Value(1))
        self.net.add_input(loop_uuid, condition_failed_transition_uuid, Value(1))
        self.net.add_input(loop_finished_uuid, condition_failed_transition_uuid, Value(1))
        self.net.add_output(loop_uuid, iteration_step_done_transition_uuid, Value(1))

        loop_done_uuid = create_place("Loop Done", self.net, counting_loop_node)

        cluster = Cluster(
            [
                loop_uuid,
                loop_statements_uuid,
                loop_finished_uuid,
                condition_passed_transition_uuid,
                condition_failed_transition_uuid,
                iteration_step_done_transition_uuid,
                loop_done_uuid,
            ]
        )

        node.cluster.add_child(cluster)
        counting_loop_node.cluster = cluster

        self.generate_statements(
            task_context,
            loop.statements,
            condition_passed_transition_uuid,
            iteration_step_done_transition_uuid,
            counting_loop_node,
            True,
        )

        self.net.add_output(loop_done_uuid, condition_failed_transition_uuid, Value(1))
        self.net.add_output(loop_uuid, first_transition_uuid, Value(1))
        self.net.add_input(loop_done_uuid, second_transition_uuid, Value(1))

        args = (loop, loop_statements_uuid, loop_finished_uuid, task_context)
        self.add_callback(first_transition_uuid, self.callbacks.counting_loop_started, *args)
        self.add_callback(
            iteration_step_done_transition_uuid, self.callbacks.counting_loop_started, *args
        )

        return condition_failed_transition_uuid

    def generate_parallel_loop(
        self,
        loop: CountingLoop,
        task_context: TaskAPI,
        first_transition_uuid: str,
        second_transition_uuid: str,
        node: Node,
    ) -> str:
        """Generates the static petri net components for a ParallelLoop.

        This method will generate a placeholder for the ParallelLoop. The real amount
        of parallel startet Tasks is only known at runtime.

        Returns:
            The uuid of the last transition of the ParallelLoop petri net component.
        """

        group_uuid = str(uuid.uuid4())
        parallel_loop_node = Node(group_uuid, "Parallel Loop", node)

        parallel_loop_started = create_place(
            "Start " + loop.statements[0].name + " in parallel",
            self.net,
            parallel_loop_node,
        )
        cluster = Cluster([parallel_loop_started])
        # node.cluster.add_child(cluster)
        parallel_loop_node.cluster = cluster
        self.net.add_output(parallel_loop_started, first_transition_uuid, Value(1))
        self.net.add_input(parallel_loop_started, second_transition_uuid, Value(1))

        args = (
            loop,
            task_context,
            loop.statements[0],
            parallel_loop_started,
            first_transition_uuid,
            second_transition_uuid,
            parallel_loop_node,
        )
        self.add_callback(first_transition_uuid, self.callbacks.parallel_loop_started, *args)
        return second_transition_uuid

    def handle_other_statements(
        self,
        statement: Any,
        task_context: TaskAPI,
        first_transition_uuid: str,
        second_transition_uuid: str,
        node: Node,
        in_loop: bool = False,
    ) -> List[str]:
        """Generates Petri Net components for newly added PFDL components.

        This function can be used by plugin developers to generate Petri Net components
        if they add new components through their plugin.

        Returns:
            A list of uuids of the last transition in the respective component.
        """
        return None

    def remove_place_on_runtime(self, place_uuid: str) -> None:
        """Removes a place from the petri net at runtime.

        This method tries to remove the place with the given id from the petri net.
        Due to the clustering plugin in the petri net library, the `remove` place method


        Args:
            place_uuid: The uuid as string of the task which should be removed from the net.
        """
        if self.net.has_place(place_uuid):
            # self.net.clusters._nodes.add(place_uuid)
            self.net.remove_place(place_uuid)
            if self.draw_net:
                draw_petri_net(self.net, self.path_for_image)

    def generate_empty_parallel_loop(
        self, first_transition_uuid: str, second_transition_uuid: str, node: Node
    ) -> None:
        empty_loop_place = create_place("Execute 0 tasks", self.net, node)
        self.net.add_output(empty_loop_place, first_transition_uuid, Value(1))
        self.net.add_input(empty_loop_place, second_transition_uuid, Value(1))

    def generate_while_loop(
        self,
        loop: CountingLoop,
        task_context: TaskAPI,
        first_transition_uuid: str,
        second_transition_uuid: str,
        node: Node,
        in_loop: bool = False,
    ) -> str:
        """Generate the Petri Net components for a While Loop.

        Returns:
            The uuid of the last transition of the WhileLoop petri net component.
        """
        group_uuid = str(uuid.uuid4())
        while_loop_node = Node(group_uuid, "While Loop", node)

        loop_uuid = create_place("Loop", self.net, while_loop_node)

        loop_text = "Loop"

        loop_statements_uuid = create_place(loop_text, self.net, while_loop_node)
        loop_finished_uuid = create_place("Number of Steps Done", self.net, while_loop_node)

        condition_passed_transition_uuid = create_transition("", "", self.net, while_loop_node)
        condition_failed_transition_uuid = create_transition("", "", self.net, while_loop_node)
        iteration_step_done_transition_uuid = create_transition("", "", self.net, while_loop_node)

        self.net.add_input(loop_uuid, condition_passed_transition_uuid, Value(1))
        self.net.add_input(loop_statements_uuid, condition_passed_transition_uuid, Value(1))
        self.net.add_input(loop_uuid, condition_failed_transition_uuid, Value(1))
        self.net.add_input(loop_finished_uuid, condition_failed_transition_uuid, Value(1))
        self.net.add_output(loop_uuid, iteration_step_done_transition_uuid, Value(1))

        loop_done_uuid = create_place("Loop Done", self.net, while_loop_node)

        cluster = Cluster(
            [
                loop_uuid,
                loop_statements_uuid,
                loop_finished_uuid,
                condition_failed_transition_uuid,
                loop_done_uuid,
                condition_passed_transition_uuid,
                iteration_step_done_transition_uuid,
            ]
        )

        node.cluster.add_child(cluster)
        while_loop_node.cluster = cluster
        self.generate_statements(
            task_context,
            loop.statements,
            condition_passed_transition_uuid,
            iteration_step_done_transition_uuid,
            while_loop_node,
            True,
        )

        self.net.add_output(loop_uuid, first_transition_uuid, Value(1))
        self.net.add_input(loop_done_uuid, second_transition_uuid, Value(1))

        args = (loop, loop_statements_uuid, loop_finished_uuid, task_context)
        self.add_callback(first_transition_uuid, self.callbacks.while_loop_started, *args)
        self.add_callback(
            iteration_step_done_transition_uuid, self.callbacks.while_loop_started, *args
        )

        self.net.add_output(loop_done_uuid, condition_failed_transition_uuid, Value(1))

        return condition_failed_transition_uuid

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


def create_place(name: str, net: PetriNet, node: Node) -> str:
    """Utility function for creating a place with the snakes module.

    This function is used to add a place with the given name and to add labels for
    scheduling (for example if the place represents an event or if its initialized).

    Args:
        name: A string representing the displayed name of the place.
        net: The petri net instance this place should be added to.
        group_uuid: The id of a group of petri net components this place belongs to

    Returns:
        A UUID as string for the added place.
    """
    place_uuid = str(uuid.uuid4())
    net.add_place(Place(place_uuid, []), cluster=node.get_path())
    net.place(place_uuid).label(name=name, group_uuid=node.group_uuid)
    return place_uuid


def create_transition(transition_name: str, transition_type: str, net: PetriNet, node: Node) -> str:
    """Utility function for creating a transition with the snakes module.

    This function is used to add a transition with the given name and to add labels for
    scheduling (currently only the type of the transition).

    Args:
        transition_name: A string representing the displayed name of the transition.
        net: The petri net instance this transition should be added to.
        group_uuid: The id of a group of petri net components this transition belongs to

    Returns:
        A UUID as string for the added transition.
    """
    transition_uuid = str(uuid.uuid4())
    net.add_transition(Transition(transition_uuid), cluster=node.get_path())
    net.transition(transition_uuid).label(
        name=transition_name,
        transitionType=transition_type,
        group_uuid=node.group_uuid,
    )
    return transition_uuid
