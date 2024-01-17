lexer grammar PFDLLexer;

// DenterHelper for generating INDENT AND DEDENT tokens to realize a python-like grammar with
// Indentations

tokens {
	INDENT,
	DEDENT
}

@lexer::header {
from antlr_denter.DenterHelper import DenterHelper
from PFDLParser import PFDLParser
}
@lexer::members {
class PFDLDenter(DenterHelper):
    def __init__(self, lexer, nl_token, indent_token, dedent_token, ignore_eof):
        super().__init__(nl_token, indent_token, dedent_token, ignore_eof)
        self.lexer: PFDLLexer = lexer

    def pull_token(self):
        return super(PFDLLexer, self.lexer).nextToken()

denter = None

def nextToken(self):
    if not self.denter:
        self.denter = self.PFDLDenter(self, self.NL, PFDLLexer.INDENT, PFDLLexer.DEDENT, ignore_eof=False)
    return self.denter.next_token()
}

// Main grammar
STRUCT: 'Struct';
TASK: 'Task';
IN: 'In';
OUT: 'Out';
LOOP: 'Loop';
WHILE: 'While';
TO: 'To';
PARALLEL: 'Parallel';
CONDITION: 'Condition';
PASSED: 'Passed';
FAILED: 'Failed';
ON_DONE: 'OnDone';
END: 'End';
NUMBER_P: 'number';
STRING_P: 'string';
BOOLEAN_P: 'boolean';
TRUE: 'true';
FALSE: 'false';

COLON: ':';
DOT: '.';
COMMA: ',';
JSON_OPEN: '{' -> pushMode(JSON);

QUOTE: '"';

ARRAY_LEFT: '[';
ARRAY_RIGHT: ']';

COMMENT: '#' ~[\n]* -> skip;
WHITESPACE: [ \t]+ -> skip;
NL: ('\r'? '\n' ' '*);

LEFT_PARENTHESIS: '(';
RIGHT_PARENTHESIS: ')';
LESS_THAN: '<';
LESS_THAN_OR_EQUAL: '<=';
GREATER_THAN: '>';
GREATER_THAN_OR_EQUAL: '>=';
EQUAL: '==';
NOT_EQUAL: '!=';
BOOLEAN_AND: 'And';
BOOLEAN_OR: 'Or';
BOOLEAN_NOT: '!';
STAR: '*';
SLASH: '/';
MINUS: '-';
PLUS: '+';

INTEGER: [0-9]+;
FLOAT: INTEGER '.' INTEGER;

STRING: '"' ('\\"' | .)*? '"';
STARTS_WITH_LOWER_C_STR: [a-z][a-zA-Z0-9_]*;
STARTS_WITH_UPPER_C_STR: [A-Z][a-zA-Z0-9_]*;

// JSON Grammar
mode JSON;

JSON_STRING: '"' ('\\"' | .)*? '"';
JSON_TRUE: 'true';
JSON_FALSE: 'false';

JSON_COLON: ':';
JSON_QUOTE: '"';

JSON_COMMENT: '#' ~[\n]+ -> skip;

JSON_ARRAY_LEFT: '[';
JSON_ARRAY_RIGHT: ']';

JSON_COMMA: ',';

NUMBER: '-'? INT ('.' [0-9]+)? EXP?;

fragment INT: '0' | [1-9] [0-9]*;

// no leading zeros

fragment EXP: [Ee] [+\-]? INT;

WS: [ \t\n\r]+ -> skip;

JSON_OPEN_2: '{' -> pushMode(JSON);
JSON_CLOSE: '}' -> popMode;
