import numpy as np
from scipy import stats
from scipy.optimize import curve_fit

class Regression:
    @staticmethod
    def linear_regression(x, y):
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        n = len(x)
        x_mean = np.mean(x)
        intercept_err = std_err * np.sqrt(1/n + x_mean**2 / np.sum((x - x_mean)**2))

        return {
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_value**2,
            'p_value': p_value,
            'slope_err': std_err,
            'intercept_err': intercept_err
        }

    @staticmethod
    def get_linear_fit(x, result):
        return x, result['slope'] * x + result['intercept']

    @staticmethod
    def polynomial_regression(x, y, degree):
        coeffs = np.polyfit(x, y, degree)
        p = np.poly1d(coeffs)
        y_fit = p(x)
        residuals = y - y_fit
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        r_squared = 1 - (ss_res / ss_tot)
        
        n = len(x)
        residual_variance = np.sum(residuals**2) / (n - degree - 1)
        var_matrix = residual_variance * np.linalg.inv(np.dot(np.vander(x, degree + 1).T, np.vander(x, degree + 1)))
        coeff_errors = np.sqrt(np.diag(var_matrix))

        return {
            'coefficients': coeffs,
            'r_squared': r_squared,
            'coeff_errors': coeff_errors
        }

    @staticmethod
    def get_polynomial_fit(x, result):
        return x, np.polyval(result['coefficients'], x)

    @staticmethod
    def nonlinear_regression(x, y, func, p0=None):
        try:
            popt, pcov = curve_fit(func, x, y, p0=p0)
            perr = np.sqrt(np.diag(pcov))
            residuals = y - func(x, *popt)
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((y - np.mean(y))**2)
            r_squared = 1 - (ss_res / ss_tot)
            return {
                'parameters': popt,
                'errors': perr,
                'r_squared': r_squared
            }
        except RuntimeError:
            return None

    @staticmethod
    def get_nonlinear_fit(x, func, result):
        return x, func(x, *result['parameters'])

    @staticmethod
    def exponential_func(x, a, b):
        return a * np.exp(b * x)

    @classmethod
    def perform_fit(cls, x, y, fit_type, degree=2):
        if fit_type == "Lineare":
            return cls.linear_regression(x, y)
        elif fit_type == "Polinomiale":
            return cls.polynomial_regression(x, y, degree)
        elif fit_type == "Esponenziale":
            return cls.nonlinear_regression(x, y, cls.exponential_func, p0=[1, 0.1])
        else:
            raise ValueError("Tipo di fit non supportato")

    @classmethod
    def get_fit_data(cls, x, result, fit_type, degree=2):
        if fit_type == "Lineare":
            return cls.get_linear_fit(x, result)
        elif fit_type == "Polinomiale":
            return cls.get_polynomial_fit(x, result)
        elif fit_type == "Esponenziale":
            return cls.get_nonlinear_fit(x, cls.exponential_func, result)
        else:
            raise ValueError("Tipo di fit non supportato")
