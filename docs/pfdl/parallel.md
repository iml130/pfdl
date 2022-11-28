# Parallel
To exexute Tasks in parallel the `Parallel` keyword is used.
All Tasks within a Parallel block will be executed concurrently by the Scheduler.
The keyword can be used inside a Task and only Tasks are allowed here.

In the example below the productionTask starts the two Tasks `paintingTask` and `cuttingTask` in parallel.

```text linenums="1"
Task productionTask
    Parallel
        paintingTask
        cuttingTask
End

Task paintingTask
    ...
End

Task cuttingTask
    ...
End
```

The Scheduler waits for the finishing of all concurrent Tasks.
Once they are finished the Scheduler continues with the next statements inside the corresponding Task.

If we add a new TaskCall after the Parallel statement in the example above an implicit synchronization is possible.
The new Task `syncTask` will be executed once the Tasks `paintingTask` and `cuttingTask` are finished.

```text linenums="1"
Task productionTask
    Parallel
        paintingTask
        cuttingTask
    syncTask
End

Task paintingTask
    ...
End

Task cuttingTask
    ...
End

Task syncTask
    ...
End

```