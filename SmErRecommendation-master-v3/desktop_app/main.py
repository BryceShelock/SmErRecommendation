import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
import os

# 先配置 Django 环境（如果需要）
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'script_murder_system.settings')
import django
django.setup()

from database import Session
from auth_manager import AuthManager
from login_window import LoginWindow
from main_window import MainWindow


def main():
    # 创建应用
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.png"))
    
    # 创建数据库会话
    session = Session()
    
    # 创建认证管理器
    auth_manager = AuthManager(session)
    
    # 创建登录窗口
    login_window = LoginWindow(session, auth_manager)
    login_window.show()
    
    # 启动应用程序事件循环
    exit_code = app.exec_()
    
    # 如果登录成功，显示主窗口
    if exit_code == 0 and auth_manager.is_logged_in():
        main_window = MainWindow(session, auth_manager)
        main_window.show()
        sys.exit(app.exec_())
    else:
        sys.exit(exit_code)

if __name__ == "__main__":
    main()