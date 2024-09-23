from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLineEdit, QLabel, QTextEdit)
from modules.error_propagation import ErrorPropagation

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

        # Input per l'espressione
        expr_layout = QHBoxLayout()
        self.expression = QLineEdit(placeholderText="Inserisci l'espressione")
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

    def add_variable(self):
        name = self.var_name.text()
        try:
            value = float(self.var_value.text())
            error = float(self.var_error.text())
            self.error_propagation.add_variable(name, value, error)
            self.update_var_list()
            self.var_name.clear()
            self.var_value.clear()
            self.var_error.clear()
        except ValueError:
            self.result.setText("Errore: Inserisci valori numerici validi.")

    def update_var_list(self):
        self.var_list.setText("\n".join(f"{k}: {v}" for k, v in self.error_propagation.get_variables().items()))

    def calculate(self):
        try:
            result = self.error_propagation.calculate(self.expression.text())
            output = f"Risultato: {result['result']:.4f}\n"
            output += f"Errore assoluto: {result['absolute_error']:.4f}\n"
            output += f"Errore relativo: {result['relative_error']:.4f}\n"
            output += f"Errore percentuale: {result['percentage_error']:.2f}%"
            self.result.setText(output)
        except Exception as e:
            self.result.setText(f"Errore: {str(e)}")

    def clear_all(self):
        self.error_propagation.clear_variables()
        self.var_list.clear()
        self.result.clear()
        self.expression.clear()
