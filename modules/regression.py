import numpy as np
from scipy import stats
from scipy.optimize import curve_fit

class Regression:
    @staticmethod
    def linear_regression(x, y, y_error=None):
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        n = len(x)

        if y_error is not None:
            y_error = np.asarray(y_error, dtype=float)
            if np.any(y_error <= 0):
                raise ValueError("Gli errori su y devono essere positivi per un fit pesato.")

            w = 1.0 / y_error**2
            S = np.sum(w)
            Sx = np.sum(w * x)
            Sy = np.sum(w * y)
            Sxx = np.sum(w * x * x)
            Sxy = np.sum(w * x * y)
            delta = S * Sxx - Sx**2

            slope = (S * Sxy - Sx * Sy) / delta
            intercept = (Sxx * Sy - Sx * Sxy) / delta
            slope_err = np.sqrt(S / delta)
            intercept_err = np.sqrt(Sxx / delta)

            residuals = y - (slope * x + intercept)
            dof = n - 2
            chi_squared = np.sum((residuals / y_error) ** 2)
            ss_tot = np.sum((y - np.mean(y))**2)
            r_squared = 1 - np.sum(residuals**2) / ss_tot if ss_tot != 0 else float('nan')

            return {
                'slope': slope,
                'intercept': intercept,
                'r_squared': r_squared,
                'p_value': None,
                'slope_err': slope_err,
                'intercept_err': intercept_err,
                'chi_squared': chi_squared,
                'reduced_chi_squared': chi_squared / dof if dof > 0 else float('nan'),
                'dof': dof
            }

        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        x_mean = np.mean(x)
        intercept_err = std_err * np.sqrt(1/n + x_mean**2 / np.sum((x - x_mean)**2))
        return {
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_value**2,
            'p_value': p_value,
            'slope_err': std_err,
            'intercept_err': intercept_err,
            'chi_squared': None,
            'reduced_chi_squared': None,
            'dof': n - 2
        }

    @staticmethod
    def get_linear_fit(x, result):
        return x, result['slope'] * x + result['intercept']

    @staticmethod
    def polynomial_regression(x, y, degree, y_error=None):
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        n = len(x)
        dof = n - degree - 1
        if dof <= 0:
            raise ValueError(
                "Punti insufficienti: servono almeno grado + 2 punti per stimare gli errori sui coefficienti."
            )

        X = np.vander(x, degree + 1)

        if y_error is not None:
            y_error = np.asarray(y_error, dtype=float)
            if np.any(y_error <= 0):
                raise ValueError("Gli errori su y devono essere positivi per un fit pesato.")

            w = 1.0 / y_error**2
            XtWX = X.T @ (w[:, None] * X)
            cov_matrix = np.linalg.inv(XtWX)
            coeffs = cov_matrix @ (X.T @ (w * y))
            residuals = y - X @ coeffs
            chi_squared = np.sum(w * residuals**2)
            reduced_chi_squared = chi_squared / dof
        else:
            coeffs = np.polyfit(x, y, degree)
            residuals = y - np.polyval(coeffs, x)
            residual_variance = np.sum(residuals**2) / dof
            cov_matrix = residual_variance * np.linalg.inv(X.T @ X)
            chi_squared = None
            reduced_chi_squared = None

        coeff_errors = np.sqrt(np.diag(cov_matrix))
        ss_tot = np.sum((y - np.mean(y))**2)
        r_squared = 1 - np.sum(residuals**2) / ss_tot if ss_tot != 0 else float('nan')

        return {
            'coefficients': coeffs,
            'r_squared': r_squared,
            'coeff_errors': coeff_errors,
            'chi_squared': chi_squared,
            'reduced_chi_squared': reduced_chi_squared,
            'dof': dof
        }

    @staticmethod
    def get_polynomial_fit(x, result):
        return x, np.polyval(result['coefficients'], x)

    @staticmethod
    def nonlinear_regression(x, y, func, p0=None, y_error=None):
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        try:
            popt, pcov = curve_fit(func, x, y, p0=p0, sigma=y_error, absolute_sigma=y_error is not None)
            perr = np.sqrt(np.diag(pcov))
            residuals = y - func(x, *popt)
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((y - np.mean(y))**2)
            r_squared = 1 - ss_res / ss_tot if ss_tot != 0 else float('nan')

            result = {
                'parameters': popt,
                'errors': perr,
                'r_squared': r_squared,
                'chi_squared': None,
                'reduced_chi_squared': None,
                'dof': len(x) - len(popt)
            }
            if y_error is not None:
                y_error = np.asarray(y_error, dtype=float)
                chi_squared = np.sum((residuals / y_error) ** 2)
                dof = result['dof']
                result['chi_squared'] = chi_squared
                result['reduced_chi_squared'] = chi_squared / dof if dof > 0 else float('nan')
            return result
        except (RuntimeError, TypeError, ValueError):
            return None

    @staticmethod
    def get_nonlinear_fit(x, func, result):
        return x, func(x, *result['parameters'])

    @staticmethod
    def exponential_func(x, a, b):
        return a * np.exp(b * x)

    @classmethod
    def perform_fit(cls, x, y, fit_type, degree=2, y_error=None):
        if fit_type == "Lineare":
            return cls.linear_regression(x, y, y_error=y_error)
        elif fit_type == "Polinomiale":
            return cls.polynomial_regression(x, y, degree, y_error=y_error)
        elif fit_type == "Esponenziale":
            return cls.nonlinear_regression(x, y, cls.exponential_func, p0=[1, 0.1], y_error=y_error)
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
