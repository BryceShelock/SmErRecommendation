from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QLineEdit, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from database import Script, Store

class HomePage(QWidget):
    def __init__(self, session, auth_manager):
        super().__init__()
        self.session = session
        self.auth_manager = auth_manager
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Hero Section
        hero_frame = QFrame()
        hero_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 40px;
            }
        """)
        hero_layout = QVBoxLayout(hero_frame)
        
        title = QLabel("探索精彩剧本杀体验")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        hero_layout.addWidget(title)
        
        subtitle = QLabel("发现最受欢迎的剧本杀密室，预约您的心仪剧本，开启精彩推理之旅。")
        subtitle.setFont(QFont("Arial", 12))
        hero_layout.addWidget(subtitle)
        
        buttons_layout = QHBoxLayout()
        browse_btn = QPushButton("浏览门店")
        browse_btn.setStyleSheet("""
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
        buttons_layout.addWidget(browse_btn)
        
        register_btn = QPushButton("立即注册")
        register_btn.setStyleSheet("""
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
        buttons_layout.addWidget(register_btn)
        hero_layout.addLayout(buttons_layout)
        
        layout.addWidget(hero_frame)
        
        # 搜索框
        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        search_layout = QHBoxLayout(search_frame)
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("搜索剧本、门店...")
        search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #dfe6e9;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        search_layout.addWidget(search_input)
        
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
        search_layout.addWidget(city_combo)
        
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
        search_layout.addWidget(type_combo)
        
        search_btn = QPushButton("搜索")
        search_btn.setStyleSheet("""
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
        search_layout.addWidget(search_btn)
        
        layout.addWidget(search_frame)
        
        # 热门剧本
        scripts_frame = QFrame()
        scripts_layout = QVBoxLayout(scripts_frame)
        
        scripts_title = QLabel("热门剧本")
        scripts_title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        scripts_layout.addWidget(scripts_title)
        
        scripts_content = QHBoxLayout()
        scripts = self.session.query(Script).order_by(Script.rating.desc()).limit(3).all()
        
        for script in scripts:
            script_card = self.create_script_card(script)
            scripts_content.addWidget(script_card)
        
        scripts_layout.addLayout(scripts_content)
        layout.addWidget(scripts_frame)
        
        # 推荐门店
        stores_frame = QFrame()
        stores_layout = QVBoxLayout(stores_frame)
        
        stores_title = QLabel("推荐门店")
        stores_title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        stores_layout.addWidget(stores_title)
        
        stores_content = QHBoxLayout()
        stores = self.session.query(Store).order_by(Store.rating.desc()).limit(3).all()
        
        for store in stores:
            store_card = self.create_store_card(store)
            stores_content.addWidget(store_card)
        
        stores_layout.addLayout(stores_content)
        layout.addWidget(stores_frame)
        
        # 系统功能
        features_frame = QFrame()
        features_layout = QVBoxLayout(features_frame)
        
        features_title = QLabel("系统功能")
        features_title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        features_layout.addWidget(features_title)
        
        features_content = QHBoxLayout()
        features = [
            ("安全保障", "所有门店经过严格筛选，确保安全可靠"),
            ("便捷预约", "在线预约系统，随时随地轻松预订"),
            ("优质体验", "精选优质剧本，专业DM带本")
        ]
        
        for title, desc in features:
            feature_card = QFrame()
            feature_card.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 10px;
                    padding: 20px;
                }
            """)
            feature_layout = QVBoxLayout(feature_card)
            
            feature_title = QLabel(title)
            feature_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            feature_layout.addWidget(feature_title)
            
            feature_desc = QLabel(desc)
            feature_desc.setWordWrap(True)
            feature_layout.addWidget(feature_desc)
            
            features_content.addWidget(feature_card)
        
        features_layout.addLayout(features_content)
        layout.addWidget(features_frame)
        
        layout.addStretch()
    
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
        layout.addLayout(bottom_layout)
        
        return card
    
    def create_store_card(self, store):
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
        title = QLabel(store.name)
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_layout.addWidget(title)
        
        rating = QLabel(f"{store.rating} ★")
        rating.setStyleSheet("color: gold;")
        title_layout.addWidget(rating)
        layout.addLayout(title_layout)
        
        # 地址
        address = QLabel(store.address)
        address.setWordWrap(True)
        layout.addWidget(address)
        
        # 电话
        phone = QLabel(f"电话：{store.phone}")
        layout.addWidget(phone)
        
        # 按钮
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
        layout.addWidget(detail_btn)
        
        return card 