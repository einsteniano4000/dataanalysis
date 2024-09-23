from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLineEdit, QLabel, QTextEdit, QSpinBox)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from modules.statistical_analysis import StatisticalAnalysis
import numpy as np

class StatisticalAnalysisWidget(QWidget):
    def __init__(self):
        super().__init__()
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
        button_layout.addWidget(calc_button)
        button_layout.addWidget(hist_button)
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
        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def calculate_stats(self):
        try:
            data = self.parse_input()
            stats = StatisticalAnalysis(data)
            summary = stats.summary()
            
            results = "Riepilogo statistico:\n"
            results += f"Media: {summary['mean']:.4f}\n"
            results += f"Deviazione Standard: {summary['std_dev']:.4f}\n"
            results += f"Errore Standard: {summary['std_error']:.4f}\n"
            results += f"Minimo: {summary['min']:.4f}\n"
            results += f"Massimo: {summary['max']:.4f}\n"
            results += f"Mediana: {summary['median']:.4f}\n"
            results += f"Skewness: {summary['skewness']:.4f}\n"
            results += f"Kurtosis: {summary['kurtosis']:.4f}\n"
            results += f"Semidispersione Massima: {summary['max_semi_dispersion']:.4f}\n"
            
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
