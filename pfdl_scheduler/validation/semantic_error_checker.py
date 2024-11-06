# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains the SemanticErrorChecker class."""

# standard libraries
from typing import Dict, List, Union, Any

# 3rd party libraries
from antlr4.ParserRuleContext import ParserRuleContext

# local sources
from pfdl_scheduler.model.instance import Instance
from pfdl_scheduler.model.process import Process
from pfdl_scheduler.model.struct import Struct
from pfdl_scheduler.model.array import Array
from pfdl_scheduler.model.task import Task
from pfdl_scheduler.model.service import Service
from pfdl_scheduler.model.parallel import Parallel
from pfdl_scheduler.model.task_call import TaskCall
from pfdl_scheduler.model.counting_loop import CountingLoop
from pfdl_scheduler.model.while_loop import WhileLoop
from pfdl_scheduler.model.condition import Condition

from pfdl_scheduler.pfdl_base_classes import PFDLBaseClasses
from pfdl_scheduler.validation.error_handler import ErrorHandler

from pfdl_scheduler.utils import helpers

# global defines
from pfdl_scheduler.parser.pfdl_tree_visitor import IN_KEY, OUT_KEY


class SemanticErrorChecker:
    """Checks for static semantic errors in a given Process object.

    Each of the methods in this class checks for a specific semantic error. After calling
    the validate_process method the entire given process object and all the model objects
    it contains are tested for errors.

    Attributes:
        error_handler: ErrorHandler instance for printing errors.
        process: The Process object which has to be validated.
        tasks: A Dict that contains all Task objects of the given process object.
        structs: A Dict that contains all Struct objects of the given process object.
    """

    def __init__(
        self,
        error_handler: ErrorHandler,
        process: Process,
        pfdl_base_classes: PFDLBaseClasses = PFDLBaseClasses(),
    ) -> None:
        """Initialize the object.

        Args:
            error_handler: ErrorHandler instance for printing errors.
            process: The Process object which has to be validated.
        """
        self.error_handler: ErrorHandler = error_handler
        self.process: Process = process
        self.tasks: Dict[str, Task] = process.tasks
        self.structs: Dict[str, Struct] = process.structs
        self.pfdl_base_classes: PFDLBaseClasses = pfdl_base_classes

    def validate_process(self) -> bool:
        """Starts static semantic checks.

        Returns:
            True, if the process has no errors, otherwise False.
        """
        # use & so all methods will be executed even if a method returns False
        return self.check_structs() & self.check_tasks() & self.check_instances()

    # Struct check
    def check_structs(self) -> bool:
        """Executes semantic checks for each Struct.

        Returns:
            True if all Struct definitions are valid.
        """
        valid = True
        for struct in self.structs.values():
            if not self.check_for_unknown_datatypes_in_struct_definition(struct):
                valid = False
        return valid

    def check_for_unknown_datatypes_in_struct_definition(self, struct: Struct) -> bool:
        """Checks for each attribute definition in the struct if the defined type exists.

        Returns:
            True if all datatypes in the given struct are known.
        """
        datatypes_known = True
        for identifier, attribute_type in struct.attributes.items():
            if not self.check_if_variable_definition_is_valid(
                identifier, attribute_type, struct.context
            ):
                datatypes_known = False
        return datatypes_known

    # Task check
    def check_tasks(self) -> bool:
        """Executes semantic checks for each Task.

        Returns:
            True if all Task definitions are valid.
        """
        valid = True

        start_task_found = False
        for task in self.tasks.values():
            if task.name == self.process.start_task_name:
                start_task_found = True

            # use & so all methods will be executed even if a method returns False
            if not (
                self.check_statements(task)
                & self.check_task_input_parameters(task)
                & self.check_task_output_parameters(task)
            ):
                valid = False

        if not start_task_found:
            error_msg = f"The file contains no '{self.process.start_task_name}' (Starting Point)"
            self.error_handler.print_error(error_msg, line=1, column=0, off_symbol_length=5)
            return False

        return valid

    def check_instances(self) -> bool:
        """Executes semantic checks for all Instances.

        Returns:
            True if all Instances are valid.
        """
        valid = True
        for instance in self.process.instances.values():
            struct_name = instance.struct_name
            struct = None
            if struct_name in self.process.structs:
                struct = self.process.structs[struct_name]

            # check first if the corresponding Struct exists
            if struct is None:
                error_msg = (
                    f"The Instance '{instance.name}' refers to a struct that does not exist."
                )
                self.error_handler.print_error(error_msg, context=instance.context)
                valid = False
            else:
                # execute checks. The second check can only be executed if the previous one succeeded
                valid = (
                    self.check_if_instance_attributes_exist_in_struct(struct, instance)
                    and self.check_if_value_matches_with_defined_type(struct, instance)
                ) & self.check_if_struct_attributes_are_assigned(struct, instance)
        return valid

    def check_if_instance_attributes_exist_in_struct(
        self, struct: Struct, instance: Instance
    ) -> bool:
        """Checks if all attributes in the given Instance exist in the corresponding Struct.

        Returns:
            True if all attributes in the given Instance exist in the corresponding Struct.
        """
        valid = True
        # collect all attributes of the corresponding struct, including attributes of parent structs
        struct_attributes = set(self.process.structs[struct.name].attributes.keys())

        for attribute_name, attribute_value in instance.attributes.items():
            # validate all atributes of this instance
            if not attribute_name in struct_attributes:
                error_msg = (
                    f"The attribute '{attribute_name}' in instance '{instance.name}' "
                    + "was not defined in the corresponding Struct"
                )

                self.error_handler.print_error(error_msg, context=instance.context)
                valid = False
            elif isinstance(attribute_value, self.pfdl_base_classes.get_class("Instance")):
                # the attribute is an instance so recursively check its attributes
                nested_struct = self.process.structs[struct.attributes[attribute_name]]
                if not self.check_if_instance_attributes_exist_in_struct(
                    nested_struct, attribute_value
                ):
                    valid = False
        return valid

    def check_if_struct_attributes_are_assigned(self, struct: Struct, instance: Instance) -> bool:
        """Checks if all attributes from the corresponding struct are assigned
        with values in the instance.

        Returns: True if all attributes of the instance are assigned
        """
        valid = True

        struct_attributes = struct.attributes.copy()

        for struct_attribute in struct_attributes:
            attribute_found = False
            for attribute_name, attribute_value in instance.attributes.items():
                if struct_attribute == attribute_name:
                    attribute_found = True

                    if isinstance(attribute_value, self.pfdl_base_classes.get_class("Instance")):
                        # the attribute is an instance so recursively check its attributes
                        nested_struct = self.process.structs[struct.attributes[attribute_name]]
                        if not self.check_if_struct_attributes_are_assigned(
                            nested_struct, attribute_value
                        ):
                            valid = False
                    break
            if attribute_found is False:
                error_msg = (
                    f"The attribute '{struct_attribute}' from the corresponding struct was not "
                    f"definied in instance '{instance.name}'"
                )
                self.error_handler.print_error(error_msg, context=instance.context)
                valid = False
        return valid

    def check_if_value_matches_with_defined_type(self, struct: Struct, instance: Instance) -> bool:
        """Checks if the assigned values in the Instance match with the defined type in the Struct.

        Returns:
            True if all assigned values in the Instance match
            with the defined type in the Struct.
        """
        valid = True
        for attribute_name, attribute_value in instance.attributes.items():
            struct_attr_type = None
            struct_attributes = struct.attributes

            # This method assumes that the attribute exists in the Struct, so no additional check
            struct_attr_type = struct_attributes[attribute_name]

            if isinstance(attribute_value, self.pfdl_base_classes.get_class("Instance")):
                # the attribute is an instance so recursively check its attributes
                nested_struct = self.process.structs[struct_attr_type]
                if not self.check_if_value_matches_with_defined_type(
                    nested_struct, attribute_value
                ):
                    valid = False

            elif not self.check_type_of_value(attribute_value, struct_attr_type):
                error_msg = (
                    f"The attribute '{attribute_name}' in instance '{instance.name}' has the "
                    f"wrong type: should be '{struct_attr_type}'."
                )
                self.error_handler.print_error(error_msg, context=instance.context)
                valid = False
        return valid

    def check_statements(self, task: Task) -> bool:
        """Executes semantic checks for all statements in a Task.

        Returns:
            True if all Statements are valid.
        """
        valid = True
        for statement in task.statements:
            if not self.check_statement(statement, task):
                valid = False
        return valid

    def check_statement(
        self,
        statement: Union[Service, TaskCall, WhileLoop, CountingLoop, Condition],
        task: Task,
    ) -> bool:
        """Calls check methods depending on the type of the statement.

        Returns:
            True if the given statement is valid.
        """
        if isinstance(statement, self.pfdl_base_classes.get_class("Service")):
            return self.check_service(statement, task)
        if isinstance(statement, self.pfdl_base_classes.get_class("TaskCall")):
            return self.check_task_call(statement, task)
        if isinstance(statement, self.pfdl_base_classes.get_class("Parallel")):
            return self.check_parallel(statement, task)
        if isinstance(statement, self.pfdl_base_classes.get_class("WhileLoop")):
            return self.check_while_loop(statement, task)
        if isinstance(statement, self.pfdl_base_classes.get_class("CountingLoop")):
            return self.check_counting_loop(statement, task)
        return self.check_conditional_statement(statement, task)

    def check_parallel(self, parallel: Parallel, task: Task) -> bool:
        """Calls check methods for the Parallel statement.

        Returns:
            True if the given Parallel statement is valid.
        """

        valid = True
        for task_call in parallel.task_calls:
            if not self.check_task_call(task_call, task):
                valid = False
        return valid

    def check_task_input_parameters(self, task: Task) -> bool:
        """Checks if the input parameters are valid.

        Returns:
            True if the input parameters of the given Task are valid.
        """
        valid = True
        # input_parameters: <identifier>: <variable_type>
        for identifier, variable_type in task.input_parameters.items():
            if not self.check_if_variable_definition_is_valid(
                identifier, variable_type, context=task.context_dict[IN_KEY]
            ):
                valid = False
        return valid

    def check_task_output_parameters(self, task: Task) -> bool:
        """Checks if the output parameters are valid.

        Checks if the variable names used as parameters are variables
        defined in the Task.

        Returns:
            True if the output parameters of the given Task are valid.
        """
        valid = True
        for output_param in task.output_parameters:
            if not output_param in task.variables:
                error_msg = (
                    f"An unknown variable '{output_param}' is used "
                    f"in the Task Output of Task '{task.name}'"
                )
                self.error_handler.print_error(error_msg, context=task.context_dict[OUT_KEY])
                valid = False
        return valid

    def check_service(self, service: Service, task: Task) -> bool:
        """Calls check methods for the Service or Service Call statement.

        Returns:
            True if the given Service statement is valid.
        """
        if not self.check_call_parameters(service, task):
            return False
        return True

    def check_task_call(self, task_call: TaskCall, task_context: Task) -> bool:
        """Calls check methods for the TaskCall statement.

        Args:
            task_call: The task call to be checked.
            task_context: The task in which the task call is defined.

        Returns:
            True if the given TaskCall statement is valid.
        """
        if self.check_if_task_in_taskcall_exists(task_call.name, task_call.context):
            if not (
                self.check_call_parameters(task_call, task_context)
                and self.check_if_task_call_matches_with_called_task(task_call, task_context)
            ):
                return False
        else:
            return False
        return True

    def check_if_task_call_matches_with_called_task(self, task_call: TaskCall, task: Task) -> bool:
        """Checks if the parameters of the Taskcall matches with the parameters of the Task.

        This method assumes that the validity of the input parameter itself was already checked.

        Multiple Checks are done:
            (1) Checks if length of parameters of Taskcall and Task match.
            (2) Checks if types of input parameters match.
            (3) Checks if types of output parameters match.

        Args:
            task_call: The task call to be checked.
            task_context: The task in which the task call is defined.

        Returns:
            True if the parameters matches.
        """
        called_task = self.tasks[task_call.name]
        if not self.check_if_task_call_parameter_length_match(task_call):
            return False

        valid = True
        for i, input_parameter in enumerate(task_call.input_parameters):
            identifier = list(called_task.input_parameters.items())[i][0]
            defined_type = list(called_task.input_parameters.items())[i][1]
            if not self.check_if_input_parameter_matches(
                input_parameter, identifier, defined_type, task_call, called_task, task
            ):
                valid = False

        for i, (identifier, data_type) in enumerate(task_call.output_parameters.items()):
            variable_in_called_task = called_task.output_parameters[i]
            if variable_in_called_task in called_task.variables:

                type_of_variable = ""
                if isinstance(
                    called_task.variables[variable_in_called_task],
                    self.pfdl_base_classes.get_class("Instance"),
                ):
                    type_of_variable = called_task.variables[variable_in_called_task].struct_name
                else:
                    type_of_variable = called_task.variables[variable_in_called_task]

                if str(type_of_variable) != str(data_type):
                    error_msg = (
                        f"Type of TaskCall output parameter at position {str((i+1))} does not "
                        f"match with type '{type_of_variable}' of output parameter "
                        f"'{variable_in_called_task}' in Task '{called_task.name}'"
                    )
                    self.error_handler.print_error(
                        error_msg,
                        context=task_call.context,
                        off_symbol_length=len(task_call.name),
                    )
                    valid = False

        return valid

    def check_if_input_parameter_matches(
        self,
        input_parameter: Union[str, List[str], Struct],
        identifier: str,
        defined_type: Union[str, Array],
        task_call: TaskCall,
        called_task: Task,
        task_context: Task,
    ) -> bool:
        """Checks if the input parameters of a Taskcall matches with the called Task.

        This method assumes that the validity of the input parameter itself was already checked.

        Args:
            input_parameter: The input parameter of the TaskCall.
            identifier: Parameter name of the input in the called task (only for error message).
            defined_type: Type of the input in the called task.
            task_call: The TaskCall the input parameter is from.
            called_task: The Task the TaskCall is refering to (the called task).
            task_context: The Task in which the TaskCall was evoked.
        Returns:
            True if the input parameters of a Taskcall matches with the called Task.
        """
        if isinstance(input_parameter, str):
            if input_parameter in task_context.variables:
                type_of_variable = ""
                variable = task_context.variables[input_parameter]
                if isinstance(variable, self.pfdl_base_classes.get_class("Instance")):
                    type_of_variable = variable.struct_name
                else:
                    type_of_variable = variable

                # str() because of possible Arrays as
                # types (we can compare types by converting Array object to string)
                if str(type_of_variable) != str(defined_type):
                    error_msg = (
                        f"Type of TaskCall parameter '{input_parameter}' does not match "
                        f"with type '{defined_type}' of Input Parameter '{identifier}' in"
                        f" Task '{called_task.name}'"
                    )
                    self.error_handler.print_error(
                        error_msg,
                        context=task_call.context,
                        off_symbol_length=len(task_call.name),
                    )
                    return False
            else:
                error_msg = (
                    f"Type of TaskCall parameter '{input_parameter}' does not match with "
                    f"type '{defined_type}' of Input Parameter '{identifier}' in Task "
                    f"'{called_task.name}'"
                )
                self.error_handler.print_error(
                    error_msg,
                    context=task_call.context,
                    off_symbol_length=len(task_call.name),
                )
                return False
        elif isinstance(input_parameter, list):
            # At this point it is known that the variable chain is valid, so dont check again
            current_struct = self.structs[task_context.variables[input_parameter[0]]]
            i = 1
            while i < len(input_parameter) - 1:
                element = current_struct.attributes[input_parameter[i]]
                if isinstance(element, self.pfdl_base_classes.get_class("Array")):
                    i = i + 1
                    current_struct = self.structs[element.type_of_elements]
                else:
                    current_struct = self.structs[element]
                i = i + 1

            index = len(input_parameter) - 1
            if input_parameter[index].startswith("["):
                given_type = current_struct.name
            else:
                given_type = current_struct.attributes[input_parameter[index]]
            if given_type != defined_type:
                error_msg = (
                    "Type of TaskCall parameter "
                    f"'{input_parameter[len(input_parameter)-1]}' does not match with "
                    f"type '{defined_type}' of Input Parameter '{identifier}' "
                    f"in Task '{called_task.name}'"
                )
                self.error_handler.print_error(
                    error_msg,
                    context=task_call.context,
                    off_symbol_length=len(task_call.name),
                )
                return False
        elif isinstance(input_parameter, self.pfdl_base_classes.get_class("Struct")):
            if input_parameter.name != defined_type:
                error_msg = (
                    f"Type of TaskCall parameter '{input_parameter.name}' does not match "
                    f"with type '{defined_type}' of Input Parameter '{identifier}' in "
                    f"Task '{called_task.name}'"
                )
                self.error_handler.print_error(
                    error_msg,
                    context=task_call.context,
                    off_symbol_length=len(task_call.name),
                )
                return False
        return True

    def check_if_task_call_parameter_length_match(self, task_call: TaskCall) -> bool:
        """Checks if the length of the Task call parameters match with the called Task.

        Returns:
            True if the parameter lengths matches.
        """
        called_task = self.tasks[task_call.name]
        if len(called_task.input_parameters) != len(task_call.input_parameters):
            error_msg = "Inputparameter length of Task Call and called Task dont match"
            self.error_handler.print_error(error_msg, context=task_call.context)
            return False
        if len(called_task.output_parameters) != len(task_call.output_parameters):
            error_msg = "Outputparameter length of Task Call and called Task dont match"
            self.error_handler.print_error(error_msg, context=task_call.context)
            return False
        return True

    def check_call_parameters(self, called_entity: Union[Service, TaskCall], task: Task) -> bool:
        """Checks if the parameters of a Service or Task call are valid (input and output).

        Args:
            called_entity: The evoked call (service or task call).

        Returns:
            True if the parameters of a Service or Task call are valid.
        """
        valid = True
        if called_entity.input_parameters:
            valid = self.check_call_input_parameters(called_entity, task)
        if called_entity.output_parameters:
            valid = valid & self.check_call_output_parameters(called_entity)

        return valid

    def check_call_input_parameters(
        self, called_entity: Union[Service, TaskCall], task: Task
    ) -> bool:
        """Checks if the input parameters of a Service or Task Call are valid.

        Args:
            called_entity: The evoked call (service or task call).

        Returns:
            True if the input parameters of a Service or Task Call are valid.
        """
        valid = True

        for input_parameter in called_entity.input_parameters:
            if isinstance(input_parameter, self.pfdl_base_classes.get_class("Struct")):
                if not self.check_instantiated_struct_attributes(input_parameter):
                    valid = False
            elif isinstance(input_parameter, list):
                if not self.check_attribute_access(
                    input_parameter, called_entity.context_dict[IN_KEY], task
                ):
                    valid = False
            elif not input_parameter in task.variables:
                error_msg = (
                    f"An unknown variable '{input_parameter}' is used as input of"
                    f" {type(called_entity).__name__} '{called_entity.name}'"
                )
                self.error_handler.print_error(error_msg, context=called_entity.context)
                valid = False
        return valid

    def check_attribute_access(
        self, variable_list: List[str], context: ParserRuleContext, task: Task
    ) -> bool:
        """Checks if the attribute access via a variable list (for example x.y.z) is valid.

        Returns:
            True if the attribute access is valid.
        """
        variable = variable_list[0]

        if variable in task.variables:
            if task.variables[variable].__class__.__name__ == "Instance":
                struct = self.structs[task.variables[variable].struct_name]
            if task.variables[variable] in self.structs:
                struct = self.structs[task.variables[variable]]
            predecessor = struct
            for i in range(1, len(variable_list)):
                attribute = variable_list[i]
                if not (attribute.startswith("[") and attribute.endswith("]")):
                    if attribute not in predecessor.attributes:
                        error_msg = f"Struct '{predecessor.name}' has no attribute '{attribute}'"
                        self.error_handler.print_error(error_msg, context=context)
                        return False
                    if i < len(variable_list) - 1:
                        # check if this attribute is an array (next element is [])
                        if not (
                            variable_list[i + 1].startswith("[")
                            and variable_list[i + 1].endswith("]")
                        ):
                            if predecessor.attributes[attribute] not in self.structs:
                                error_msg = f"Attribute '{attribute}' is not a Struct"
                                self.error_handler.print_error(error_msg, context=context)
                                return False
                            predecessor = self.structs[predecessor.attributes[attribute]]
                        else:
                            predecessor = self.structs[
                                predecessor.attributes[attribute].type_of_elements
                            ]
        else:
            error_msg = f"Unknown variable '{variable}'."
            self.error_handler.print_error(error_msg, context=context)
            return False
        return True

    def check_call_output_parameters(self, called_entity: Union[Service, TaskCall]) -> bool:
        """Checks if the output parameters of a Service or Task Call are valid.

        The output parameter of a call only consists of the visible variable name and
        the type of the variable. So all there is to check is the variable definition.
        This methods just calls the `check_if_variable_definition_is_valid` method for all
        output parameters.

        Args:
            called_entity: The evoked call (service or task call).

        Returns:
            True if the output parameters of a Service or Task Call are valid.
        """
        valid = True
        for identifier, variable_type in called_entity.output_parameters.items():
            if not self.check_if_variable_definition_is_valid(
                identifier, variable_type, called_entity.context
            ):
                valid = False
        return valid

    def check_instantiated_struct_attributes(self, struct_instance: Struct) -> bool:
        """Calls multiple check methods to validate an instantiated Struct.

        Multiple Checks are done:
            (1) Check if the name of the struct instance exists in the struct definitions.
            (2) Check if attributes from the struct definition are missing.
            (3) Check if there are attributes in the instance that do not exist in the definition.
            (4) Check if attributes in the instance do not match with attributes in the definition.

        Args:
            struct_instance: The instantiated struct that is checked.

        Returns:
            True if the instantiated Struct is valid.
        """
        valid = True
        if self.check_if_struct_exists(struct_instance):
            struct_definition = self.structs[struct_instance.name]

            if not self.check_for_missing_attribute_in_struct(struct_instance, struct_definition):
                valid = False

            for identifier in struct_instance.attributes:
                if not (
                    self.check_for_unknown_attribute_in_struct(
                        struct_instance, identifier, struct_definition
                    )
                    and self.check_for_wrong_attribute_type_in_struct(
                        struct_instance, identifier, struct_definition
                    )
                ):
                    valid = False
        else:
            valid = False

        return valid

    def check_if_struct_exists(self, struct: Struct) -> bool:
        """Checks if the given Struct instance refers to a existing Struct definition.

        Returns:
            True if the given Struct instance refers to a existing Struct definition.
        """
        if struct.name not in self.structs:
            error_msg = f"Unknown Struct '{struct.name}'"
            self.error_handler.print_error(error_msg, context=struct.context)
            return False
        return True

    def check_for_unknown_attribute_in_struct(
        self, struct_instance: Struct, identifier: str, struct_definition: Struct
    ) -> bool:
        """Checks if the given identifier in the instantiated struct
        exists in the struct definition.

        Args:
            struct_instance: The instantiated struct that is checked.
            identifier: The identifier in the struct instance which should be checked.
            struct_definition: The corresponding struct definition.

        Returns:
            True if the given identifier exists in the struct definition.
        """
        if identifier not in struct_definition.attributes:
            error_msg = (
                f"Unknown attribute '{identifier}' in instantiated "
                f"struct '{struct_definition.name}'"
            )
            self.error_handler.print_error(error_msg, context=struct_instance.context)
            return False
        return True

    def check_for_wrong_attribute_type_in_struct(
        self, struct_instance: Struct, identifier: str, struct_definition: Struct
    ) -> bool:
        """Calls check methods for the attribute assignments in an instantiated Struct.

        This methods assumes that the given identifier is not unknown.
        Args:
            struct_instance: The instantiated struct that is checked.
            identifier: The identifier in the struct instance which should be checked.
            struct_definition: The corresponding struct definition.

        Returns:
            True if the given identifier in the struct instance matches with the struct definition.
        """
        correct_attribute_type = struct_definition.attributes[identifier]
        attribute = struct_instance.attributes[identifier]

        if isinstance(correct_attribute_type, str):
            if correct_attribute_type in self.structs:
                # check for structs which has structs as attribute
                if isinstance(attribute, self.pfdl_base_classes.get_class("Struct")):
                    attribute.name = correct_attribute_type
                    struct_def = self.structs[correct_attribute_type]
                    struct_correct = True
                    for identifier in attribute.attributes:
                        if not self.check_for_wrong_attribute_type_in_struct(
                            attribute, identifier, struct_def
                        ):
                            struct_correct = False
                    return struct_correct
                error_msg = (
                    f"Attribute '{identifier}' has the wrong type in the "
                    f"instantiated Struct '{struct_instance.name}', expected "
                    f"Struct '{correct_attribute_type}'"
                )
                self.error_handler.print_error(error_msg, context=struct_instance.context)
                return False
            if not self.check_type_of_value(attribute, correct_attribute_type):
                error_msg = (
                    f"Attribute '{identifier}' has the wrong type in the instantiated"
                    f" Struct '{struct_instance.name}', expected '{correct_attribute_type}'"
                )
                self.error_handler.print_error(error_msg, context=struct_instance.context)
                return False

        elif isinstance(correct_attribute_type, self.pfdl_base_classes.get_class("Array")):
            if not isinstance(
                attribute, self.pfdl_base_classes.get_class("Array")
            ) or not self.check_array(attribute, correct_attribute_type):
                error_msg = (
                    f"Attribute '{identifier}' has the wrong type in the instantiated"
                    f" Struct '{struct_instance.name}', expected 'Array'"
                )
                self.error_handler.print_error(error_msg, context=struct_instance.context)
                return False
        return True

    def check_array(self, instantiated_array: Array, array_definition: Array) -> bool:
        """Calls check methods to validate the instantiated array.

        Returns:
            True if the given array is valid.
        """
        error_msg = ""
        element_type = array_definition.type_of_elements
        for value in instantiated_array.values:
            # type of Struct not checked yet
            if isinstance(value, self.pfdl_base_classes.get_class("Struct")):
                if value.name == "":
                    value.name = array_definition.type_of_elements
                if not self.check_instantiated_struct_attributes(value):
                    return False
            if not self.check_type_of_value(value, element_type):
                error_msg = (
                    f"Array has elements that does not match "
                    f"with the defined type '{element_type}'"
                )
                self.error_handler.print_error(error_msg, context=instantiated_array.context)
                return False

        if not self.instantiated_array_length_correct(instantiated_array, array_definition):
            error_msg = "Length of the defined array and the instantiated do not match"
            self.error_handler.print_error(error_msg, context=instantiated_array.context)
            return False

        return True

    def check_for_missing_attribute_in_struct(
        self, struct: Struct, struct_definition: Struct
    ) -> bool:
        """Checks if an instantiated Struct is missing an attribute from the Struct definition.

        Returns:
            True if no attributes are missing.
        """
        for attribute in struct_definition.attributes:
            if attribute not in struct.attributes:
                error_msg = (
                    f"Attribute '{attribute}' is not defined in "
                    f"the instantiated struct '{struct.name}'"
                )
                self.error_handler.print_error(error_msg, context=struct.context)
                return False
        return True

    def check_while_loop(self, while_loop: WhileLoop, task: Task) -> bool:
        """Calls check methods for the While Loop statement.

        Returns:
            True if the While Loop statement is valid.
        """
        valid = True
        for statement in while_loop.statements:
            if not self.check_statement(statement, task):
                valid = False

        if not self.check_expression(while_loop.expression, while_loop.context, task):
            valid = False
        return valid

    def check_counting_loop(self, counting_loop: CountingLoop, task: Task) -> bool:
        """Calls check methods for the Counting Loop statement.

        Returns:
            True if the Counting Loop statement is valid.
        """
        if counting_loop.parallel:
            if len(counting_loop.statements) == 1 and isinstance(
                counting_loop.statements[0], self.pfdl_base_classes.get_class("TaskCall")
            ):
                return True
            error_msg = "Only a single task call is allowed in a parallel loop statement!"
            self.error_handler.print_error(error_msg, context=counting_loop.context)
            return False
        else:
            valid = True
            for statement in counting_loop.statements:
                if not self.check_statement(statement, task):
                    valid = False

            return valid

    def check_conditional_statement(self, condition: Condition, task: Task) -> bool:
        """Calls check methods for the conditional statement.

        Calls check_statement for the Passed and Failed statements and checks if the
        boolean expression is valid.

        Returns:
            True if the conditional statement is valid.
        """
        valid = True
        for statement in condition.passed_stmts:
            if not self.check_statement(statement, task):
                valid = False

        for statement in condition.failed_stmts:
            if not self.check_statement(statement, task):
                valid = False

        if not self.check_expression(condition.expression, condition.context, task):
            valid = False
        return valid

    def check_expression(
        self, expression: Union[str, dict], context: ParserRuleContext, task: Task
    ) -> bool:
        """Executes checks to test given expression.

        Returns:
            True if the given expression is valid.
        """
        if isinstance(expression, (list, str)):
            if not self.check_single_expression(expression, context, task):
                return False
        elif isinstance(expression, dict):
            if len(expression) == 2:
                if not self.check_unary_operation(expression, context, task):
                    return False
            else:
                if not self.check_binary_operation(expression, context, task):
                    return False
        return True

    def check_single_expression(
        self, expression: Union[str, list], context: ParserRuleContext, task: Task
    ) -> bool:
        """Checks if a single expression is a valid expression.

        Returns:
            True if the given single expression is a valid expression.
        """
        if isinstance(expression, (str, int, float, bool)):
            return True
        if isinstance(expression, list):
            if not self.check_attribute_access(expression, context, task):
                return False

            # only numbers and booleans are allowed, so check the variable type
            variable_type = helpers.get_type_of_variable_list(expression, task, self.structs)
            if not (isinstance(variable_type, str) and variable_type in ["number", "boolean"]):
                msg = "The given attribute can not be resolved to a boolean expression"
                self.error_handler.print_error(
                    msg, context=context, off_symbol_length=len(expression)
                )
                return False
        return True

    def check_unary_operation(self, expression, context: ParserRuleContext, task: Task) -> bool:
        """Checks if a unary expression is a valid expression.

        Returns:
            True if the given unary expression is a valid expression.
        """
        return self.check_expression(expression["value"], context, task)

    def check_binary_operation(self, expression, context: ParserRuleContext, task: Task) -> bool:
        """Checks if a binary expression is a valid expression.

        Returns:
            True if the given binary expression is a valid expression.
        """
        left = expression["left"]
        right = expression["right"]

        if expression["binOp"] in ["<", ">", "<=", ">="]:
            # Check if left and right side represent numbers or strings
            if self.expression_is_number(left, task) and self.expression_is_number(right, task):
                return True
            if self.expression_is_string(left, task) and self.expression_is_string(right, task):
                return True

            msg = (
                "Types of right and left side of the comparison dont match. "
                "This might be caused by some of the Rule parameters that are not initialised."
            )
            self.error_handler.print_error(msg, context=context)
            return False
        if expression["binOp"] in ["*", "/", "+", "-"]:
            if self.expression_is_number(left, task) and self.expression_is_number(right, task):
                return True
            msg = "Right and left side have to be numbers when using arithmetic operators"
            self.error_handler.print_error(msg, context=context)
            return False
        if left == "(" and right == ")":
            return self.check_expression(expression["binOp"], context, task)

        # expression is either 'and', 'or', '==' or '!='
        return self.check_expression(left, context, task) and self.check_expression(
            right, context, task
        )

    def expression_is_number(self, expression, task: Task) -> bool:
        """Checks if the given expression is a number (int or float).

        Returns:
            True if the given expression is a number.
        """
        if isinstance(expression, (int, float, bool)):
            return True
        if isinstance(expression, list):
            given_type = helpers.get_type_of_variable_list(expression, task, self.structs)
            return isinstance(given_type, str) and given_type == "number"
        if isinstance(expression, dict):
            if expression["left"] == "(" and expression["right"] == ")":
                return self.expression_is_number(expression["binOp"], task)
            else:
                return self.expression_is_number(
                    expression["left"], task
                ) and self.expression_is_number(expression["right"], task)

        return False

    def expression_is_string(self, expression, task: Task) -> bool:
        """Checks if the given expression is a PFDL string.

        Returns:
            True if the given expression is a PFDL string.
        """
        if isinstance(expression, str):
            return True
        if isinstance(expression, list):
            given_type = helpers.get_type_of_variable_list(expression, task, self.structs)
            return isinstance(given_type, str) and given_type == "string"
        return False

    def check_if_variable_definition_is_valid(
        self, identifier: str, variable_type: Union[str, Array], context
    ) -> bool:
        """Checks if the variable has the correct type.

        Returns:
            True if variable definition is valid.
        """
        valid = True
        if isinstance(variable_type, str):
            if not self.variable_type_exists(variable_type):
                valid = False
        elif isinstance(variable_type, self.pfdl_base_classes.get_class("Array")):
            element_type = variable_type.type_of_elements
            if not self.variable_type_exists(element_type):
                valid = False

        if not valid:
            error_msg = (
                f"Unknown data type '{variable_type}' for task " f"input variable '{identifier}'"
            )
            self.error_handler.print_error(error_msg, context=context)
            return False

        return True

    def check_if_task_in_taskcall_exists(self, task_name: str, context: ParserRuleContext) -> bool:
        """Checks if the Task name in the Taskcall belongs to a Task.

        Returns:
            True if the given name belongs to a Task.
        """
        if task_name not in self.tasks:
            error_msg = "Unknown Task '" + task_name + "'"
            self.error_handler.print_error(error_msg, context=context)
            return False
        return True

    def variable_type_exists(self, variable_type: str) -> bool:
        """Checks if the given variable type exists in the PFDL file.

        A variable type can be a primitive (number, string or boolean) or
        an identifier of a defined Struct.

        Returns:
            True if the variable type exists within the PFDL file.
        """
        if variable_type[0].isupper():
            if variable_type not in self.structs:
                return False
        elif variable_type not in ["number", "string", "boolean"]:
            return False
        return True

    def check_type_of_value(self, value: Any, value_type: str) -> bool:
        """Checks if the given value is the given type in the DSL.

        Returns:
            True if the value is from the given value type.
        """
        if value_type == "number":
            # bool is a subclass of int so check it before
            if isinstance(value, bool):
                return False
            return isinstance(value, (int, float))
        if value_type == "boolean":
            return isinstance(value, bool)
        if value_type == "string":
            return isinstance(value, str)
        if isinstance(value, self.pfdl_base_classes.get_class("Struct")):
            return value.name == value_type
        # value was a string
        return True

    def instantiated_array_length_correct(
        self, instantiated_array: Array, array_definition: Array
    ) -> bool:
        """Checks if the length of the instantiated array matches with the array definition.

        Returns:
            True if both lengths are equal.
        """
        if array_definition.length != -1:
            return instantiated_array.length == array_definition.length
        # dynamic length
        return True
