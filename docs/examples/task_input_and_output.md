# Task input and output

Tasks can define an Input and an Output to pass data when calling each other.
The following examples demonstrate both cases.

## Task input
In this example the Task `paintingTask` calls the Service `Painting` which returns a `PaintingResult`.
The other Task `cuttingTask` calls a Service `Cutting` which needs a `PaintingResult` as input.
To pass the variable `pr` from one Task to the other, `cuttingTask` defines in lines 41-42 a possible input.
This Task is called in the lines 35-37 by the `paintingTask` with parameter `pr`.

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
    hight: number
End

Struct CuttingResult
    parts_count: number
    sheet_parts: SheetPart[]
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
            pr: PaintingResult

    cuttingTask
        In
            pr
End

Task cuttingTask
    In
        pr: PaintingResult

    Cutting
        In
            pr
        Out
            cr: CuttingResult
End
```

## Task output
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
    hight: number
End

Struct CuttingResult
    parts_count: number
    sheet_parts: SheetPart[]
End

Task productionTask
    cuttingTask
End

# cuttingTask calls paintingTask and uses the output in Cutting
Task cuttingTask
    paintingTask
        Out
            pr: PaintResult

    Cutting
        In
            pr
        Out
            cr: CuttingResult
End

Task paintingTask
    Painting
        In
            Color
                {
                    "name": "green",
                    "saturation": 5,
                    "rgb": [0, 255, 0]
                }
        Out
            pr: PaintingResult

    Out
        pr
End
```