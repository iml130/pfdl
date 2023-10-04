<!--
SPDX-FileCopyrightText: The PFDL Contributors
SPDX-License-Identifier: MIT
-->
<style>
.figure_1{
    width: 60%;
    display: block;
    margin-left: auto;
    margin-right: auto;
}
.figure_2{
    width: 80%;
    display: block;
    margin-left: auto;
    margin-right: auto;
}
</style>


# The Production Flow Description Language
The main building blocks of a PFDL program are *Structs* and *Tasks*. Within the task different statements can be executed like a *Service call* or control structures like loops, conditions, concurrency and synchronization.

## Formal Grammar
In the following we present you the formal grammar of the PFDL.
The grammar definiton can be consulted to understand the syntax.

This grammar is a simplified representation of a context free grammar.
Terminal symbols are represented in bold.
Parentheses indicate an optional usage while the pipe symbol `|` denotes a choice. 
Entities that are overlined can be repeated zero, one or more times.
An overline with a plus sign was added in addition which implicates a repetition of at least one or more.

<div class="figure_1">
<img src="../../img/formal_grammar.png#only-light" alt="Formal grammar of the PFDL"/>
<img src="../../img/formal_grammar_dark.png#only-dark" alt="Formal grammar of the PFDL"/>
<br><br>
<b>Fig. 1:</b> The formal grammar of the Production Flow Description Language (PFDL).

<br><br>
</div>



## PFDL Overview

The following figure depicts the formal grammar above graphically.
A visual representation of the different functionalities is followed by the corresponding code snippets in the PFDL.

<div class="figure_2">
<img src="../../img/pfdl_overview.png#only-light" alt="pfdl_overview"/>
<img src="../../img/pfdl_overview_dark.png#only-dark" alt="pfdl_overview"/>
<br><br>
<b>Fig. 2:</b> A summary of the different building blocks of the PFDL. The left side visualises the functionality while the right side is the corresponding PFDL code snippet.

<br><br>
</div>

## Allowed Characters
Most of the correct syntax can be obtained from the formal grammar above.
In the following sections we will explain the correct syntax for the different building blocks of the language (Structs, Tasks, etc.).

We use the terms lower- and uppercase strings definied as followed in the different sections:

**Lowercase String**: starts with a lowercase char and after that you can use every letter, number and the char '_'. Regular Expression: `[a-z][a-zA-Z0-9_]*`

**Uppercase String**: same as lowercase, except for an uppercase char at the beginning. Regular Expression: `[A-Z][a-zA-Z0-9_]*`