from sympy import symbols, sympify, diff
from sympy.parsing.sympy_parser import parse_expr

class ErrorPropagation:
    def __init__(self):
        self.variables = {}

    def add_variable(self, name, value, error):
        self.variables[name] = {"value": value, "error": error}

    def calculate(self, expression_str):
        try:
            expr = parse_expr(expression_str)
            var_symbols = {name: symbols(name) for name in self.variables.keys()}
            result = expr.evalf(subs={var_symbols[name]: var['value'] for name, var in self.variables.items()})
            
            error = 0
            for var_name, var_data in self.variables.items():
                partial_derivative = diff(expr, var_symbols[var_name])
                error_contribution = abs(partial_derivative.evalf(subs={var_symbols[name]: var['value'] for name, var in self.variables.items()})) * var_data['error']
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
