from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QSplitter, QLineEdit, QSpinBox, QPushButton, QLabel, QDoubleSpinBox
from PyQt5.QtCore import Qt
from modules.data_manager import DataManager
from gui.series_management_widget import SeriesManagementWidget
from gui.plot_widget import PlotWidget
from gui.statistical_analysis_widget import StatisticalAnalysisWidget
from gui.error_propagation_widget import ErrorPropagationWidget

class FormulaInputWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.formula_input = QLineEdit()
        self.formula_input.setPlaceholderText("Inserisci la formula (es. x**2 + 2*x + 1)")
        layout.addWidget(QLabel("Formula:"))
        layout.addWidget(self.formula_input)

        range_layout = QHBoxLayout()
        self.x_min_input = QDoubleSpinBox()
        self.x_min_input.setRange(-1000, 1000)
        self.x_min_input.setValue(-10)
        self.x_max_input = QDoubleSpinBox()
        self.x_max_input.setRange(-1000, 1000)
        self.x_max_input.setValue(10)
        range_layout.addWidget(QLabel("X min:"))
        range_layout.addWidget(self.x_min_input)
        range_layout.addWidget(QLabel("X max:"))
        range_layout.addWidget(self.x_max_input)
        layout.addLayout(range_layout)

        self.points_input = QSpinBox()
        self.points_input.setRange(2, 1000)
        self.points_input.setValue(100)
        layout.addWidget(QLabel("Numero di punti:"))
        layout.addWidget(self.points_input)

        button_layout = QHBoxLayout()
        self.generate_button = QPushButton("Genera Grafico")
        self.remove_last_button = QPushButton("Rimuovi ultimo grafico")
        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.remove_last_button)
        layout.addLayout(button_layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analisi Dati e Visualizzazione")
        self.setGeometry(100, 100, 1200, 800)
        self.data_manager = DataManager()
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        series_tab = QWidget()
        series_layout = QHBoxLayout(series_tab)
        
        splitter = QSplitter(Qt.Horizontal)
        
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        
        self.series_widget = SeriesManagementWidget(self.data_manager)
        left_layout.addWidget(self.series_widget)
        
        self.formula_widget = FormulaInputWidget()
        left_layout.addWidget(self.formula_widget)
        
        left_layout.addStretch(1)
        
        self.plot_widget = PlotWidget(self.data_manager)
        
        splitter.addWidget(left_container)
        splitter.addWidget(self.plot_widget)
        
        splitter.setSizes([300, 700])
        
        series_layout.addWidget(splitter)
        tab_widget.addTab(series_tab, "Visualizzazione Dati")

        stat_analysis_tab = StatisticalAnalysisWidget()
        tab_widget.addTab(stat_analysis_tab, "Analisi Statistica")

        error_prop_tab = ErrorPropagationWidget()
        tab_widget.addTab(error_prop_tab, "Propagazione Errori")

        self.series_widget.seriesUpdated.connect(self.plot_widget.update_plot)
        self.series_widget.seriesRemoved.connect(self.plot_widget.remove_series)
        self.formula_widget.generate_button.clicked.connect(self.generate_plot_from_formula)
        self.formula_widget.remove_last_button.clicked.connect(self.remove_last_plot)

    def generate_plot_from_formula(self):
        formula = self.formula_widget.formula_input.text()
        num_points = self.formula_widget.points_input.value()
        x_min = self.formula_widget.x_min_input.value()
        x_max = self.formula_widget.x_max_input.value()
        self.plot_widget.plot_from_formula(formula, num_points, x_min, x_max)
        self.series_widget.update_series_list()

    def remove_last_plot(self):
        self.plot_widget.remove_last_plot()
        self.series_widget.update_series_list()

if __name__ == "__main__":
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec_()
