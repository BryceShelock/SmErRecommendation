import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import Order, Script, User, init_db
from datetime import datetime, timedelta
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

class OrderWindow:
    def __init__(self, auth_manager):
        self.root = tk.Toplevel()
        self.root.title("我的订单")
        self.root.geometry("1000x600")
        self.auth_manager = auth_manager
        self.session = init_db()
        
        # 设置主题样式
        self.setup_styles()
        self.init_ui()
        
        # 加载数据
        self.load_orders()
    
    def setup_styles(self):
        style = ttk.Style()
        
        # 配置主按钮样式
        style.configure(
            "Action.TButton",
            font=("Microsoft YaHei UI", 10),
            padding=5
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
        
        # 配置标签样式
        style.configure(
            "TLabel",
            font=("Microsoft YaHei UI", 10)
        )
        
        # 配置下拉框样式
        style.configure(
            "TCombobox",
            font=("Microsoft YaHei UI", 10)
        )
        
        # 配置输入框样式
        style.configure(
            "TEntry",
            font=("Microsoft YaHei UI", 10)
        )
    
    def show_guide(self):
        guide_text = """
欢迎使用订单管理！

基本操作指南：
1. 查看订单：
   - 在列表中查看所有订单信息
   - 使用搜索框可以按剧本名称搜索
   - 使用筛选下拉框可以按状态筛选

2. 订单操作：
   - 点击"取消订单"可以取消未完成的订单
   - 点击"查看详情"可以查看订单详细信息

3. 使用提示：
   - 点击列表中的订单可以选中它
   - 使用搜索框可以快速找到特定订单
   - 使用筛选下拉框可以按状态筛选订单

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
        
        # 搜索和筛选框
        search_frame = ttk.LabelFrame(main_frame, text="搜索和筛选", padding="10")
        search_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 关键词搜索
        ttk.Label(search_frame, text="关键词：").grid(row=0, column=0, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.grid(row=0, column=1, padx=5)
        ttk.Label(search_frame, text="(可搜索剧本名称)").grid(row=0, column=2, padx=5)
        
        # 状态筛选
        ttk.Label(search_frame, text="状态：").grid(row=0, column=3, padx=5)
        self.status_var = tk.StringVar(value="全部")
        status_combo = ttk.Combobox(
            search_frame,
            textvariable=self.status_var,
            values=["全部", "待支付", "已支付", "已完成", "已取消"],
            state="readonly",
            width=10
        )
        status_combo.grid(row=0, column=4, padx=5)
        
        # 搜索按钮
        ttk.Button(
            search_frame,
            text="搜索",
            command=self.search_orders,
            style="Action.TButton"
        ).grid(row=0, column=5, padx=5)
        
        # 订单列表
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.order_tree = ttk.Treeview(
            list_frame,
            columns=("script", "price", "status", "created_at"),
            show="headings",
            height=15
        )
        self.order_tree.heading("script", text="剧本")
        self.order_tree.heading("price", text="价格")
        self.order_tree.heading("status", text="状态")
        self.order_tree.heading("created_at", text="下单时间")
        
        # 设置列宽
        self.order_tree.column("script", width=300)
        self.order_tree.column("price", width=100)
        self.order_tree.column("status", width=100)
        self.order_tree.column("created_at", width=200)
        
        self.order_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.order_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.order_tree.configure(yscrollcommand=scrollbar.set)
        
        # 订单操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Button(
            button_frame,
            text="取消订单",
            command=self.cancel_order,
            style="Action.TButton"
        ).grid(row=0, column=0, padx=5)
        
        ttk.Button(
            button_frame,
            text="查看详情",
            command=self.view_order_details,
            style="Action.TButton"
        ).grid(row=0, column=1, padx=5)
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
    
    def load_orders(self):
        # 清空现有数据
        for item in self.order_tree.get_children():
            self.order_tree.delete(item)
        
        # 获取当前用户的订单
        orders = self.session.query(Order).filter_by(
            user_id=self.auth_manager.get_current_user().id
        ).order_by(Order.created_at.desc()).all()
        
        for order in orders:
            self.order_tree.insert(
                "",
                tk.END,
                values=(
                    order.script.title,
                    f"¥{order.price:.2f}",
                    order.status.value,
                    order.created_at.strftime("%Y-%m-%d %H:%M:%S")
                ),
                tags=(str(order.id),)
            )
    
    def search_orders(self):
        # 清空现有数据
        for item in self.order_tree.get_children():
            self.order_tree.delete(item)
        
        # 获取搜索条件
        keyword = self.search_var.get().strip()
        status = self.status_var.get()
        
        # 构建查询
        query = self.session.query(Order).filter_by(
            user_id=self.auth_manager.get_current_user().id
        )
        
        if keyword:
            query = query.join(Script).filter(Script.title.like(f"%{keyword}%"))
        
        if status != "全部":
            status_map = {
                "待支付": OrderStatus.pending,
                "已支付": OrderStatus.paid,
                "已完成": OrderStatus.completed,
                "已取消": OrderStatus.cancelled
            }
            query = query.filter(Order.status == status_map[status])
        
        # 执行查询
        orders = query.order_by(Order.created_at.desc()).all()
        
        for order in orders:
            self.order_tree.insert(
                "",
                tk.END,
                values=(
                    order.script.title,
                    f"¥{order.price:.2f}",
                    order.status.value,
                    order.created_at.strftime("%Y-%m-%d %H:%M:%S")
                ),
                tags=(str(order.id),)
            )
    
    def cancel_order(self):
        selected = self.order_tree.selection()
        if not selected:
            self.show_warning("警告", "请先选择要取消的订单")
            return
        
        order_id = int(self.order_tree.item(selected[0])["tags"][0])
        order = self.session.query(Order).get(order_id)
        
        if not order:
            self.show_error("错误", "订单不存在")
            return
        
        if order.status != OrderStatus.pending:
            self.show_warning("警告", "只能取消待支付的订单")
            return
        
        if self.show_confirmation(
            "确认取消",
            f"确定要取消订单吗？\n\n"
            f"剧本：{order.script.title}\n"
            f"价格：¥{order.price:.2f}\n"
            f"下单时间：{order.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        ):
            try:
                order.status = OrderStatus.cancelled
                self.session.commit()
                self.show_success("成功", "订单已取消")
                self.load_orders()
            except Exception as e:
                self.session.rollback()
                self.show_error(
                    "错误",
                    "取消订单失败",
                    str(e)
                )
    
    def view_order_details(self):
        selected = self.order_tree.selection()
        if not selected:
            self.show_warning("警告", "请先选择要查看的订单")
            return
        
        order_id = int(self.order_tree.item(selected[0])["tags"][0])
        order = self.session.query(Order).get(order_id)
        
        if not order:
            self.show_error("错误", "订单不存在")
            return
        
        details = f"""
订单详情：

剧本：{order.script.title}
价格：¥{order.price:.2f}
状态：{order.status.value}
下单时间：{order.created_at.strftime('%Y-%m-%d %H:%M:%S')}
支付时间：{order.paid_at.strftime('%Y-%m-%d %H:%M:%S') if order.paid_at else '未支付'}
完成时间：{order.completed_at.strftime('%Y-%m-%d %H:%M:%S') if order.completed_at else '未完成'}
取消时间：{order.cancelled_at.strftime('%Y-%m-%d %H:%M:%S') if order.cancelled_at else '未取消'}

商家信息：
名称：{order.script.merchant.username}
邮箱：{order.script.merchant.email}
"""
        self.show_success("订单详情", details) 