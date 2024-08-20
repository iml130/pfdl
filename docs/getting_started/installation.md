<!--
SPDX-FileCopyrightText: The PFDL Contributors
SPDX-License-Identifier: MIT
-->
<style>
.figure{
    width: 70%;
    margin: 0 auto;
    padding: 0px;
}
.column {
  float: left;
  width: 50%;
  padding: 5px;
}

/* Clear floats after image containers */
.row::after {
  content: "";
  clear: both;
  display: table;
}
</style>

# Installation

This guide will lead you through the installation.
Afterwards the scheduler will be tested with a simple PFDL file.
We expect you to have cloned the [official PFDL repository](https://github.com/iml130/pfdl) while trying the steps below.

There are two ways to use the PFDL.
You can use the grammar only or use the Scheduler.
In the following we provide an installation guide for both cases.

### Grammar
At first you need the ANTLR tool to generate the Lexer and Parser files from the ANTLR grammar specifications.
Check out the Quick Start guide on the [official ANTLR site](https://www.antlr.org/index.html) to learn how to install ANTLR on your system (**Note**: we use ANTLR4, there is no support for ANTLR3).

To generate the files you can run the following command from the projects root directory:

```text
    antlr4 -Dlanguage=Python3 -visitor PFDLLexer.g4 PFDLParser.g4
```

This will generate the files from the PFDLLexer.g4 and PFDLParser.g4 specification files.
The -visitor argument makes sure that a Visitor class is generated too.
This will help to obtain the model after parsing.
The -Dlanguage argument specifies the code generation target language.
In our case python is used.

However, if you would like to use the PFDL grammar for your own purposes you can generate the files in a language of your choice too.
A list of all possible targets and download links can be found [here](https://www.antlr.org/download.html).


### Scheduler

The scheduler and especially the scheduler class can be used like every other python module.

#### Requirements
The following requirements are needed to run the scheduler:

* Pip packages from requirements.txt (`pip install -r requirements.txt`)
* [GraphViz](https://graphviz.org/) (if you want to use the scheduler/run the scheduler_demo.py)

Check if you correctly installed GraphViz (On Windows you need to put the path of the bin folder which is in the GraphViz folder into the PATH environment variable.
On Ubuntu it should be fine if you install it via apt or apt-get).
The installation process is not checked for macOS yet.
For troubleshooting on any OS visit the [Download](https://graphviz.org/download/) section of the official GraphViz documentation.

#### Run the validation
If you just want to validate your PFDL files run the following command from the root directory of the project.
All errors will be printed in the console, so if nothing is shown the file is valid.

```text
    python validate_pfdl_file.py <path_to_pfdl_file>
```

#### Run the Scheduler
To make use of the scheduler you can import the scheduler class and use it like in the scheduler_demo.py.
We will provide a pip package for the scheduler module later so there is no need to clone the repo anymore.
If you want to run the scheduler from the command line, you can execute the scheduler_demo.py which is a small example program to demonstrate the use of the scheduler class.
Run the following command from the root directory of the project.

```text
    python scheduler_demo.py <path_to_pfdl_file>
```

It will parse the given file and validates it.
If the program is valid a petri net will be generated in the root directory.

## Simple Example

To test your installation you can run a simple PFDL file.
The demo file implements a DemoInterface which uses the Scheduler and serves as demonstration of how to use the Scheduler.
You can view the source code of the whole file here:

??? quote "View Source of `scheduler_demo.py`"
    ```python3 linenums="1"
    """This file contains an interface to demonstrate the use of the PFDL Scheduler."""

    # standard libraries
    import argparse

    # local sources
    from pfdl_scheduler.api.service_api import ServiceAPI
    from pfdl_scheduler.api.task_api import TaskAPI
    from pfdl_scheduler.model.struct import Struct
    from pfdl_scheduler.scheduler import Scheduler, Event


    class DemoInterface:
        """A dummy interface which demonstrates the use of the scheduler functions.

        At start the interface register its callback functions and variable access function
        to the scheduler. The callback functions provide a simple debug message to show
        the functionality of the scheduler.

        Attributes:
            scheduler: A Scheduler instance
            wetness: A dummy variable which is used in the PFDL examples
            parts_count: A dummy variable which is used in the PFDL examples
        """

        def __init__(self, scheduler: Scheduler) -> None:
            """Initialize the object"""
            self.scheduler: Scheduler = scheduler
            self.wetness: int = 11
            self.parts_count: int = 3

        def cb_task_started(self, task_api: TaskAPI) -> None:
            task_name = task_api.task.name
            task_id = task_api.uuid
            print("Task " + task_name + " with UUID '" + task_id + "' started")

        def cb_service_started(self, service_api: ServiceAPI) -> None:
            service_name = service_api.service.name
            service_id = service_api.uuid
            print("Service " + service_name + " with UUID '" + service_id + "' started")

        def cb_service_finished(self, service_api: ServiceAPI) -> None:
            service_name = service_api.service.name
            service_id = service_api.uuid
            print("Service " + service_name + " with UUID '" + service_id + "' finished")

        def cb_task_finished(self, task_api: TaskAPI) -> None:
            task_name = task_api.task.name
            task_id = task_api.uuid
            print("Task " + task_name + " with UUID '" + task_id + "' finished")

        def variable_access_function(self, var_name, task_context: TaskAPI) -> Struct:
            """Simulate a variable access function which returns a Struct variable.

            This dummy method simulates an access to variables from the PFDL. The returned structs
            are used in the examples folder.

            Returns:
                A struct variable corresponding to the given variable name in the given task context.
            """
            print("Request variable '" + var_name + "' from task with UUID '" + task_context.uuid + "'")
            dummy_struct = Struct()

            if var_name == "pr" or var_name == "dr":
                dummy_struct.attributes = {"wetness": self.wetness}
            elif var_name == "cr":
                dummy_struct.attributes = {"parts_count": self.parts_count}
            return dummy_struct

        def start(self):
            self.scheduler.register_callback_task_started(self.cb_task_started)
            self.scheduler.register_callback_service_started(self.cb_service_started)
            self.scheduler.register_callback_service_finished(self.cb_service_finished)
            self.scheduler.register_callback_task_finished(self.cb_task_finished)
            self.scheduler.register_variable_access_function(self.variable_access_function)
            self.scheduler.start()

            while self.scheduler.running:
                input_str = str(input("Wait for input:>"))
                splitted = input_str.split(",")
                service_id = splitted[0]
                event_type = splitted[1]

                event = Event(event_type=event_type, data={"service_id": service_id})
                self.scheduler.fire_event(event)


    def main():
        parser = argparse.ArgumentParser(description="Process some integers.")
        parser.add_argument("file_path", type=str, help="the path for the PFDL file.")
        parser.add_argument(
            "--test_ids",
            action="store_true",
            help="services and tasks get test ids starting from 0.",
        )
        args = parser.parse_args()
        scheduler = Scheduler(args.file_path, args.test_ids)
        demo_interface = DemoInterface(scheduler)
        demo_interface.start()


    if __name__ == "__main__":
        main()
    ```

Within the scheduler_demo.py file the Scheduler is created and started with the given PFDL file.
The start method of the interface registers the callback functions to the Scheduler so they are called when specific events occur.
After the registration the scheduler is started and then executed in a while loop.
In this loop an input to the Scheduler is emulated with the help of Python's input function.
The given event of the user is then fired to the Scheduler.

```python3 linenums="1"
def start(self):
    self.scheduler.register_callback_task_started(self.cb_task_started)
    self.scheduler.register_callback_service_started(self.cb_service_started)
    self.scheduler.register_callback_service_finished(self.cb_service_finished)
    self.scheduler.register_callback_task_finished(self.cb_task_finished)
    self.scheduler.register_variable_access_function(self.variable_access_function)
    self.scheduler.start()

    while self.scheduler.running:
        input_str = str(input("Wait for input:>"))
        splitted = input_str.split(",")
        service_id = splitted[0]
        event_type = splitted[1]

        event = Event(event_type=event_type, data={"service_id": service_id})
        self.scheduler.fire_event(event)
```

There are four methods which serve as callback functions for the scheduler.
The `cb_task_started` method for example gets called when a Task is started in the Scheduler.
A [TaskAPI](../scheduler/api.md#pfdl_scheduler.api.task_api.TaskAPI) object is passed to the function which gives context information about the started Task.
In this simple example the UUID of the started Task and its name are being printed to the console.
The UUID gets created when the Task is started and identifies the specific instance of the Task.
If the same [Task](../scheduler/developer_reference.md#pfdl_scheduler.model.task) is called multiple times, for example in a loop, each instance get a unique ID for identification.
The TaskAPI object consists of the called Task (or: Task definition), the unique ID and the TaskContext which is also a TaskAPI object.
This TaskContext represents the calling Task (can also be none, if the TaskAPI object describes the `productionTask`).

```python3 linenums="1" hl_lines="1-4"
def cb_task_started(self, task_api: TaskAPI) -> None:
    task_name = task_api.task.name
    task_id = task_api.uuid
    print("Task " + task_name + " with UUID '" + task_id + "' started")

def cb_service_started(self, service_api: ServiceAPI) -> None:
    service_name = service_api.service.name
    service_id = service_api.uuid
    print("Service " + service_name + " with UUID '" + service_id + "' started")

def cb_service_finished(self, service_api: ServiceAPI) -> None:
    service_name = service_api.service.name
    service_id = service_api.uuid
    print("Service " + service_name + " with UUID '" + service_id + "' finished")

def cb_task_finished(self, task_api: TaskAPI) -> None:
    task_name = task_api.task.name
    task_id = task_api.uuid
    print("Task " + task_name + " with UUID '" + task_id + "' finished")
```

The `variable_access_function` emulates the variable management of a real system.
As you can see in this dummy function a Struct is created which is filled with a fixed value depending on the requested variable name.
To test the PFDl example files the function creates Struct with reasonable values if the variable names are `pr`, `dr` or `cr` which are all used in the example files.
A real variable access function would look up the variable name in some kind of storage / memory and return the real value of it.

```python3 linenums="1" hl_lines="11-17"
def variable_access_function(self, var_name, task_context: TaskAPI) -> Struct:
    """Simulate a variable access function which returns a Struct variable.

    This dummy method simulates an access to variables from the PFDL. The returned structs
    are used in the examples folder.

    Returns:
        A struct variable corresponding to the given variable name in the given task context.
    """
    print("Request variable '" + var_name + "' from task with UUID '" + task_context.uuid + "'")
    dummy_struct = Struct()

    if var_name == "pr" or var_name == "dr":
        dummy_struct.attributes = {"wetness": self.wetness}
    elif var_name == "cr":
        dummy_struct.attributes = {"parts_count": self.parts_count}
    return dummy_struct
```

Now it is time to test the DemoInterface.
Before you start the Scheduler we explain in short the used PFDL file.
In this simple scenario there is only the service `Painting`.
This service could command a painting machine to paint the piece that is currently on it.
To customize the painting process a `Color` parameter is passed to the service.
The Struct `Color`, which is used as a description for Color variables, consists of the color name and a RGB value in form of an array.
As the painting machine can measure the wetness of the piece, the service will return a `PaintResult` which contains the wetness.
The whole production order starts with the `productionTask` and so from it the Task `paintingTask` is called which executes the `Painting` service.
The example PFDL file looks like the following:

```text linenums="1"
Struct Color
    name: string
    rgb: number[3]
End

Struct PaintResult
    wetness: number
End

Task productionTask
    paintingTask
End

Task paintingTask
    Painting
        In
            Color 
            {
                "name": "green",
                "rgb": [0, 255, 0]
            }
        Out
            pr: PaintResult
End
```

Run the following command to start the scheduler_demo.py file with the simple PFDL example:

```text
    python scheduler_demo.py examples/simple_task.pfdl
```

Now that the scheduler is started a png file with the name "petri_net.png" should have appeared in the temp folder of the project (if there is no temp folder, one will be created).
This file shows the generated Petri net for the PFDL file.
A token should be in the `Painting started` place.

The demo waits for user input.
As it is for testing purposes only, the syntax for firing an event is simplified.
You can copy the UUID of the started service and seperate it with a comma and write `service_finished`.
This will tell the scheduler that the service with the given UUID is finished.
Substitute the UUID with the one of the service and enter the command.

```text
    <uuid of the service>,service_finished
```

After entering this command the token should be in the last place of the petri net as the service has finished now and no other statement is inside the `paintingTask`.
If the scheduler_demo terminates after the command and the token is in the `productionTask_finished` place everything works like it should.

Both states of the petri net are depicted in Figure 1.
On the left you can see the initial petri net after the scheduling starts.
A token is set on the `Painting started` place.
The petri net on the right shows the state after the service is finished.

<div class="figure">
<div class="row">
<div class="column">
<img src="../../img/petri_net_1.png#only-light" alt="Initial Petri Net for the Simple Task example"/>
<img src="../../img/petri_net_1_dark.png#only-dark" alt="Initial Petri Net for the Simple Task example"/>
</div>
<div class="column">
<img src="../../img/petri_net_2.png#only-light" alt="Initial Petri Net for the Simple Task example"/>
<img src="../../img/petri_net_2_dark.png#only-dark" alt="Initial Petri Net for the Simple Task example"/>
</div>
<br><br>
<b>Fig.1:</b> On the left you can see the initial petri net after the scheduling starts.
A token is set on the Painting started place.
The petri net on the right shows the state after the service is finished
<br><br>
</div>
</div>

If everything looks as described you have succesfully run your first PFDL file with the Scheduler!
You can now work on your own PFDL files or start integrating the Scheduler into your projects.
For advanced examples visit the [Examples](../examples/introduction.md) section.