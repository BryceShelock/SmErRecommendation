import tkinter as tk
from tkinter import ttk, messagebox
from database import Script, Review, init_db
from datetime import datetime

class ScriptDetailWindow:
    def __init__(self, auth_manager, script):
        self.root = tk.Toplevel()
        self.root.title(f"剧本详情 - {script.title}")
        self.root.geometry("800x600")
        self.auth_manager = auth_manager
        self.script = script
        self.session = init_db()
        self.init_ui()
    
    def init_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 剧本基本信息
        info_frame = ttk.LabelFrame(main_frame, text="基本信息", padding="10")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # 标题
        ttk.Label(
            info_frame,
            text=self.script.title,
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 难度
        ttk.Label(
            info_frame,
            text="难度：",
            font=("Arial", 10)
        ).grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(
            info_frame,
            text=str(self.script.difficulty),
            font=("Arial", 10)
        ).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # 时长
        ttk.Label(
            info_frame,
            text="时长：",
            font=("Arial", 10)
        ).grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Label(
            info_frame,
            text=f"{self.script.duration}分钟",
            font=("Arial", 10)
        ).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # 价格
        ttk.Label(
            info_frame,
            text="价格：",
            font=("Arial", 10)
        ).grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Label(
            info_frame,
            text=f"¥{self.script.price}/人",
            font=("Arial", 10)
        ).grid(row=3, column=1, sticky=tk.W, pady=2)
        
        # 玩家数量
        ttk.Label(
            info_frame,
            text="玩家数量：",
            font=("Arial", 10)
        ).grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Label(
            info_frame,
            text=f"{self.script.min_players}-{self.script.max_players}人",
            font=("Arial", 10)
        ).grid(row=4, column=1, sticky=tk.W, pady=2)
        
        # 地点
        ttk.Label(
            info_frame,
            text="地点：",
            font=("Arial", 10)
        ).grid(row=5, column=0, sticky=tk.W, pady=2)
        ttk.Label(
            info_frame,
            text=self.script.location,
            font=("Arial", 10)
        ).grid(row=5, column=1, sticky=tk.W, pady=2)
        
        # 商家
        ttk.Label(
            info_frame,
            text="商家：",
            font=("Arial", 10)
        ).grid(row=6, column=0, sticky=tk.W, pady=2)
        ttk.Label(
            info_frame,
            text=self.script.merchant.username,
            font=("Arial", 10)
        ).grid(row=6, column=1, sticky=tk.W, pady=2)
        
        # 剧本简介
        desc_frame = ttk.LabelFrame(main_frame, text="剧本简介", padding="10")
        desc_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        desc_text = tk.Text(
            desc_frame,
            wrap=tk.WORD,
            width=60,
            height=5
        )
        desc_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        desc_text.insert("1.0", self.script.description)
        desc_text.config(state=tk.DISABLED)
        
        # 评价列表
        review_frame = ttk.LabelFrame(main_frame, text="评价", padding="10")
        review_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 评价列表
        self.review_tree = ttk.Treeview(
            review_frame,
            columns=("user", "rating", "content", "time"),
            show="headings",
            height=6
        )
        self.review_tree.heading("user", text="用户")
        self.review_tree.heading("rating", text="评分")
        self.review_tree.heading("content", text="评价内容")
        self.review_tree.heading("time", text="评价时间")
        
        self.review_tree.column("user", width=100)
        self.review_tree.column("rating", width=50)
        self.review_tree.column("content", width=400)
        self.review_tree.column("time", width=150)
        
        self.review_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(review_frame, orient=tk.VERTICAL, command=self.review_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.review_tree.configure(yscrollcommand=scrollbar.set)
        
        # 加载评价
        self.load_reviews()
        
        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # 预约按钮
        ttk.Button(
            button_frame,
            text="预约",
            command=self.make_reservation,
            style="Action.TButton"
        ).grid(row=0, column=0, padx=5)
        
        # 评价按钮
        ttk.Button(
            button_frame,
            text="写评价",
            command=self.write_review,
            style="Action.TButton"
        ).grid(row=0, column=1, padx=5)
        
        # 设置样式
        style = ttk.Style()
        style.configure(
            "Action.TButton",
            font=("Arial", 10),
            padding=5
        )
        
        # 配置网格权重
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        review_frame.columnconfigure(0, weight=1)
        review_frame.rowconfigure(0, weight=1)
    
    def load_reviews(self):
        # 清空现有数据
        for item in self.review_tree.get_children():
            self.review_tree.delete(item)
        
        # 加载评价
        reviews = self.session.query(Review).filter_by(script_id=self.script.id).order_by(Review.created_at.desc()).all()
        
        for review in reviews:
            self.review_tree.insert(
                "",
                tk.END,
                values=(
                    review.user.username,
                    str(review.rating),
                    review.content,
                    review.created_at.strftime("%Y-%m-%d %H:%M")
                )
            )
    
    def make_reservation(self):
        if not self.auth_manager.get_current_user():
            messagebox.showwarning("提示", "请先登录")
            return
        
        # 创建预约对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("预约剧本")
        dialog.geometry("400x300")
        
        # 预约表单
        ttk.Label(
            dialog,
            text="预约时间",
            font=("Arial", 12)
        ).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        date_var = tk.StringVar()
        date_entry = ttk.Entry(dialog, textvariable=date_var, width=20)
        date_entry.grid(row=1, column=0, sticky=tk.W, pady=5)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        time_var = tk.StringVar()
        time_entry = ttk.Entry(dialog, textvariable=time_var, width=20)
        time_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        time_entry.insert(0, "19:00")
        
        ttk.Label(
            dialog,
            text="玩家数量",
            font=("Arial", 12)
        ).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        player_var = tk.StringVar()
        player_combo = ttk.Combobox(
            dialog,
            textvariable=player_var,
            values=[str(i) for i in range(self.script.min_players, self.script.max_players + 1)],
            state="readonly",
            width=5
        )
        player_combo.grid(row=3, column=0, sticky=tk.W, pady=5)
        player_combo.current(0)
        
        # 计算总价
        def update_price(*args):
            try:
                players = int(player_var.get())
                total = self.script.price * players
                price_label.config(text=f"总价：¥{total}")
            except ValueError:
                price_label.config(text="总价：¥0")
        
        player_var.trace("w", update_price)
        
        price_label = ttk.Label(
            dialog,
            text="总价：¥0",
            font=("Arial", 12)
        )
        price_label.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # 确认按钮
        def confirm():
            try:
                # 解析日期和时间
                date_str = date_var.get()
                time_str = time_var.get()
                order_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                
                # 验证时间
                if order_time < datetime.now():
                    messagebox.showerror("错误", "预约时间不能早于当前时间")
                    return
                
                # 创建订单
                order = Order(
                    user=self.auth_manager.get_current_user(),
                    script=self.script,
                    order_time=order_time,
                    player_count=int(player_var.get()),
                    total_price=self.script.price * int(player_var.get()),
                    status="pending"
                )
                
                self.session.add(order)
                self.session.commit()
                
                messagebox.showinfo("成功", "预约成功，请等待商家确认")
                dialog.destroy()
            except Exception as e:
                self.session.rollback()
                messagebox.showerror("错误", f"预约失败: {str(e)}")
        
        ttk.Button(
            dialog,
            text="确认预约",
            command=confirm,
            style="Action.TButton"
        ).grid(row=4, column=0, columnspan=2, pady=20)
        
        # 设置样式
        style = ttk.Style()
        style.configure(
            "Action.TButton",
            font=("Arial", 10),
            padding=5
        )
        
        # 配置网格权重
        dialog.columnconfigure(1, weight=1)
    
    def write_review(self):
        if not self.auth_manager.get_current_user():
            messagebox.showwarning("提示", "请先登录")
            return
        
        # 创建评价对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("写评价")
        dialog.geometry("400x300")
        
        # 评分
        ttk.Label(
            dialog,
            text="评分",
            font=("Arial", 12)
        ).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        rating_var = tk.StringVar()
        rating_combo = ttk.Combobox(
            dialog,
            textvariable=rating_var,
            values=["1", "2", "3", "4", "5"],
            state="readonly",
            width=5
        )
        rating_combo.grid(row=0, column=1, sticky=tk.W, pady=5)
        rating_combo.current(4)  # 默认5分
        
        # 评价内容
        ttk.Label(
            dialog,
            text="评价内容",
            font=("Arial", 12)
        ).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        content_text = tk.Text(dialog, width=40, height=10)
        content_text.grid(row=2, column=0, columnspan=2, pady=5)
        
        # 提交按钮
        def submit():
            try:
                # 创建评价
                review = Review(
                    user=self.auth_manager.get_current_user(),
                    script=self.script,
                    rating=int(rating_var.get()),
                    content=content_text.get("1.0", tk.END).strip()
                )
                
                self.session.add(review)
                self.session.commit()
                
                messagebox.showinfo("成功", "评价成功")
                dialog.destroy()
                self.load_reviews()  # 重新加载评价列表
            except Exception as e:
                self.session.rollback()
                messagebox.showerror("错误", f"评价失败: {str(e)}")
        
        ttk.Button(
            dialog,
            text="提交评价",
            command=submit,
            style="Action.TButton"
        ).grid(row=3, column=0, columnspan=2, pady=20)
        
        # 设置样式
        style = ttk.Style()
        style.configure(
            "Action.TButton",
            font=("Arial", 10),
            padding=5
        )
        
        # 配置网格权重
        dialog.columnconfigure(1, weight=1) 