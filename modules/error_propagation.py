from sympy import symbols, sympify, diff, Abs
from sympy.parsing.sympy_parser import parse_expr
import numpy as np

class ErrorPropagation:
    def __init__(self):
        self.variables = {}

    def add_variable(self, name, value, error):
        try:
            # Check if the value is a NumPy constant
            if isinstance(value, str) and value.startswith('np.'):
                value = eval(value)
            if isinstance(error, str) and error.startswith('np.'):
                error = eval(error)
            
            self.variables[name] = {"value": float(value), "error": float(error)}
        except Exception as e:
            raise ValueError(f"Errore nell'aggiunta della variabile: {str(e)}")

    def calculate(self, expression_str):
        try:
            # Replace numpy functions with their sympy equivalents
            for np_func in ['sin', 'cos', 'tan', 'exp', 'log', 'sqrt']:
                expression_str = expression_str.replace(f'np.{np_func}', np_func)
            
            # Replace numpy constants
            expression_str = expression_str.replace('np.pi', str(np.pi))
            expression_str = expression_str.replace('np.e', str(np.e))
            
            expr = parse_expr(expression_str)
            var_symbols = {name: symbols(name) for name in self.variables.keys()}
            result = expr.evalf(subs={var_symbols[name]: var['value'] for name, var in self.variables.items()})
            
            error = 0
            for var_name, var_data in self.variables.items():
                partial_derivative = diff(expr, var_symbols[var_name])
                error_contribution = Abs(partial_derivative.evalf(subs={var_symbols[name]: var['value'] for name, var in self.variables.items()})) * var_data['error']
                error += error_contribution  # Somma lineare invece di quadratura
            
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
