import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import Script, Order, init_db
from script_management import AddScriptDialog
from datetime import datetime, timedelta
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

class MerchantWindow:
    def __init__(self, auth_manager):
        self.root = tk.Toplevel()
        self.root.title("商家管理")
        self.root.geometry("1200x800")
        self.auth_manager = auth_manager
        self.session = init_db()
        
        # 设置主题样式
        self.setup_styles()
        self.init_ui()
        
        # 显示操作引导
        self.show_guide()
    
    def setup_styles(self):
        style = ttk.Style()
        
        # 配置主按钮样式
        style.configure(
            "Action.TButton",
            font=("Microsoft YaHei UI", 10),
            padding=5,
            background="#4a90e2"
        )
        
        # 配置标签页样式
        style.configure(
            "TNotebook",
            background="#f5f5f5",
            tabmargins=[2, 5, 2, 0]
        )
        style.configure(
            "TNotebook.Tab",
            font=("Microsoft YaHei UI", 10),
            padding=[10, 5],
            background="#e1e1e1"
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", "#4a90e2")],
            foreground=[("selected", "white")]
        )
        
        # 配置标签框样式
        style.configure(
            "TLabelframe",
            font=("Microsoft YaHei UI", 10),
            background="#f5f5f5"
        )
        style.configure(
            "TLabelframe.Label",
            font=("Microsoft YaHei UI", 10, "bold"),
            background="#f5f5f5"
        )
        
        # 配置树形视图样式
        style.configure(
            "Treeview",
            font=("Microsoft YaHei UI", 10),
            rowheight=25,
            background="white",
            fieldbackground="white"
        )
        style.configure(
            "Treeview.Heading",
            font=("Microsoft YaHei UI", 10, "bold"),
            background="#e1e1e1"
        )
        style.map(
            "Treeview",
            background=[("selected", "#4a90e2")],
            foreground=[("selected", "white")]
        )
    
    def show_guide(self):
        guide_text = """
欢迎使用商家管理系统！

基本操作指南：
1. 在"剧本管理"标签页中，您可以：
   - 添加、编辑和删除剧本
   - 批量上架或下架剧本
   - 使用搜索和筛选功能快速找到特定剧本
   - 查看剧本统计信息

2. 在"订单管理"标签页中，您可以：
   - 查看和管理所有订单
   - 确认或完成订单
   - 导出订单数据
   - 查看订单统计信息

3. 在"数据统计"标签页中，您可以：
   - 查看剧本评分分布
   - 查看订单时间分布
   - 查看收入统计
   - 查看剧本热度统计

4. 使用提示：
   - 点击列表中的项目可以选中它
   - 使用搜索框可以按关键词搜索
   - 使用筛选下拉框可以按状态和时间范围筛选
   - 点击导出按钮可以将数据导出为CSV文件

需要帮助时，请随时点击右上角的帮助按钮。
"""
        messagebox.showinfo("操作指南", guide_text)
    
    def show_error(self, title, message, detail=None):
        """显示格式化的错误消息"""
        if detail:
            message = f"{message}\n\n详细信息：\n{detail}"
        messagebox.showerror(title, message)
    
    def show_success(self, title, message):
        """显示格式化的成功消息"""
        messagebox.showinfo(title, message)
    
    def show_warning(self, title, message):
        """显示格式化的警告消息"""
        messagebox.showwarning(title, message)
    
    def show_confirmation(self, title, message):
        """显示格式化的确认对话框"""
        return messagebox.askyesno(title, message)
    
    def init_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建帮助按钮
        help_button = ttk.Button(
            main_frame,
            text="帮助",
            command=self.show_guide,
            style="Action.TButton"
        )
        help_button.grid(row=0, column=1, sticky=tk.E, pady=(0, 10))
        
        # 创建标签页
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 剧本管理标签页
        script_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(script_frame, text="剧本管理")
        
        # 搜索和筛选框
        search_frame = ttk.LabelFrame(script_frame, text="搜索和筛选", padding="10")
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # 关键词搜索
        ttk.Label(search_frame, text="关键词：").grid(row=0, column=0, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.grid(row=0, column=1, padx=5)
        ttk.Label(search_frame, text="(可搜索剧本标题)").grid(row=0, column=2, padx=5)
        
        # 难度筛选
        ttk.Label(search_frame, text="难度：").grid(row=0, column=3, padx=5)
        self.difficulty_var = tk.StringVar(value="全部")
        difficulty_combo = ttk.Combobox(
            search_frame,
            textvariable=self.difficulty_var,
            values=["全部", "简单", "中等", "困难"],
            state="readonly",
            width=10
        )
        difficulty_combo.grid(row=0, column=4, padx=5)
        
        # 状态筛选
        ttk.Label(search_frame, text="状态：").grid(row=0, column=5, padx=5)
        self.status_var = tk.StringVar(value="全部")
        status_combo = ttk.Combobox(
            search_frame,
            textvariable=self.status_var,
            values=["全部", "待审核", "已上架", "已下架"],
            state="readonly",
            width=10
        )
        status_combo.grid(row=0, column=6, padx=5)
        
        # 搜索按钮
        ttk.Button(
            search_frame,
            text="搜索",
            command=self.search_scripts,
            style="Action.TButton"
        ).grid(row=0, column=7, padx=5)
        
        # 批量操作按钮
        batch_frame = ttk.Frame(search_frame)
        batch_frame.grid(row=0, column=8, padx=5)
        
        ttk.Button(
            batch_frame,
            text="批量上架",
            command=lambda: self.batch_update_status("已上架"),
            style="Action.TButton"
        ).grid(row=0, column=0, padx=2)
        
        ttk.Button(
            batch_frame,
            text="批量下架",
            command=lambda: self.batch_update_status("已下架"),
            style="Action.TButton"
        ).grid(row=0, column=1, padx=2)
        
        ttk.Button(
            batch_frame,
            text="批量删除",
            command=self.batch_delete_scripts,
            style="Action.TButton"
        ).grid(row=0, column=2, padx=2)
        
        # 导出按钮
        ttk.Button(
            search_frame,
            text="导出剧本",
            command=self.export_scripts,
            style="Action.TButton"
        ).grid(row=0, column=9, padx=5)
        
        # 剧本列表
        list_frame = ttk.Frame(script_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.script_tree = ttk.Treeview(
            list_frame,
            columns=("title", "difficulty", "duration", "price", "players", "status"),
            show="headings",
            height=10
        )
        self.script_tree.heading("title", text="标题")
        self.script_tree.heading("difficulty", text="难度")
        self.script_tree.heading("duration", text="时长")
        self.script_tree.heading("price", text="价格")
        self.script_tree.heading("players", text="玩家数")
        self.script_tree.heading("status", text="状态")
        
        # 设置列宽
        self.script_tree.column("title", width=200)
        self.script_tree.column("difficulty", width=100)
        self.script_tree.column("duration", width=100)
        self.script_tree.column("price", width=100)
        self.script_tree.column("players", width=100)
        self.script_tree.column("status", width=100)
        
        self.script_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.script_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.script_tree.configure(yscrollcommand=scrollbar.set)
        
        # 剧本操作按钮
        button_frame = ttk.Frame(script_frame)
        button_frame.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        ttk.Button(
            button_frame,
            text="添加剧本",
            command=self.add_script,
            style="Action.TButton"
        ).grid(row=0, column=0, padx=5)
        
        ttk.Button(
            button_frame,
            text="编辑剧本",
            command=self.edit_script,
            style="Action.TButton"
        ).grid(row=0, column=1, padx=5)
        
        ttk.Button(
            button_frame,
            text="删除剧本",
            command=self.delete_script,
            style="Action.TButton"
        ).grid(row=0, column=2, padx=5)
        
        # 剧本统计
        stats_frame = ttk.LabelFrame(script_frame, text="剧本统计", padding="10")
        stats_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # 创建统计图表
        self.create_script_stats(stats_frame)
        
        # 订单管理标签页
        order_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(order_frame, text="订单管理")
        
        # 搜索和筛选框
        order_search_frame = ttk.LabelFrame(order_frame, text="搜索和筛选", padding="10")
        order_search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # 关键词搜索
        ttk.Label(order_search_frame, text="关键词：").grid(row=0, column=0, padx=5)
        self.order_search_var = tk.StringVar()
        ttk.Entry(order_search_frame, textvariable=self.order_search_var, width=20).grid(row=0, column=1, padx=5)
        
        # 状态筛选
        ttk.Label(order_search_frame, text="状态：").grid(row=0, column=2, padx=5)
        self.order_status_var = tk.StringVar(value="全部")
        order_status_combo = ttk.Combobox(
            order_search_frame,
            textvariable=self.order_status_var,
            values=["全部", "待确认", "已确认", "已完成", "已取消"],
            state="readonly",
            width=10
        )
        order_status_combo.grid(row=0, column=3, padx=5)
        
        # 时间范围
        ttk.Label(order_search_frame, text="时间范围：").grid(row=0, column=4, padx=5)
        self.order_date_range_var = tk.StringVar(value="全部")
        order_date_range_combo = ttk.Combobox(
            order_search_frame,
            textvariable=self.order_date_range_var,
            values=["全部", "今天", "本周", "本月", "最近三个月"],
            state="readonly",
            width=10
        )
        order_date_range_combo.grid(row=0, column=5, padx=5)
        
        # 搜索按钮
        ttk.Button(
            order_search_frame,
            text="搜索",
            command=self.search_orders,
            style="Action.TButton"
        ).grid(row=0, column=6, padx=5)
        
        # 导出按钮
        ttk.Button(
            order_search_frame,
            text="导出订单",
            command=self.export_orders,
            style="Action.TButton"
        ).grid(row=0, column=7, padx=5)
        
        # 订单列表
        self.order_tree = ttk.Treeview(
            order_frame,
            columns=("script", "customer", "time", "players", "price", "status"),
            show="headings",
            height=10
        )
        self.order_tree.heading("script", text="剧本")
        self.order_tree.heading("customer", text="客户")
        self.order_tree.heading("time", text="预约时间")
        self.order_tree.heading("players", text="玩家数")
        self.order_tree.heading("price", text="总价")
        self.order_tree.heading("status", text="状态")
        self.order_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(order_frame, orient=tk.VERTICAL, command=self.order_tree.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.order_tree.configure(yscrollcommand=scrollbar.set)
        
        # 订单操作按钮
        order_button_frame = ttk.Frame(order_frame)
        order_button_frame.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        ttk.Button(
            order_button_frame,
            text="确认订单",
            command=self.confirm_order,
            style="Action.TButton"
        ).grid(row=0, column=0, padx=5)
        
        ttk.Button(
            order_button_frame,
            text="完成订单",
            command=self.complete_order,
            style="Action.TButton"
        ).grid(row=0, column=1, padx=5)
        
        # 订单统计
        order_stats_frame = ttk.LabelFrame(order_frame, text="订单统计", padding="10")
        order_stats_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # 创建统计图表
        self.create_order_stats(order_stats_frame)
        
        # 数据统计标签页
        stats_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(stats_frame, text="数据统计")
        
        # 创建统计图表
        self.create_stats(stats_frame)
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        for frame in [script_frame, order_frame, stats_frame]:
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(1, weight=1)
        
        # 加载数据
        self.load_data()
    
    def create_script_stats(self, parent):
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        
        # 获取剧本数据
        scripts = self.session.query(Script).filter_by(
            merchant_id=self.auth_manager.get_current_user().id
        ).all()
        
        # 难度统计
        difficulty_counts = {}
        for script in scripts:
            difficulty_counts[script.difficulty] = difficulty_counts.get(script.difficulty, 0) + 1
        
        # 绘制难度统计饼图
        ax1.pie(difficulty_counts.values(), labels=difficulty_counts.keys(), autopct='%1.1f%%')
        ax1.set_title('剧本难度分布')
        
        # 状态统计
        status_counts = {}
        for script in scripts:
            status_counts[script.status] = status_counts.get(script.status, 0) + 1
        
        # 绘制状态统计饼图
        ax2.pie(status_counts.values(), labels=status_counts.keys(), autopct='%1.1f%%')
        ax2.set_title('剧本状态分布')
        
        # 调整布局
        plt.tight_layout()
        
        # 创建画布
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E))
    
    def create_order_stats(self, parent):
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        
        # 获取订单数据
        orders = self.session.query(Order).join(Script).filter(
            Script.merchant_id == self.auth_manager.get_current_user().id
        ).all()
        
        # 状态统计
        status_counts = {}
        for order in orders:
            status_counts[order.status] = status_counts.get(order.status, 0) + 1
        
        # 绘制状态统计饼图
        ax1.pie(status_counts.values(), labels=status_counts.keys(), autopct='%1.1f%%')
        ax1.set_title('订单状态分布')
        
        # 收入统计
        dates = [order.order_time.date() for order in orders]
        incomes = [order.total_price for order in orders]
        date_incomes = pd.Series(incomes, index=dates).groupby(level=0).sum()
        
        # 绘制收入统计折线图
        ax2.plot(date_incomes.index, date_incomes.values)
        ax2.set_title('收入统计')
        ax2.set_xlabel('日期')
        ax2.set_ylabel('收入（元）')
        
        # 调整布局
        plt.tight_layout()
        
        # 创建画布
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E))
    
    def create_stats(self, parent):
        # 创建图表
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        
        # 获取数据
        scripts = self.session.query(Script).filter_by(
            merchant_id=self.auth_manager.get_current_user().id
        ).all()
        
        orders = self.session.query(Order).join(Script).filter(
            Script.merchant_id == self.auth_manager.get_current_user().id
        ).all()
        
        # 剧本评分统计
        ratings = []
        for script in scripts:
            if script.reviews:
                avg_rating = sum(review.rating for review in script.reviews) / len(script.reviews)
                ratings.append(avg_rating)
        
        if ratings:
            ax1.hist(ratings, bins=10, range=(0, 5))
            ax1.set_title('剧本评分分布')
            ax1.set_xlabel('评分')
            ax1.set_ylabel('剧本数')
        
        # 订单时间分布
        dates = [order.order_time.date() for order in orders]
        date_counts = pd.Series(dates).value_counts().sort_index()
        
        ax2.plot(date_counts.index, date_counts.values)
        ax2.set_title('订单时间分布')
        ax2.set_xlabel('日期')
        ax2.set_ylabel('订单数')
        
        # 收入统计
        dates = [order.order_time.date() for order in orders]
        incomes = [order.total_price for order in orders]
        date_incomes = pd.Series(incomes, index=dates).groupby(level=0).sum()
        
        ax3.plot(date_incomes.index, date_incomes.values)
        ax3.set_title('收入统计')
        ax3.set_xlabel('日期')
        ax3.set_ylabel('收入（元）')
        
        # 剧本热度统计
        script_orders = {}
        for order in orders:
            script_orders[order.script.title] = script_orders.get(order.script.title, 0) + 1
        
        if script_orders:
            scripts = list(script_orders.keys())
            orders = list(script_orders.values())
            ax4.bar(scripts, orders)
            ax4.set_title('剧本热度统计')
            ax4.set_xlabel('剧本')
            ax4.set_ylabel('订单数')
            plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # 调整布局
        plt.tight_layout()
        
        # 创建画布
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def search_scripts(self):
        # 清空现有数据
        for item in self.script_tree.get_children():
            self.script_tree.delete(item)
        
        # 获取搜索条件
        keyword = self.search_var.get().strip()
        difficulty = self.difficulty_var.get()
        status = self.status_var.get()
        
        # 构建查询
        query = self.session.query(Script).filter_by(
            merchant_id=self.auth_manager.get_current_user().id
        )
        
        if keyword:
            query = query.filter(Script.title.like(f"%{keyword}%"))
        
        if difficulty != "全部":
            query = query.filter(Script.difficulty == difficulty)
        
        if status != "全部":
            query = query.filter(Script.status == status)
        
        # 执行查询
        scripts = query.all()
        
        for script in scripts:
            self.script_tree.insert(
                "",
                tk.END,
                values=(
                    script.title,
                    script.difficulty,
                    f"{script.duration}小时",
                    f"¥{script.price}",
                    f"{script.min_players}-{script.max_players}人",
                    script.status
                ),
                tags=(str(script.id),)
            )
    
    def search_orders(self):
        # 清空现有数据
        for item in self.order_tree.get_children():
            self.order_tree.delete(item)
        
        # 获取搜索条件
        keyword = self.order_search_var.get().strip()
        status = self.order_status_var.get()
        date_range = self.order_date_range_var.get()
        
        # 构建查询
        query = self.session.query(Order).join(Script).filter(
            Script.merchant_id == self.auth_manager.get_current_user().id
        )
        
        if keyword:
            query = query.join(User).filter(User.username.like(f"%{keyword}%"))
        
        if status != "全部":
            query = query.filter(Order.status == status)
        
        if date_range != "全部":
            now = datetime.now()
            if date_range == "今天":
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif date_range == "本周":
                start_date = now - timedelta(days=now.weekday())
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            elif date_range == "本月":
                start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            else:  # 最近三个月
                start_date = now - timedelta(days=90)
            query = query.filter(Order.order_time >= start_date)
        
        # 执行查询
        orders = query.all()
        
        for order in orders:
            self.order_tree.insert(
                "",
                tk.END,
                values=(
                    order.script.title,
                    order.user.username,
                    order.order_time.strftime("%Y-%m-%d %H:%M"),
                    f"{order.player_count}人",
                    f"¥{order.total_price}",
                    order.status
                ),
                tags=(str(order.id),)
            )
    
    def batch_update_status(self, status):
        selected = self.script_tree.selection()
        if not selected:
            self.show_warning("操作提示", "请先选择要操作的剧本")
            return
        
        if self.show_confirmation(
            "确认操作",
            f'确定要将选中的{len(selected)}个剧本{status}吗？\n'
            '此操作将影响所有选中的剧本。'
        ):
            try:
                for item in selected:
                    script_id = int(self.script_tree.item(item)["tags"][0])
                    script = self.session.query(Script).get(script_id)
                    script.status = status
                
                self.session.commit()
                self.load_data()
                self.show_success("操作成功", f"已成功将{len(selected)}个剧本{status}")
            except Exception as e:
                self.session.rollback()
                self.show_error(
                    "操作失败",
                    f"批量{status}剧本时发生错误",
                    str(e)
                )
    
    def batch_delete_scripts(self):
        selected = self.script_tree.selection()
        if not selected:
            self.show_warning("操作提示", "请先选择要删除的剧本")
            return
        
        if self.show_confirmation(
            "确认删除",
            f'确定要删除选中的{len(selected)}个剧本吗？\n'
            '此操作不可恢复！\n'
            '注意：这将同时删除这些剧本的所有评价和订单。'
        ):
            try:
                for item in selected:
                    script_id = int(self.script_tree.item(item)["tags"][0])
                    script = self.session.query(Script).get(script_id)
                    script.status = "deleted"  # 软删除
                
                self.session.commit()
                self.load_data()
                self.show_success("操作成功", f"已成功删除{len(selected)}个剧本")
            except Exception as e:
                self.session.rollback()
                self.show_error(
                    "删除失败",
                    "批量删除剧本时发生错误",
                    str(e)
                )
    
    def export_scripts(self):
        # 获取要导出的剧本
        scripts = []
        for item in self.script_tree.get_children():
            values = self.script_tree.item(item)["values"]
            scripts.append({
                "标题": values[0],
                "难度": values[1],
                "时长": values[2],
                "价格": values[3],
                "玩家数": values[4],
                "状态": values[5]
            })
        
        if not scripts:
            self.show_warning("导出提示", "没有可导出的剧本数据")
            return
        
        # 选择保存路径
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv")],
            title="导出剧本"
        )
        
        if not file_path:
            return
        
        try:
            # 写入CSV文件
            with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=["标题", "难度", "时长", "价格", "玩家数", "状态"])
                writer.writeheader()
                writer.writerows(scripts)
            
            self.show_success("导出成功", f"剧本数据已成功导出到：\n{file_path}")
        except Exception as e:
            self.show_error(
                "导出失败",
                "导出剧本数据时发生错误",
                str(e)
            )
    
    def export_orders(self):
        # 获取要导出的订单
        orders = []
        for item in self.order_tree.get_children():
            values = self.order_tree.item(item)["values"]
            orders.append({
                "剧本": values[0],
                "客户": values[1],
                "预约时间": values[2],
                "玩家数": values[3],
                "总价": values[4],
                "状态": values[5]
            })
        
        if not orders:
            messagebox.showwarning("警告", "没有可导出的订单")
            return
        
        # 选择保存路径
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv")],
            title="导出订单"
        )
        
        if not file_path:
            return
        
        try:
            # 写入CSV文件
            with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=["剧本", "客户", "预约时间", "玩家数", "总价", "状态"])
                writer.writeheader()
                writer.writerows(orders)
            
            messagebox.showinfo("成功", "订单导出成功")
        except Exception as e:
            messagebox.showerror("错误", f"导出订单失败: {str(e)}")
    
    def load_data(self):
        self.search_scripts()
        self.search_orders()
    
    def add_script(self):
        dialog = AddScriptDialog(self.root)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            try:
                script = Script(
                    title=dialog.result["title"],
                    difficulty=dialog.result["difficulty"],
                    duration=dialog.result["duration"],
                    description=dialog.result["description"],
                    merchant=self.auth_manager.get_current_user(),
                    price=0.0,  # 默认价格
                    min_players=4,  # 默认最少玩家数
                    max_players=8,  # 默认最多玩家数
                    status="active"
                )
                self.session.add(script)
                self.session.commit()
                self.load_data()
                messagebox.showinfo("成功", "剧本添加成功")
            except Exception as e:
                self.session.rollback()
                messagebox.showerror("错误", f"添加剧本失败: {str(e)}")
    
    def edit_script(self):
        selected = self.script_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要编辑的剧本")
            return
        
        script_id = int(self.script_tree.item(selected)["tags"][0])
        script = self.session.query(Script).get(script_id)
        
        dialog = AddScriptDialog(self.root)
        dialog.name_input.insert(0, script.title)
        dialog.difficulty_var.set(str(script.difficulty))
        dialog.duration_var.set(str(script.duration))
        dialog.desc_input.insert("1.0", script.description)
        
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            try:
                script.title = dialog.result["title"]
                script.difficulty = dialog.result["difficulty"]
                script.duration = dialog.result["duration"]
                script.description = dialog.result["description"]
                self.session.commit()
                self.load_data()
                messagebox.showinfo("成功", "剧本更新成功")
            except Exception as e:
                self.session.rollback()
                messagebox.showerror("错误", f"更新剧本失败: {str(e)}")
    
    def delete_script(self):
        selected = self.script_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的剧本")
            return
        
        script_id = int(self.script_tree.item(selected)["tags"][0])
        script = self.session.query(Script).get(script_id)
        
        if messagebox.askyesno(
            "确认删除",
            f'确定要删除剧本 "{script.title}" 吗？\n'
            '注意：这将同时删除该剧本的所有评价和订单。'
        ):
            try:
                script.status = "deleted"  # 软删除
                self.session.commit()
                self.load_data()
                messagebox.showinfo("成功", "剧本删除成功")
            except Exception as e:
                self.session.rollback()
                messagebox.showerror("错误", f"删除剧本失败: {str(e)}")
    
    def confirm_order(self):
        selected = self.order_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要确认的订单")
            return
        
        order_id = int(self.order_tree.item(selected)["tags"][0])
        order = self.session.query(Order).get(order_id)
        
        if messagebox.askyesno(
            "确认操作",
            f'确定要确认订单 "{order.script.title}" 吗？'
        ):
            try:
                order.status = "已确认"
                self.session.commit()
                self.load_data()
                messagebox.showinfo("成功", "订单确认成功")
            except Exception as e:
                self.session.rollback()
                messagebox.showerror("错误", f"确认订单失败: {str(e)}")
    
    def complete_order(self):
        selected = self.order_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要完成的订单")
            return
        
        order_id = int(self.order_tree.item(selected)["tags"][0])
        order = self.session.query(Order).get(order_id)
        
        if messagebox.askyesno(
            "确认操作",
            f'确定要完成订单 "{order.script.title}" 吗？'
        ):
            try:
                order.status = "已完成"
                self.session.commit()
                self.load_data()
                messagebox.showinfo("成功", "订单完成成功")
            except Exception as e:
                self.session.rollback()
                messagebox.showerror("错误", f"完成订单失败: {str(e)}") 