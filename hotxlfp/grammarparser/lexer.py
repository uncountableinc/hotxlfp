# -*- coding: utf-8 -*-
import ply.lex as lex
from ..formulas import error, dispatcher
import re

tokens = (
    'SCIENTIFIC_NOTATION_E',
    'STRING',
    'FUNCTION',
    'FUNCTION_3ARGS',
    'XLERROR',
    'ABSOLUTE_CELL',
    'MIXED_CELL',
    'RELATIVE_CELL',
    'VARIABLE',
    'NUMBER',
    'LBRACKET',
    'RBRACKET',
    'AMP',
    'DECIMAL',
    'COLON',
    'SEMICOLON',
    'COMMA',
    'BACKSLASH',
    'MULT',
    'DIV',
    'MINUS',
    'PLUS',
    'CARET',
    'LPAREN',
    'RPAREN',
    'GREATER',
    'LESS',
    'GREATEREQ',
    'LESSEQ',
    'NOTEQUAL',
    'EQUAL',
    'PERCENT',
)



def t_SCIENTIFIC_NOTATION_E(t):
    r'(?<=\d)\s*[eE]\s*(?=\-?\s*?\.?\d)'  # Lookahead to not confuse with variables and functions
    return t


def t_WHITESPACE(t):
    r'\s+'
    pass  # Ignore whitespace


def t_STRING(t):
    r'"(\\["]|[^"])*"|\'(\\[\']|[^\'])*\''
    return t

available_functions = dispatcher._registry_.keys()
fixed_argument_functions_mapping = {
    3: ["IF"]
}
fixed_argument_functions = {function for functions in fixed_argument_functions_mapping.values() for function in functions}
fixed_argument_functions_mapping[None] = [function for function in available_functions if function not in fixed_argument_functions]

def _build_n_args_function_regex(num_arguments):
    function_options = '|'.join(
        f'({re.escape(function)})' for function in fixed_argument_functions_mapping[num_arguments])
    lookahead = '(?=\s*[(])'
    return f"({function_options}){lookahead}"

@lex.TOKEN(_build_n_args_function_regex(None))
def t_FUNCTION(t):
    return t

@lex.TOKEN(_build_n_args_function_regex(3))
def t_FUNCTION_3ARGS(t):
    return t


def t_XLERROR(t):
    r'\#[A-Z0-9\/]+(\!|\?)?'
    return t


def t_ABSOLUTE_CELL(t):
    r'\$[A-Za-z]+\$[0-9]+'
    return t


def t_MIXED_CELL(t):
    r'(\$[A-Za-z]+[0-9]+)|([A-Za-z]+\$[0-9]+)'
    return t


def t_RELATIVE_CELL(t):
    r'[A-Za-z]+[0-9]+'
    return t


def t_VARIABLE(t):
    r'([A-Za-z]{1,}[A-Za-z_0-9]+)|([A-Za-z_]+)'
    return t


def t_NUMBER(t):
    r'[0-9]+'
    return t


def t_LBRACKET(t):
    r'\{'
    return t


def t_RBRACKET(t):
    r'\}'
    return t


def t_AMP(t):
    r'\&'
    return t


def t_SINGLESPACE(t):
    r'\ '
    return t


def t_DECIMAL(t):
    r'\.'
    return t


def t_COLON(t):
    r'\:'
    return t


def t_SEMICOLON(t):
    r'\;'
    return t


def t_COMMA(t):
    r'\,'
    return t


def t_BACKSLASH(t):
    r'\\'
    return t


def t_MULT(t):
    r'\*'
    return t


def t_DIV(t):
    r'\/'
    return t


def t_MINUS(t):
    r'\-'
    return t


def t_PLUS(t):
    r'\+'
    return t


def t_CARET(t):
    r'\^'
    return t


def t_LPAREN(t):
    r'\('
    return t


def t_RPAREN(t):
    r'\)'
    return t


def t_NOTEQUAL(t):
    r'\<\>'
    return t


def t_GREATEREQ(t):
    r'\>\='
    return t


def t_LESSEQ(t):
    r'\<\='
    return t


def t_GREATER(t):
    r'\>'
    return t


def t_LESS(t):
    r'\<'
    return t


def t_QUOTATION(t):
    r'\"'
    return t


def t_APOSTROPHE(t):
    r'\''
    return t


def t_EXCLAMATION(t):
    r'\!'
    return t


def t_EQUAL(t):
    r'\='
    return t


def t_PERCENT(t):
    r'\%'
    return t


def t_HASH(t):
    r'\#'
    return t


def t_error(t):
    raise error.NAME


def build():
    return lex.lex()
