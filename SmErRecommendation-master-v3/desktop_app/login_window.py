from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebEngineCore import QWebEngineHttpRequest
from PyQt5.QtNetwork import QNetworkCookie
from PyQt5.QtWidgets import QFrame, QDesktopWidget
from werkzeug.security import generate_password_hash
from database import User

class LoginWindow(QWidget):
    def __init__(self, session, auth_manager):
        super().__init__()
        self.session = session
        self.auth_manager = auth_manager
        self.init_ui()
    
    def init_ui(self):
        screen = QDesktopWidget().screenGeometry()
        screen_width, screen_height = screen.width(), screen.height()

        self.setWindowTitle("登录")

        window_width = int(screen_width * 0.5)  # 80% of screen width
        window_height = int(screen_height * 0.5)

        # self.setFixedSize(2048, 2048)
        self.setGeometry(
            (screen_width - window_width) // 2,  # Center X
            (screen_height - window_height) // 2,  # Center Y
            window_width, 
            window_height
        )
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Web视图
        self.web_view = QWebEngineView()
        self.web_view.setUrl(QUrl("http://localhost:8001/login"))
        
        # 监听登录成功
        self.web_view.loadFinished.connect(self.check_login_status)
        
        layout.addWidget(self.web_view)
    
    def check_login_status(self):
        # 检查是否登录成功
        if self.auth_manager.is_logged_in():
            self.close()

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "错误", "请输入用户名和密码！")
            return
        
        if self.auth_manager.login(username, password):
            self.close()
        else:
            QMessageBox.warning(self, "错误", "用户名或密码错误！")
    
    def show_register(self):
        form_frame = self.findChild(QFrame)
        form_frame.hide()
        self.register_frame.show()
    
    def show_login(self):
        self.register_frame.hide()
        form_frame = self.findChild(QFrame)
        form_frame.show()
    
    def register(self):
        username = self.reg_username_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text()
        password = self.reg_password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        # 验证输入
        if not all([username, email, phone, password, confirm_password]):
            QMessageBox.warning(self, "错误", "请填写所有字段！")
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "错误", "两次输入的密码不一致！")
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "错误", "密码长度不能小于6位！")
            return
        
        # 检查用户名是否已存在
        if self.session.query(User).filter_by(username=username).first():
            QMessageBox.warning(self, "错误", "用户名已存在！")
            return
        
        # 创建新用户
        new_user = User(
            username=username,
            email=email,
            phone=phone,
            password=generate_password_hash(password),
            gender="男"  # 默认性别
        )
        
        try:
            self.session.add(new_user)
            self.session.commit()
            QMessageBox.information(self, "成功", "注册成功！")
            self.show_login()
        except Exception as e:
            self.session.rollback()
            QMessageBox.warning(self, "错误", f"注册失败：{str(e)}") 