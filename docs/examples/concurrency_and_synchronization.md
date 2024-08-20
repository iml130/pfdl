<!--
SPDX-FileCopyrightText: The PFDL Contributors
SPDX-License-Identifier: MIT
-->
# Concurrency and Synchronization

As already stated in the [parallel](../pfdl/parallel.md) section, there is no keyword for the synchronization. The next statement after a parallel block is only started if all concurrently running tasks are finished.

The following example demonstrates the use of the parallel keyword and the implicit synchronization.

```text linenums="1"
Struct Color
    name: string
    rgb: number[3]
End

Struct PaintingResult
    wetness: number
End

Struct SheetPart
    width: number
    length: number
End

Struct CuttingResult
    parts_count: number
    sheet_parts: SheetPart[]
End

Task productionTask
    # Execute paintingTask and cuttingTask in Parallel
    Parallel
        paintingTask
        cuttingTask

    # gets started when paintingTask and cuttingTask are finished
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

Task cuttingTask
    Cutting
        Out
            cr: CuttingResult
End
```