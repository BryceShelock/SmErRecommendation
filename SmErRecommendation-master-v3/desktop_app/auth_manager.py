from sqlalchemy.orm import Session
from database import User, UserRole
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
import re

class AuthManager:
    def __init__(self, session: Session):
        self.session = session
        self.current_user = None
    
    def login(self, username: str, password: str) -> bool:
        """用户登录"""
        user = self.session.query(User).filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            self.current_user = user
            return True
        return False
    
    def register(self, username: str, password: str, email: str) -> tuple[bool, str]:
        """用户注册"""
        # 验证用户名
        if not re.match(r'^[a-zA-Z0-9_]{4,20}$', username):
            return False, "用户名必须是4-20位字母、数字或下划线"
        
        # 验证密码
        if not re.match(r'^[a-zA-Z0-9_]{6,20}$', password):
            return False, "密码必须是6-20位字母、数字或下划线"
        
        # 验证邮箱
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return False, "邮箱格式不正确"
        
        # 检查用户名是否已存在
        if self.session.query(User).filter_by(username=username).first():
            return False, "用户名已存在"
        
        # 检查邮箱是否已存在
        if self.session.query(User).filter_by(email=email).first():
            return False, "邮箱已被注册"
        
        # 创建新用户
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            email=email,
            role=UserRole.USER
        )
        
        try:
            self.session.add(user)
            self.session.commit()
            return True, "注册成功"
        except Exception as e:
            self.session.rollback()
            return False, f"注册失败: {str(e)}"
    
    def logout(self):
        """用户登出"""
        self.current_user = None
    
    def is_logged_in(self) -> bool:
        """检查用户是否已登录"""
        return self.current_user is not None
    
    def get_current_user(self) -> User:
        """获取当前登录用户"""
        return self.current_user
    
    def is_admin(self) -> bool:
        """检查当前用户是否是管理员"""
        return self.is_logged_in() and self.current_user.role == UserRole.ADMIN
    
    def is_merchant(self) -> bool:
        """检查当前用户是否是商家"""
        return self.is_logged_in() and self.current_user.role == UserRole.MERCHANT
    
    def verify_password(self, password: str) -> bool:
        """验证密码"""
        if not self.current_user:
            return False
        return check_password_hash(self.current_user.password_hash, password) 