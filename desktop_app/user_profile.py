import tkinter as tk
from tkinter import ttk, messagebox
from database import User, init_db

class UserProfileWindow:
    def __init__(self, auth_manager):
        self.root = tk.Toplevel()
        self.root.title("个人资料")
        self.root.geometry("600x500")
        self.auth_manager = auth_manager
        self.session = init_db()
        self.init_ui()
    
    def init_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(
            main_frame,
            text="个人资料",
            font=("Arial", 24, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=20)
        
        # 用户名
        username_label = ttk.Label(main_frame, text="用户名:")
        username_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar(value=self.auth_manager.get_current_user().username)
        username_entry = ttk.Entry(main_frame, textvariable=self.username_var, state="readonly")
        username_entry.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # 昵称
        nickname_label = ttk.Label(main_frame, text="昵称:")
        nickname_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        self.nickname_var = tk.StringVar(value=self.auth_manager.get_current_user().nickname or "")
        nickname_entry = ttk.Entry(main_frame, textvariable=self.nickname_var)
        nickname_entry.grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        # 邮箱
        email_label = ttk.Label(main_frame, text="邮箱:")
        email_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        self.email_var = tk.StringVar(value=self.auth_manager.get_current_user().email)
        email_entry = ttk.Entry(main_frame, textvariable=self.email_var)
        email_entry.grid(row=3, column=1, sticky=tk.EW, pady=5)
        
        # 手机号
        phone_label = ttk.Label(main_frame, text="手机号:")
        phone_label.grid(row=4, column=0, sticky=tk.W, pady=5)
        self.phone_var = tk.StringVar(value=self.auth_manager.get_current_user().phone or "")
        phone_entry = ttk.Entry(main_frame, textvariable=self.phone_var)
        phone_entry.grid(row=4, column=1, sticky=tk.EW, pady=5)
        
        # 修改密码
        password_frame = ttk.LabelFrame(main_frame, text="修改密码", padding="10")
        password_frame.grid(row=5, column=0, columnspan=2, sticky=tk.EW, pady=20)
        
        # 当前密码
        current_password_label = ttk.Label(password_frame, text="当前密码:")
        current_password_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.current_password_var = tk.StringVar()
        current_password_entry = ttk.Entry(password_frame, textvariable=self.current_password_var, show="*")
        current_password_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # 新密码
        new_password_label = ttk.Label(password_frame, text="新密码:")
        new_password_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.new_password_var = tk.StringVar()
        new_password_entry = ttk.Entry(password_frame, textvariable=self.new_password_var, show="*")
        new_password_entry.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # 确认新密码
        confirm_password_label = ttk.Label(password_frame, text="确认新密码:")
        confirm_password_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        self.confirm_password_var = tk.StringVar()
        confirm_password_entry = ttk.Entry(password_frame, textvariable=self.confirm_password_var, show="*")
        confirm_password_entry.grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        save_button = ttk.Button(
            button_frame,
            text="保存修改",
            command=self.save_changes,
            style="Action.TButton"
        )
        save_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ttk.Button(
            button_frame,
            text="取消",
            command=self.root.destroy,
            style="Action.TButton"
        )
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # 设置样式
        style = ttk.Style()
        style.configure(
            "Action.TButton",
            font=("Arial", 10),
            padding=5
        )
        
        # 配置网格权重
        main_frame.columnconfigure(1, weight=1)
        password_frame.columnconfigure(1, weight=1)
    
    def save_changes(self):
        user = self.auth_manager.get_current_user()
        
        # 验证当前密码
        if self.current_password_var.get():
            if not self.auth_manager.verify_password(self.current_password_var.get(), user.password):
                messagebox.showerror("错误", "当前密码不正确")
                return
            
            # 验证新密码
            if self.new_password_var.get() != self.confirm_password_var.get():
                messagebox.showerror("错误", "两次输入的新密码不一致")
                return
            
            if len(self.new_password_var.get()) < 6:
                messagebox.showerror("错误", "新密码长度不能少于6位")
                return
            
            user.password = self.auth_manager.hash_password(self.new_password_var.get())
        
        try:
            # 更新用户信息
            user.nickname = self.nickname_var.get()
            user.email = self.email_var.get()
            user.phone = self.phone_var.get()
            
            self.session.commit()
            messagebox.showinfo("成功", "个人资料更新成功")
            self.root.destroy()
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("错误", f"更新个人资料失败: {str(e)}") 