from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QMessageBox, QTextEdit, QSpinBox,
    QDialog, QComboBox, QDialogButtonBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from database import Script, Review
from datetime import datetime
import sys
from pathlib import Path
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)
from booking.models import Review, User, ScriptRoom
import random

class ReviewsPage(QWidget):
    def __init__(self, session, auth_manager):
        super().__init__()
        self.session = session
        self.auth_manager = auth_manager
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # 标题和功能按钮区域
        header_layout = QHBoxLayout()
        
        # 标题
        title = QLabel("我的评价")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        # 添加自动生成评价按钮
        auto_review_btn = QPushButton("自动生成评价")
        auto_review_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c5ce7;
                color: white;
                border: none;
                padding: 8px 15px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #5b4ecd;
            }
        """)
        auto_review_btn.clicked.connect(self.auto_generate_review)
        header_layout.addWidget(auto_review_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.addLayout(header_layout)
        
        # 评价列表
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
        
        # 获取用户的评价
        reviews = self.session.query(Review).filter_by(
            user_id=self.auth_manager.current_user.id
        ).all()
        
        if not reviews:
            no_reviews = QLabel("暂无评价")
            no_reviews.setFont(QFont("Arial", 14))
            no_reviews.setAlignment(Qt.AlignmentFlag.AlignCenter)
            content_layout.addWidget(no_reviews)
        else:
            for review in reviews:
                script = self.session.query(Script).get(review.script_id)
                if script:
                    review_card = self.create_review_card(script, review)
                    content_layout.addWidget(review_card)
        
        content_layout.addStretch()
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
    
    def create_review_card(self, script, review):
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
        
        # 评分
        rating_layout = QHBoxLayout()
        rating_label = QLabel("评分：")
        rating_label.setFont(QFont("Arial", 12))
        rating_layout.addWidget(rating_label)
        
        rating = QLabel("★" * review.rating)
        rating.setStyleSheet("color: gold;")
        rating_layout.addWidget(rating)
        layout.addLayout(rating_layout)
        
        # 评价内容
        content = QLabel(review.content)
        content.setWordWrap(True)
        layout.addWidget(content)
        
        # 评价时间
        time = QLabel(f"评价时间：{review.created_at.strftime('%Y-%m-%d %H:%M')}")
        time.setStyleSheet("color: #666;")
        layout.addWidget(time)
        
        # 按钮
        buttons_layout = QHBoxLayout()
        
        edit_btn = QPushButton("编辑评价")
        edit_btn.setStyleSheet("""
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
        edit_btn.clicked.connect(lambda: self.edit_review(script, review))
        buttons_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("删除评价")
        delete_btn.setStyleSheet("""
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
        delete_btn.clicked.connect(lambda: self.delete_review(review.id))
        buttons_layout.addWidget(delete_btn)
        
        layout.addLayout(buttons_layout)
        return card
    
    def edit_review(self, script, review):
        dialog = QMessageBox(self)
        dialog.setWindowTitle("编辑评价")
        dialog.setText(f"编辑对《{script.title}》的评价")
        
        # 创建评分输入框
        rating_layout = QHBoxLayout()
        rating_label = QLabel("评分：")
        rating_spin = QSpinBox()
        rating_spin.setRange(1, 5)
        rating_spin.setValue(review.rating)
        rating_layout.addWidget(rating_label)
        rating_layout.addWidget(rating_spin)
        
        # 创建评价内容输入框
        content_edit = QTextEdit()
        content_edit.setPlainText(review.content)
        content_edit.setMinimumHeight(100)
        
        # 添加到对话框
        dialog.layout().addLayout(rating_layout)
        dialog.layout().addWidget(content_edit)
        
        # 添加按钮
        dialog.addButton("保存", QMessageBox.ButtonRole.AcceptRole)
        dialog.addButton("取消", QMessageBox.ButtonRole.RejectRole)
        
        if dialog.exec() == QMessageBox.DialogCode.Accepted:
            # 更新评价
            review.rating = rating_spin.value()
            review.content = content_edit.toPlainText()
            review.updated_at = datetime.now()
            
            try:
                self.session.commit()
                QMessageBox.information(self, "成功", "评价修改成功！")
                # 刷新页面
                self.init_ui()
            except Exception as e:
                self.session.rollback()
                QMessageBox.warning(self, "错误", f"修改失败：{str(e)}")
    
    def delete_review(self, review_id):
        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除这条评价吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            review = self.session.query(Review).get(review_id)
            if review:
                try:
                    self.session.delete(review)
                    self.session.commit()
                    QMessageBox.information(self, "成功", "评价已删除！")
                    # 刷新页面
                    self.init_ui()
                except Exception as e:
                    self.session.rollback()
                    QMessageBox.warning(self, "错误", f"删除失败：{str(e)}")
    
    def auto_generate_review(self):
        # 创建对话框来选择剧本
        dialog = QDialog(self)
        dialog.setWindowTitle("自动生成评价")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # 脚本选择提示
        script_label = QLabel("选择要评价的剧本：")
        script_label.setFont(QFont("Arial", 12))
        layout.addWidget(script_label)
        
        # 获取所有未评价过的剧本
        existing_reviews = self.session.query(Review.script_id).filter_by(
            user_id=self.auth_manager.current_user.id
        ).all()
        reviewed_script_ids = [r[0] for r in existing_reviews]
        
        # 获取未评价过的剧本
        available_scripts = self.session.query(Script).filter(
            ~Script.id.in_(reviewed_script_ids) if reviewed_script_ids else True
        ).all()
        
        if not available_scripts:
            QMessageBox.information(self, "提示", "您已评价过所有剧本！")
            return
        
        # 剧本下拉选择框
        script_combo = QComboBox()
        for script in available_scripts:
            script_combo.addItem(script.title, script.id)
        layout.addWidget(script_combo)
        
        # 评分选择
        rating_layout = QHBoxLayout()
        rating_label = QLabel("评分：")
        rating_label.setFont(QFont("Arial", 12))
        rating_layout.addWidget(rating_label)
        
        rating_combo = QComboBox()
        rating_combo.addItems(["随机评分", "1星", "2星", "3星", "4星", "5星"])
        rating_layout.addWidget(rating_combo)
        layout.addLayout(rating_layout)
        
        # 对话框按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        # 显示对话框
        if dialog.exec() == QDialog.DialogCode.Accepted:
            script_id = script_combo.currentData()
            selected_script = self.session.query(Script).get(script_id)
            
            # 根据选项生成评分
            rating_index = rating_combo.currentIndex()
            if rating_index == 0:  # 随机评分
                rating = random.randint(1, 5)
            else:
                rating = rating_index
            
            # 自动生成评价内容
            review_content = self.generate_review_text(selected_script, rating)
            
            # 创建并保存评价
            new_review = Review(
                user_id=self.auth_manager.current_user.id,
                script_id=script_id,
                rating=rating,
                content=review_content,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            try:
                self.session.add(new_review)
                self.session.commit()
                QMessageBox.information(self, "成功", "已自动生成评价！")
                # 刷新页面
                self.init_ui()
            except Exception as e:
                self.session.rollback()
                QMessageBox.warning(self, "错误", f"生成评价失败：{str(e)}")
    
    def generate_review_text(self, script, rating):
        """根据剧本类型和评分自动生成评价内容"""
        # 积极评价
        positive_reviews = [
            f"《{script.title}》是一部非常精彩的剧本，情节设计巧妙，人物关系复杂且合理，值得一试！",
            f"非常喜欢这个剧本的故事背景，《{script.title}》给了我很多惊喜，解谜过程很有成就感。",
            f"我和朋友们一起玩了《{script.title}》，剧情扣人心弦，难度适中，推荐给大家！",
            f"这个剧本故事情节很吸引人，剧本设计也很用心，《{script.title}》是我玩过的最好的剧本之一。",
            f"《{script.title}》的剧情转折很意外，角色设定也很有深度，非常值得体验。"
        ]
        
        # 中性评价
        neutral_reviews = [
            f"《{script.title}》整体还不错，但剧情有些地方不够连贯，值得一玩但有提升空间。",
            f"剧本《{script.title}》的设定比较新颖，但解谜过程稍显单调，期待后续有更多改进。",
            f"体验了《{script.title}》，剧情还算合理，但缺少高潮部分，整体感觉一般。",
            f"这个剧本的背景设定很有趣，但部分解谜环节设计不太合理，《{script.title}》还有改进空间。",
            f"《{script.title}》的故事有吸引力，但节奏控制不够好，中间部分稍显拖沓。"
        ]
        
        # 负面评价
        negative_reviews = [
            f"《{script.title}》的剧情设计有些混乱，线索之间缺乏联系，体验不太好。",
            f"这个剧本逻辑漏洞较多，解谜过程令人困惑，《{script.title}》体验一般。",
            f"《{script.title}》的流程设计不够合理，部分内容缺乏必要说明，不太推荐。",
            f"剧本《{script.title}》的故事情节过于简单，缺乏吸引力，有些失望。",
            f"《{script.title}》整体体验一般，角色塑造不够立体，剧情发展也比较平淡。"
        ]
        
        # 根据类型添加特定内容
        type_specific = {
            "推理": [
                "推理部分很有挑战性，",
                "线索设置巧妙，",
                "案件设计很有创意，",
                "推理过程引人入胜，",
                "谜题设计很精巧，"
            ],
            "恐怖": [
                "恐怖氛围营造得很到位，",
                "恐怖元素设计得很巧妙，",
                "紧张感和恐怖感很强，",
                "惊吓效果很好，",
                "恐怖情节很有层次感，"
            ],
            "情感": [
                "情感描写很细腻，",
                "人物情感刻画得很深刻，",
                "情感线安排很合理，",
                "感情戏很打动人，",
                "情感发展很自然，"
            ],
            "欢乐": [
                "笑点设计很巧妙，",
                "欢乐元素很丰富，",
                "喜剧效果很好，",
                "让人捧腹大笑，",
                "欢乐气氛很浓厚，"
            ]
        }
        
        # 根据评分选择对应评价
        if rating >= 4:  # 4-5星用积极评价
            base_review = random.choice(positive_reviews)
        elif rating >= 3:  # 3星用中性评价
            base_review = random.choice(neutral_reviews)
        else:  # 1-2星用负面评价
            base_review = random.choice(negative_reviews)
        
        # 添加类型特定内容
        if script.type in type_specific:
            type_comment = random.choice(type_specific[script.type])
            base_review = base_review.replace("。", f"，{type_comment}。")
        
        # 添加有关难度的评论
        difficulty_comments = {
            "简单": "难度适合新手，很容易上手。",
            "中等": "难度适中，有一定挑战性。",
            "困难": "难度较高，适合有经验的玩家。"
        }
        
        if script.difficulty in difficulty_comments:
            base_review += " " + difficulty_comments[script.difficulty]
        
        return base_review

if __name__ == "__main__":

    user = User.objects.get(username='user2')
    room = ScriptRoom.objects.first()

    Review.objects.create(user=user, script_room=room, rating=4, comment='非常棒的一次体验！')
