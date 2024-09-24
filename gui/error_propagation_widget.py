from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLineEdit, QLabel, QTextEdit, QCompleter)
from PyQt5.QtCore import QStringListModel, Qt
from modules.error_propagation import ErrorPropagation
import numpy as np

class ErrorPropagationWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.error_propagation = ErrorPropagation()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Input per le variabili
        var_layout = QHBoxLayout()
        self.var_name = QLineEdit(placeholderText="Nome variabile")
        self.var_value = QLineEdit(placeholderText="Valore")
        self.var_error = QLineEdit(placeholderText="Errore")
        add_var_button = QPushButton("Aggiungi Variabile")
        add_var_button.clicked.connect(self.add_variable)
        var_layout.addWidget(self.var_name)
        var_layout.addWidget(self.var_value)
        var_layout.addWidget(self.var_error)
        var_layout.addWidget(add_var_button)
        layout.addLayout(var_layout)

        # Lista delle variabili
        self.var_list = QTextEdit()
        self.var_list.setReadOnly(True)
        layout.addWidget(QLabel("Variabili:"))
        layout.addWidget(self.var_list)

        # Input per l'espressione con autocompletamento
        expr_layout = QHBoxLayout()
        self.expression = QLineEdit(placeholderText="Inserisci l'espressione")
        self.setup_autocomplete()
        calc_button = QPushButton("Calcola")
        calc_button.clicked.connect(self.calculate)
        expr_layout.addWidget(self.expression)
        expr_layout.addWidget(calc_button)
        layout.addLayout(expr_layout)

        # Risultato
        self.result = QTextEdit()
        self.result.setReadOnly(True)
        layout.addWidget(QLabel("Risultato:"))
        layout.addWidget(self.result)

        # Pulsante Clear
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.clear_all)
        layout.addWidget(clear_button)

        self.setLayout(layout)

    def setup_autocomplete(self):
        np_functions = [func for func in dir(np) if callable(getattr(np, func)) and not func.startswith("_")]
        np_constants = [const for const in dir(np) if not callable(getattr(np, const)) and not const.startswith("_")]
        autocomplete_list = ["np." + item for item in np_functions + np_constants]
        
        completer = QCompleter(autocomplete_list)
        completer.setCaseSensitivity(False)
        completer.setFilterMode(Qt.MatchContains)
        self.expression.setCompleter(completer)

    def add_variable(self):
        name = self.var_name.text()
        value = self.var_value.text()
        error = self.var_error.text()
        try:
            self.error_propagation.add_variable(name, value, error)
            self.update_var_list()
            self.var_name.clear()
            self.var_value.clear()
            self.var_error.clear()
        except ValueError as e:
            self.result.setText(f"Errore: {str(e)}")

    def update_var_list(self):
        self.var_list.setText("\n".join(f"{k}: {v}" for k, v in self.error_propagation.get_variables().items()))

    def calculate(self):
        try:
            result = self.error_propagation.calculate(self.expression.text())
            output = f"Risultato: {result['result']:.12f}\n"
            output += f"Errore assoluto: {result['absolute_error']:.12f}\n"
            output += f"Errore relativo: {result['relative_error']:.12f}\n"
            output += f"Errore percentuale: {result['percentage_error']:.12f}%"
            self.result.setText(output)
        except Exception as e:
            self.result.setText(f"Errore: {str(e)}")

    def clear_all(self):
        self.error_propagation.clear_variables()
        self.var_list.clear()
        self.result.clear()
        self.expression.clear()
