import tkinter as tk
from tkinter import ttk, messagebox
from database import User, init_db

class AddUserDialog:
    def __init__(self, parent=None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("添加用户")
        self.dialog.geometry("400x300")
        self.result = None
        self.init_ui()
        
        # 设置模态窗口
        self.dialog.transient(parent)
        self.dialog.grab_set()
    
    def init_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 用户名
        username_label = ttk.Label(main_frame, text="用户名:")
        username_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_input = ttk.Entry(main_frame, width=30)
        self.username_input.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # 密码
        password_label = ttk.Label(main_frame, text="密码:")
        password_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_input = ttk.Entry(main_frame, width=30, show="*")
        self.password_input.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # 确认密码
        confirm_label = ttk.Label(main_frame, text="确认密码:")
        confirm_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        self.confirm_input = ttk.Entry(main_frame, width=30, show="*")
        self.confirm_input.grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        # 邮箱
        email_label = ttk.Label(main_frame, text="邮箱:")
        email_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        self.email_input = ttk.Entry(main_frame, width=30)
        self.email_input.grid(row=3, column=1, sticky=tk.EW, pady=5)
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        save_button = ttk.Button(
            button_frame,
            text="保存",
            command=self.on_save,
            style="Action.TButton"
        )
        save_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ttk.Button(
            button_frame,
            text="取消",
            command=self.on_cancel,
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
        for i in range(5):
            main_frame.rowconfigure(i, weight=1)
    
    def on_save(self):
        self.result = {
            "username": self.username_input.get(),
            "password": self.password_input.get(),
            "confirm": self.confirm_input.get(),
            "email": self.email_input.get()
        }
        self.dialog.destroy()
    
    def on_cancel(self):
        self.dialog.destroy()

class UserManagementWindow:
    def __init__(self, auth_manager):
        self.root = tk.Toplevel()
        self.root.title("用户管理")
        self.root.geometry("800x600")
        self.auth_manager = auth_manager
        self.session = init_db()
        self.init_ui()
    
    def init_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加用户按钮
        add_button = ttk.Button(
            main_frame,
            text="添加用户",
            command=self.add_user,
            style="Action.TButton"
        )
        add_button.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # 用户列表
        self.user_tree = ttk.Treeview(
            main_frame,
            columns=("username", "email", "created_at", "review_count"),
            show="headings"
        )
        self.user_tree.heading("username", text="用户名")
        self.user_tree.heading("email", text="邮箱")
        self.user_tree.heading("created_at", text="注册时间")
        self.user_tree.heading("review_count", text="评价数量")
        self.user_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.user_tree.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.user_tree.configure(yscrollcommand=scrollbar.set)
        
        # 设置样式
        style = ttk.Style()
        style.configure(
            "Action.TButton",
            font=("Arial", 10),
            padding=5
        )
        
        # 配置网格权重
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 加载数据
        self.load_users()
    
    def load_users(self):
        # 清空现有数据
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        
        users = self.session.query(User).all()
        for user in users:
            item = self.user_tree.insert(
                "",
                tk.END,
                values=(
                    user.username,
                    user.email,
                    str(user.created_at),
                    str(len(user.reviews))
                ),
                tags=(str(user.id),)
            )
            
            # 添加编辑和删除按钮
            edit_button = ttk.Button(
                self.user_tree,
                text="编辑",
                command=lambda u=user: self.edit_user(u),
                style="Action.TButton"
            )
            delete_button = ttk.Button(
                self.user_tree,
                text="删除",
                command=lambda u=user: self.delete_user(u),
                style="Action.TButton"
            )
            
            self.user_tree.set(item, "edit_button", edit_button)
            self.user_tree.set(item, "delete_button", delete_button)
    
    def add_user(self):
        dialog = AddUserDialog(self.root)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            if dialog.result["password"] != dialog.result["confirm"]:
                messagebox.showerror("错误", "两次输入的密码不一致")
                return
            
            try:
                user = User(
                    username=dialog.result["username"],
                    password=self.auth_manager.hash_password(dialog.result["password"]),
                    email=dialog.result["email"]
                )
                self.session.add(user)
                self.session.commit()
                self.load_users()
                messagebox.showinfo("成功", "用户添加成功")
            except Exception as e:
                self.session.rollback()
                messagebox.showerror("错误", f"添加用户失败: {str(e)}")
    
    def edit_user(self, user):
        dialog = AddUserDialog(self.root)
        dialog.username_input.insert(0, user.username)
        dialog.email_input.insert(0, user.email)
        
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            if dialog.result["password"]:
                if dialog.result["password"] != dialog.result["confirm"]:
                    messagebox.showerror("错误", "两次输入的密码不一致")
                    return
                user.password = self.auth_manager.hash_password(dialog.result["password"])
            
            try:
                user.username = dialog.result["username"]
                user.email = dialog.result["email"]
                self.session.commit()
                self.load_users()
                messagebox.showinfo("成功", "用户信息更新成功")
            except Exception as e:
                self.session.rollback()
                messagebox.showerror("错误", f"更新用户信息失败: {str(e)}")
    
    def delete_user(self, user):
        if user == self.auth_manager.get_current_user():
            messagebox.showerror("错误", "不能删除当前登录的用户")
            return
        
        if messagebox.askyesno(
            "确认删除",
            f'确定要删除用户 "{user.username}" 吗？\n'
            '注意：这将同时删除该用户的所有评价。'
        ):
            try:
                self.session.delete(user)
                self.session.commit()
                self.load_users()
                messagebox.showinfo("成功", "用户删除成功")
            except Exception as e:
                self.session.rollback()
                messagebox.showerror("错误", f"删除用户失败: {str(e)}") 