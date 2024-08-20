<!--
SPDX-FileCopyrightText: The PFDL Contributors
SPDX-License-Identifier: MIT
-->
# Structs

A struct is a collection of variables.
PFDL is strongly typed, where each variable of a struct has a name as an identifier and a designated data type.
The supported data types are equal to [JSON’s](https://www.json.org/json-en.html) data types: string, number, boolean, and arrays.
Structs can be used to define the input and output of Service-calls as well as Task-calls.

The following example shows a simple struct definition.
The struct `Color` has 2 attributes, `name` and `rgb`.

As already explained, Arrays are also a possible type for struct attributes.
In the example below the type of attribute `rgb` is an number array with fixed size 3.
It is also possible to omit the number for dynmaic arrays (e.g. a service returns a struct with an dynamic array).

```text linenums="1"
Struct Color
    name: string
    rgb: number[3]
End
```

## Composition
Attributes of structs can also have other Structs as type.
This allows a composition and reuse of other structs inside a struct.

In the following example the Struct `CuttingResult` has an attribute `sheet_parts` which is a dynamic array of type `SheetPart`.
In this example scenario a machine cut a piece in multiple parts with different sizes and it is only known at runtime how many parts there will be.

```text linenums="1"
Struct SheetPart
    width: number
    height: number
End

Struct CuttingResult
    parts_count: number
    sheet_parts: SheetPart[]
End
```

## Instantiation
Structs must be instantiated in the form of a JSON object.
You can also create JSON objects inside this instantiation to create composite structs.

```text linenums="1"
Color
{
    "name": "green",
    "rgb": [0, 255, 0]
}

# nested struct creation
CuttingResult
{
    "parts_count": 2,
    "sheet_parts": [
        {
            width: 5,
            length: 10,
            height: 3
        },
        {
            width: 5,
            length: 5,
            height: 3
        }
    ]
}
```