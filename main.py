import sys
import os

# Aggiungi la directory principale al percorso di Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from gui.main_window import MainWindow
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
