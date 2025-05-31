from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QListWidget, QListWidgetItem, QLineEdit, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from database import User, Script, Review, Favorite, Booking
from werkzeug.security import generate_password_hash

class ProfilePage(QWidget):
    def __init__(self, session, auth_manager):
        super().__init__()
        self.session = session
        self.auth_manager = auth_manager
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # 个人信息卡片
        profile_frame = QFrame()
        profile_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        profile_layout = QVBoxLayout(profile_frame)
        
        title = QLabel("个人信息")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        profile_layout.addWidget(title)
        
        # 用户信息
        user = self.session.query(User).filter_by(id=self.auth_manager.current_user.id).first()
        
        # 用户名
        username_layout = QHBoxLayout()
        username_label = QLabel("用户名：")
        username_label.setFont(QFont("Arial", 12))
        username_layout.addWidget(username_label)
        
        self.username_input = QLineEdit(user.username)
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #dfe6e9;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        username_layout.addWidget(self.username_input)
        profile_layout.addLayout(username_layout)
        
        # 邮箱
        email_layout = QHBoxLayout()
        email_label = QLabel("邮箱：")
        email_label.setFont(QFont("Arial", 12))
        email_layout.addWidget(email_label)
        
        self.email_input = QLineEdit(user.email)
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #dfe6e9;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        email_layout.addWidget(self.email_input)
        profile_layout.addLayout(email_layout)
        
        # 手机号
        phone_layout = QHBoxLayout()
        phone_label = QLabel("手机号：")
        phone_label.setFont(QFont("Arial", 12))
        phone_layout.addWidget(phone_label)
        
        self.phone_input = QLineEdit(user.phone)
        self.phone_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #dfe6e9;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        phone_layout.addWidget(self.phone_input)
        profile_layout.addLayout(phone_layout)
        
        # 性别
        gender_layout = QHBoxLayout()
        gender_label = QLabel("性别：")
        gender_label.setFont(QFont("Arial", 12))
        gender_layout.addWidget(gender_label)
        
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["男", "女"])
        self.gender_combo.setCurrentText(user.gender)
        self.gender_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #dfe6e9;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        gender_layout.addWidget(self.gender_combo)
        profile_layout.addLayout(gender_layout)
        
        # 保存按钮
        save_btn = QPushButton("保存修改")
        save_btn.setStyleSheet("""
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
        save_btn.clicked.connect(self.save_profile)
        profile_layout.addWidget(save_btn)
        
        layout.addWidget(profile_frame)
        
        # 修改密码卡片
        password_frame = QFrame()
        password_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        password_layout = QVBoxLayout(password_frame)
        
        password_title = QLabel("修改密码")
        password_title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        password_layout.addWidget(password_title)
        
        # 原密码
        old_password_layout = QHBoxLayout()
        old_password_label = QLabel("原密码：")
        old_password_label.setFont(QFont("Arial", 12))
        old_password_layout.addWidget(old_password_label)
        
        self.old_password_input = QLineEdit()
        self.old_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.old_password_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #dfe6e9;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        old_password_layout.addWidget(self.old_password_input)
        password_layout.addLayout(old_password_layout)
        
        # 新密码
        new_password_layout = QHBoxLayout()
        new_password_label = QLabel("新密码：")
        new_password_label.setFont(QFont("Arial", 12))
        new_password_layout.addWidget(new_password_label)
        
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #dfe6e9;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        new_password_layout.addWidget(self.new_password_input)
        password_layout.addLayout(new_password_layout)
        
        # 确认密码
        confirm_password_layout = QHBoxLayout()
        confirm_password_label = QLabel("确认密码：")
        confirm_password_label.setFont(QFont("Arial", 12))
        confirm_password_layout.addWidget(confirm_password_label)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #dfe6e9;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        confirm_password_layout.addWidget(self.confirm_password_input)
        password_layout.addLayout(confirm_password_layout)
        
        # 修改密码按钮
        change_password_btn = QPushButton("修改密码")
        change_password_btn.setStyleSheet("""
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
        change_password_btn.clicked.connect(self.change_password)
        password_layout.addWidget(change_password_btn)
        
        layout.addWidget(password_frame)
        layout.addStretch()
    
    def save_profile(self):
        user = self.session.query(User).filter_by(id=self.auth_manager.current_user.id).first()
        
        # 更新用户信息
        user.username = self.username_input.text()
        user.email = self.email_input.text()
        user.phone = self.phone_input.text()
        user.gender = self.gender_combo.currentText()
        
        try:
            self.session.commit()
            QMessageBox.information(self, "成功", "个人信息修改成功！")
        except Exception as e:
            self.session.rollback()
            QMessageBox.warning(self, "错误", f"修改失败：{str(e)}")
    
    def change_password(self):
        old_password = self.old_password_input.text()
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        # 验证原密码
        if not self.auth_manager.verify_password(old_password):
            QMessageBox.warning(self, "错误", "原密码错误！")
            return
        
        # 验证新密码
        if new_password != confirm_password:
            QMessageBox.warning(self, "错误", "两次输入的新密码不一致！")
            return
        
        if len(new_password) < 6:
            QMessageBox.warning(self, "错误", "新密码长度不能小于6位！")
            return
        
        # 更新密码
        user = self.session.query(User).filter_by(id=self.auth_manager.current_user.id).first()
        user.password = generate_password_hash(new_password)
        
        try:
            self.session.commit()
            QMessageBox.information(self, "成功", "密码修改成功！")
            # 清空输入框
            self.old_password_input.clear()
            self.new_password_input.clear()
            self.confirm_password_input.clear()
        except Exception as e:
            self.session.rollback()
            QMessageBox.warning(self, "错误", f"修改失败：{str(e)}")

    def create_stat_card(self, title, value, icon):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #f5f6fa;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        layout = QVBoxLayout(card)
        
        # 图标
        icon_label = QLabel(f"<i class='bi {icon}'></i>")
        icon_label.setStyleSheet("""
            QLabel {
                color: #6c5ce7;
                font-size: 24px;
            }
        """)
        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 数值
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        value_label.setStyleSheet("color: #2d3436;")
        layout.addWidget(value_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 标题
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #636e72;")
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        return card 