# The Scheduler class

The PFDL scheduler is the interface between the PFDL core (model, petri net) and the outside world. If you want to receive the current state of the Production Order or push it further by sending status updates of the services you can register callback functions and fire events.

::: pfdl_scheduler.scheduler.Scheduler
    options:
        members:
            - start
            - fire_event
            - register_callback_service_started
            - register_callback_service_finished
            - register_callback_task_finished
            - register_variable_access_function

## Scheduler Callbacks
This section is an introduction of how to use the schedulers callback functions.

In general, the callback functions can be subdivided into two classes:
The first contains callback functions that are used by the scheduler to communicate the start or the finish of a task or service respectively: 

The task started callback creates an object of this task inside the EE.
The required information to create this object are inside the TASK API object that is provided by the scheduler.
Most important for this callback are the task’s input variables.
As tasks are nested inside other tasks, each new task object is a new level where local variables can be defined.
The input variables that have to be part of the new task object are provided by the task_api.task_call.input_parameters object.
New tasks can rename their input. The corresponding input values are provided in two different ways. First, variables can be transmitted to the new task object based on a variable inside the task_context. The second case describes the introduction of a new variable based on a literal structure definition inside the pfdl file. In this case, the variable’s value is provided by the task_api.task_call.input_parameters object. 
 
Similar to the task started callback function, the task finished callback is used to update the task objects in the data lifecycle object. However, the task finished callback deletes them. In this case, variables in the task context object are either updated or added. The corresponding variables and values are provided that are returned from the task object can be extracted from the task_api.task.output_parameters object. The corresponding variable names are stored inside the task_api.task_call.output_parameters object. 

The service started callback leads to a service execution on the field level. In this connection, the PFDL scheduler schedules one service. Its input variables can be accessed through the service.service.input_parameters object. Here, it is either possible to use literal input values from the PFDL file, or use existing variables from the task object to parameterize the service. To identify the task object from which the variables values have to be queried, each service provides a service context object that identifies the task object in which context the service is executed. Services are never added to the data lifecycle object; however, their execution can be illustrated by providing, e.g. a state variable to mirror the execution’s state and a service execution variable to specify the currently executed service. 

As Services possess output variables, the Service finished callback function is used to either update existing variables in the task object or to add new ones. Equally to the service started callback, the service finished callback provides a service.task_context.uuid object to identify the task object that has to be adjusted. 

The second class contains two callback functions that are used by the scheduler to access information from the EE. The first of these functions places tokens inside the petri net as soon as a service execution is completed. The second delivers a structure variable from the Data Lifecycle Object to the scheduler. This callback is required by the scheduler to access runtime data and thus, enables the scheduler to execute PFDL condition blocks. In this context, the scheduler always receives the complete structure and accesses single structure fields by itself. To identify the structure in the Data Lifecycle Object, the scheduler provides the tasks uuid, the task_contexts uuid and the variable name.  

::: pfdl_scheduler.scheduling.event.Event

::: pfdl_scheduler.scheduling.task_callbacks.TaskCallbacks