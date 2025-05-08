import hashlib
from database import User, init_db

class AuthManager:
    def __init__(self):
        self.session = init_db()
        self.current_user = None
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, username, password, email):
        try:
            hashed_password = self.hash_password(password)
            user = User(username=username, password=hashed_password, email=email)
            self.session.add(user)
            self.session.commit()
            return True, "注册成功"
        except Exception as e:
            self.session.rollback()
            return False, f"注册失败: {str(e)}"
    
    def login(self, username, password):
        try:
            hashed_password = self.hash_password(password)
            user = self.session.query(User).filter_by(
                username=username,
                password=hashed_password
            ).first()
            
            if user:
                self.current_user = user
                return True, "登录成功"
            return False, "用户名或密码错误"
        except Exception as e:
            return False, f"登录失败: {str(e)}"
    
    def logout(self):
        self.current_user = None
        return True, "已退出登录"
    
    def get_current_user(self):
        return self.current_user 