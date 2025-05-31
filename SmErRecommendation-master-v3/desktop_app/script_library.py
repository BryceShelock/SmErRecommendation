from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QScrollArea, QFrame, QCheckBox, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from database import Script, StoreScript, Store

class ScriptLibraryPage(QWidget):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # 标题
        title = QLabel("剧本库")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 搜索和筛选区域
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        filter_layout = QHBoxLayout(filter_frame)
        
        # 搜索框
        search_input = QLineEdit()
        search_input.setPlaceholderText("搜索剧本...")
        search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #dfe6e9;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        filter_layout.addWidget(search_input)
        
        # 城市选择
        city_combo = QComboBox()
        city_combo.addItems(["选择城市", "北京", "上海", "广州", "深圳"])
        city_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 1px solid #dfe6e9;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        filter_layout.addWidget(city_combo)
        
        # 剧本类型
        type_combo = QComboBox()
        type_combo.addItems(["剧本类型", "推理", "恐怖", "情感", "欢乐"])
        type_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 1px solid #dfe6e9;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        filter_layout.addWidget(type_combo)
        
        # 排序方式
        sort_combo = QComboBox()
        sort_combo.addItems(["按热度排序", "按评分排序", "按价格从低到高", "按价格从高到低"])
        sort_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 1px solid #dfe6e9;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        filter_layout.addWidget(sort_combo)
        
        layout.addWidget(filter_frame)
        
        # 剧本列表区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        scripts_widget = QWidget()
        scripts_layout = QVBoxLayout(scripts_widget)
        
        # 获取剧本列表
        scripts = self.session.query(Script).all()
        
        for script in scripts:
            script_card = self.create_script_card(script)
            scripts_layout.addWidget(script_card)
        
        scripts_layout.addStretch()
        scroll_area.setWidget(scripts_widget)
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
        layout = QHBoxLayout(card)
        
        # 剧本封面
        cover_label = QLabel()
        cover_label.setFixedSize(200, 150)
        cover_label.setStyleSheet("""
            QLabel {
                background-color: #f5f6fa;
                border-radius: 5px;
            }
        """)
        layout.addWidget(cover_label)
        
        # 剧本信息
        info_layout = QVBoxLayout()
        
        # 标题和评分
        title_layout = QHBoxLayout()
        title = QLabel(script.title)
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_layout.addWidget(title)
        
        rating = QLabel(f"{script.rating} ★")
        rating.setStyleSheet("color: gold;")
        title_layout.addWidget(rating)
        info_layout.addLayout(title_layout)
        
        # 描述
        desc = QLabel(script.description)
        desc.setWordWrap(True)
        info_layout.addWidget(desc)
        
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
        info_layout.addLayout(tags_layout)
        
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
        info_layout.addLayout(bottom_layout)
        
        layout.addLayout(info_layout)
        return card 