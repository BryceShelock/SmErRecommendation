from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from database import Script, Favorite

class FavoritesPage(QWidget):
    def __init__(self, session, auth_manager):
        super().__init__()
        self.session = session
        self.auth_manager = auth_manager
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # 标题
        title = QLabel("我的收藏")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 收藏列表
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        
        # 获取收藏的剧本
        favorites = self.session.query(Favorite).filter_by(
            user_id=self.auth_manager.current_user.id
        ).all()
        
        if not favorites:
            no_favorites = QLabel("暂无收藏的剧本")
            no_favorites.setFont(QFont("Arial", 14))
            no_favorites.setAlignment(Qt.AlignmentFlag.AlignCenter)
            content_layout.addWidget(no_favorites)
        else:
            for favorite in favorites:
                script = self.session.query(Script).get(favorite.script_id)
                if script:
                    script_card = self.create_script_card(script)
                    content_layout.addWidget(script_card)
        
        content_layout.addStretch()
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
    
    def create_script_card(self, script):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        layout = QVBoxLayout(card)
        
        # 标题和评分
        title_layout = QHBoxLayout()
        title = QLabel(script.title)
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_layout.addWidget(title)
        
        rating = QLabel(f"{script.rating} ★")
        rating.setStyleSheet("color: gold;")
        title_layout.addWidget(rating)
        layout.addLayout(title_layout)
        
        # 描述
        desc = QLabel(script.description)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # 标签
        tags_layout = QHBoxLayout()
        type_tag = QLabel(script.type)
        type_tag.setStyleSheet("""
            QLabel {
                background-color: #a29bfe;
                color: white;
                padding: 5px 10px;
                border-radius: 5px;
            }
        """)
        tags_layout.addWidget(type_tag)
        
        difficulty_tag = QLabel(f"难度: {script.difficulty}")
        difficulty_tag.setStyleSheet("""
            QLabel {
                background-color: #ff7675;
                color: white;
                padding: 5px 10px;
                border-radius: 5px;
            }
        """)
        tags_layout.addWidget(difficulty_tag)
        layout.addLayout(tags_layout)
        
        # 价格和按钮
        bottom_layout = QHBoxLayout()
        price = QLabel(f"¥{script.price}/人")
        price.setStyleSheet("""
            QLabel {
                color: #6c5ce7;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        bottom_layout.addWidget(price)
        
        detail_btn = QPushButton("查看详情")
        detail_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #6c5ce7;
                border: 2px solid #6c5ce7;
                padding: 5px 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f5f6fa;
            }
        """)
        bottom_layout.addWidget(detail_btn)
        
        remove_btn = QPushButton("取消收藏")
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff7675;
                color: white;
                border: none;
                padding: 5px 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #fab1a0;
            }
        """)
        remove_btn.clicked.connect(lambda: self.remove_favorite(script.id))
        bottom_layout.addWidget(remove_btn)
        
        layout.addLayout(bottom_layout)
        return card
    
    def remove_favorite(self, script_id):
        reply = QMessageBox.question(
            self,
            "确认取消收藏",
            "确定要取消收藏这个剧本吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            favorite = self.session.query(Favorite).filter_by(
                user_id=self.auth_manager.current_user.id,
                script_id=script_id
            ).first()
            
            if favorite:
                try:
                    self.session.delete(favorite)
                    self.session.commit()
                    QMessageBox.information(self, "成功", "已取消收藏！")
                    # 刷新页面
                    self.init_ui()
                except Exception as e:
                    self.session.rollback()
                    QMessageBox.warning(self, "错误", f"取消收藏失败：{str(e)}") 