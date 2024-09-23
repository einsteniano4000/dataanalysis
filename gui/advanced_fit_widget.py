from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLineEdit, QLabel, QComboBox, QTextEdit, QFileDialog)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from modules.regression import Regression
import numpy as np

class AdvancedFitWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.regression = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Input per i dati
        data_layout = QHBoxLayout()
        self.x_input = QLineEdit(placeholderText="Valori X (separati da virgola)")
        self.y_input = QLineEdit(placeholderText="Valori Y (separati da virgola)")
        data_layout.addWidget(QLabel("X:"))
        data_layout.addWidget(self.x_input)
        data_layout.addWidget(QLabel("Y:"))
        data_layout.addWidget(self.y_input)
        layout.addLayout(data_layout)

        # Input per gli errori
        error_layout = QHBoxLayout()
        self.x_err_input = QLineEdit(placeholderText="Errori X (opzionale)")
        self.y_err_input = QLineEdit(placeholderText="Errori Y (opzionale)")
        error_layout.addWidget(QLabel("Errori X:"))
        error_layout.addWidget(self.x_err_input)
        error_layout.addWidget(QLabel("Errori Y:"))
        error_layout.addWidget(self.y_err_input)
        layout.addLayout(error_layout)

        # Selezione del tipo di fit
        fit_type_layout = QHBoxLayout()
        self.fit_type = QComboBox()
        self.fit_type.addItems(["Lineare", "Polinomiale", "Esponenziale"])
        fit_type_layout.addWidget(QLabel("Tipo di fit:"))
        fit_type_layout.addWidget(self.fit_type)
        layout.addLayout(fit_type_layout)

        # Grado polinomiale (per fit polinomiale)
        self.poly_degree_widget = QWidget()
        poly_degree_layout = QHBoxLayout(self.poly_degree_widget)
        self.poly_degree = QLineEdit("2")
        poly_degree_layout.addWidget(QLabel("Grado polinomiale:"))
        poly_degree_layout.addWidget(self.poly_degree)
        layout.addWidget(self.poly_degree_widget)
        self.poly_degree_widget.hide()

        # Pulsanti
        button_layout = QHBoxLayout()
        fit_button = QPushButton("Esegui Fit")
        fit_button.clicked.connect(self.perform_fit)
        save_button = QPushButton("Salva Grafico")
        save_button.clicked.connect(self.save_plot)
        button_layout.addWidget(fit_button)
        button_layout.addWidget(save_button)
        layout.addLayout(button_layout)

        # Area per il grafico
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Area per i risultati del fit
        self.fit_results = QTextEdit()
        self.fit_results.setReadOnly(True)
        layout.addWidget(QLabel("Risultati del Fit:"))
        layout.addWidget(self.fit_results)

        self.setLayout(layout)

        # Connetti il cambio di tipo di fit all'aggiornamento dell'interfaccia
        self.fit_type.currentTextChanged.connect(self.update_ui)

    def update_ui(self):
        # Mostra il campo per il grado polinomiale solo se è selezionato il fit polinomiale
        self.poly_degree_widget.setVisible(self.fit_type.currentText() == "Polinomiale")

    def parse_input(self, input_string):
        return np.array([float(x.strip()) for x in input_string.split(',') if x.strip()])

    def perform_fit(self):
        try:
            x = self.parse_input(self.x_input.text())
            y = self.parse_input(self.y_input.text())
            x_err = self.parse_input(self.x_err_input.text()) if self.x_err_input.text() else None
            y_err = self.parse_input(self.y_err_input.text()) if self.y_err_input.text() else None
            
            self.regression = Regression(x, y)

            fit_type = self.fit_type.currentText()
            
            if fit_type == "Lineare":
                result = self.regression.linear_regression()
                x_fit, y_fit = self.regression.get_linear_fit()
                equation = f"y = {result['slope']:.4f}x + {result['intercept']:.4f}"
                self.plot_fit(x, y, x_fit, y_fit, equation, x_err, y_err)
                self.display_results(result, equation)
            
            elif fit_type == "Polinomiale":
                degree = int(self.poly_degree.text())
                result = self.regression.polynomial_regression(degree)
                x_fit, y_fit = self.regression.get_polynomial_fit(degree)
                equation = f"y = {' + '.join([f'{p:.4f}x^{degree-i}' for i, p in enumerate(result['coefficients'])])}"
                self.plot_fit(x, y, x_fit, y_fit, equation, x_err, y_err)
                self.display_results(result, equation)
            
            elif fit_type == "Esponenziale":
                def exp_func(x, a, b):
                    return a * np.exp(b * x)
                result = self.regression.nonlinear_regression(exp_func, p0=[1, 0.1])
                if result:
                    x_fit, y_fit = self.regression.get_nonlinear_fit(exp_func, p0=[1, 0.1])
                    equation = f"y = {result['parameters'][0]:.4f} * exp({result['parameters'][1]:.4f}x)"
                    self.plot_fit(x, y, x_fit, y_fit, equation, x_err, y_err)
                    self.display_results(result, equation)

        except ValueError as e:
            self.fit_results.setText(f"Errore: {str(e)}")

    def plot_fit(self, x, y, x_fit, y_fit, equation, x_err=None, y_err=None):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.errorbar(x, y, xerr=x_err, yerr=y_err, fmt='o', label='Dati')
        ax.plot(x_fit, y_fit, 'r-', label='Fit')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title('Fit dei Dati')
        ax.legend()
        ax.text(0.05, 0.95, equation, transform=ax.transAxes, 
                verticalalignment='top', fontsize=10, bbox=dict(facecolor='white', alpha=0.7))
        self.canvas.draw()

    def display_results(self, result, equation):
        text = f"Equazione: {equation}\n\n"
        if 'slope' in result:  # Linear regression
            text += f"Pendenza: {result['slope']:.4f} ± {result['slope_err']:.4f}\n"
            text += f"Intercetta: {result['intercept']:.4f} ± {result['intercept_err']:.4f}\n"
        elif 'coefficients' in result:  # Polynomial regression
            text += "Coefficienti:\n"
            for i, (coeff, err) in enumerate(zip(result['coefficients'], result['coeff_errors'])):
                text += f"  p{i}: {coeff:.4f} ± {err:.4f}\n"
        else:  # Nonlinear regression
            text += "Parametri:\n"
            for i, (param, error) in enumerate(zip(result['parameters'], result['errors'])):
                text += f"  p{i}: {param:.4f} ± {error:.4f}\n"
        text += f"\nR²: {result['r_squared']:.4f}"
        if 'p_value' in result:
            text += f"\np-value: {result['p_value']:.4f}"
        self.fit_results.setText(text)

    def save_plot(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Salva Grafico", "", "PNG Files (*.png);;All Files (*)")
        if file_name:
            self.figure.savefig(file_name)
