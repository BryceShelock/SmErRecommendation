import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("剧本杀推荐系统")
        self.resize(1200, 800)
        self.browser = QWebEngineView()
        # 加载首页
        self.browser.load(QUrl("http://127.0.0.1:8001"))
        self.setCentralWidget(self.browser)

def main():
    app = QApplication(sys.argv)
    window = BrowserWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 