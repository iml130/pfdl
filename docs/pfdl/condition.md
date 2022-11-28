# Condition
Because some production steps needs to fulfill conditions sometimes there is a control structure `Condition` for this specific case.
The `Condition` block consists of a `Condition` which includes a boolean expression, a `Passed` block in which instructions are given for the case that the boolean expression evaluates to True.
If the expression is not met the statements inside the `Failed` block are executed.

In the following example the `paintingTask` dries the painted material afterwards by calling the Service `Drying`.
The output of the Service call is saved in a variable `dr` of type `DryingResult` which provides information about the wetness of the paint.
If the wetness in form of a number value is below a certain threshold (here: 10) the Task should continue with the next production steps, otherwise it dries again.

The `Failed` block is optional: You can omit it and if the condition is not met the scheduler will execute the next statement after the `Condition` block.

```text linenums="1"
Struct DryingResult
   wetness: number
End

Task paintingTask
    ...
    Drying
        Out
            dr: DryingResult

    Condition
        dr.wetness < 10
    Passed
        ... # continue 
    Failed
        Drying
            In
                dr
            Out
                dr: DryingResult
End
```