<!--
SPDX-FileCopyrightText: The PFDL Contributors
SPDX-License-Identifier: MIT
-->
<div align="center">
  
Production Flow Description Language
===========================
<img src="https://github.com/iml130/pfdl/blob/main/docs/img/pfdl_logo_without_font.png?raw=true" alt="pfdl_logo" width="600"/>
<br><br>

![Tests](https://github.com/iml130/pfdl/actions/workflows/tests.yml/badge.svg?branch=main)
![Lint Check](https://github.com/iml130/pfdl/actions/workflows/lint.yml/badge.svg?branch=main)
![Code Coverage](https://github.com/iml130/pfdl/actions/workflows/code_coverage.yml/badge.svg?branch=main)
![Build and deploy Docu](https://github.com/iml130/pfdl/actions/workflows/build_and_deploy_docu.yml/badge.svg?branch=main)
[![REUSE status](https://api.reuse.software/badge/github.com/iml130/pfdl)](https://api.reuse.software/info/github.com/iml130/pfdl)

**DISCLAIMER**:
This project is not intended for everyday use and made available without any support.
However, we welcome any kind of feedback via the issue tracker or by e-mail.
</div>

---
<div align="left">

The **P**roduction **F**low **D**escription **L**anguage (**PFDL**) is a domain specific language for the description of production orders in the manufacturing of the future.
With the help of the PFDL customized products and their production steps can be described.

This project consists of the PFDL Grammar and Scheduler.
The Scheduler is the main part of the language. It parses PFDL files and generates a Petri net for scheduling the production task if the given file is valid.

For more infos visit the official :books: [Documentation](https://iml130.github.io/pfdl/).

## Requirements
- Pip packages from requirements.txt (`pip install -r requirements.txt`)
- [GraphViz](https://graphviz.org/) (if you want to use the scheduler/run the scheduler_demo.py)

## How to Start

### Validation
If you just want to validate your PFDL files run the following command from the root directory of the project.
All errors will be printed in the console, so if nothing is shown the file valid.
> python validate_pfdl_file.py --file_path <path_to_pfdl_file>

You can also use the flag --folder_path to check all PFDL files within a folder.

### Scheduler
To make use of the scheduler you can import the scheduler class and use it like in the scheduler_demo.py.
We will provide a pip package for the scheduler module later so there is no need to run it anymore.
If you want to run the scheduler from the command line, you can execute the scheduler_demo.py which is a small example program to demonstrate the use of the scheduler class.
Run the following command from the root directory of the project.
> python scheduler_demo.py <path_to_pfdl_file>

It will parse the given file and validates it. If the program is valid a petri net will be generated in the root directory.

## Tests
We also provivde unit tests e.g. for the static semantic validaton methods. To run all the test files you can use a testing environment (e.g. Testing in VSCode) or just execute the following command in the projects root directory:
> python -m unittest discover -v

## Use the PFDL Scheduler as Submodule
If you want to use the PFDL Scheduler in your existing project you can use this project as a submodule.
To run the Scheduler succesfully from your python code you have to add the pfdl_scheduler folder to the sys path somewhere before using (importing) it:

```python
import sys
import os
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, currentdir + "/pfdl_scheduler")

# you can use the PFDL Scheduler classes now
from pfdl_scheduler.scheduler import Scheduler
```

## Troubleshooting
No PetriNet is generated / there is an error while generating the net
> Check if you correctly installed GraphViz (On Windows you need to put the bin folder inside the GraphViz folder into the PATH environment variable. On Ubuntu it should be fine if you install GraphViz via apt-get)

## License
PDFL is licensed under the MIT License. See [LICENSE](https://github.com/iml130/pfdl/blob/main/LICENSE) for details on the licensing terms.

## Academic Attribution
If you use the PFDL for research, please include the following reference in any resulting publication.

- [PFDL: A Production Flow Description Language for an Order-Controlled Production](https://doi.org/10.23919/ICCAS55662.2022.10003953)
```plain
@INPROCEEDINGS{PFDL_Detzner_2022,
  author={Detzner, Peter and Ebner, Andreas and Hörstrup, Maximilian and Kerner, Sören},
  booktitle={2022 22nd International Conference on Control, Automation and Systems (ICCAS)}, 
  title={PFDL: A Production Flow Description Language for an Order-Controlled Production}, 
  year={2022},
  volume={},
  number={},
  pages={1099-1106},
  doi={10.23919/ICCAS55662.2022.10003953}}
```
