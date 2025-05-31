import sys
from PyQt5.QtWidgets import QApplication
from database import init_db
from main import MainWindow

def main():
    # 初始化数据库
    session = init_db()
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle("Fusion")
    
    # 创建主窗口
    window = MainWindow(session)
    window.show()
    
    # 运行应用
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 