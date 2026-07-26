from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QComboBox, QTextEdit, QSplitter, QLineEdit, QFileDialog)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from modules.data_visualization import DataVisualization
from modules.regression import Regression
from utils.helpers import evaluate_formula, format_value_with_error, round_to_significant_figures
import numpy as np

class PlotWidget(QWidget):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.data_viz = DataVisualization()
        self.regression = Regression()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        splitter = QSplitter(Qt.Vertical)

        plot_widget = QWidget()
        plot_layout = QVBoxLayout(plot_widget)
        self.toolbar = NavigationToolbar(self.data_viz.canvas, self)
        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.data_viz.canvas)

        labels_layout = QHBoxLayout()
        self.title_input = QLineEdit(placeholderText="Titolo del grafico")
        self.x_label_input = QLineEdit(placeholderText="Etichetta asse X")
        self.y_label_input = QLineEdit(placeholderText="Etichetta asse Y")
        labels_layout.addWidget(self.title_input)
        labels_layout.addWidget(self.x_label_input)
        labels_layout.addWidget(self.y_label_input)
        plot_layout.addLayout(labels_layout)

        update_labels_button = QPushButton("Aggiorna Etichette")
        update_labels_button.clicked.connect(self.update_labels)
        plot_layout.addWidget(update_labels_button)

        fit_layout = QHBoxLayout()
        self.fit_type = QComboBox()
        self.fit_type.addItems(["Nessun Fit", "Lineare", "Polinomiale", "Esponenziale"])
        self.fit_type.currentTextChanged.connect(self.on_fit_type_changed)
        
        self.poly_degree_label = QLabel("Grado polinomiale:")
        self.poly_degree_input = QLineEdit("2")
        
        fit_button = QPushButton("Esegui Fit")
        fit_button.clicked.connect(self.perform_fit)
        fit_layout.addWidget(QLabel("Tipo di Fit:"))
        fit_layout.addWidget(self.fit_type)
        fit_layout.addWidget(self.poly_degree_label)
        fit_layout.addWidget(self.poly_degree_input)
        fit_layout.addWidget(fit_button)
        plot_layout.addLayout(fit_layout)

        save_button = QPushButton("Salva Grafico")
        save_button.clicked.connect(self.save_plot)
        plot_layout.addWidget(save_button)

        splitter.addWidget(plot_widget)

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        splitter.addWidget(self.results_text)

        layout.addWidget(splitter)
        self.setLayout(layout)
        
        # Imposta lo stato iniziale del campo grado polinomiale
        self.on_fit_type_changed(self.fit_type.currentText())

    def on_fit_type_changed(self, fit_type):
        if fit_type == "Polinomiale":
            self.poly_degree_label.setVisible(True)
            self.poly_degree_input.setVisible(True)
        else:
            self.poly_degree_label.setVisible(False)
            self.poly_degree_input.setVisible(False)

    def update_plot(self):
        visible_series = self.data_manager.get_visible_series()
        self.data_viz.plot_series(visible_series)
        self.results_text.clear()
        self.update_labels()

    def update_labels(self):
        title = self.title_input.text()
        x_label = self.x_label_input.text()
        y_label = self.y_label_input.text()
        self.data_viz.set_labels(title, x_label, y_label)

    def perform_fit(self):
        fit_type = self.fit_type.currentText()
        if fit_type == "Nessun Fit":
            return

        results_text = ""
        for series in self.data_manager.get_visible_series():
            try:
                if fit_type == "Polinomiale":
                    degree = int(self.poly_degree_input.text())
                    result = self.regression.perform_fit(series.x_data, series.y_data, fit_type,
                                                          degree=degree, y_error=series.y_error)
                    x_fit, y_fit = self.regression.get_fit_data(series.x_data, result, fit_type, degree=degree)
                else:
                    result = self.regression.perform_fit(series.x_data, series.y_data, fit_type,
                                                          y_error=series.y_error)
                    x_fit, y_fit = self.regression.get_fit_data(series.x_data, result, fit_type)
            except ValueError as e:
                results_text += f"Serie: {series.name}\nErrore nel fit: {str(e)}\n\n"
                continue

            if result:
                if fit_type == "Lineare":
                    equation = f"y = {result['slope']:.4f}x + {result['intercept']:.4f}"
                    results_text += f"Serie: {series.name}\n"
                    results_text += f"Equazione: {equation}\n"
                    results_text += f"Pendenza: {format_value_with_error(result['slope'], result['slope_err'])}\n"
                    results_text += f"Intercetta: {format_value_with_error(result['intercept'], result['intercept_err'])}\n"
                elif fit_type == "Polinomiale":
                    degree = len(result['coefficients']) - 1
                    equation = f"y = {' + '.join([f'{p:.4f}x^{degree-i}' for i, p in enumerate(result['coefficients'])])}"
                    results_text += f"Serie: {series.name}\n"
                    results_text += f"Equazione: {equation}\n"
                    for i, (coeff, err) in enumerate(zip(result['coefficients'], result['coeff_errors'])):
                        results_text += f"Coefficiente x^{degree-i}: {format_value_with_error(coeff, err)}\n"
                elif fit_type == "Esponenziale":
                    equation = f"y = {result['parameters'][0]:.4f} * exp({result['parameters'][1]:.4f}x)"
                    results_text += f"Serie: {series.name}\n"
                    results_text += f"Equazione: {equation}\n"
                    results_text += f"A: {format_value_with_error(result['parameters'][0], result['errors'][0])}\n"
                    results_text += f"B: {format_value_with_error(result['parameters'][1], result['errors'][1])}\n"

                results_text += f"R²: {round_to_significant_figures(result['r_squared'], 4):g}\n"
                if result.get('reduced_chi_squared') is not None:
                    results_text += (f"χ²: {round_to_significant_figures(result['chi_squared'], 4):g} (dof={result['dof']})\n"
                                     f"χ² ridotto: {round_to_significant_figures(result['reduced_chi_squared'], 4):g}\n")
                results_text += "\n"
                self.data_viz.plot_fit(series, x_fit, y_fit, equation)
            else:
                results_text += f"Serie: {series.name}\nIl fit non è converso.\n\n"

        self.results_text.setText(results_text)

    def save_plot(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Salva Grafico", "", "PNG Files (*.png);;All Files (*)")
        if file_name:
            self.data_viz.save_plot(file_name)

    def plot_from_formula(self, formula, num_points, x_min=-10, x_max=10):
        try:
            x = np.linspace(x_min, x_max, num_points)
            y = evaluate_formula(formula, x)
            
            series_name = f"Formula: {formula}"
            self.data_manager.add_series(series_name, x, y)
            
            self.update_plot()
            
            self.data_viz.set_axis_limits(x_min, x_max, min(y), max(y))
            self.data_viz.add_grid()
            
            self.results_text.setText(f"Grafico generato dalla formula: {formula}\n"
                                      f"Numero di punti: {num_points}\n"
                                      f"Range X: [{x_min}, {x_max}]")
        except Exception as e:
            self.results_text.setText(f"Errore nella generazione del grafico: {str(e)}")

    def remove_last_plot(self):
        if self.data_manager.remove_last_series():
            self.update_plot()
            self.results_text.setText("Ultimo grafico rimosso.")
        else:
            self.results_text.setText("Nessun grafico da rimuovere.")

    def remove_series(self, series_id):
        if self.data_manager.remove_series(series_id):
            self.update_plot()
            self.results_text.setText(f"Serie con ID {series_id} rimossa.")
        else:
            self.results_text.setText(f"Impossibile rimuovere la serie con ID {series_id}.")
