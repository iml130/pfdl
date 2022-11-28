# Task
A Task is an executable unit which executes the statements within sequentially.
The name of the Task should be a [lowercase string](../#allowed-characters).

## The Production Task
A Task with the name `productionTask` serves as the starting point of the production order.
Every PFDL program has to define this Task.
This is comparable to a main method in conventional programming languages.
The examples below show the use of such a Task.


## Call a Task
Tasks can be called within other Tasks just like Service calls. In the example below the `productionTask` calls the Task `paintingTask` which executes the Service `Painting`.
```text linenums="1"
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
			pr: PaintingResult
End
```

## Input and Output of Tasks
When Tasks are called they can receive input parameters and return an output too (just like [Services](service.md)).
This can be used to transfer variables from one Task to another.
Variables are always bound to a Service so with this functionality it is possible to use a variable from one Task in other Tasks.

The input must be defined at the start of a Task definition with the keyword `In`.
Afer the `In` keyword one can insert an arbitrary amount of variable definitions, consisting of the variable name that is used within the Task and its type.

The output must be defined at the end of a Task definition with the keyword `Out`.
Only variable names known in the Tasks can be used here per line as output of the Task.

In the following example the Task `paintingTask` defines an input and an output.
The input variable `paint_color` must be of type `Color`.
After the Service `Painting` is finished we receive a variable `pr` of type `PaintingResult`.
This variable is defined as the output of the Task.
The `productionTask` calls the Task `paintingTask` and instantiates a `Color` variable which serves as the input.
The output is defined in the variable `pr` of type `PaintingResult`.

**Note:** Variable `pr` has the same name and the same value as in `paintingTask` but technically they are two different variables.
```text linenums="1"
Task productionTask
	paintingTask
		In
			Color 
			{
				"name": "green",
				"rgb": [0, 255, 0]
			}
		Out
			pr: PaintingResult
End

Task paintingTask
	In
		paint_color: Color
	Painting
		In
			paint_color
		Out
			pr: PaintingResult
	Out
		pr
End
```