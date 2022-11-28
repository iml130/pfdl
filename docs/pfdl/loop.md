# Loop
To execute statements for a specified number of repetitions, the usage of the `Loop` keyword is required.
There are two types of loops available: Counting Loops and While Loops.

## While Loop

While loops can be defined by adding the keyword `While` and an boolean expression after the `Loop` keyword.

```text linenums="1"
Struct Color
    name: string
    rgb: number[3]
End

Struct PaintingResult
    wetness: number
End

Struct DryingResult
   wetness: number
End

Task productionTask
    paintAndCutTask
End

Task paintAndCutTask
    ...

    Loop While dr_1.wetness > 5
        Drying
            In
                dr_1
            Out
                dr_1: DryingResult
End
```


## Counting Loop

To define a counting loop one have to specify a counting variable followed by the keyword `To` and a number (fixed value or variable) to define the counting limit.

```text linenums="1"
...
Struct SheetPart
    width: number
    hight: number
End

Struct CuttingResult
    parts_count: number
    sheet_parts: SheetPart[]
End

Task paintAndCutTask
    ...

    Loop i To cr.parts_count
        millingTask
            In
                cr.sheet_parts[i]
End

Task millingTask
    In 
        part_in: SheetPart
    Milling
        In
            part_in
End
```

### Parallel keyword in Counting Loop
If you want to iterate over the elements of an array and a (partial) job has to be executed in parallel for each element, the parallel keyword can be written before a counting loop.
This starts as many jobs in parallel as there would be loop iterations.
This is a supplement to the parallel keyword, as only a fixed number of orders can be started in parallel.
However, it can only be known at runtime how many jobs have to be started in parallel.
The example below shows the usage of the parallel loop.
The task `task_1` is started as many times as there are parts.

```text linenums="1"
Task parallel_task
    ...

    Parallel Loop i To cr.parts_count
        task_1
            In
                cr.sheet_parts[i]
End
```