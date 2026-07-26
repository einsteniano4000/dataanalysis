from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLineEdit, QLabel, QTextEdit, QSpinBox, QInputDialog, QMessageBox)
from PySide6.QtCore import Qt, Signal
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from modules.statistical_analysis import StatisticalAnalysis
from utils.helpers import format_value_with_error, round_to_significant_figures
import numpy as np

class StatisticalAnalysisWidget(QWidget):
    variableComputed = Signal(str, float, float)

    def __init__(self):
        super().__init__()
        self.last_summary = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Input per i dati
        data_layout = QHBoxLayout()
        self.data_input = QLineEdit(placeholderText="Inserisci i dati separati da virgola")
        data_layout.addWidget(QLabel("Dati:"))
        data_layout.addWidget(self.data_input)
        layout.addLayout(data_layout)

        # Pulsanti per le operazioni
        button_layout = QHBoxLayout()
        calc_button = QPushButton("Calcola Statistiche")
        calc_button.clicked.connect(self.calculate_stats)
        hist_button = QPushButton("Crea Istogramma")
        hist_button.clicked.connect(self.create_histogram)
        send_to_error_prop_button = QPushButton("Invia media a Propagazione Errori →")
        send_to_error_prop_button.clicked.connect(self.send_mean_to_error_propagation)
        button_layout.addWidget(calc_button)
        button_layout.addWidget(hist_button)
        button_layout.addWidget(send_to_error_prop_button)
        layout.addLayout(button_layout)

        # Numero di bin per l'istogramma
        bin_layout = QHBoxLayout()
        self.bin_input = QSpinBox()
        self.bin_input.setRange(1, 100)
        self.bin_input.setValue(10)
        bin_layout.addWidget(QLabel("Numero di bin:"))
        bin_layout.addWidget(self.bin_input)
        layout.addLayout(bin_layout)

        # Area per i risultati
        self.results_area = QTextEdit()
        self.results_area.setReadOnly(True)
        layout.addWidget(QLabel("Risultati:"))
        layout.addWidget(self.results_area)

        # Area per il grafico
        self.figure = plt.figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def calculate_stats(self):
        try:
            data = self.parse_input()
            stats = StatisticalAnalysis(data)
            summary = stats.summary()
            self.last_summary = summary

            results = "Riepilogo statistico:\n"
            results += f"Media: {format_value_with_error(summary['mean'], summary['std_error'])}\n"
            results += f"Deviazione Standard: {round_to_significant_figures(summary['std_dev'], 4):g}\n"
            results += f"Minimo: {round_to_significant_figures(summary['min'], 4):g}\n"
            results += f"Massimo: {round_to_significant_figures(summary['max'], 4):g}\n"
            results += f"Mediana: {round_to_significant_figures(summary['median'], 4):g}\n"
            results += f"Skewness: {round_to_significant_figures(summary['skewness'], 4):g}\n"
            results += f"Kurtosis: {round_to_significant_figures(summary['kurtosis'], 4):g}\n"
            results += f"Semidispersione Massima: {round_to_significant_figures(summary['max_semi_dispersion'], 4):g}\n"
            
            self.results_area.setText(results)
        except ValueError as e:
            self.results_area.setText(f"Errore: {str(e)}")

    def create_histogram(self):
        try:
            data = self.parse_input()
            if len(data) == 0:
                raise ValueError("Nessun dato valido inserito")

            stats = StatisticalAnalysis(data)
            
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            # Crea l'istogramma
            n, bins, patches = ax.hist(data, bins=self.bin_input.value())
            
            # Aggiungi linee verticali per media e deviazione standard
            mean = stats.mean()
            std = stats.std_dev()
            ax.axvline(mean, color='r', linestyle='dashed', linewidth=2, label=f'Media: {mean:.2f}')
            ax.axvline(mean + std, color='g', linestyle='dashed', linewidth=2, label=f'Dev. Std: {std:.2f}')
            ax.axvline(mean - std, color='g', linestyle='dashed', linewidth=2)
            
            ax.set_title("Istogramma dei dati")
            ax.set_xlabel("Valore")
            ax.set_ylabel("Frequenza")
            ax.legend()
            
            self.canvas.draw()
            print("Istogramma creato e visualizzato")  # Messaggio di debug
        except ValueError as e:
            self.results_area.setText(f"Errore: {str(e)}")
            print(f"Errore nella creazione dell'istogramma: {str(e)}")  # Messaggio di debug
        except Exception as e:
            self.results_area.setText(f"Si è verificato un errore imprevisto: {str(e)}")
            print(f"Errore imprevisto: {str(e)}")  # Messaggio di debug

    def parse_input(self):
        try:
            return np.array([float(x.strip()) for x in self.data_input.text().split(',') if x.strip()])
        except ValueError:
            raise ValueError("I dati inseriti non sono validi. Assicurati di inserire numeri separati da virgole.")

    def send_mean_to_error_propagation(self):
        if self.last_summary is None:
            QMessageBox.warning(self, "Attenzione", "Calcola prima le statistiche.")
            return
        name, ok = QInputDialog.getText(self, "Nome variabile",
                                         "Nome della variabile da usare in Propagazione Errori:")
        if ok and name:
            self.variableComputed.emit(name, self.last_summary['mean'], self.last_summary['std_error'])
