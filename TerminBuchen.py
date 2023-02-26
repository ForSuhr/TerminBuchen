from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QVBoxLayout, \
    QHBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from PyQt5.QtGui import QRegularExpressionValidator
from PyQt5.QtCore import QRegularExpression
import threading
import sys
from selenium import webdriver
from time import sleep


class TerminBuchenModel:

    def __init__(self, controller):
        self.controller = controller
        self.delay = None
        self.driver = None
        self.buchen_event = threading.Event()
        self.keep_running = True
        
    def __del__(self):
        if self.driver is not None:
            self.driver.quit()

    def open_web(self):
        chromedriver = r".\chromedriver"
        self.driver = webdriver.Chrome(chromedriver)
        URL = self.controller.view.qle_url.text()
        self.driver.get(URL)

    def buchen(self):
        qle_delay = self.controller.view.qle_delay.text()
        self.delay = int(qle_delay)
        self.buchen_event.set()

    def stop(self):
        self.buchen_event.clear()
        self.driver.quit()

    def get_current_url(self):
        try:
            self.controller.view.qle_url.setText(self.driver.current_url)
        except ConnectionAbortedError('Fail to request.'):
            pass

    def send_dgram(self):
        while self.keep_running:
            state = self.buchen_event.isSet()
            if state:
                try:
                    self.driver.execute_script('document.getElementById("applicationForm:managedForm:proceed").click()')
                except ConnectionAbortedError('Fail to request.'):
                    pass
                finally:
                    sleep(self.delay)
                    self.get_current_url()


class TerminBuchenView(QWidget):

    def __init__(self, controller):
        super().__init__()
        self.msg_no_browser = None
        self.controller = controller
        self.validator_url = None
        self.msg_invalid_url = None
        self.btn_get_url = None
        self.btn_stop = None
        self.qle_delay = None
        self.qle_url = None
        self.btn_open_web = None
        self.btn_buchen = None
        self.initUI()

    def closeEvent(self, event):
        self.controller.model.keep_running = False

    def initUI(self):
        self.setWindowTitle("Termin Buchen")
        self.resize(400, 100)
        self.center()

        mainLayout = QVBoxLayout(self)
        hbox_r1 = QHBoxLayout()
        hbox_r2 = QHBoxLayout()
        ql_http = QLabel('Website', self)
        self.qle_url = QLineEdit(self)
        self.validator_url = QRegularExpressionValidator(self)
        self.validator_url.setRegularExpression(QRegularExpression("^(http|https)://.*$"))
        self.btn_open_web = QPushButton('Öffnen', self)
        self.qle_url.setValidator(self.validator_url)
        self.msg_invalid_url = QMessageBox()
        self.msg_invalid_url.setText('Invalid URL')
        self.msg_no_browser = QMessageBox()
        self.msg_no_browser.setText('No browser opened')
        self.btn_get_url = QPushButton('Get URL', self)
        self.btn_buchen = QPushButton('Buchen', self)
        self.btn_stop = QPushButton('Stop', self)
        ql_delay = QLabel('Delay in seconds', self)
        self.qle_delay = QLineEdit('30', self)
        hbox_r1.addWidget(ql_http)
        hbox_r1.addWidget(self.qle_url)
        hbox_r1.addWidget(self.btn_open_web)
        hbox_r2.addWidget(ql_delay)
        hbox_r2.addWidget(self.qle_delay)
        hbox_r2.addWidget(self.btn_get_url)
        hbox_r2.addWidget(self.btn_buchen)
        hbox_r2.addWidget(self.btn_stop)
        self.setLayout(mainLayout)
        mainLayout.addLayout(hbox_r1)
        mainLayout.addLayout(hbox_r2)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())  
        

class TerminBuchenController:

    def __init__(self):
        self.view = TerminBuchenView(self)
        self.model = TerminBuchenModel(self)

        self.view.btn_open_web.clicked.connect(self.on_btn_open_web_clicked)
        self.view.btn_buchen.clicked.connect(self.on_btn_buchen_clicked)
        self.view.btn_stop.clicked.connect(self.on_btn_stop_clicked)
        self.view.btn_stop.setEnabled(False)
        self.view.btn_get_url.clicked.connect(self.on_btn_get_url_clicked)

        self.t = threading.Thread(target=self.model.send_dgram)
        self.t.start()

    def on_btn_open_web_clicked(self):
        if self.view.qle_url.hasAcceptableInput():
            self.model.open_web()
        else:
            self.view.msg_invalid_url.exec()

    def on_btn_get_url_clicked(self):
        if self.model.driver is not None:
            self.model.get_current_url()
        else:
            self.view.msg_no_browser.exec()

    def on_btn_buchen_clicked(self):
        self.model.buchen()
        self.view.btn_buchen.setEnabled(False)
        self.view.btn_stop.setEnabled(True)

    def on_btn_stop_clicked(self):
        self.model.stop()
        self.view.btn_stop.setEnabled(False)
        self.view.btn_buchen.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    termin_buchen_controller = TerminBuchenController()
    termin_buchen_controller.view.show()
    sys.exit(app.exec_())
    pass
