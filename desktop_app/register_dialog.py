from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt

class RegisterDialog(QDialog):
    def __init__(self, auth_manager, parent=None):
        super().__init__(parent)
        self.auth_manager = auth_manager
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('注册')
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel('用户注册')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet('font-size: 20px; margin: 20px;')
        layout.addWidget(title)
        
        # 用户名输入
        username_layout = QHBoxLayout()
        username_label = QLabel('用户名:')
        self.username_input = QLineEdit()
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)
        
        # 密码输入
        password_layout = QHBoxLayout()
        password_label = QLabel('密码:')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)
        
        # 确认密码
        confirm_layout = QHBoxLayout()
        confirm_label = QLabel('确认密码:')
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        confirm_layout.addWidget(confirm_label)
        confirm_layout.addWidget(self.confirm_input)
        layout.addLayout(confirm_layout)
        
        # 邮箱输入
        email_layout = QHBoxLayout()
        email_label = QLabel('邮箱:')
        self.email_input = QLineEdit()
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)
        layout.addLayout(email_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 注册按钮
        register_button = QPushButton('注册')
        register_button.clicked.connect(self.handle_register)
        button_layout.addWidget(register_button)
        
        # 取消按钮
        cancel_button = QPushButton('取消')
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 14px;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.setLayout(layout)
    
    def handle_register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_input.text()
        email = self.email_input.text()
        
        if not username or not password or not confirm_password or not email:
            QMessageBox.warning(self, '错误', '请填写所有字段')
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, '错误', '两次输入的密码不一致')
            return
        
        success, message = self.auth_manager.register(username, password, email)
        if success:
            QMessageBox.information(self, '成功', message)
            self.accept()
        else:
            QMessageBox.warning(self, '错误', message) 