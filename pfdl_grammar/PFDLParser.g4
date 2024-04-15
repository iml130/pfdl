parser grammar PFDLParser;

options {
    tokenVocab = PFDLLexer;
}

program:
    (NL | struct | task)* EOF;

struct:
    STRUCT STARTS_WITH_UPPER_C_STR INDENT (variable_definition NL+)+ DEDENT END;

task:
    TASK STARTS_WITH_LOWER_C_STR INDENT task_in? statement+ task_out? DEDENT END;

task_in:
    IN INDENT (variable_definition NL+)+ DEDENT;

task_out:
    OUT INDENT (STARTS_WITH_LOWER_C_STR NL+)+ DEDENT;

statement:
    service_call 
    | task_call
    | parallel
    | while_loop
    | counting_loop 
    | condition;

service_call:
    STARTS_WITH_UPPER_C_STR NL+
    | STARTS_WITH_UPPER_C_STR INDENT call_input? call_output? DEDENT;

task_call:
    STARTS_WITH_LOWER_C_STR NL+
    | STARTS_WITH_LOWER_C_STR INDENT call_input? call_output? DEDENT;

call_input:
    IN INDENT (parameter NL+ | struct_initialization)+ DEDENT;

call_output:
    OUT INDENT (variable_definition NL+)+ DEDENT;

parallel:
    PARALLEL INDENT task_call+ DEDENT;

while_loop:
    LOOP WHILE expression INDENT statement+ DEDENT;

counting_loop:
    PARALLEL? LOOP STARTS_WITH_LOWER_C_STR TO (attribute_access | INTEGER) INDENT statement+ DEDENT;

condition:
    CONDITION INDENT expression NL+ DEDENT condition_passed condition_failed?;

condition_passed:
    PASSED INDENT statement+ DEDENT;

condition_failed:
    FAILED INDENT statement+ DEDENT;

parameter:
    STARTS_WITH_LOWER_C_STR
    | attribute_access;

struct_initialization:
    STARTS_WITH_UPPER_C_STR INDENT json_object NL+ DEDENT
    | STARTS_WITH_UPPER_C_STR NL* json_object NL*;

variable_definition:
    STARTS_WITH_LOWER_C_STR COLON variable_type;

variable_type: primitive array?;

primitive:
    NUMBER_P
    | STRING_P
    | BOOLEAN_P
    | STARTS_WITH_UPPER_C_STR;

attribute_access:
    STARTS_WITH_LOWER_C_STR (DOT STARTS_WITH_LOWER_C_STR array?)+;

array:
    ARRAY_LEFT (INTEGER | STARTS_WITH_LOWER_C_STR)? ARRAY_RIGHT;

number:
    INTEGER
    | FLOAT;

value:
    TRUE 
    | FALSE
    | number
    | STRING
    | attribute_access;

expression:
    LEFT_PARENTHESIS expression RIGHT_PARENTHESIS
    | expression STAR expression
    | expression SLASH expression
    | expression MINUS expression
    | expression PLUS expression
    | expression binOperation expression
    | unOperation expression
    | expression BOOLEAN_AND expression
    | expression BOOLEAN_OR expression 
    | value;

binOperation:
    LESS_THAN
    | LESS_THAN_OR_EQUAL
    | GREATER_THAN
    | GREATER_THAN_OR_EQUAL
    | EQUAL
    | NOT_EQUAL;

unOperation:
    BOOLEAN_NOT;

// Rules for JSON Objects
json_object:
    json_open_bracket pair (JSON_COMMA pair)* JSON_CLOSE
    | json_open_bracket JSON_CLOSE;

pair:
    JSON_STRING JSON_COLON json_value;

json_open_bracket:
    JSON_OPEN | JSON_OPEN_2;

json_value:
   JSON_STRING
   | JSON_TRUE
   | JSON_FALSE
   | NUMBER
   | json_object
   | json_array;

json_array
   : JSON_ARRAY_LEFT json_value (JSON_COMMA json_value)* JSON_ARRAY_RIGHT
   | JSON_ARRAY_LEFT JSON_ARRAY_RIGHT;
