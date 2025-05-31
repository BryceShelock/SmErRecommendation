from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame

class RegisterWindow(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.auth_manager = parent.auth_manager
        
        # 设置窗口属性
        self.setWindowTitle("注册")
        self.setFixedSize(400, 400)
        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint)
        
        # 初始化UI
        self.init_ui()
    
    def init_ui(self):
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # 标题
        title = QLabel("注册")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 表单容器
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
            }
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(20)
        
        # 用户名
        username_label = QLabel("用户名")
        username_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        form_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #dfe6e9;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        form_layout.addWidget(self.username_input)
        
        # 密码
        password_label = QLabel("密码")
        password_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        form_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #dfe6e9;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        form_layout.addWidget(self.password_input)
        
        # 确认密码
        confirm_label = QLabel("确认密码")
        confirm_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        form_layout.addWidget(confirm_label)
        
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("请再次输入密码")
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #dfe6e9;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        form_layout.addWidget(self.confirm_input)
        
        # 邮箱
        email_label = QLabel("邮箱")
        email_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        form_layout.addWidget(email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("请输入邮箱")
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #dfe6e9;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        form_layout.addWidget(self.email_input)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #6c5ce7;
                border: 2px solid #6c5ce7;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f5f6fa;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        register_btn = QPushButton("注册")
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c5ce7;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #a29bfe;
            }
        """)
        register_btn.clicked.connect(self.register)
        button_layout.addWidget(register_btn)
        
        form_layout.addLayout(button_layout)
        layout.addWidget(form_frame)
    
    def register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        confirm = self.confirm_input.text().strip()
        email = self.email_input.text().strip()
        
        if not username:
            QMessageBox.warning(self, "警告", "请输入用户名")
            return
        
        if not password:
            QMessageBox.warning(self, "警告", "请输入密码")
            return
        
        if not confirm:
            QMessageBox.warning(self, "警告", "请确认密码")
            return
        
        if not email:
            QMessageBox.warning(self, "警告", "请输入邮箱")
            return
        
        if password != confirm:
            QMessageBox.critical(self, "错误", "两次输入的密码不一致")
            return
        
        success, message = self.auth_manager.register(username, password, email)
        if success:
            QMessageBox.information(self, "成功", message)
            self.accept()
        else:
            QMessageBox.critical(self, "错误", message) 