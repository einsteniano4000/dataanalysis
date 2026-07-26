import numpy as np
import pytest

from modules.regression import Regression


# --- Lineare -----------------------------------------------------------

def test_linear_regression_unweighted_has_no_chi_squared():
    x = np.linspace(0, 10, 10)
    y = 2 * x + 1
    result = Regression.linear_regression(x, y)
    assert result['chi_squared'] is None
    assert result['reduced_chi_squared'] is None
    assert result['dof'] == len(x) - 2


def test_linear_regression_weighted_perfect_fit_has_zero_chi_squared():
    x = np.linspace(0, 10, 10)
    y = 2 * x + 1
    y_error = np.full_like(x, 0.5)
    result = Regression.linear_regression(x, y, y_error=y_error)
    assert result['slope'] == pytest.approx(2.0)
    assert result['intercept'] == pytest.approx(1.0)
    assert result['chi_squared'] == pytest.approx(0.0, abs=1e-9)
    assert result['reduced_chi_squared'] == pytest.approx(0.0, abs=1e-9)
    assert result['dof'] == len(x) - 2


def test_linear_regression_weighted_matches_unweighted_for_uniform_errors():
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 7.0, 9.0])
    y = np.array([2.1, 3.9, 6.2, 7.8, 10.1, 14.2, 17.9])
    unweighted = Regression.linear_regression(x, y)
    weighted = Regression.linear_regression(x, y, y_error=np.full_like(x, 1.0))
    # Con errori uniformi il fit pesato deve coincidere con quello OLS.
    assert weighted['slope'] == pytest.approx(unweighted['slope'], rel=1e-9)
    assert weighted['intercept'] == pytest.approx(unweighted['intercept'], rel=1e-9)


def test_linear_regression_chi_squared_grows_with_larger_residuals():
    x = np.linspace(0, 10, 10)
    y_error = np.full_like(x, 0.1)
    small_residuals = np.array([0.05, -0.05] * 5)
    large_residuals = np.array([2.0, -2.0] * 5)
    r_close = Regression.linear_regression(x, 2 * x + 1 + small_residuals, y_error=y_error)
    r_far = Regression.linear_regression(x, 2 * x + 1 + large_residuals, y_error=y_error)
    assert r_far['chi_squared'] > r_close['chi_squared']


def test_linear_regression_rejects_nonpositive_errors():
    x = np.linspace(0, 5, 5)
    y = 2 * x
    with pytest.raises(ValueError):
        Regression.linear_regression(x, y, y_error=np.zeros_like(x))


# --- Polinomiale ---------------------------------------------------------

def test_polynomial_regression_weighted_perfect_fit():
    x = np.linspace(-3, 3, 12)
    y = 2 * x**2 - x + 5
    y_error = np.full_like(x, 0.2)
    result = Regression.polynomial_regression(x, y, degree=2, y_error=y_error)
    np.testing.assert_allclose(result['coefficients'], [2, -1, 5], atol=1e-8)
    assert result['chi_squared'] == pytest.approx(0.0, abs=1e-6)
    assert result['reduced_chi_squared'] == pytest.approx(0.0, abs=1e-6)
    assert result['dof'] == len(x) - 3


def test_polynomial_regression_unweighted_has_no_chi_squared():
    x = np.linspace(-3, 3, 12)
    y = 2 * x**2 - x + 5
    result = Regression.polynomial_regression(x, y, degree=2)
    assert result['chi_squared'] is None
    assert result['reduced_chi_squared'] is None


def test_polynomial_regression_insufficient_points_raises():
    x = np.array([1.0, 2.0, 3.0])
    y = np.array([1.0, 4.0, 9.0])
    with pytest.raises(ValueError):
        Regression.polynomial_regression(x, y, degree=5)


def test_polynomial_regression_rejects_nonpositive_errors():
    x = np.linspace(0, 5, 6)
    y = x**2
    with pytest.raises(ValueError):
        Regression.polynomial_regression(x, y, degree=2, y_error=np.full_like(x, -1.0))


# --- Esponenziale ----------------------------------------------------------

def test_nonlinear_regression_weighted_chi_squared():
    x = np.linspace(0, 5, 10)
    y = 2.0 * np.exp(0.5 * x)
    y_error = np.full_like(x, 0.01)
    result = Regression.nonlinear_regression(x, y, Regression.exponential_func, p0=[1, 0.1], y_error=y_error)
    assert result is not None
    np.testing.assert_allclose(result['parameters'], [2.0, 0.5], rtol=1e-4)
    assert result['chi_squared'] == pytest.approx(0.0, abs=1e-4)
    assert result['dof'] == len(x) - 2


def test_nonlinear_regression_unweighted_has_no_chi_squared():
    x = np.linspace(0, 5, 10)
    y = 2.0 * np.exp(0.5 * x)
    result = Regression.nonlinear_regression(x, y, Regression.exponential_func, p0=[1, 0.1])
    assert result['chi_squared'] is None
    assert result['reduced_chi_squared'] is None


def test_nonlinear_regression_returns_none_on_bad_data():
    x = np.array([1.0])
    y = np.array([1.0])
    result = Regression.nonlinear_regression(x, y, Regression.exponential_func, p0=[1, 0.1])
    assert result is None


# --- perform_fit / get_fit_data ------------------------------------------

def test_perform_fit_propagates_y_error_and_chi_squared():
    x = np.linspace(0, 10, 10)
    y = 2 * x + 1
    y_error = np.full_like(x, 0.3)
    result = Regression.perform_fit(x, y, "Lineare", y_error=y_error)
    assert result['chi_squared'] is not None
    assert result['reduced_chi_squared'] == pytest.approx(0.0, abs=1e-9)


@pytest.mark.parametrize("fit_type,kwargs", [
    ("Lineare", {}),
    ("Polinomiale", {"degree": 2}),
    ("Esponenziale", {}),
])
def test_reduced_chi_squared_equals_chi_squared_over_dof(fit_type, kwargs):
    x = np.linspace(1, 10, 10)
    y_error = np.full_like(x, 0.2)
    if fit_type == "Esponenziale":
        y = 1.5 * np.exp(0.2 * x) + np.array([0.1, -0.1] * 5)
    elif fit_type == "Polinomiale":
        y = x**2 + np.array([0.1, -0.1] * 5)
    else:
        y = 3 * x + 2 + np.array([0.1, -0.1] * 5)

    result = Regression.perform_fit(x, y, fit_type, y_error=y_error, **kwargs)
    assert result is not None
    assert result['reduced_chi_squared'] == pytest.approx(result['chi_squared'] / result['dof'])
