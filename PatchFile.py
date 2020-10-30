import sys
import os
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QLineEdit
from PyQt5.QtCore import Qt
import hashlib
import shutil
import re


with open("patch_path.txt", "r+") as f:
    patchPath = f.readline()


class PatchGenGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PatchFileGen")
        self.setWindowIcon(QtGui.QIcon("miku.png"))
        self.resize(400, 300)
        self.line = QLineEdit(self)
        self.line.move(100, 50)
        self.line.resize(200, 32)
        self.line.textChanged.connect(self.on_text_changed)

        self.btn = QPushButton('Patch', self)
        self.btn.setDisabled(True)
        self.btn.setGeometry(100, 100, 200, 50)
        self.btn.clicked.connect(self.makePatch)
        self.btn.setShortcut("Return")
        self.setAcceptDrops(True)
        self.pak = ""

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    self.pak = str(url.toLocalFile())
                else:
                    self.pak = str(url.toString())
            self.on_text_changed()
        else:
            event.ignore()

    def makePatch(self):
        file_name = self.pak
        versionInput = self.line.text()
        if len(versionInput) == 1:
            versionInput = f"00{versionInput}"
        elif len(versionInput) == 2:
            versionInput = f"0{versionInput}"
        elif len(versionInput) == 3:
            versionInput = f"{versionInput}"
        else:
            sys.exit()

        path = f"{patchPath}00000{versionInput}"
        try:
            os.mkdir(path)
        except OSError:
            pass

        with open(f"{patchPath}PatchInfoServer.cfg", "w") as versionCfg:
            versionCfg.write(f"Version {versionInput}")

        # Make Patch.md5
        with open(f"{patchPath}00000{versionInput}/Patch00000{versionInput}.pak.md5", "w") as patchMD5:
            patchMD5.write(f"{hashlib.md5(open(file_name, 'rb').read()).hexdigest()}\n")

        # Make Patch.txt file
        with open(file_name, "rb") as pak:
            findregex = re.findall(rb"(resource.*?|mapdata.*?)\x00\B", pak.read())
            decoded = [byte_out.decode("utf-8") for byte_out in findregex]
            output_decoded = map(lambda decoded: f"D {decoded}", decoded)
            output_txt = "\n".join(list(output_decoded))

        with open(f"{patchPath}00000{versionInput}/Patch00000{versionInput}.txt", "w") as patchTxt:
            patchTxt.write(output_txt)

        try:
            shutil.copy2(file_name, f"{patchPath}00000{versionInput}/Patch00000{versionInput}.pak")
        except shutil.SameFileError:
            pass

        sys.exit()

    @QtCore.pyqtSlot()
    def on_text_changed(self):
        self.btn.setEnabled(bool(self.line.text()) and bool(self.pak != ""))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    MainGUI = PatchGenGUI()
    MainGUI.show()

    sys.exit(app.exec_())
