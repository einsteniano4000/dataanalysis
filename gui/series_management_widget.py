from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QListWidget, QListWidgetItem, QInputDialog, QFileDialog,
                             QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
import numpy as np
import csv

class SeriesManagementWidget(QWidget):
    seriesUpdated = pyqtSignal()
    seriesRemoved = pyqtSignal(int)

    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.series_list = QListWidget()
        layout.addWidget(self.series_list)

        button_layout = QHBoxLayout()
        add_example_button = QPushButton("Aggiungi Serie di Esempio")
        add_manual_button = QPushButton("Inserisci Dati Manualmente")
        load_csv_button = QPushButton("Carica da CSV")
        remove_button = QPushButton("Rimuovi Serie Selezionata")
        
        button_layout.addWidget(add_example_button)
        button_layout.addWidget(add_manual_button)
        button_layout.addWidget(load_csv_button)
        button_layout.addWidget(remove_button)
        
        layout.addLayout(button_layout)

        self.setLayout(layout)

        add_example_button.clicked.connect(self.add_example_series)
        add_manual_button.clicked.connect(self.add_manual_series)
        load_csv_button.clicked.connect(self.load_csv_series)
        remove_button.clicked.connect(self.remove_series)
        self.series_list.itemChanged.connect(self.toggle_series_visibility)

        self.update_series_list()

    def update_series_list(self):
        self.series_list.clear()
        for series in self.data_manager.get_all_series():
            item = QListWidgetItem(series.name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if series.visible else Qt.Unchecked)
            item.setData(Qt.UserRole, series.id)
            self.series_list.addItem(item)

    def toggle_series_visibility(self, item):
        series_id = item.data(Qt.UserRole)
        series = next((s for s in self.data_manager.get_all_series() if s.id == series_id), None)
        if series:
            series.visible = item.checkState() == Qt.Checked
            self.seriesUpdated.emit()

    def add_example_series(self):
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        series_name = f"Esempio {len(self.data_manager.get_all_series()) + 1}"
        self.data_manager.add_series(series_name, x, y)
        self.update_series_list()
        self.seriesUpdated.emit()

    def add_manual_series(self):
        series_name, ok = QInputDialog.getText(self, "Nome Serie", "Inserisci il nome della serie:")
        if ok and series_name:
            x_values, ok = QInputDialog.getText(self, "Valori X", "Inserisci i valori di X separati da virgola:")
            if ok:
                y_values, ok = QInputDialog.getText(self, "Valori Y", "Inserisci i valori di Y separati da virgola:")
                if ok:
                    x_errors, ok = QInputDialog.getText(self, "Errori X", "Inserisci gli errori di X separati da virgola (opzionale):")
                    y_errors, ok = QInputDialog.getText(self, "Errori Y", "Inserisci gli errori di Y separati da virgola (opzionale):")
                    
                    try:
                        x = np.array([float(x.strip()) for x in x_values.split(',')])
                        y = np.array([float(y.strip()) for y in y_values.split(',')])
                        x_err = np.array([float(xe.strip()) for xe in x_errors.split(',')]) if x_errors else None
                        y_err = np.array([float(ye.strip()) for ye in y_errors.split(',')]) if y_errors else None
                        
                        if len(x) != len(y):
                            raise ValueError("Il numero di valori X e Y deve essere uguale.")
                        if x_err is not None and len(x) != len(x_err):
                            raise ValueError("Il numero di errori X deve essere uguale al numero di valori X.")
                        if y_err is not None and len(y) != len(y_err):
                            raise ValueError("Il numero di errori Y deve essere uguale al numero di valori Y.")
                        
                        self.data_manager.add_series(series_name, x, y, x_err, y_err)
                        self.update_series_list()
                        self.seriesUpdated.emit()
                    except ValueError as e:
                        QMessageBox.warning(self, "Errore", str(e))
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", f"Si è verificato un errore: {str(e)}")

    def load_csv_series(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Carica file CSV", "", "CSV Files (*.csv);;All Files (*)")
        if file_name:
            try:
                with open(file_name, 'r') as csv_file:
                    csv_reader = csv.reader(csv_file)
                    headers = next(csv_reader)
                    if len(headers) < 2 or len(headers) > 4:
                        raise ValueError("Il file CSV deve avere da 2 a 4 colonne.")
                    
                    x, y, x_err, y_err = [], [], [], []
                    for row in csv_reader:
                        x.append(float(row[0]))
                        y.append(float(row[1]))
                        if len(row) > 2:
                            x_err.append(float(row[2]))
                        if len(row) > 3:
                            y_err.append(float(row[3]))
                    
                    series_name = file_name.split('/')[-1].split('.')[0]
                    self.data_manager.add_series(series_name, np.array(x), np.array(y), 
                                                 np.array(x_err) if x_err else None, 
                                                 np.array(y_err) if y_err else None)
                    self.update_series_list()
                    self.seriesUpdated.emit()
                    QMessageBox.information(self, "Successo", f"Serie '{series_name}' caricata con successo.")
            except Exception as e:
                QMessageBox.warning(self, "Errore", f"Errore nel caricamento del file CSV: {str(e)}")

    def remove_series(self):
        current_item = self.series_list.currentItem()
        if current_item:
            series_id = current_item.data(Qt.UserRole)
            if self.data_manager.remove_series(series_id):
                self.seriesRemoved.emit(series_id)
                self.update_series_list()
                self.seriesUpdated.emit()
            else:
                QMessageBox.warning(self, "Errore", "Impossibile rimuovere la serie selezionata.")
        else:
            QMessageBox.warning(self, "Errore", "Nessuna serie selezionata.")

    def remove_last_series(self):
        if self.data_manager.remove_last_series():
            self.update_series_list()
            self.seriesUpdated.emit()
        else:
            QMessageBox.warning(self, "Errore", "Nessuna serie da rimuovere.")
