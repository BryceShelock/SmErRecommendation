from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from home_page import HomePage
from profile_page import ProfilePage
from favorites_page import FavoritesPage
from reviews_page import ReviewsPage
from bookings_page import BookingsPage

class MainWindow(QMainWindow):
    def __init__(self, session, auth_manager):
        super().__init__()
        self.session = session
        self.auth_manager = auth_manager
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("剧本杀推荐系统")
        self.setMinimumSize(1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 侧边栏
        sidebar = QFrame()
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #2d3436;
                min-width: 200px;
                max-width: 200px;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Logo
        logo = QLabel("剧本杀推荐")
        logo.setFont(QFont("Arial", 20, QFont.Bold))
        logo.setStyleSheet("""
            QLabel {
                color: white;
                padding: 20px;
                background-color: #1e272e;
            }
        """)
        logo.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(logo)
        
        # 导航按钮
        self.nav_buttons = []
        
        # 首页
        home_btn = self.create_nav_button("首页", "bi-house")
        home_btn.clicked.connect(lambda: self.load_page("index"))
        sidebar_layout.addWidget(home_btn)
        self.nav_buttons.append(home_btn)
        
        # 我的收藏
        favorites_btn = self.create_nav_button("我的收藏", "bi-heart")
        favorites_btn.clicked.connect(lambda: self.load_page("favorites"))
        sidebar_layout.addWidget(favorites_btn)
        self.nav_buttons.append(favorites_btn)
        
        # 我的预约
        bookings_btn = self.create_nav_button("我的预约", "bi-calendar")
        bookings_btn.clicked.connect(lambda: self.load_page("bookings"))
        sidebar_layout.addWidget(bookings_btn)
        self.nav_buttons.append(bookings_btn)
        
        # 我的评价
        reviews_btn = self.create_nav_button("我的评价", "bi-star")
        reviews_btn.clicked.connect(lambda: self.load_page("reviews"))
        sidebar_layout.addWidget(reviews_btn)
        self.nav_buttons.append(reviews_btn)
        
        # 个人中心
        profile_btn = self.create_nav_button("个人中心", "bi-person")
        profile_btn.clicked.connect(lambda: self.load_page("profile"))
        sidebar_layout.addWidget(profile_btn)
        self.nav_buttons.append(profile_btn)
        
        sidebar_layout.addStretch()
        
        # 退出登录
        logout_btn = self.create_nav_button("退出登录", "bi-box-arrow-right")
        logout_btn.clicked.connect(self.logout)
        sidebar_layout.addWidget(logout_btn)
        
        layout.addWidget(sidebar)
        
        # 内容区域
        content = QFrame()
        content.setStyleSheet("""
            QFrame {
                background-color: #f5f6fa;
            }
        """)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Web视图
        self.web_view = QWebEngineView()
        content_layout.addWidget(self.web_view)
        
        layout.addWidget(content)
        
        # 默认加载首页
        self.load_page("index")
    
    def create_nav_button(self, text, icon):
        button = QPushButton(text)
        button.setFont(QFont("Arial", 12))
        button.setStyleSheet("""
            QPushButton {
                color: white;
                border: none;
                padding: 15px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #1e272e;
            }
            QPushButton:checked {
                background-color: #6c5ce7;
            }
        """)
        button.setCheckable(True)
        return button
    
    def load_page(self, page_name):
        page_map = {
            "index": "index",
            "favorites": "my-favorites/",
            "bookings": "my-bookings/",
            "reviews": "my-reviews/",
            "profile": "profile/",
        }
        url_path = page_map.get(page_name, "index")
        url = QUrl(f"http://localhost:8001/{url_path}")
        self.web_view.load(url)
    
    def get_page_index(self, page_name):
        pages = ["index", "favorites", "bookings", "reviews", "profile"]
        return pages.index(page_name) if page_name in pages else 0
    
    def logout(self):
        self.auth_manager.logout()
        self.close() 