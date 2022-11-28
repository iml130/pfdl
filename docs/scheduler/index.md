# Using the PFDL scheduler

This section can be used as a reference while developing software with the PFDL Scheduler.
All classes that can be used are documented here.

The [Scheduler](scheduler_class.md) section gives an overview of all functions that are needed for starting the scheduler and registering your callback functions to get status updates while the petri net is traversed.

In the [SchedulerAPI](api.md) section the API classes can be found which will be passed to you by the callback functions.
This objects refering to a called Task or Service provides identification and context informationen to keep track of the current status of the production order.

If you want to work with the generated model of the PFDL file the [Model classes](model_classes.md) section gives an detailed overview over all model classes and their attributes.

If you want to work on the code of the PFDL Scheduler the [Developers Reference](developer_reference.md) section provides documentation about all the remaining internal classes.