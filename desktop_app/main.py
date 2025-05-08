import sys
import tkinter as tk
from tkinter import ttk, messagebox
from database import User, UserRole, init_db
from auth_window import AuthWindow
from user_profile import UserProfileWindow
from script_recommendation import ScriptRecommendationWindow
from merchant_window import MerchantWindow
from admin_window import AdminWindow
from order_window import OrderWindow

class AuthManager:
    def __init__(self):
        self.current_user = None
    
    def set_current_user(self, user):
        self.current_user = user
    
    def get_current_user(self):
        return self.current_user
    
    def is_authenticated(self):
        return self.current_user is not None
    
    def is_admin(self):
        return self.is_authenticated() and self.current_user.role == UserRole.admin
    
    def is_merchant(self):
        return self.is_authenticated() and self.current_user.role == UserRole.merchant
    
    def logout(self):
        self.current_user = None

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("剧本杀推荐系统")
        self.root.geometry("800x600")
        self.auth_manager = AuthManager()
        self.session = init_db()
        self.init_ui()
    
    def init_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建菜单栏
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # 用户菜单
        self.user_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="用户", menu=self.user_menu)
        self.user_menu.add_command(label="登录/注册", command=self.show_auth_window)
        self.user_menu.add_command(label="个人资料", command=self.show_profile_window)
        self.user_menu.add_separator()
        self.user_menu.add_command(label="退出", command=self.logout)
        
        # 剧本菜单
        self.script_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="剧本", menu=self.script_menu)
        self.script_menu.add_command(label="剧本推荐", command=self.show_recommendation_window)
        self.script_menu.add_command(label="我的订单", command=self.show_order_window)
        
        # 管理菜单
        self.admin_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="管理", menu=self.admin_menu)
        self.admin_menu.add_command(label="商家管理", command=self.show_merchant_window)
        self.admin_menu.add_command(label="管理员控制台", command=self.show_admin_window)
        
        # 欢迎信息
        self.welcome_label = ttk.Label(
            main_frame,
            text="欢迎使用剧本杀推荐系统",
            font=("Arial", 24, "bold")
        )
        self.welcome_label.grid(row=0, column=0, pady=20)
        
        # 系统信息
        info_frame = ttk.LabelFrame(main_frame, text="系统信息", padding="10")
        info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(
            info_frame,
            text="本系统提供以下功能：",
            font=("Arial", 12)
        ).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        features = [
            "• 个性化剧本推荐",
            "• 剧本搜索和筛选",
            "• 剧本评价和评分",
            "• 在线预约和订单管理",
            "• 商家剧本管理",
            "• 用户管理"
        ]
        
        for i, feature in enumerate(features, 1):
            ttk.Label(
                info_frame,
                text=feature,
                font=("Arial", 10)
            ).grid(row=i, column=0, sticky=tk.W, pady=2)
        
        # 设置样式
        style = ttk.Style()
        style.configure(
            "Action.TButton",
            font=("Arial", 10),
            padding=5
        )
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # 初始化菜单状态
        self.update_menu_state()
        self.update_welcome_message()
    
    def update_menu_state(self):
        # 更新用户菜单
        if self.auth_manager.is_authenticated():
            self.user_menu.entryconfig("登录/注册", state="disabled")
            self.user_menu.entryconfig("个人资料", state="normal")
            self.user_menu.entryconfig("退出", state="normal")
            self.script_menu.entryconfig("剧本推荐", state="normal")
            self.script_menu.entryconfig("我的订单", state="normal")
        else:
            self.user_menu.entryconfig("登录/注册", state="normal")
            self.user_menu.entryconfig("个人资料", state="disabled")
            self.user_menu.entryconfig("退出", state="disabled")
            self.script_menu.entryconfig("剧本推荐", state="disabled")
            self.script_menu.entryconfig("我的订单", state="disabled")
        
        # 更新管理菜单
        if self.auth_manager.is_merchant():
            self.admin_menu.entryconfig("商家管理", state="normal")
            self.admin_menu.entryconfig("管理员控制台", state="disabled")
        elif self.auth_manager.is_admin():
            self.admin_menu.entryconfig("商家管理", state="disabled")
            self.admin_menu.entryconfig("管理员控制台", state="normal")
        else:
            self.admin_menu.entryconfig("商家管理", state="disabled")
            self.admin_menu.entryconfig("管理员控制台", state="disabled")
    
    def show_auth_window(self):
        if not self.auth_manager.is_authenticated():
            auth_window = AuthWindow(self.auth_manager)
            self.root.wait_window(auth_window.root)  # 等待登录窗口关闭
            self.update_menu_state()  # 更新菜单状态
            self.update_welcome_message()  # 更新欢迎信息
    
    def show_profile_window(self):
        if self.auth_manager.is_authenticated():
            UserProfileWindow(self.auth_manager)
    
    def show_recommendation_window(self):
        if self.auth_manager.is_authenticated():
            ScriptRecommendationWindow(self.auth_manager)
        else:
            messagebox.showwarning("警告", "请先登录")
    
    def show_order_window(self):
        if self.auth_manager.is_authenticated():
            OrderWindow(self.auth_manager)
        else:
            messagebox.showwarning("警告", "请先登录")
    
    def show_merchant_window(self):
        if self.auth_manager.is_merchant():
            MerchantWindow(self.auth_manager)
        else:
            messagebox.showwarning("警告", "只有商家才能访问此功能")
    
    def show_admin_window(self):
        if self.auth_manager.is_admin():
            AdminWindow(self.auth_manager)
        else:
            messagebox.showwarning("警告", "只有管理员才能访问此功能")
    
    def logout(self):
        if messagebox.askyesno("确认", "确定要退出登录吗？"):
            self.auth_manager.logout()
            self.update_menu_state()
            messagebox.showinfo("成功", "已退出登录")
    
    def update_welcome_message(self):
        if self.auth_manager.is_authenticated():
            user = self.auth_manager.get_current_user()
            self.welcome_label.config(
                text=f"欢迎回来，{user.username}！",
                font=("Arial", 24, "bold")
            )
        else:
            self.welcome_label.config(
                text="欢迎使用剧本杀推荐系统",
                font=("Arial", 24, "bold")
            )
    
    def run(self):
        self.root.mainloop()

def main():
    app = MainWindow()
    app.run()

if __name__ == "__main__":
    main() 