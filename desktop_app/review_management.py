import tkinter as tk
from tkinter import ttk, messagebox
from database import Review, Script, User, init_db

class AddReviewDialog:
    def __init__(self, session, parent=None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("添加评价")
        self.dialog.geometry("400x400")
        self.session = session
        self.result = None
        self.init_ui()
        
        # 设置模态窗口
        self.dialog.transient(parent)
        self.dialog.grab_set()
    
    def init_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 选择剧本
        script_label = ttk.Label(main_frame, text="剧本:")
        script_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.script_var = tk.StringVar()
        self.script_combo = ttk.Combobox(
            main_frame,
            textvariable=self.script_var,
            state="readonly"
        )
        scripts = self.session.query(Script).all()
        self.script_combo["values"] = [script.title for script in scripts]
        self.script_combo.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # 评分
        rating_label = ttk.Label(main_frame, text="评分(1-5):")
        rating_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.rating_var = tk.StringVar(value="3.0")
        rating_spin = ttk.Spinbox(
            main_frame,
            from_=1.0,
            to=5.0,
            increment=0.5,
            textvariable=self.rating_var,
            width=5
        )
        rating_spin.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 评价内容
        comment_label = ttk.Label(main_frame, text="评价内容:")
        comment_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.comment_text = tk.Text(main_frame, height=10, width=30)
        self.comment_text.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
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
        for i in range(4):
            main_frame.rowconfigure(i, weight=1)
    
    def on_save(self):
        script_title = self.script_var.get()
        script = self.session.query(Script).filter_by(title=script_title).first()
        
        self.result = {
            "script": script,
            "rating": float(self.rating_var.get()),
            "comment": self.comment_text.get("1.0", tk.END).strip()
        }
        self.dialog.destroy()
    
    def on_cancel(self):
        self.dialog.destroy()

class ReviewManagementWindow:
    def __init__(self, auth_manager):
        self.root = tk.Toplevel()
        self.root.title("评价管理")
        self.root.geometry("800x600")
        self.auth_manager = auth_manager
        self.session = init_db()
        self.init_ui()
    
    def init_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加评价按钮
        add_button = ttk.Button(
            main_frame,
            text="添加评价",
            command=self.add_review,
            style="Action.TButton"
        )
        add_button.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # 评价列表
        self.review_tree = ttk.Treeview(
            main_frame,
            columns=("script", "user", "rating", "comment", "created_at"),
            show="headings"
        )
        self.review_tree.heading("script", text="剧本")
        self.review_tree.heading("user", text="用户")
        self.review_tree.heading("rating", text="评分")
        self.review_tree.heading("comment", text="评价内容")
        self.review_tree.heading("created_at", text="时间")
        self.review_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.review_tree.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.review_tree.configure(yscrollcommand=scrollbar.set)
        
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
        self.load_reviews()
    
    def load_reviews(self):
        # 清空现有数据
        for item in self.review_tree.get_children():
            self.review_tree.delete(item)
        
        reviews = self.session.query(Review).all()
        for review in reviews:
            item = self.review_tree.insert(
                "",
                tk.END,
                values=(
                    review.script.title,
                    review.user.username,
                    str(review.rating),
                    review.comment,
                    str(review.created_at)
                ),
                tags=(str(review.id),)
            )
            
            # 添加编辑和删除按钮
            edit_button = ttk.Button(
                self.review_tree,
                text="编辑",
                command=lambda r=review: self.edit_review(r),
                style="Action.TButton"
            )
            delete_button = ttk.Button(
                self.review_tree,
                text="删除",
                command=lambda r=review: self.delete_review(r),
                style="Action.TButton"
            )
            
            self.review_tree.set(item, "edit_button", edit_button)
            self.review_tree.set(item, "delete_button", delete_button)
    
    def add_review(self):
        dialog = AddReviewDialog(self.session, self.root)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            try:
                review = Review(
                    user=self.auth_manager.get_current_user(),
                    script=dialog.result["script"],
                    rating=dialog.result["rating"],
                    comment=dialog.result["comment"]
                )
                self.session.add(review)
                self.session.commit()
                self.load_reviews()
                messagebox.showinfo("成功", "评价添加成功")
            except Exception as e:
                self.session.rollback()
                messagebox.showerror("错误", f"添加评价失败: {str(e)}")
    
    def edit_review(self, review):
        dialog = AddReviewDialog(self.session, self.root)
        dialog.script_var.set(review.script.title)
        dialog.rating_var.set(str(review.rating))
        dialog.comment_text.insert("1.0", review.comment)
        
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            try:
                review.script = dialog.result["script"]
                review.rating = dialog.result["rating"]
                review.comment = dialog.result["comment"]
                self.session.commit()
                self.load_reviews()
                messagebox.showinfo("成功", "评价更新成功")
            except Exception as e:
                self.session.rollback()
                messagebox.showerror("错误", f"更新评价失败: {str(e)}")
    
    def delete_review(self, review):
        if messagebox.askyesno(
            "确认删除",
            "确定要删除这条评价吗？"
        ):
            try:
                self.session.delete(review)
                self.session.commit()
                self.load_reviews()
                messagebox.showinfo("成功", "评价删除成功")
            except Exception as e:
                self.session.rollback()
                messagebox.showerror("错误", f"删除评价失败: {str(e)}") 