import tkinter as tk
from tkinter import ttk, messagebox
from auth import AuthManager

class LoginWindow:
    def __init__(self, auth_manager, on_success):
        self.root = tk.Toplevel()
        self.root.title("登录")
        self.root.geometry("400x300")
        self.auth_manager = auth_manager
        self.on_success = on_success
        self.init_ui()
        
        # 设置模态窗口
        self.root.transient()
        self.root.grab_set()
    
    def init_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(
            main_frame,
            text="剧本杀密室推荐系统",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=20)
        
        # 用户名
        username_label = ttk.Label(main_frame, text="用户名:")
        username_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # 密码
        password_label = ttk.Label(main_frame, text="密码:")
        password_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(main_frame, width=30, show="*")
        self.password_entry.grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        # 登录按钮
        login_button = ttk.Button(
            button_frame,
            text="登录",
            command=self.handle_login,
            style="Action.TButton"
        )
        login_button.pack(side=tk.LEFT, padx=5)
        
        # 注册按钮
        register_button = ttk.Button(
            button_frame,
            text="注册",
            command=self.show_register,
            style="Action.TButton"
        )
        register_button.pack(side=tk.LEFT, padx=5)
        
        # 设置样式
        style = ttk.Style()
        style.configure(
            "Action.TButton",
            font=("Arial", 10),
            padding=5
        )
        
        # 配置网格权重
        main_frame.columnconfigure(1, weight=1)
        for i in range(4):
            main_frame.rowconfigure(i, weight=1)
    
    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("错误", "请输入用户名和密码")
            return
        
        success, message = self.auth_manager.login(username, password)
        if success:
            messagebox.showinfo("成功", message)
            self.root.destroy()
            self.on_success()
        else:
            messagebox.showerror("错误", message)
    
    def show_register(self):
        RegisterDialog(self.root, self.auth_manager)

class RegisterDialog:
    def __init__(self, parent, auth_manager):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("注册")
        self.dialog.geometry("400x350")
        self.auth_manager = auth_manager
        self.init_ui()
        
        # 设置模态窗口
        self.dialog.transient(parent)
        self.dialog.grab_set()
    
    def init_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 用户名
        username_label = ttk.Label(main_frame, text="用户名:")
        username_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # 密码
        password_label = ttk.Label(main_frame, text="密码:")
        password_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(main_frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # 确认密码
        confirm_label = ttk.Label(main_frame, text="确认密码:")
        confirm_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        self.confirm_entry = ttk.Entry(main_frame, width=30, show="*")
        self.confirm_entry.grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        # 邮箱
        email_label = ttk.Label(main_frame, text="邮箱:")
        email_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        self.email_entry = ttk.Entry(main_frame, width=30)
        self.email_entry.grid(row=3, column=1, sticky=tk.EW, pady=5)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        # 注册按钮
        register_button = ttk.Button(
            button_frame,
            text="注册",
            command=self.handle_register,
            style="Action.TButton"
        )
        register_button.pack(side=tk.LEFT, padx=5)
        
        # 取消按钮
        cancel_button = ttk.Button(
            button_frame,
            text="取消",
            command=self.dialog.destroy,
            style="Action.TButton"
        )
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # 配置网格权重
        main_frame.columnconfigure(1, weight=1)
        for i in range(5):
            main_frame.rowconfigure(i, weight=1)
    
    def handle_register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        email = self.email_entry.get()
        
        if not username or not password or not confirm or not email:
            messagebox.showerror("错误", "请填写所有字段")
            return
        
        if password != confirm:
            messagebox.showerror("错误", "两次输入的密码不一致")
            return
        
        success, message = self.auth_manager.register(username, password, email)
        if success:
            messagebox.showinfo("成功", message)
            self.dialog.destroy()
        else:
            messagebox.showerror("错误", message) 