import sys
from functools import partial

# Import QApplication and the required widgets from PyQt5.QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QTextBrowser
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout

from PyQt5.QtGui import QFont
from PyQt5.QtGui import QPixmap



# Create a subclass of QMainWindow to setup the calculator's GUI
class PyCalcUi(QMainWindow):
    """PyCalc's View (GUI)."""
    def __init__(self):
        """View initializer."""
        super().__init__()
        # Set some main window's properties
        self.setWindowTitle('Generador de facturas Vincles')
        self.setFixedSize(500, 800)
        # Set the central widget and the general layout
        self.generalLayout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)
        # Create the display and the buttons
        self._createDisplay()

    def _createDisplay(self):
        # Database
        self.database_label = QLabel('Base de datos de clientes', parent=self)
        self.database_label.setFont(QFont('Arial', 16))
        self.generalLayout.addWidget(self.database_label)

        self.database_file = QLineEdit()
        self.database_file.setFixedHeight(35)
        self.database_file.setAlignment(Qt.AlignLeft)
        self.database_file.setReadOnly(True)

        self.database_button = QPushButton('Seleccionar')

        self.database_layout = QHBoxLayout()
        self.database_layout.addWidget(self.database_file)
        self.database_layout.addWidget(self.database_button)
        self.generalLayout.addLayout(self.database_layout)

        # Visits
        self.visits_label = QLabel('Fichero de visitas', parent=self)
        self.visits_label.setFont(QFont('Arial', 16))
        self.generalLayout.addWidget(self.visits_label)

        self.visits_file = QLineEdit()
        self.visits_file.setFixedHeight(35)
        self.visits_file.setAlignment(Qt.AlignLeft)
        self.visits_file.setReadOnly(True)

        self.visits_button = QPushButton('Seleccionar')

        self.visits_layout = QHBoxLayout()
        self.visits_layout.addWidget(self.visits_file)
        self.visits_layout.addWidget(self.visits_button)
        self.generalLayout.addLayout(self.visits_layout)

        # Destination folder
        self.folder_label = QLabel('Base de datos de clientes', parent=self)
        self.folder_label.setFont(QFont('Arial', 16))
        self.generalLayout.addWidget(self.folder_label)

        self.folder_file = QLineEdit()
        self.folder_file.setFixedHeight(35)
        self.folder_file.setAlignment(Qt.AlignLeft)
        self.folder_file.setReadOnly(True)

        self.folder_button = QPushButton('Seleccionar')

        self.folder_layout = QHBoxLayout()
        self.folder_layout.addWidget(self.folder_file)
        self.folder_layout.addWidget(self.folder_button)
        self.generalLayout.addLayout(self.folder_layout)


        # Log
        self.log_browser = QTextBrowser(parent=self)
        self.generalLayout.addWidget(self.log_browser)


        # Generate button
        self.generate_button = QPushButton('Generar facturas')
        self.generate_button.setFont(QFont('Arial', 22))
        self.generalLayout.addWidget(self.generate_button)


        # Logo
        logo_im = QPixmap("template/logo.png")
        self.logo = QLabel()
        self.logo.setPixmap(logo_im)
        self.logo.setScaledContents(True)
        self.generalLayout.addWidget(self.logo)
#        file_select = QFileDialog.getOpenFileName(self, 'Open file', '.', '*xls')
#        self.generalLayout.addWidget(file_select)

        #  if filename:
        #      self.inputFileLineEdit.setText(filename)


# Client code
def main():
    """Main function."""
    # Create an instance of QApplication
    pycalc = QApplication(sys.argv)
    # Show the calculator's GUI
    view = PyCalcUi()
    view.show()
    # Create instances of the model and the controller
    # Execute the calculator's main loop
    sys.exit(pycalc.exec_())

if __name__ == '__main__':
    main()
