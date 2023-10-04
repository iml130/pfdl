<!--
SPDX-FileCopyrightText: The PFDL Contributors
SPDX-License-Identifier: MIT
-->
<style>
.figure{
    width: 100%;
    display: block;
    margin-left: auto;
    margin-right: auto;
}
</style>

# Architecture
The next sections are both for users of the PFDL Scheduler and for those who want to work on the Scheduler itself.
Thus, in the following the basic architecture of the Scheduler will be explained as well as things like the [CI/CD pipeline](ci_cd.md).
If you just want to look up terms used in this docu refer to the [Glossary](glossary.md).

To better understand the architecture of the PFDL and its scheduler we will explain the main concepts and systems in the following.
The overall architecture consisting of the PFDL Scheduler and a so called [Execution Engine (EE)](#execution-engine) is depicted in the figure below.
The EE is developed in parallel to the Scheduler and is used for direct control of the [Field Devices](#field-level-devices) on the factory floor.

<div class="figure">
<img src="../../img/pfdl_architecture_overview.png#only-light" alt="Architecture overview of the whole system"/>
<img src="../../img/pfdl_architecture_overview_dark.png#only-dark" alt="Architecture overview of the whole system"/>
<br><br>
<b>Fig.1:</b> An overview of the PFDL architecture.
A PFDL file serves as the input for the Scheduler which processes it and transforms it in an internal representation.
This is used to interact with the execution engines.
<br>
</div>

## Parsing
The PFDL file is the input for the PFDL interpreter, which consists of the **Lexer** and **Parser**.
The grammar of the PFDL is implemented with [ANTLR](http://antlr.org) and the **Lexer** and **Parser** are generated from the ANTLR grammar specification files.

The generated parse tree from the **Parser** serves as input to the **Visitor** which traverses the given tree and generates the PFDL domain model from it.
A shortened UML class diagram of the domain model is shown in the figure below.

## Model creation and validation
<div class="figure">
<img src="../../img/pfdl_domain_model.png#only-light" alt="pfdl_domain_model"/>
<img src="../../img/pfdl_domain_model_dark.png#only-dark" alt="pfdl_domain_model"/>
<br><br>
<b>Fig.2:</b> The domain model of PFDL files. The main class is the Process class which represents the production process described by the PFDL file.

<br><br>
</div>

This model can be checked for static semantic errors (errors that were not found while parsing) by the **Semantic Validation** unit.

## Petri Net generation an execution
If the validation is passed the model gets converted into a Petri Net by the **Petri Net Generator**.
This structure represents the production order as a formal description.
Note that the transformation into a Petri Net is only one of many possible ways to transform the model.

The scheduler provides interfaces for interaction with the Petri net.
The **Petri Net Logic** unit takes care of the evaluation of the petri net and the firing of events into it.
You can register callback functions which will be called when specific states in the net are reached (e.g: a specific service has started or finished). It is also possible to pass Events to the Scheduler, e.g. when a service finished its execution. The net will then evaluate its state and call the corresponding callback functions for the new state.

## Dashboard Connection
It is possible to connect the Scheduler with a Dashboard.
This will add the corresponding Production Order to the Dashboard when the Scheduler is started.
Now, all updates of the order are visualized in real time.

To enable this functionality, an address to the dashboard can be passed to the `Scheduler` class.
If such an address is given, the Scheduler will send log messages (e.g. Task started, Service finished, ...), Petri Net updates, and order updates to the corresponding address.
You can, however, also send messages to the dashboard from outside of the scheduler.
The API specification can be found in the [Dashboard API](../scheduler/dashboard.md) section.
**Note:** Currently, our Dashboard is not open source, but you could also write your own visualization if you stick to the API specification.

## Execution Engine
The **Execution Engine (EE)** provides an interface that connects the PFDL Scheduler to the Field Level Devices.
Our approach implements the EE as an OPC UA Server, however, the concept of the EE is not OPC UA specific and can be transferred to different implementation approaches.  
Since the Scheduler works with a petri net at the moment, the EE is launched with the start of the petri net execution, executes the scheduled services on the field level and is shut down as soon as the petri net reaches its last place.
In this context, the EE offers several functionalities: Besides providing an interface to both, the field level resources and the PFDL Scheduler, it features a Data Lifecycle Object that handles the data management during the petri net execution.
As the PFDL allows to define task specific variables, condition blocks based on runtime data, as well as input and output variables for services, the Data Lifecycle Object enriches the defined variables from the PFDL with the runtime data received from the Field Level.
In consequence, the PFDL Scheduler is able to access this data by requesting it from the Data Lifecycle Object.
Lastly the EE contains a functionality to assign services to resources in case of several resources offering identical services.

The Execution Engine - PFDL Scheduler interface is based upon callback functions that are provided by the PFDL Scheduler. From these callbacks, the EE receives information about the tasks and services that are currently scheduled. Besides, it enables the Execution Engine to initiate transitions of the Petri Net by placing tokens in it. As the Execution Engine contains the runtime data from a Petri Net Execution, the Execution Engine - PFDL Scheduler interface enables the Scheduler to access this data. 

The Execution Engine – Device Interface enables the communication between the Execution Engine and Field Level Devices and ultimately facilitates the execution of Services that are scheduled by the PFDL Scheduler. This Communication is not bound to any communication protocol, but can feature different protocols. As our approach to the Execution Engine is implemented as an OPC UA Server, we use OPC UA Clients to communicate with Field Level Devices. However, other communication protocols, such as MQTT, can be implemented.

### Data Lifecycle Object
The Data Lifecycle Object manages the runtime data that is required during the execution of one PFDL file.
It is dynamic, which allows variables and tasks defined in the PFDL to be instantiated, updated and deleted during runtime.
As soon as a task is started, it is added as a task object to the data lifecycle object. Since tasks are nested, each new task provides a task context which identifies the location of this task in the Data Lifecycle structure.
With these context references, the data lifecycle object aggregates a tree of tasks, whose root is the production task.
Each new added task object either extends an existing branch of task objects or creates a new one. 

To declare task specific variables, data types for all Structs, which are defined within a PFDL file, have to be added to the Execution Engine.
In addition, these data types are used for the parameterization of a service.
As soon as a variable appears in a PFDL task, the data lifecycle object uses the corresponding data type to instantiate the variable.
Once instantiated, the variable values are updated in accordance to the Petri Net execution.
In general, two different levels of variable declaration have to be distinguished.
First, there are variables that are defined on the level of the production task.
These variables exist while the execution of the Petri Net is in progress.
One instantiated, their values are only updated and they will never be deleted.
Second, there are variables that are defined on levels atop of the production task.
These variables are the input for concrete services or other tasks and disappear from the data lifecycle object after the completion of the task, which instantiates them.
Before deletion, they can consign their values to a task on the aggregation level below.

### Field Level Devices
The Field level constitutes the lowest level of the automation pyramid and captures all kind of devices that are found in industrial manufacturing systems.
These devices are either sensors or actors and directly influence processes by measuring data or performing an arbitrary step of a manufacturing process.