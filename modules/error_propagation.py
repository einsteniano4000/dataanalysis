from sympy import symbols, sympify, diff, Abs, cbrt, asin, acos, atan
from sympy.parsing.sympy_parser import parse_expr
import numpy as np

class ErrorPropagation:
    def __init__(self):
        self.variables = {}
        self.np_to_sympy = {
            'sin': 'sin',
            'cos': 'cos',
            'tan': 'tan',
            'exp': 'exp',
            'log': 'log',
            'sqrt': 'sqrt',
            'cbrt': 'cbrt',
            'arcsin': 'asin',
            'arccos': 'acos',
            'arctan': 'atan',
            'pi': str(np.pi),
            'e': str(np.e)
        }

    def add_variable(self, name, value, error):
        try:
            if isinstance(value, str) and value.startswith('np.'):
                value = eval(value)
            if isinstance(error, str) and error.startswith('np.'):
                error = eval(error)
            
            self.variables[name] = {"value": float(value), "error": float(error)}
        except Exception as e:
            raise ValueError(f"Errore nell'aggiunta della variabile: {str(e)}")

    def calculate(self, expression_str):
        try:
            for np_func, sympy_func in self.np_to_sympy.items():
                expression_str = expression_str.replace(f'np.{np_func}', sympy_func)
            
            expr = parse_expr(expression_str)
            var_symbols = {name: symbols(name) for name in self.variables.keys()}
            result = expr.evalf(subs={var_symbols[name]: var['value'] for name, var in self.variables.items()})
            
            error = 0
            for var_name, var_data in self.variables.items():
                partial_derivative = diff(expr, var_symbols[var_name])
                error_contribution = Abs(partial_derivative.evalf(subs={var_symbols[name]: var['value'] for name, var in self.variables.items()})) * var_data['error']
                error += error_contribution
            
            relative_error = error / abs(result)
            percentage_error = relative_error * 100

            return {
                'result': float(result),
                'absolute_error': float(error),
                'relative_error': float(relative_error),
                'percentage_error': float(percentage_error)
            }
        except Exception as e:
            raise ValueError(f"Errore nel calcolo: {str(e)}")

    def get_variables(self):
        return {name: f"{var['value']} ± {var['error']}" for name, var in self.variables.items()}

    def clear_variables(self):
        self.variables.clear()
