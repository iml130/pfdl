# Service

A Service in the PFDL corresponds to a service in a service oriented architecture.
In the context of production and manufacturing a Service-call can be used to invoke a service of a field device of the factory floor. 

It is important to note that the Service-call within the PFDL file can be mapped to every service that is avaiable.
Due to the scheduler it is possible to pass input into the scheduler.
After the scheduling starts for each defined service inside the PFDL file a [UUID](https://datatracker.ietf.org/doc/html/rfc4122) is generated. 
This UUID can be used to map the "logical" service to the real service.
For example: You specify a Service "Painting" inside the PFDL file.
You can know decide to which of your own services this logical Service corresponds.
If you register a callback function you get notified when Services starts and receive the logical name of the started service.

A Service-call in the PFDL looks like the following:
```text linenums="1"
<Service name>
    In
        <input parameters>
    Out
        <output parameters>
```

The service parameters can be either passed directly via a struct instantiation in a JSON-manner or by passing a variable name, which refers to an already defined and instantiated struct.
Values that are returned by a Service-call can be stored in a struct.
Consequently, an output of a service call can be the the input for the next service.

A real example of a Service-call is shown below. The service `Painting` is invoked with a parameter from type `Color`. This is an exmaple for the initialization in a JSON-manner.
The ouput of the service will be saved in a variable `pr` of type `PaintingResult`.

```text linenums="1"
Painting
    In
        Color
        {
            "name": "green",
            "rgb": [0, 255, 0]
        }
    Out
        pr : PaintingResult
```

**Note**: Every statement within a task that starts with an Uppercase character is assumed to be a Service-call. There is no additional keyword to specifiy a Service-call.