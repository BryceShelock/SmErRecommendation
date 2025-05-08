import tkinter as tk
from tkinter import ttk, messagebox
from database import Script, Review, Order, init_db
from datetime import datetime, timedelta
from script_detail import ScriptDetailWindow

class ScriptRecommendationWindow:
    def __init__(self, auth_manager):
        self.root = tk.Toplevel()
        self.root.title("剧本推荐")
        self.root.geometry("1000x600")
        self.auth_manager = auth_manager
        self.session = init_db()
        self.init_ui()
    
    def init_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建标签页
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 个性化推荐标签页
        recommend_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(recommend_frame, text="个性化推荐")
        
        # 推荐剧本列表
        self.recommend_tree = ttk.Treeview(
            recommend_frame,
            columns=("title", "difficulty", "duration", "rating", "price"),
            show="headings"
        )
        self.recommend_tree.heading("title", text="剧本名称")
        self.recommend_tree.heading("difficulty", text="难度")
        self.recommend_tree.heading("duration", text="时长")
        self.recommend_tree.heading("rating", text="评分")
        self.recommend_tree.heading("price", text="价格")
        self.recommend_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(recommend_frame, orient=tk.VERTICAL, command=self.recommend_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.recommend_tree.configure(yscrollcommand=scrollbar.set)
        
        # 热门剧本标签页
        popular_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(popular_frame, text="热门剧本")
        
        # 热门剧本列表
        self.popular_tree = ttk.Treeview(
            popular_frame,
            columns=("title", "difficulty", "duration", "rating", "price"),
            show="headings"
        )
        self.popular_tree.heading("title", text="剧本名称")
        self.popular_tree.heading("difficulty", text="难度")
        self.popular_tree.heading("duration", text="时长")
        self.popular_tree.heading("rating", text="评分")
        self.popular_tree.heading("price", text="价格")
        self.popular_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(popular_frame, orient=tk.VERTICAL, command=self.popular_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.popular_tree.configure(yscrollcommand=scrollbar.set)
        
        # 搜索标签页
        search_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(search_frame, text="搜索")
        
        # 搜索框
        search_box = ttk.Frame(search_frame)
        search_box.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(
            search_box,
            text="关键词："
        ).grid(row=0, column=0, padx=5)
        
        self.search_entry = ttk.Entry(search_box, width=30)
        self.search_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(
            search_box,
            text="难度："
        ).grid(row=0, column=2, padx=5)
        
        self.difficulty_var = tk.StringVar()
        difficulty_combo = ttk.Combobox(
            search_box,
            textvariable=self.difficulty_var,
            values=["全部", "1", "2", "3", "4", "5"],
            state="readonly",
            width=5
        )
        difficulty_combo.current(0)
        difficulty_combo.grid(row=0, column=3, padx=5)
        
        ttk.Label(
            search_box,
            text="时长："
        ).grid(row=0, column=4, padx=5)
        
        self.duration_var = tk.StringVar()
        duration_combo = ttk.Combobox(
            search_box,
            textvariable=self.duration_var,
            values=["全部", "1小时以内", "1-2小时", "2-3小时", "3小时以上"],
            state="readonly",
            width=10
        )
        duration_combo.current(0)
        duration_combo.grid(row=0, column=5, padx=5)
        
        ttk.Button(
            search_box,
            text="搜索",
            command=self.search_scripts,
            style="Action.TButton"
        ).grid(row=0, column=6, padx=5)
        
        # 搜索结果列表
        self.search_tree = ttk.Treeview(
            search_frame,
            columns=("title", "difficulty", "duration", "rating", "price"),
            show="headings"
        )
        self.search_tree.heading("title", text="剧本名称")
        self.search_tree.heading("difficulty", text="难度")
        self.search_tree.heading("duration", text="时长")
        self.search_tree.heading("rating", text="评分")
        self.search_tree.heading("price", text="价格")
        self.search_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(search_frame, orient=tk.VERTICAL, command=self.search_tree.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.search_tree.configure(yscrollcommand=scrollbar.set)
        
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
        
        for frame in [recommend_frame, popular_frame, search_frame]:
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(0, weight=1)
        
        # 绑定双击事件
        self.recommend_tree.bind("<Double-1>", self.on_script_double_click)
        self.popular_tree.bind("<Double-1>", self.on_script_double_click)
        self.search_tree.bind("<Double-1>", self.on_script_double_click)
        
        # 加载数据
        self.load_recommendations()
        self.load_popular_scripts()
    
    def load_recommendations(self):
        # 清空现有数据
        for item in self.recommend_tree.get_children():
            self.recommend_tree.delete(item)
        
        # 获取推荐剧本
        scripts = self.session.query(Script).filter_by(status="active").all()
        
        for script in scripts:
            # 计算平均评分
            ratings = [review.rating for review in script.reviews]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            
            item = self.recommend_tree.insert(
                "",
                tk.END,
                values=(
                    script.title,
                    str(script.difficulty),
                    f"{script.duration}分钟",
                    f"{avg_rating:.1f}",
                    f"¥{script.price}"
                ),
                tags=(str(script.id),)
            )
    
    def load_popular_scripts(self):
        # 清空现有数据
        for item in self.popular_tree.get_children():
            self.popular_tree.delete(item)
        
        # 获取热门剧本（按评价数量排序）
        scripts = self.session.query(Script).filter_by(status="active").all()
        scripts.sort(key=lambda x: len(x.reviews), reverse=True)
        
        for script in scripts:
            # 计算平均评分
            ratings = [review.rating for review in script.reviews]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            
            item = self.popular_tree.insert(
                "",
                tk.END,
                values=(
                    script.title,
                    str(script.difficulty),
                    f"{script.duration}分钟",
                    f"{avg_rating:.1f}",
                    f"¥{script.price}"
                ),
                tags=(str(script.id),)
            )
    
    def search_scripts(self):
        # 清空现有数据
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        
        # 获取搜索条件
        keyword = self.search_entry.get().strip()
        difficulty = self.difficulty_var.get()
        duration = self.duration_var.get()
        
        # 构建查询
        query = self.session.query(Script).filter_by(status="active")
        
        if keyword:
            query = query.filter(Script.title.like(f"%{keyword}%"))
        
        if difficulty != "全部":
            query = query.filter(Script.difficulty == int(difficulty))
        
        if duration != "全部":
            if duration == "1小时以内":
                query = query.filter(Script.duration <= 60)
            elif duration == "1-2小时":
                query = query.filter(Script.duration > 60, Script.duration <= 120)
            elif duration == "2-3小时":
                query = query.filter(Script.duration > 120, Script.duration <= 180)
            else:  # 3小时以上
                query = query.filter(Script.duration > 180)
        
        # 执行查询
        scripts = query.all()
        
        for script in scripts:
            # 计算平均评分
            ratings = [review.rating for review in script.reviews]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            
            item = self.search_tree.insert(
                "",
                tk.END,
                values=(
                    script.title,
                    str(script.difficulty),
                    f"{script.duration}分钟",
                    f"{avg_rating:.1f}",
                    f"¥{script.price}"
                ),
                tags=(str(script.id),)
            )
    
    def on_script_double_click(self, event):
        tree = event.widget
        selected = tree.selection()
        if not selected:
            return
        
        script_id = int(tree.item(selected[0])["tags"][0])
        script = self.session.query(Script).get(script_id)
        
        if script:
            ScriptDetailWindow(self.auth_manager, script)
    
    def make_reservation(self, script):
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
            values=[str(i) for i in range(script.min_players, script.max_players + 1)],
            state="readonly",
            width=5
        )
        player_combo.grid(row=3, column=0, sticky=tk.W, pady=5)
        player_combo.current(0)
        
        # 计算总价
        def update_price(*args):
            try:
                players = int(player_var.get())
                total = script.price * players
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
                    script=script,
                    order_time=order_time,
                    player_count=int(player_var.get()),
                    total_price=script.price * int(player_var.get()),
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