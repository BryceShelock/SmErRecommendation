import tkinter as tk
from tkinter import ttk, messagebox
from database import User, UserRole, init_db
import bcrypt

class AuthWindow:
    def __init__(self, auth_manager):
        self.root = tk.Toplevel()
        self.root.title("用户认证")
        self.root.geometry("400x500")
        self.auth_manager = auth_manager
        self.session = init_db()
        self.init_ui()
    
    def init_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建标签页
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 登录标签页
        login_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(login_frame, text="登录")
        
        # 登录表单
        ttk.Label(
            login_frame,
            text="用户名",
            font=("Arial", 12)
        ).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.login_username = ttk.Entry(login_frame, width=30)
        self.login_username.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(
            login_frame,
            text="密码",
            font=("Arial", 12)
        ).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.login_password = ttk.Entry(login_frame, width=30, show="*")
        self.login_password.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(
            login_frame,
            text="登录",
            command=self.login,
            style="Action.TButton"
        ).grid(row=4, column=0, sticky=(tk.W, tk.E), pady=20)
        
        # 注册标签页
        register_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(register_frame, text="注册")
        
        # 注册表单
        ttk.Label(
            register_frame,
            text="用户名",
            font=("Arial", 12)
        ).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.register_username = ttk.Entry(register_frame, width=30)
        self.register_username.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(
            register_frame,
            text="密码",
            font=("Arial", 12)
        ).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.register_password = ttk.Entry(register_frame, width=30, show="*")
        self.register_password.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(
            register_frame,
            text="确认密码",
            font=("Arial", 12)
        ).grid(row=4, column=0, sticky=tk.W, pady=5)
        
        self.register_confirm = ttk.Entry(register_frame, width=30, show="*")
        self.register_confirm.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(
            register_frame,
            text="邮箱",
            font=("Arial", 12)
        ).grid(row=6, column=0, sticky=tk.W, pady=5)
        
        self.register_email = ttk.Entry(register_frame, width=30)
        self.register_email.grid(row=7, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(
            register_frame,
            text="用户类型",
            font=("Arial", 12)
        ).grid(row=8, column=0, sticky=tk.W, pady=5)
        
        self.register_role = ttk.Combobox(
            register_frame,
            values=["普通用户", "商家"],
            state="readonly",
            width=27
        )
        self.register_role.current(0)
        self.register_role.grid(row=9, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(
            register_frame,
            text="注册",
            command=self.register,
            style="Action.TButton"
        ).grid(row=10, column=0, sticky=(tk.W, tk.E), pady=20)
        
        # 设置样式
        style = ttk.Style()
        style.configure(
            "Action.TButton",
            font=("Arial", 10),
            padding=5
        )
        
        # 配置网格权重
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        for frame in [login_frame, register_frame]:
            frame.columnconfigure(0, weight=1)
    
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