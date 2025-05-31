import tkinter as tk
from tkinter import ttk, messagebox
from database import Post, Comment, init_db
from datetime import datetime

class CommentsWindow:
    def __init__(self, parent, auth_manager, post):
        self.root = tk.Toplevel(parent)
        self.root.title("评论")
        self.root.geometry("800x600")
        self.auth_manager = auth_manager
        self.post = post
        self.session = init_db()
        self.init_styles()
        self.init_ui()
        self.load_comments()
    
    def init_styles(self):
        style = ttk.Style()
        
        # 定义颜色变量
        self.colors = {
            'primary': '#6c5ce7',
            'secondary': '#a29bfe',
            'dark': '#2d3436',
            'light': '#f5f6fa',
            'accent': '#fd79a8'
        }
        
        # 配置基本样式
        style.configure('TFrame', background=self.colors['light'])
        style.configure('TLabel', background=self.colors['light'])
        style.configure('TButton', padding=10)
        
        # 标题样式
        style.configure('Title.TLabel',
                       font=('Arial', 24, 'bold'),
                       foreground=self.colors['dark'])
        
        # 卡片样式
        style.configure('Card.TFrame',
                       background='white',
                       relief='flat',
                       borderwidth=0)
        
        # 按钮样式
        style.configure('Primary.TButton',
                       background=self.colors['primary'],
                       foreground='white',
                       font=('Arial', 10, 'bold'),
                       padding=10)
        
        style.configure('Outline.TButton',
                       background='white',
                       foreground=self.colors['primary'],
                       font=('Arial', 10, 'bold'),
                       padding=10)
        
        # 标签样式
        style.configure('Info.TLabel',
                       font=('Arial', 12),
                       background='white')
        
        # 卡片标题样式
        style.configure('CardTitle.TLabel',
                       font=('Arial', 16, 'bold'),
                       background='white')
    
    def init_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, style='TFrame')
        main_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # 创建标题
        ttk.Label(
            main_frame,
            text="评论",
            style='Title.TLabel'
        ).pack(anchor='w', pady=(0, 20))
        
        # 创建帖子内容
        post_frame = ttk.Frame(main_frame, style='Card.TFrame')
        post_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(
            post_frame,
            text=self.post.title,
            style='CardTitle.TLabel'
        ).pack(anchor='w')
        
        ttk.Label(
            post_frame,
            text=self.post.content,
            style='Info.TLabel',
            wraplength=700
        ).pack(anchor='w', pady=5)
        
        # 创建评论列表
        self.comments_frame = ttk.Frame(main_frame, style='TFrame')
        self.comments_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # 创建评论输入框
        input_frame = ttk.Frame(main_frame, style='Card.TFrame')
        input_frame.pack(fill='x')
        
        self.comment_text = tk.Text(input_frame, font=('Arial', 12), height=3)
        self.comment_text.pack(fill='x', pady=(0, 10))
        
        ttk.Button(
            input_frame,
            text="发表评论",
            style='Primary.TButton',
            command=self.create_comment
        ).pack(anchor='e')
    
    def create_comment_card(self, comment):
        # 创建评论卡片
        card = ttk.Frame(self.comments_frame, style='Card.TFrame')
        card.pack(fill='x', pady=10)
        
        # 评论头部
        header_frame = ttk.Frame(card, style='Card.TFrame')
        header_frame.pack(fill='x', pady=5)
        
        ttk.Label(
            header_frame,
            text=comment.author.username,
            style='CardTitle.TLabel'
        ).pack(side='left')
        
        ttk.Label(
            header_frame,
            text=self.get_time_ago(comment.created_at),
            style='Info.TLabel'
        ).pack(side='right')
        
        # 评论内容
        ttk.Label(
            card,
            text=comment.content,
            style='Info.TLabel',
            wraplength=700
        ).pack(anchor='w', pady=5)
    
    def load_comments(self):
        # 清空现有评论
        for widget in self.comments_frame.winfo_children():
            widget.destroy()
        
        # 加载评论
        comments = self.session.query(Comment).filter_by(post_id=self.post.id).order_by(Comment.created_at.desc()).all()
        
        for comment in comments:
            self.create_comment_card(comment)
    
    def create_comment(self):
        if not self.auth_manager.is_authenticated():
            messagebox.showwarning("警告", "请先登录")
            return
        
        content = self.comment_text.get("1.0", "end-1c").strip()
        
        if not content:
            messagebox.showwarning("警告", "请输入评论内容")
            return
        
        user = self.auth_manager.get_current_user()
        comment = Comment(
            content=content,
            author_id=user.id,
            post_id=self.post.id
        )
        
        self.session.add(comment)
        self.session.commit()
        
        self.comment_text.delete("1.0", "end")
        self.load_comments()
    
    def get_time_ago(self, dt):
        now = datetime.now()
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days}天前"
        elif diff.seconds >= 3600:
            return f"{diff.seconds // 3600}小时前"
        elif diff.seconds >= 60:
            return f"{diff.seconds // 60}分钟前"
        else:
            return "刚刚"
    
    def run(self):
        self.root.mainloop() 