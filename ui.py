import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot
import threading
import math
from audio import PlaybackAudio



class App(QMainWindow,QWidget):
    def __init__(self):
        super().__init__()
        self.title = "Audio Analyzer"
        self.is_running = True
        self.inputs = []
        self.init_ui()
        self.ui_audio_thread = threading.Thread(target=self.displayItems)
        self.ui_audio_thread.start()
        

    def init_ui(self):

        self.grid_layout = QGridLayout()
        self.addTracker()

        self.setWindowTitle(self.title)

        self.note_label = QLabel("Note:",self)
        self.freq_label = QLabel("Frequency:",self)
        self.amp_label = QLabel("Amplitude:",self)

        self.grid_layout.addWidget(self.note_label,0,0)
        self.grid_layout.addWidget(self.freq_label,0,1)
        self.grid_layout.addWidget(self.amp_label,0,2)

        self.central = QWidget()
        self.central.setLayout(self.grid_layout)
        self.setCentralWidget(self.central)

        self.show()

    def addTracker(self):
        self.audio = PlaybackAudio()
        ### add threading to prevent freezing in while loop
        self.audio_thread = threading.Thread(target=self.audio.record_audio)
        self.audio_thread.start()
    def displayItems(self):
        while self.is_running:
            # {0: note,1: amp,2: freq}
            items = self.audio.get_items()
            self.note_label.setText("Note:{}".format(items[0]))
            self.amp_label.setText("Amplitude:{}".format(int(items[1])))
            self.freq_label.setText("Frequency:{}".format(int(items[2])))

    def closeEvent(self,event):
        self.is_running = False
        self.audio.stop_recording()
        self.close()
  
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())