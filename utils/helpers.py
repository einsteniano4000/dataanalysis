import ast
import math
import operator
import re

import numpy as np
from sympy import sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, exp, log, sqrt, cbrt, Abs, sympify, pi as sympy_pi, E as sympy_e

# NOTA IMPORTANTE: qui NON si usa sympy.parse_expr/sympify su stringhe non
# fidate. parse_expr esegue una eval() interna e alcune sue trasformazioni
# (es. lambda_notation) possono eseguire codice arbitrario anche impostando
# global_dict['__builtins__'] = {} (verificato: "exec('...')" viene comunque
# eseguito). L'unico modo sicuro di valutare un'espressione digitata da un
# utente è costruire noi stessi l'AST con ast.parse (che non esegue nulla) e
# interpretarlo con una whitelist esplicita di nodi/funzioni.


class UnsafeExpressionError(ValueError):
    pass


_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}
_UNARYOPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _eval_ast_node(node, names, funcs):
    if isinstance(node, ast.Expression):
        return _eval_ast_node(node.body, names, funcs)
    if isinstance(node, ast.Constant):
        if not isinstance(node.value, (int, float)):
            raise UnsafeExpressionError(f"Valore non consentito: {node.value!r}")
        return node.value
    if isinstance(node, ast.Name):
        if node.id in names:
            return names[node.id]
        raise UnsafeExpressionError(f"Nome non riconosciuto: '{node.id}'")
    if isinstance(node, ast.BinOp) and type(node.op) in _BINOPS:
        return _BINOPS[type(node.op)](
            _eval_ast_node(node.left, names, funcs), _eval_ast_node(node.right, names, funcs)
        )
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARYOPS:
        return _UNARYOPS[type(node.op)](_eval_ast_node(node.operand, names, funcs))
    if isinstance(node, ast.Call):
        if node.keywords or not isinstance(node.func, ast.Name) or node.func.id not in funcs:
            raise UnsafeExpressionError("Chiamata di funzione non consentita.")
        args = [_eval_ast_node(arg, names, funcs) for arg in node.args]
        return funcs[node.func.id](*args)
    raise UnsafeExpressionError("Espressione non consentita.")


def _parse_safe_ast(expression_str):
    # "np.sin(x)" -> "sin(x)": i nomi delle funzioni sono risolti dalla whitelist.
    stripped = re.sub(r'\bnp\.', '', expression_str)
    try:
        return ast.parse(stripped, mode='eval')
    except SyntaxError as e:
        raise UnsafeExpressionError(f"Espressione non valida: {e}") from e


NUMPY_FUNCTIONS = {
    'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
    'arcsin': np.arcsin, 'arccos': np.arccos, 'arctan': np.arctan,
    'asin': np.arcsin, 'acos': np.arccos, 'atan': np.arctan,
    'sinh': np.sinh, 'cosh': np.cosh, 'tanh': np.tanh,
    'exp': np.exp, 'log': np.log, 'log10': np.log10, 'log2': np.log2,
    'sqrt': np.sqrt, 'cbrt': np.cbrt, 'abs': np.abs,
}
NUMPY_CONSTANTS = {'pi': np.pi, 'e': np.e}

SYMPY_FUNCTIONS = {
    'sin': sin, 'cos': cos, 'tan': tan,
    'arcsin': asin, 'arccos': acos, 'arctan': atan,
    'asin': asin, 'acos': acos, 'atan': atan,
    'sinh': sinh, 'cosh': cosh, 'tanh': tanh,
    'exp': exp, 'log': log, 'sqrt': sqrt, 'cbrt': cbrt, 'abs': Abs,
}
SYMPY_CONSTANTS = {'pi': sympy_pi, 'e': sympy_e}


def evaluate_scalar_expression(expression_str):
    """Valuta un'espressione numerica costante (es. 'np.sqrt(2)') senza eval()."""
    tree = _parse_safe_ast(expression_str)
    result = _eval_ast_node(tree, dict(NUMPY_CONSTANTS), NUMPY_FUNCTIONS)
    return float(result)


def evaluate_formula(formula_str, x_values):
    """Valuta f(x) su un array senza eval()."""
    tree = _parse_safe_ast(formula_str)
    x_values = np.asarray(x_values, dtype=float)
    names = {**NUMPY_CONSTANTS, 'x': x_values}
    y = np.asarray(_eval_ast_node(tree, names, NUMPY_FUNCTIONS), dtype=float)
    if y.shape != x_values.shape:
        y = np.full_like(x_values, y)
    return y


def build_sympy_expression(expression_str, symbol_map):
    """Costruisce un'espressione sympy (per derivate simboliche) senza mai
    passare la stringa dell'utente a parse_expr. sympify() qui riceve solo
    il risultato gia' calcolato (un numero o un'espressione sympy), mai la
    stringa originale, quindi non riapre la falla: si limita a incapsulare
    un eventuale numero puro (es. formula "5" senza variabili) in un oggetto
    sympy dotato di .evalf()."""
    tree = _parse_safe_ast(expression_str)
    names = {**SYMPY_CONSTANTS, **symbol_map}
    result = _eval_ast_node(tree, names, SYMPY_FUNCTIONS)
    return sympify(result)


def round_to_significant_figures(value, sig_figs=4):
    """Arrotonda un numero senza incertezza associata a `sig_figs` cifre significative."""
    if value == 0 or not math.isfinite(value):
        return value
    order = math.floor(math.log10(abs(value)))
    return round(value, sig_figs - 1 - order)


def format_value_with_error(value, error):
    """Formatta 'valore ± errore' secondo la convenzione di laboratorio: l'errore
    si arrotonda a 1 cifra significativa (2 se la prima cifra e' 1), e il valore
    centrale si arrotonda allo stesso ordine di grandezza. Es: 9.80665 ± 0.324
    -> '9.8 ± 0.3'."""
    if error is None or not math.isfinite(error) or error == 0:
        rounded = round_to_significant_figures(value, 4)
        return f"{rounded:g}"

    order = math.floor(math.log10(abs(error)))
    leading_digit = int(abs(error) / 10**order + 1e-9)
    sig_figs = 2 if leading_digit == 1 else 1
    decimals = sig_figs - 1 - order

    rounded_error = round(error, decimals)
    rounded_value = round(value, decimals)
    if decimals > 0:
        return f"{rounded_value:.{decimals}f} ± {rounded_error:.{decimals}f}"
    return f"{rounded_value:.0f} ± {rounded_error:.0f}"
