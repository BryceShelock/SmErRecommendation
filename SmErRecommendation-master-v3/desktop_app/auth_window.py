import tkinter as tk
from tkinter import ttk, messagebox
from database import User, UserRole, init_db
import bcrypt
from PIL import Image, ImageTk
import os

class AuthWindow:
    def __init__(self, auth_manager):
        self.root = tk.Toplevel()
        self.root.title("用户认证")
        self.root.geometry("500x700")
        self.auth_manager = auth_manager
        self.session = init_db()
        self.init_styles()
        self.init_ui()
    
    def init_styles(self):
        style = ttk.Style()
        
        # 定义颜色变量
        self.colors = {
            'primary': '#6c5ce7',
            'secondary': '#a29bfe',
            'dark': '#2d3436',
            'light': '#f5f6fa',
            'accent': '#fd79a8',
            'success': '#07C160',
            'danger': '#E6162D',
            'info': '#12B7F5'
        }
        
        # 配置基本样式
        style.configure('TFrame', background=self.colors['light'])
        style.configure('TLabel', background=self.colors['light'])
        style.configure('TButton', padding=10)
        
        # 标题样式
        style.configure('Title.TLabel',
                       font=('Arial', 24, 'bold'),
                       foreground=self.colors['dark'])
        
        # 副标题样式
        style.configure('Subtitle.TLabel',
                       font=('Arial', 12),
                       foreground=self.colors['dark'])
        
        # 卡片样式
        style.configure('Card.TFrame',
                       background='white',
                       relief='flat',
                       borderwidth=0)
        
        # 按钮样式
        style.configure('Primary.TButton',
                       background=self.colors['primary'],
                       foreground='white',
                       font=('Arial', 10, 'bold'),
                       padding=10)
        
        style.configure('Outline.TButton',
                       background='white',
                       foreground=self.colors['primary'],
                       font=('Arial', 10, 'bold'),
                       padding=10)
        
        # 输入框样式
        style.configure('Entry.TEntry',
                       padding=10,
                       font=('Arial', 10))
    
    def create_social_button(self, parent, text, color, command=None):
        btn = tk.Button(
            parent,
            text=text,
            bg=color,
            fg='white',
            font=('Arial', 12, 'bold'),
            width=40,
            height=40,
            relief='flat',
            command=command
        )
        btn.pack(side='left', padx=5)
        return btn
    
    def init_ui(self):
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, style='TFrame')
        self.main_frame.pack(fill='both', expand=True)
        
        # 创建标签页
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 登录标签页
        login_frame = ttk.Frame(self.notebook, style='Card.TFrame')
        self.notebook.add(login_frame, text="登录")
        
        # 登录表单容器
        login_container = ttk.Frame(login_frame, style='Card.TFrame')
        login_container.pack(fill='both', expand=True, padx=30, pady=30)
        
        # 欢迎标题
        ttk.Label(
            login_container,
            text="欢迎回来",
            style='Title.TLabel'
        ).pack(pady=(0, 30))
        
        # 用户名输入框
        username_frame = ttk.Frame(login_container)
        username_frame.pack(fill='x', pady=5)
        
        ttk.Label(
            username_frame,
            text="用户名/手机号",
            font=('Arial', 10)
        ).pack(anchor='w')
        
        self.login_username = ttk.Entry(
            username_frame,
            style='Entry.TEntry',
            width=40
        )
        self.login_username.pack(fill='x', pady=5)
        
        # 密码输入框
        password_frame = ttk.Frame(login_container)
        password_frame.pack(fill='x', pady=5)
        
        ttk.Label(
            password_frame,
            text="密码",
            font=('Arial', 10)
        ).pack(anchor='w')
        
        self.login_password = ttk.Entry(
            password_frame,
            style='Entry.TEntry',
            width=40,
            show="•"
        )
        self.login_password.pack(fill='x', pady=5)
        
        # 记住我和忘记密码
        options_frame = ttk.Frame(login_container)
        options_frame.pack(fill='x', pady=10)
        
        self.remember_var = tk.BooleanVar()
        ttk.Checkbutton(
            options_frame,
            text="记住我",
            variable=self.remember_var
        ).pack(side='left')
        
        ttk.Label(
            options_frame,
            text="忘记密码？",
            foreground=self.colors['primary'],
            cursor="hand2"
        ).pack(side='right')
        
        # 登录按钮
        ttk.Button(
            login_container,
            text="登录",
            style='Primary.TButton',
            command=self.login
        ).pack(fill='x', pady=20)
        
        # 注册链接
        register_frame = ttk.Frame(login_container)
        register_frame.pack(fill='x', pady=10)
        
        ttk.Label(
            register_frame,
            text="还没有账号？",
            font=('Arial', 10)
        ).pack(side='left')
        
        ttk.Label(
            register_frame,
            text="立即注册",
            foreground=self.colors['primary'],
            cursor="hand2",
            font=('Arial', 10, 'bold')
        ).pack(side='left', padx=5)
        
        # 社交登录
        social_frame = ttk.Frame(login_container)
        social_frame.pack(fill='x', pady=30)
        
        ttk.Label(
            social_frame,
            text="其他登录方式",
            font=('Arial', 10),
            foreground='#666'
        ).pack(pady=10)
        
        social_buttons = ttk.Frame(social_frame)
        social_buttons.pack()
        
        self.create_social_button(social_buttons, "微信", self.colors['success'])
        self.create_social_button(social_buttons, "微博", self.colors['danger'])
        self.create_social_button(social_buttons, "QQ", self.colors['info'])
        
        # 注册标签页
        register_frame = ttk.Frame(self.notebook, style='Card.TFrame')
        self.notebook.add(register_frame, text="注册")
        
        # 注册表单容器
        register_container = ttk.Frame(register_frame, style='Card.TFrame')
        register_container.pack(fill='both', expand=True, padx=30, pady=30)
        
        # 注册标题
        ttk.Label(
            register_container,
            text="创建账号",
            style='Title.TLabel'
        ).pack(pady=(0, 30))
        
        # 用户名输入框
        username_frame = ttk.Frame(register_container)
        username_frame.pack(fill='x', pady=5)
        
        ttk.Label(
            username_frame,
            text="用户名",
            font=('Arial', 10)
        ).pack(anchor='w')
        
        self.register_username = ttk.Entry(
            username_frame,
            style='Entry.TEntry',
            width=40
        )
        self.register_username.pack(fill='x', pady=5)
        
        # 密码输入框
        password_frame = ttk.Frame(register_container)
        password_frame.pack(fill='x', pady=5)
        
        ttk.Label(
            password_frame,
            text="密码",
            font=('Arial', 10)
        ).pack(anchor='w')
        
        self.register_password = ttk.Entry(
            password_frame,
            style='Entry.TEntry',
            width=40,
            show="•"
        )
        self.register_password.pack(fill='x', pady=5)
        
        # 确认密码输入框
        confirm_frame = ttk.Frame(register_container)
        confirm_frame.pack(fill='x', pady=5)
        
        ttk.Label(
            confirm_frame,
            text="确认密码",
            font=('Arial', 10)
        ).pack(anchor='w')
        
        self.register_confirm = ttk.Entry(
            confirm_frame,
            style='Entry.TEntry',
            width=40,
            show="•"
        )
        self.register_confirm.pack(fill='x', pady=5)
        
        # 邮箱输入框
        email_frame = ttk.Frame(register_container)
        email_frame.pack(fill='x', pady=5)
        
        ttk.Label(
            email_frame,
            text="邮箱",
            font=('Arial', 10)
        ).pack(anchor='w')
        
        self.register_email = ttk.Entry(
            email_frame,
            style='Entry.TEntry',
            width=40
        )
        self.register_email.pack(fill='x', pady=5)
        
        # 用户类型选择
        role_frame = ttk.Frame(register_container)
        role_frame.pack(fill='x', pady=5)
        
        ttk.Label(
            role_frame,
            text="用户类型",
            font=('Arial', 10)
        ).pack(anchor='w')
        
        self.register_role = ttk.Combobox(
            role_frame,
            values=["普通用户", "商家"],
            state="readonly",
            width=38
        )
        self.register_role.current(0)
        self.register_role.pack(fill='x', pady=5)
        
        # 注册按钮
        ttk.Button(
            register_container,
            text="注册",
            style='Primary.TButton',
            command=self.register
        ).pack(fill='x', pady=20)
        
        # 登录链接
        login_link_frame = ttk.Frame(register_container)
        login_link_frame.pack(fill='x', pady=10)
        
        ttk.Label(
            login_link_frame,
            text="已有账号？",
            font=('Arial', 10)
        ).pack(side='left')
        
        ttk.Label(
            login_link_frame,
            text="立即登录",
            foreground=self.colors['primary'],
            cursor="hand2",
            font=('Arial', 10, 'bold')
        ).pack(side='left', padx=5)
    
    def login(self):
        username = self.login_username.get().strip()
        password = self.login_password.get()
        
        if not username or not password:
            messagebox.showwarning("警告", "请输入用户名和密码")
            return
        
        user = self.session.query(User).filter_by(username=username).first()
        
        if not user:
            messagebox.showerror("错误", "用户名不存在")
            return
        
        if not user.is_active:
            messagebox.showerror("错误", "账号已被禁用")
            return
        
        if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            messagebox.showerror("错误", "密码错误")
            return
        
        # 设置当前用户
        self.auth_manager.set_current_user(user)
        messagebox.showinfo("成功", "登录成功")
        
        # 关闭登录窗口
        self.root.destroy()
    
    def register(self):
        username = self.register_username.get().strip()
        password = self.register_password.get()
        confirm = self.register_confirm.get()
        email = self.register_email.get().strip()
        role = self.register_role.get()
        
        if not username or not password or not confirm or not email:
            messagebox.showwarning("警告", "请填写所有必填字段")
            return
        
        if password != confirm:
            messagebox.showerror("错误", "两次输入的密码不一致")
            return
        
        if len(password) < 6:
            messagebox.showerror("错误", "密码长度不能少于6个字符")
            return
        
        if self.session.query(User).filter_by(username=username).first():
            messagebox.showerror("错误", "用户名已存在")
            return
        
        if self.session.query(User).filter_by(email=email).first():
            messagebox.showerror("错误", "邮箱已被注册")
            return
        
        try:
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            user = User(
                username=username,
                password_hash=password_hash,
                email=email,
                role=UserRole.merchant if role == "商家" else UserRole.user,
                is_active=True
            )
            self.session.add(user)
            self.session.commit()
            messagebox.showinfo("成功", "注册成功，请登录")
            self.notebook.select(0)  # 切换到登录标签页
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("错误", f"注册失败: {str(e)}") 