# Control structures

## Condition
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
   Painting
        In
            Color 
            {
                "name": "green",
                "rgb": [0, 255, 0]
            }
        Out
            pr: PaintingResult

    Condition
        pr.wetness > 10
    Passed
        Drying
            In
                pr
End
```

## Counting loop
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
    Cutting
        Out
            cr: CuttingResult
    Loop i To cr.parts_count
        Milling
            cr.sheet_parts[i]
End
```

## While loop
```text linenums="1"
Struct Color
    name: string
    rgb: number[3]
End

Struct PaintingResult
    wetness: number
End

Task productionTask
    Painting
        In
            Color 
            {
                "name": "green",
                "rgb": [0, 255, 0]
            }
        Out
            pr: PaintingResult

    Loop While pr.wetness > 10
        Drying
            In
                pr
            Out
                pr: PaintingResult
End
```