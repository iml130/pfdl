# Comments

A comment starts with a hash character (`#`) that is not part of a string literal, and ends at the end of the physical line.
That means a comment can appear on its own or at the end of a statement.
In-line comments are not supported.

This example shows a mimicked multi-line comment that consists of three `#` that are joined together:

```text linenums="1"
###
# This task shows the usage of comments
###
Task paintingTask
	Painting
		In
            # Represents a color
            Color
			{
				"name": "green",
				"rgb": [0, 255, 0]
			}
        # Task output
		Out
			pr: PaintingResult
End # End of the task
```