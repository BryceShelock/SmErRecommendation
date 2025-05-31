import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import User, Script, Review, UserRole, init_db
from datetime import datetime, timedelta
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import psutil
import threading
import time

class AdminWindow:
    def __init__(self, auth_manager):
        self.root = tk.Toplevel()
        self.root.title("管理员控制台")
        self.root.geometry("1200x800")
        self.auth_manager = auth_manager
        self.session = init_db()
        
        # 设置主题样式
        self.setup_styles()
        self.init_ui()
        
        # 显示操作引导
        self.show_guide()
        
        # 启动系统监控
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_system)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
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
        
        # 配置进度条样式
        style.configure(
            "TProgressbar",
            background="#4a90e2",
            troughcolor="#e1e1e1"
        )
    
    def show_guide(self):
        guide_text = """
欢迎使用管理员控制台！

基本操作指南：
1. 在"用户管理"标签页中，您可以：
   - 添加、编辑和删除用户
   - 管理用户角色和状态
   - 使用搜索和筛选功能快速找到特定用户
   - 查看用户统计信息

2. 在"剧本管理"标签页中，您可以：
   - 审核剧本
   - 下架违规剧本
   - 查看剧本统计信息
   - 导出剧本数据

3. 在"评价管理"标签页中，您可以：
   - 查看和管理用户评价
   - 删除违规评价
   - 查看评价统计信息
   - 导出评价数据

4. 在"系统监控"标签页中，您可以：
   - 实时监控系统资源使用情况
   - 查看系统信息
   - 监控CPU、内存和磁盘使用率

5. 使用提示：
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
        
        # 用户管理标签页
        user_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(user_frame, text="用户管理")
        
        # 搜索和筛选框
        search_frame = ttk.LabelFrame(user_frame, text="搜索和筛选", padding="10")
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # 关键词搜索
        ttk.Label(search_frame, text="关键词：").grid(row=0, column=0, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.grid(row=0, column=1, padx=5)
        ttk.Label(search_frame, text="(可搜索用户名或邮箱)").grid(row=0, column=2, padx=5)
        
        # 角色筛选
        ttk.Label(search_frame, text="角色：").grid(row=0, column=3, padx=5)
        self.role_var = tk.StringVar(value="全部")
        role_combo = ttk.Combobox(
            search_frame,
            textvariable=self.role_var,
            values=["全部", "用户", "商家", "管理员"],
            state="readonly",
            width=10
        )
        role_combo.grid(row=0, column=4, padx=5)
        
        # 状态筛选
        ttk.Label(search_frame, text="状态：").grid(row=0, column=5, padx=5)
        self.status_var = tk.StringVar(value="全部")
        status_combo = ttk.Combobox(
            search_frame,
            textvariable=self.status_var,
            values=["全部", "正常", "禁用"],
            state="readonly",
            width=10
        )
        status_combo.grid(row=0, column=6, padx=5)
        
        # 搜索按钮
        ttk.Button(
            search_frame,
            text="搜索",
            command=self.search_users,
            style="Action.TButton"
        ).grid(row=0, column=7, padx=5)
        
        # 导出按钮
        ttk.Button(
            search_frame,
            text="导出用户",
            command=self.export_users,
            style="Action.TButton"
        ).grid(row=0, column=8, padx=5)
        
        # 用户列表
        list_frame = ttk.Frame(user_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.user_tree = ttk.Treeview(
            list_frame,
            columns=("username", "role", "email", "status"),
            show="headings",
            height=10
        )
        self.user_tree.heading("username", text="用户名")
        self.user_tree.heading("role", text="角色")
        self.user_tree.heading("email", text="邮箱")
        self.user_tree.heading("status", text="状态")
        
        # 设置列宽
        self.user_tree.column("username", width=150)
        self.user_tree.column("role", width=100)
        self.user_tree.column("email", width=200)
        self.user_tree.column("status", width=100)
        
        self.user_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.user_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.user_tree.configure(yscrollcommand=scrollbar.set)
        
        # 用户操作按钮
        button_frame = ttk.Frame(user_frame)
        button_frame.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        ttk.Button(
            button_frame,
            text="添加用户",
            command=self.add_user,
            style="Action.TButton"
        ).grid(row=0, column=0, padx=5)
        
        ttk.Button(
            button_frame,
            text="编辑用户",
            command=self.edit_user,
            style="Action.TButton"
        ).grid(row=0, column=1, padx=5)
        
        ttk.Button(
            button_frame,
            text="删除用户",
            command=self.delete_user,
            style="Action.TButton"
        ).grid(row=0, column=2, padx=5)
        
        # 用户统计
        stats_frame = ttk.LabelFrame(user_frame, text="用户统计", padding="10")
        stats_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # 创建统计图表
        self.create_user_stats(stats_frame)
        
        # 剧本管理标签页
        script_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(script_frame, text="剧本管理")
        
        # 搜索和筛选框
        script_search_frame = ttk.LabelFrame(script_frame, text="搜索和筛选", padding="10")
        script_search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # 关键词搜索
        ttk.Label(script_search_frame, text="关键词：").grid(row=0, column=0, padx=5)
        self.script_search_var = tk.StringVar()
        ttk.Entry(script_search_frame, textvariable=self.script_search_var, width=20).grid(row=0, column=1, padx=5)
        
        # 难度筛选
        ttk.Label(script_search_frame, text="难度：").grid(row=0, column=2, padx=5)
        self.script_difficulty_var = tk.StringVar(value="全部")
        script_difficulty_combo = ttk.Combobox(
            script_search_frame,
            textvariable=self.script_difficulty_var,
            values=["全部", "简单", "中等", "困难"],
            state="readonly",
            width=10
        )
        script_difficulty_combo.grid(row=0, column=3, padx=5)
        
        # 状态筛选
        ttk.Label(script_search_frame, text="状态：").grid(row=0, column=4, padx=5)
        self.script_status_var = tk.StringVar(value="全部")
        script_status_combo = ttk.Combobox(
            script_search_frame,
            textvariable=self.script_status_var,
            values=["全部", "待审核", "已上架", "已下架"],
            state="readonly",
            width=10
        )
        script_status_combo.grid(row=0, column=5, padx=5)
        
        # 搜索按钮
        ttk.Button(
            script_search_frame,
            text="搜索",
            command=self.search_scripts,
            style="Action.TButton"
        ).grid(row=0, column=6, padx=5)
        
        # 导出按钮
        ttk.Button(
            script_search_frame,
            text="导出剧本",
            command=self.export_scripts,
            style="Action.TButton"
        ).grid(row=0, column=7, padx=5)
        
        # 剧本列表
        self.script_tree = ttk.Treeview(
            script_frame,
            columns=("title", "merchant", "status", "reviews"),
            show="headings",
            height=10
        )
        self.script_tree.heading("title", text="标题")
        self.script_tree.heading("merchant", text="商家")
        self.script_tree.heading("status", text="状态")
        self.script_tree.heading("reviews", text="评价数")
        self.script_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(script_frame, orient=tk.VERTICAL, command=self.script_tree.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.script_tree.configure(yscrollcommand=scrollbar.set)
        
        # 剧本操作按钮
        script_button_frame = ttk.Frame(script_frame)
        script_button_frame.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        ttk.Button(
            script_button_frame,
            text="审核剧本",
            command=self.review_script,
            style="Action.TButton"
        ).grid(row=0, column=0, padx=5)
        
        ttk.Button(
            script_button_frame,
            text="下架剧本",
            command=self.take_down_script,
            style="Action.TButton"
        ).grid(row=0, column=1, padx=5)
        
        # 剧本统计
        script_stats_frame = ttk.LabelFrame(script_frame, text="剧本统计", padding="10")
        script_stats_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # 创建统计图表
        self.create_script_stats(script_stats_frame)
        
        # 评价管理标签页
        review_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(review_frame, text="评价管理")
        
        # 搜索和筛选框
        review_search_frame = ttk.LabelFrame(review_frame, text="搜索和筛选", padding="10")
        review_search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # 关键词搜索
        ttk.Label(review_search_frame, text="关键词：").grid(row=0, column=0, padx=5)
        self.review_search_var = tk.StringVar()
        ttk.Entry(review_search_frame, textvariable=self.review_search_var, width=20).grid(row=0, column=1, padx=5)
        
        # 评分筛选
        ttk.Label(review_search_frame, text="评分：").grid(row=0, column=2, padx=5)
        self.rating_var = tk.StringVar(value="全部")
        rating_combo = ttk.Combobox(
            review_search_frame,
            textvariable=self.rating_var,
            values=["全部", "1星", "2星", "3星", "4星", "5星"],
            state="readonly",
            width=10
        )
        rating_combo.grid(row=0, column=3, padx=5)
        
        # 时间范围
        ttk.Label(review_search_frame, text="时间范围：").grid(row=0, column=4, padx=5)
        self.review_date_range_var = tk.StringVar(value="全部")
        review_date_range_combo = ttk.Combobox(
            review_search_frame,
            textvariable=self.review_date_range_var,
            values=["全部", "今天", "本周", "本月", "最近三个月"],
            state="readonly",
            width=10
        )
        review_date_range_combo.grid(row=0, column=5, padx=5)
        
        # 搜索按钮
        ttk.Button(
            review_search_frame,
            text="搜索",
            command=self.search_reviews,
            style="Action.TButton"
        ).grid(row=0, column=6, padx=5)
        
        # 导出按钮
        ttk.Button(
            review_search_frame,
            text="导出评价",
            command=self.export_reviews,
            style="Action.TButton"
        ).grid(row=0, column=7, padx=5)
        
        # 评价列表
        self.review_tree = ttk.Treeview(
            review_frame,
            columns=("script", "user", "rating", "content"),
            show="headings",
            height=10
        )
        self.review_tree.heading("script", text="剧本")
        self.review_tree.heading("user", text="用户")
        self.review_tree.heading("rating", text="评分")
        self.review_tree.heading("content", text="评价内容")
        self.review_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(review_frame, orient=tk.VERTICAL, command=self.review_tree.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.review_tree.configure(yscrollcommand=scrollbar.set)
        
        # 评价操作按钮
        review_button_frame = ttk.Frame(review_frame)
        review_button_frame.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        ttk.Button(
            review_button_frame,
            text="删除评价",
            command=self.delete_review,
            style="Action.TButton"
        ).grid(row=0, column=0, padx=5)
        
        # 评价统计
        review_stats_frame = ttk.LabelFrame(review_frame, text="评价统计", padding="10")
        review_stats_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # 创建统计图表
        self.create_review_stats(review_stats_frame)
        
        # 系统监控标签页
        monitor_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(monitor_frame, text="系统监控")
        
        # CPU使用率
        cpu_frame = ttk.LabelFrame(monitor_frame, text="CPU使用率", padding="10")
        cpu_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.cpu_label = ttk.Label(cpu_frame, text="0%", font=("Microsoft YaHei UI", 10))
        self.cpu_label.grid(row=0, column=0, padx=5)
        
        self.cpu_progress = ttk.Progressbar(
            cpu_frame,
            length=200,
            mode="determinate",
            style="TProgressbar"
        )
        self.cpu_progress.grid(row=0, column=1, padx=5)
        
        # 内存使用率
        memory_frame = ttk.LabelFrame(monitor_frame, text="内存使用率", padding="10")
        memory_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.memory_label = ttk.Label(memory_frame, text="0%", font=("Microsoft YaHei UI", 10))
        self.memory_label.grid(row=0, column=0, padx=5)
        
        self.memory_progress = ttk.Progressbar(
            memory_frame,
            length=200,
            mode="determinate",
            style="TProgressbar"
        )
        self.memory_progress.grid(row=0, column=1, padx=5)
        
        # 磁盘使用率
        disk_frame = ttk.LabelFrame(monitor_frame, text="磁盘使用率", padding="10")
        disk_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.disk_label = ttk.Label(disk_frame, text="0%", font=("Microsoft YaHei UI", 10))
        self.disk_label.grid(row=0, column=0, padx=5)
        
        self.disk_progress = ttk.Progressbar(
            disk_frame,
            length=200,
            mode="determinate",
            style="TProgressbar"
        )
        self.disk_progress.grid(row=0, column=1, padx=5)
        
        # 系统信息
        info_frame = ttk.LabelFrame(monitor_frame, text="系统信息", padding="10")
        info_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.info_text = tk.Text(
            info_frame,
            height=10,
            width=50,
            font=("Microsoft YaHei UI", 10)
        )
        self.info_text.grid(row=0, column=0, padx=5, pady=5)
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        for frame in [user_frame, script_frame, review_frame, monitor_frame]:
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(1, weight=1)
        
        # 加载数据
        self.load_data()
    
    def create_user_stats(self, parent):
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        
        # 获取用户数据
        users = self.session.query(User).all()
        
        # 角色统计
        role_counts = {}
        for user in users:
            role_counts[user.role.value] = role_counts.get(user.role.value, 0) + 1
        
        # 绘制角色统计饼图
        ax1.pie(role_counts.values(), labels=role_counts.keys(), autopct='%1.1f%%')
        ax1.set_title('用户角色分布')
        
        # 状态统计
        status_counts = {}
        for user in users:
            status_counts["正常" if user.is_active else "禁用"] = status_counts.get("正常" if user.is_active else "禁用", 0) + 1
        
        # 绘制状态统计饼图
        ax2.pie(status_counts.values(), labels=status_counts.keys(), autopct='%1.1f%%')
        ax2.set_title('用户状态分布')
        
        # 调整布局
        plt.tight_layout()
        
        # 创建画布
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E))
    
    def create_script_stats(self, parent):
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        
        # 获取剧本数据
        scripts = self.session.query(Script).all()
        
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
    
    def create_review_stats(self, parent):
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        
        # 获取评价数据
        reviews = self.session.query(Review).all()
        
        # 评分统计
        rating_counts = {}
        for review in reviews:
            rating_counts[review.rating] = rating_counts.get(review.rating, 0) + 1
        
        # 绘制评分统计饼图
        ax1.pie(rating_counts.values(), labels=[f"{k}星" for k in rating_counts.keys()], autopct='%1.1f%%')
        ax1.set_title('评价评分分布')
        
        # 时间统计
        dates = [review.created_at.date() for review in reviews]
        date_counts = pd.Series(dates).value_counts().sort_index()
        
        # 绘制时间统计折线图
        ax2.plot(date_counts.index, date_counts.values)
        ax2.set_title('评价时间分布')
        ax2.set_xlabel('日期')
        ax2.set_ylabel('评价数')
        
        # 调整布局
        plt.tight_layout()
        
        # 创建画布
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E))
    
    def monitor_system(self):
        while self.monitoring:
            try:
                # CPU使用率
                cpu_percent = psutil.cpu_percent()
                self.cpu_label.config(text=f"{cpu_percent}%")
                self.cpu_progress["value"] = cpu_percent
                
                # 内存使用率
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                self.memory_label.config(text=f"{memory_percent}%")
                self.memory_progress["value"] = memory_percent
                
                # 磁盘使用率
                disk = psutil.disk_usage('/')
                disk_percent = disk.percent
                self.disk_label.config(text=f"{disk_percent}%")
                self.disk_progress["value"] = disk_percent
                
                # 系统信息
                info = f"""操作系统: {psutil.sys.platform}
CPU核心数: {psutil.cpu_count()}
总内存: {memory.total / (1024 * 1024 * 1024):.1f}GB
可用内存: {memory.available / (1024 * 1024 * 1024):.1f}GB
总磁盘空间: {disk.total / (1024 * 1024 * 1024):.1f}GB
可用磁盘空间: {disk.free / (1024 * 1024 * 1024):.1f}GB
"""
                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(tk.END, info)
                
                time.sleep(1)
            except Exception as e:
                self.show_error(
                    "监控错误",
                    "系统监控过程中发生错误",
                    str(e)
                )
                time.sleep(5)
    
    def search_users(self):
        # 清空现有数据
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        
        # 获取搜索条件
        keyword = self.search_var.get().strip()
        role = self.role_var.get()
        status = self.status_var.get()
        
        # 构建查询
        query = self.session.query(User)
        
        if keyword:
            query = query.filter(
                (User.username.like(f"%{keyword}%")) |
                (User.email.like(f"%{keyword}%"))
            )
        
        if role != "全部":
            role_map = {
                "用户": UserRole.user,
                "商家": UserRole.merchant,
                "管理员": UserRole.admin
            }
            query = query.filter(User.role == role_map[role])
        
        if status != "全部":
            query = query.filter(User.is_active == (status == "正常"))
        
        # 执行查询
        users = query.all()
        
        for user in users:
            self.user_tree.insert(
                "",
                tk.END,
                values=(
                    user.username,
                    user.role.value,
                    user.email,
                    "正常" if user.is_active else "禁用"
                ),
                tags=(str(user.id),)
            )
    
    def search_scripts(self):
        # 清空现有数据
        for item in self.script_tree.get_children():
            self.script_tree.delete(item)
        
        # 获取搜索条件
        keyword = self.script_search_var.get().strip()
        difficulty = self.script_difficulty_var.get()
        status = self.script_status_var.get()
        
        # 构建查询
        query = self.session.query(Script)
        
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
                    script.merchant.username,
                    script.status,
                    len(script.reviews)
                ),
                tags=(str(script.id),)
            )
    
    def search_reviews(self):
        # 清空现有数据
        for item in self.review_tree.get_children():
            self.review_tree.delete(item)
        
        # 获取搜索条件
        keyword = self.review_search_var.get().strip()
        rating = self.rating_var.get()
        date_range = self.review_date_range_var.get()
        
        # 构建查询
        query = self.session.query(Review)
        
        if keyword:
            query = query.join(Script).filter(Script.title.like(f"%{keyword}%"))
        
        if rating != "全部":
            rating_value = int(rating[0])
            query = query.filter(Review.rating == rating_value)
        
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
            query = query.filter(Review.created_at >= start_date)
        
        # 执行查询
        reviews = query.all()
        
        for review in reviews:
            self.review_tree.insert(
                "",
                tk.END,
                values=(
                    review.script.title,
                    review.user.username,
                    f"{review.rating}星",
                    review.content
                ),
                tags=(str(review.id),)
            )
    
    def export_users(self):
        # 获取要导出的用户
        users = []
        for item in self.user_tree.get_children():
            values = self.user_tree.item(item)["values"]
            users.append({
                "用户名": values[0],
                "角色": values[1],
                "邮箱": values[2],
                "状态": values[3]
            })
        
        if not users:
            self.show_warning("导出提示", "没有可导出的用户数据")
            return
        
        # 选择保存路径
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv")],
            title="导出用户"
        )
        
        if not file_path:
            return
        
        try:
            # 写入CSV文件
            with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=["用户名", "角色", "邮箱", "状态"])
                writer.writeheader()
                writer.writerows(users)
            
            self.show_success("导出成功", f"用户数据已成功导出到：\n{file_path}")
        except Exception as e:
            self.show_error(
                "导出失败",
                "导出用户数据时发生错误",
                str(e)
            )
    
    def export_scripts(self):
        # 获取要导出的剧本
        scripts = []
        for item in self.script_tree.get_children():
            values = self.script_tree.item(item)["values"]
            scripts.append({
                "标题": values[0],
                "商家": values[1],
                "状态": values[2],
                "评价数": values[3]
            })
        
        if not scripts:
            messagebox.showwarning("警告", "没有可导出的剧本")
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
                writer = csv.DictWriter(f, fieldnames=["标题", "商家", "状态", "评价数"])
                writer.writeheader()
                writer.writerows(scripts)
            
            messagebox.showinfo("成功", "剧本导出成功")
        except Exception as e:
            messagebox.showerror("错误", f"导出剧本失败: {str(e)}")
    
    def export_reviews(self):
        # 获取要导出的评价
        reviews = []
        for item in self.review_tree.get_children():
            values = self.review_tree.item(item)["values"]
            reviews.append({
                "剧本": values[0],
                "用户": values[1],
                "评分": values[2],
                "评价内容": values[3]
            })
        
        if not reviews:
            messagebox.showwarning("警告", "没有可导出的评价")
            return
        
        # 选择保存路径
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv")],
            title="导出评价"
        )
        
        if not file_path:
            return
        
        try:
            # 写入CSV文件
            with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=["剧本", "用户", "评分", "评价内容"])
                writer.writeheader()
                writer.writerows(reviews)
            
            messagebox.showinfo("成功", "评价导出成功")
        except Exception as e:
            messagebox.showerror("错误", f"导出评价失败: {str(e)}")
    
    def load_data(self):
        self.search_users()
        self.search_scripts()
        self.search_reviews()
    
    def add_user(self):
        # FIXME: 实现添加用户功能
        pass
    
    def edit_user(self):
        # FIXME: 实现编辑用户功能
        pass
    
    def delete_user(self):
        # FIXME: 实现删除用户功能
        pass
    
    def review_script(self):
        # FIXME: 实现审核剧本功能
        pass
    
    def take_down_script(self):
        # FIXME: 实现下架剧本功能
        pass
    
    def delete_review(self):
        # FIXME: 实现删除评价功能
        pass 