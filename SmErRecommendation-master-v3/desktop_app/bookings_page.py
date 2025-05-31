from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from database import Script, Booking, Store
from datetime import datetime

class BookingsPage(QWidget):
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
        title = QLabel("我的预约")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 状态筛选
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        filter_layout = QHBoxLayout(filter_frame)
        
        status_label = QLabel("状态：")
        status_label.setFont(QFont("Arial", 12))
        filter_layout.addWidget(status_label)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["全部", "待确认", "已确认", "已完成", "已取消"])
        self.status_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #dfe6e9;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        self.status_combo.currentTextChanged.connect(self.filter_bookings)
        filter_layout.addWidget(self.status_combo)
        
        filter_layout.addStretch()
        layout.addWidget(filter_frame)
        
        # 预约列表
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(20)
        
        # 获取预约列表
        self.update_bookings()
        
        self.content_layout.addStretch()
        scroll_area.setWidget(self.content_widget)
        layout.addWidget(scroll_area)
    
    def update_bookings(self, status="全部"):
        # 清除现有内容
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 获取预约列表
        query = self.session.query(Booking).filter_by(
            user_id=self.auth_manager.current_user.id
        )
        
        if status != "全部":
            query = query.filter_by(status=status)
        
        bookings = query.order_by(Booking.booking_time.desc()).all()
        
        if not bookings:
            no_bookings = QLabel("暂无预约")
            no_bookings.setFont(QFont("Arial", 14))
            no_bookings.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(no_bookings)
        else:
            for booking in bookings:
                script = self.session.query(Script).get(booking.script_id)
                store = self.session.query(Store).get(booking.store_id)
                if script and store:
                    booking_card = self.create_booking_card(script, store, booking)
                    self.content_layout.addWidget(booking_card)
    
    def filter_bookings(self):
        status = self.status_combo.currentText()
        self.update_bookings(status)
    
    def create_booking_card(self, script, store, booking):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        layout = QVBoxLayout(card)
        
        # 剧本标题
        title = QLabel(script.title)
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 门店信息
        store_info = QLabel(f"门店：{store.name}")
        store_info.setFont(QFont("Arial", 12))
        layout.addWidget(store_info)
        
        # 预约时间
        booking_time = QLabel(f"预约时间：{booking.booking_time.strftime('%Y-%m-%d %H:%M')}")
        booking_time.setFont(QFont("Arial", 12))
        layout.addWidget(booking_time)
        
        # 人数
        players = QLabel(f"人数：{booking.players}人")
        players.setFont(QFont("Arial", 12))
        layout.addWidget(players)
        
        # 价格
        price = QLabel(f"总价：¥{booking.total_price}")
        price.setFont(QFont("Arial", 12))
        layout.addWidget(price)
        
        # 状态
        status_layout = QHBoxLayout()
        status_label = QLabel("状态：")
        status_label.setFont(QFont("Arial", 12))
        status_layout.addWidget(status_label)
        
        status = QLabel(booking.status)
        status.setStyleSheet(self.get_status_style(booking.status))
        status_layout.addWidget(status)
        layout.addLayout(status_layout)
        
        # 按钮
        buttons_layout = QHBoxLayout()
        
        if booking.status == "待确认":
            cancel_btn = QPushButton("取消预约")
            cancel_btn.setStyleSheet("""
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
            cancel_btn.clicked.connect(lambda: self.cancel_booking(booking.id))
            buttons_layout.addWidget(cancel_btn)
        
        if booking.status == "已完成":
            review_btn = QPushButton("评价")
            review_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6c5ce7;
                    color: white;
                    border: none;
                    padding: 5px 15px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #a29bfe;
                }
            """)
            review_btn.clicked.connect(lambda: self.review_script(script.id))
            buttons_layout.addWidget(review_btn)
        
        layout.addLayout(buttons_layout)
        return card
    
    def get_status_style(self, status):
        styles = {
            "待确认": "color: #fdcb6e;",
            "已确认": "color: #00b894;",
            "已完成": "color: #0984e3;",
            "已取消": "color: #d63031;"
        }
        return styles.get(status, "")
    
    def cancel_booking(self, booking_id):
        reply = QMessageBox.question(
            self,
            "确认取消",
            "确定要取消这个预约吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            booking = self.session.query(Booking).get(booking_id)
            if booking:
                try:
                    booking.status = "已取消"
                    booking.updated_at = datetime.now()
                    self.session.commit()
                    QMessageBox.information(self, "成功", "预约已取消！")
                    # 刷新页面
                    self.update_bookings(self.status_combo.currentText())
                except Exception as e:
                    self.session.rollback()
                    QMessageBox.warning(self, "错误", f"取消失败：{str(e)}")
    
    def review_script(self, script_id):
        # TODO: 跳转到评价页面
        pass 