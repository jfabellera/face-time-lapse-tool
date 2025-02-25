import traceback
from PyQt5 import QtCore, QtGui, QtWidgets
import subprocess
import os


os.environ["PYTHONUNBUFFERED"] = "1"


def error_text(err_msg):
    return "<html><head/><body><p><span style=\"color:red\">Error: " + err_msg + "<\span></p></body></html>"


# class for communicating with main thread and worker thread
class WorkerSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(tuple)
    result = QtCore.pyqtSignal(object)
    progress = QtCore.pyqtSignal(float, object)


# worker thread class
class Worker(QtCore.QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.kwargs['progress_callback'] = self.signals.progress

    @QtCore.pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


# confirm dialog box
class Ui_Confirm(object):
    def __init__(self):
        self.val = False

    def setupUi(self, Confirm):
        Confirm.setObjectName("Confirm")
        Confirm.setEnabled(True)
        Confirm.resize(372, 109)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Confirm.sizePolicy().hasHeightForWidth())
        Confirm.setSizePolicy(sizePolicy)
        Confirm.setAcceptDrops(False)
        self.buttonConfirm = QtWidgets.QDialogButtonBox(Confirm)
        self.buttonConfirm.setGeometry(QtCore.QRect(10, 70, 351, 32))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonConfirm.sizePolicy().hasHeightForWidth())
        self.buttonConfirm.setSizePolicy(sizePolicy)
        self.buttonConfirm.setOrientation(QtCore.Qt.Horizontal)
        self.buttonConfirm.setStandardButtons(QtWidgets.QDialogButtonBox.No | QtWidgets.QDialogButtonBox.Yes)
        self.buttonConfirm.setObjectName("buttonConfirm")
        self.label = QtWidgets.QLabel(Confirm)
        self.label.setGeometry(QtCore.QRect(10, 10, 351, 61))
        self.label.setObjectName("label")

        self.retranslateUi(Confirm)
        self.buttonConfirm.clicked.connect(Confirm.accept)
        self.buttonConfirm.accepted.connect(self.accept)
        self.buttonConfirm.clicked.connect(Confirm.reject)
        self.buttonConfirm.rejected.connect(self.reject)
        QtCore.QMetaObject.connectSlotsByName(Confirm)

    def retranslateUi(self, Confirm):
        _translate = QtCore.QCoreApplication.translate
        Confirm.setWindowTitle(_translate("Confirm", "Confirm"))
        self.label.setText(_translate("Confirm",
                                      "<html><head/><body><p align=\"center\">No destination directory specified, overwrite the source directory?</p></body></html>"))

    def accept(self):
        self.val = True

    def reject(self):
        pass

    # retrieve if user clicked yes or no
    def get_value(self):
        return self.val


# main window application
class Ui_MainWindow(object):
    def __init__(self):
        self.threadpool = QtCore.QThreadPool()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(461, 251)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabs = QtWidgets.QTabWidget(self.centralwidget)
        self.tabs.setGeometry(QtCore.QRect(10, 10, 441, 221))
        self.tabs.setTabsClosable(False)
        self.tabs.setObjectName("tabs")
        self.indexTab = QtWidgets.QWidget()
        self.indexTab.setObjectName("indexTab")
        self.layoutWidget_2 = QtWidgets.QWidget(self.indexTab)
        self.layoutWidget_2.setGeometry(QtCore.QRect(10, 30, 411, 101))
        self.layoutWidget_2.setObjectName("layoutWidget_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.layoutWidget_2)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.indexComboType = QtWidgets.QComboBox(self.layoutWidget_2)
        self.indexComboType.setObjectName("indexComboType")
        self.indexComboType.addItem("")
        self.indexComboType.addItem("")
        self.gridLayout_2.addWidget(self.indexComboType, 1, 2, 1, 2)
        self.indexLabelType = QtWidgets.QLabel(self.layoutWidget_2)
        self.indexLabelType.setObjectName("indexLabelType")
        self.gridLayout_2.addWidget(self.indexLabelType, 0, 2, 1, 1)
        self.indexButtonSrc = QtWidgets.QPushButton(self.layoutWidget_2)
        self.indexButtonSrc.setObjectName("indexButtonSrc")
        self.gridLayout_2.addWidget(self.indexButtonSrc, 1, 1, 1, 1)
        self.indexLabelDst = QtWidgets.QLabel(self.layoutWidget_2)
        self.indexLabelDst.setObjectName("indexLabelDst")
        self.gridLayout_2.addWidget(self.indexLabelDst, 2, 0, 1, 1)
        self.indexButtonDst = QtWidgets.QPushButton(self.layoutWidget_2)
        self.indexButtonDst.setObjectName("indexButtonDst")
        self.gridLayout_2.addWidget(self.indexButtonDst, 3, 3, 1, 1)
        self.indexEditSrc = QtWidgets.QLineEdit(self.layoutWidget_2)
        self.indexEditSrc.setObjectName("indexEditSrc")
        self.gridLayout_2.addWidget(self.indexEditSrc, 1, 0, 1, 1)
        self.indexEditDst = QtWidgets.QLineEdit(self.layoutWidget_2)
        self.indexEditDst.setObjectName("indexEditDst")
        self.gridLayout_2.addWidget(self.indexEditDst, 3, 0, 1, 3)
        self.indexLabelSrc = QtWidgets.QLabel(self.layoutWidget_2)
        self.indexLabelSrc.setObjectName("indexLabelSrc")
        self.gridLayout_2.addWidget(self.indexLabelSrc, 0, 0, 1, 1)
        self.indexButtonSubmit = QtWidgets.QPushButton(self.indexTab)
        self.indexButtonSubmit.setGeometry(QtCore.QRect(347, 160, 75, 23))
        self.indexButtonSubmit.setObjectName("indexButtonSubmit")
        self.indexProgressBar = QtWidgets.QProgressBar(self.indexTab)
        self.indexProgressBar.setGeometry(QtCore.QRect(10, 160, 331, 23))
        self.indexProgressBar.setProperty("value", 0)
        self.indexProgressBar.setObjectName("indexProgressBar")
        self.indexProgressBar.setVisible(False)
        self.indexMsg = QtWidgets.QLabel(self.indexTab)
        self.indexMsg.setGeometry(QtCore.QRect(10, 160, 331, 23))
        self.indexMsg.setObjectName("indexMsg")
        self.indexMsg.setVisible(False)
        self.tabs.addTab(self.indexTab, "")
        self.alignTab = QtWidgets.QWidget()
        self.alignTab.setObjectName("alignTab")
        self.layoutWidget = QtWidgets.QWidget(self.alignTab)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 411, 137))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.alignLabelType = QtWidgets.QLabel(self.layoutWidget)
        self.alignLabelType.setObjectName("alignLabelType")
        self.gridLayout.addWidget(self.alignLabelType, 0, 0, 1, 1)
        self.alignLabelType_2 = QtWidgets.QLabel(self.layoutWidget)
        self.alignLabelType_2.setObjectName("alignLabelType_2")
        self.gridLayout.addWidget(self.alignLabelType_2, 0, 3, 1, 1)
        self.alignEditSrc = QtWidgets.QLineEdit(self.layoutWidget)
        self.alignEditSrc.setObjectName("alignEditSrc")
        self.gridLayout.addWidget(self.alignEditSrc, 1, 0, 1, 2)
        self.alignButtonSrc = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.alignButtonSrc.sizePolicy().hasHeightForWidth())
        self.alignButtonSrc.setSizePolicy(sizePolicy)
        self.alignButtonSrc.setObjectName("alignButtonSrc")
        self.gridLayout.addWidget(self.alignButtonSrc, 1, 2, 1, 1)
        self.alignComboType = QtWidgets.QComboBox(self.layoutWidget)
        self.alignComboType.setObjectName("alignComboType")
        self.alignComboType.addItem("")
        self.alignComboType.addItem("")
        self.gridLayout.addWidget(self.alignComboType, 1, 3, 1, 2)
        self.alignLabelDst = QtWidgets.QLabel(self.layoutWidget)
        self.alignLabelDst.setObjectName("alignLabelDst")
        self.gridLayout.addWidget(self.alignLabelDst, 2, 0, 1, 1)
        self.alignEditDst = QtWidgets.QLineEdit(self.layoutWidget)
        self.alignEditDst.setObjectName("alignEditDst")
        self.gridLayout.addWidget(self.alignEditDst, 3, 0, 1, 4)
        self.alignButtonDst = QtWidgets.QPushButton(self.layoutWidget)
        self.alignButtonDst.setObjectName("alignButtonDst")
        self.gridLayout.addWidget(self.alignButtonDst, 3, 4, 1, 1)
        self.alignLabelWidth = QtWidgets.QLabel(self.layoutWidget)
        self.alignLabelWidth.setObjectName("alignLabelWidth")
        self.gridLayout.addWidget(self.alignLabelWidth, 4, 0, 1, 1)
        self.alignLabelHeight = QtWidgets.QLabel(self.layoutWidget)
        self.alignLabelHeight.setObjectName("alignLabelHeight")
        self.gridLayout.addWidget(self.alignLabelHeight, 4, 1, 1, 1)
        self.alignLabelScale = QtWidgets.QLabel(self.layoutWidget)
        self.alignLabelScale.setObjectName("alignLabelScale")
        self.gridLayout.addWidget(self.alignLabelScale, 4, 3, 1, 1)
        self.alignEditWidth = QtWidgets.QLineEdit(self.layoutWidget)
        self.alignEditWidth.setObjectName("alignEditWidth")
        self.gridLayout.addWidget(self.alignEditWidth, 5, 0, 1, 1)
        self.alignEditHeight = QtWidgets.QLineEdit(self.layoutWidget)
        self.alignEditHeight.setObjectName("alignEditHeight")
        self.gridLayout.addWidget(self.alignEditHeight, 5, 1, 1, 2)
        self.alignEditScale = QtWidgets.QLineEdit(self.layoutWidget)
        self.alignEditScale.setObjectName("alignEditScale")
        self.gridLayout.addWidget(self.alignEditScale, 5, 3, 1, 2)
        self.alignButtonSubmit = QtWidgets.QPushButton(self.alignTab)
        self.alignButtonSubmit.setGeometry(QtCore.QRect(347, 160, 75, 23))
        self.alignButtonSubmit.setObjectName("alignButtonSubmit")
        self.alignProgressBar = QtWidgets.QProgressBar(self.alignTab)
        self.alignProgressBar.setGeometry(QtCore.QRect(10, 160, 331, 23))
        self.alignProgressBar.setProperty("value", 0)
        self.alignProgressBar.setObjectName("alignProgressBar")
        self.alignProgressBar.setVisible(False)
        self.alignMsg = QtWidgets.QLabel(self.alignTab)
        self.alignMsg.setGeometry(QtCore.QRect(10, 160, 331, 23))
        self.alignMsg.setObjectName("alignMsg")
        self.alignMsg.setVisible(False)
        self.tabs.addTab(self.alignTab, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setFixedSize(MainWindow.size())
        self.indexButtonSrc.clicked.connect(self.browse)
        self.indexButtonDst.clicked.connect(self.browse)
        self.alignButtonSrc.clicked.connect(self.browse)
        self.alignButtonDst.clicked.connect(self.browse)
        self.indexButtonSubmit.clicked.connect(self.submit)
        self.alignButtonSubmit.clicked.connect(self.submit)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Face Time-lapse Tool"))
        self.indexComboType.setItemText(0, _translate("MainWindow", "JPG"))
        self.indexComboType.setItemText(1, _translate("MainWindow", "PNG"))
        self.indexLabelType.setText(_translate("MainWindow", "Image Type"))
        self.indexButtonSrc.setText(_translate("MainWindow", "Browse"))
        self.indexLabelDst.setText(_translate("MainWindow", "Destination Directory"))
        self.indexButtonDst.setText(_translate("MainWindow", "Browse"))
        self.indexEditDst.setToolTip(_translate("MainWindow",
                                                "<html><head/><body><p>Leave blank if you would like to overwrite the source directory</p></body></html>"))
        self.indexLabelSrc.setText(_translate("MainWindow", "Source Directory"))
        self.indexButtonSubmit.setText(_translate("MainWindow", "Submit"))
        self.tabs.setTabText(self.tabs.indexOf(self.indexTab), _translate("MainWindow", "Index Files"))
        self.alignLabelType.setText(_translate("MainWindow", "Source Directory"))
        self.alignLabelType_2.setText(_translate("MainWindow", "Image Type"))
        self.alignButtonSrc.setText(_translate("MainWindow", "Browse"))
        self.alignComboType.setItemText(0, _translate("MainWindow", "JPG"))
        self.alignComboType.setItemText(1, _translate("MainWindow", "PNG"))
        self.alignLabelDst.setText(_translate("MainWindow", "Destination Directory"))
        self.alignEditDst.setToolTip(_translate("MainWindow",
                                                "<html><head/><body><p>Leave blank if you would like to overwrite the source directory</p></body></html>"))
        self.alignButtonDst.setText(_translate("MainWindow", "Browse"))
        self.alignLabelWidth.setText(_translate("MainWindow", "Width"))
        self.alignLabelHeight.setText(_translate("MainWindow", "Height"))
        self.alignLabelScale.setText(_translate("MainWindow", "Eye Distance"))
        self.alignEditWidth.setText(_translate("MainWindow", "1920"))
        self.alignEditHeight.setText(_translate("MainWindow", "1080"))
        self.alignEditScale.setText(_translate("MainWindow", "200"))
        self.alignButtonSubmit.setText(_translate("MainWindow", "Submit"))
        self.indexMsg.setText(_translate("MainWindow",
                                         "<html><head/><body><p><span style=\"color:red\">Error: Message<\span></p></body></html>"))
        self.alignMsg.setText(_translate("MainWindow",
                                         "<html><head/><body><p><span style=\"color:red\">Error: Message<\span></p></body></html>"))
        self.tabs.setTabText(self.tabs.indexOf(self.alignTab), _translate("MainWindow", "Align Images"))

    # deetermine which button was clicked and open browse window for corresponding field
    def browse(self):
        sender = MainWindow.sender()
        directory = QtWidgets.QFileDialog.getExistingDirectory(QtWidgets.QFileDialog(), "Select directory")
        if sender.objectName() == "indexButtonSrc":
            self.indexEditSrc.setText(directory)
        elif sender.objectName() == "indexButtonDst":
            self.indexEditDst.setText(directory)
        elif sender.objectName() == "alignButtonSrc":
            self.alignEditSrc.setText(directory)
        elif sender.objectName() == "alignButtonDst":
            self.alignEditDst.setText(directory)

    # validate the arguments before running the scripts
    def validate_args(self, edit_src, edit_dst, err_msg):
        run = True
        if not edit_src.displayText():
            err_msg.setText(error_text("No source directory specified"))
            run = False
        elif not os.path.isdir(edit_src.displayText()):
            err_msg.setText(error_text("Source directory does not exist"))
            run = False
        elif not edit_dst.displayText():
            Dialog = QtWidgets.QDialog()
            dialog_ui = Ui_Confirm()
            dialog_ui.setupUi(Dialog)
            Dialog.exec_()
            if dialog_ui.get_value():
                edit_dst.setText(edit_src.displayText())
            else:
                err_msg.setText(error_text("No destination directory specified"))
                run = False
        elif not os.path.isdir(edit_dst.displayText()):
            err_msg.setText(error_text("Destination directory does not exist"))
            run = False

        return run

    # function to run the corresponding script, in a function so it can be threaded
    def run_script(self, file, src, dst, err_msg, prog_bar, cmb, sender, progress_callback):
        # all arguments have been validated at this point
        err_msg.setVisible(False)
        prog_bar.setVisible(True)
        cmd = ['python', file, '-s' + src.displayText(),
               '-d' + dst.displayText(), '-t' + cmb.currentText().lower(), '-G']
        if sender.objectName() == "alignButtonSubmit":
            cmd.extend(['-W' + self.alignEditWidth.displayText(), '-H' + self.alignEditHeight.displayText(),
                        '-S' + self.alignEditScale.displayText()])
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        prog_bar.setVisible(True)
        while True:
            if process.poll() is not None:
                break
            output = process.stdout.readline()
            if output:
                progress_callback.emit(float(output.strip().decode('ascii')), prog_bar)
        rc = process.poll()

    # communicate with thread to get progressbar value
    def progress_fn(self, n, prog_bar):
        prog_bar.setProperty("value", n)

    def print_output(self, s):
        print(s)

    def thread_complete(self):
        print("THREAD COMPLETE!")

    # when submit button has been clicked, run the corresponding script
    def submit(self):
        sender = MainWindow.sender()

        # set up variables for the correct script
        if sender.objectName() == "indexButtonSubmit":
            file = 'index-files.py'
            src = self.indexEditSrc
            dst = self.indexEditDst
            err_msg = self.indexMsg
            prog_bar = self.indexProgressBar
            cmb = self.indexComboType
        else:
            file = 'align-faces.py'
            src = self.alignEditSrc
            dst = self.alignEditDst
            err_msg = self.alignMsg
            prog_bar = self.alignProgressBar
            cmb = self.alignComboType

        # validate then run
        if self.validate_args(src, dst, err_msg):
            # run function in another thread
            worker = Worker(self.run_script, file, src, dst, err_msg, prog_bar, cmb, sender)
            worker.signals.result.connect(self.print_output)
            worker.signals.finished.connect(self.thread_complete)
            worker.signals.progress.connect(self.progress_fn)
            self.threadpool.start(worker)
        else:
            prog_bar.setVisible(False)
            err_msg.setVisible(True)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    sys.exit(app.exec_())
