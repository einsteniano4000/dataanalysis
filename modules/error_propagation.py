from sympy import symbols, diff, Abs, sqrt
import numpy as np
from utils.helpers import evaluate_scalar_expression, build_sympy_expression

class ErrorPropagation:
    def __init__(self):
        self.variables = {}

    def add_variable(self, name, value, error):
        try:
            if isinstance(value, str) and value.startswith('np.'):
                value = evaluate_scalar_expression(value)
            if isinstance(error, str) and error.startswith('np.'):
                error = evaluate_scalar_expression(error)
            
            self.variables[name] = {"value": float(value), "error": float(error)}
        except Exception as e:
            raise ValueError(f"Errore nell'aggiunta della variabile: {str(e)}")

    def calculate(self, expression_str):
        try:
            var_symbols = {name: symbols(name) for name in self.variables.keys()}
            expr = build_sympy_expression(expression_str, var_symbols)
            subs = {var_symbols[name]: var['value'] for name, var in self.variables.items()}
            result = expr.evalf(subs=subs)

            error_sq = 0
            for var_name, var_data in self.variables.items():
                partial_derivative = diff(expr, var_symbols[var_name])
                error_contribution = Abs(partial_derivative.evalf(subs=subs)) * var_data['error']
                error_sq += error_contribution ** 2
            error = sqrt(error_sq)

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
