import sys
from functools import partial

# Import QApplication and the required widgets from PyQt5.QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QFileDialog

from PyQt5.QtCore import Qt
from PyQt5.QtCore    import QThreadPool
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
from PyQt5.QtGui import QColor

from vincles.worker import Worker
from datetime import datetime


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

        # QT thread pool
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(1)


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
        select_database_file = filepath_browser_config(self, 'Base de datos de clientes (*.xls*)',
                                                'database_file')
        self.database_button.clicked.connect(select_database_file)

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
        select_visits_file = filepath_browser_config(self, 'Fichero con el historico de visitas (*.xls*)',
                                                'visits_file')
        self.visits_button.clicked.connect(select_visits_file)

        self.visits_layout = QHBoxLayout()
        self.visits_layout.addWidget(self.visits_file)
        self.visits_layout.addWidget(self.visits_button)
        self.generalLayout.addLayout(self.visits_layout)

        # Destination folder
        self.folder_label = QLabel('Carpeta destino', parent=self)
        self.folder_label.setFont(QFont('Arial', 16))
        self.generalLayout.addWidget(self.folder_label)

        self.folder_file = QLineEdit()
        self.folder_file.setFixedHeight(35)
        self.folder_file.setAlignment(Qt.AlignLeft)
        self.folder_file.setReadOnly(True)

        self.folder_button = QPushButton('Seleccionar')
        select_folder      = path_browser_config(self, 'Carpeta para los resultados',
                                                'folder_file')
        self.folder_button.clicked.connect(select_folder)

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
        self.generate_button.clicked.connect(test_fn(self))


        # Logo
        logo_im = QPixmap("template/logo.png")
        self.logo = QLabel()
        self.logo.setPixmap(logo_im)
        self.logo.setScaledContents(True)
        self.generalLayout.addWidget(self.logo)


def test_fn(window):
    def fn():
        print(window.visits_file.text())
        print(window.database_file.text())
        print(window.folder_file.text())


        worker = Worker(visits=window.visits_file.text(),
                        patients=window.database_file.text(),
                        output=window.folder_file.text())
        worker.signals.progress.connect(update_log(window))
        worker.signals.error.connect(update_log(window, error=True))
        window.threadpool.start(worker)

    return fn


def filepath_browser_config(window, filetype_str, widget_name):
    """
    Factory of functions to create a widget to select a file
    Parameters
    window (QApplication): Parent window
    filetype_str (string): Description of the filetype to be selected
    widget (QtWidgets): Widget to show the filename selected.
    Returns:
    function: Function to be connected to the file select button
    """
    path = '/home/jmbenlloch/vincles/'

    def file_browser():
        file_select = QFileDialog.getOpenFileName(window,
                                        'Open file', path, filetype_str)

        fname = file_select[0]
        widget = getattr(window, widget_name)
        widget.setText(fname)

    return file_browser


def path_browser_config(window, filetype_str, widget_name):
    """
    Factory of functions to create a widget to select a file
    Parameters
    window (QApplication): Parent window
    filetype_str (string): Description of the filetype to be selected
    widget (QtWidgets): Widget to show the filename selected.
    Returns:
    function: Function to be connected to the file select button
    """
    path = '/home/jmbenlloch/vincles/'

    def file_browser():
        file_select = QFileDialog.getExistingDirectory(window,
                                        'Open file', path)

        widget = getattr(window, widget_name)
        widget.setText(file_select)

    return file_browser


def update_log(window, error=False):
    def fn(status):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f'{date} - {status}'

        color = QColor(0, 0, 0)
        if error:
            color = QColor(255, 0, 0)
        window.log_browser.setTextColor(color)

        window.log_browser.append(f'{date} - {status}')
        # set scroll to the end
        scrollbar = window.log_browser.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    return fn


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
