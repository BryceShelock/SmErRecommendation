import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from database import Post, PostCategory, Comment, Like, init_db
import os
from datetime import datetime
from create_post_window import CreatePostWindow
from comments_window import CommentsWindow

class CommunityWindow:
    def __init__(self, parent, auth_manager):
        self.root = tk.Toplevel(parent)
        self.root.title("剧本杀社区")
        self.root.geometry("1200x800")
        self.auth_manager = auth_manager
        self.session = init_db()
        self.init_styles()
        self.init_ui()
        self.load_posts()
    
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
        
        # 副标题样式
        style.configure('Subtitle.TLabel',
                       font=('Arial', 12),
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
        
        # 分类项样式
        style.configure('Category.TButton',
                       background='white',
                       font=('Arial', 10),
                       padding=10)
        
        style.map('Category.TButton',
                 background=[('active', self.colors['light'])],
                 foreground=[('active', self.colors['primary'])])
    
    def init_ui(self):
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, style='TFrame')
        self.main_frame.pack(fill='both', expand=True)
        
        # 创建画布和滚动条
        canvas = tk.Canvas(self.main_frame, background=self.colors['light'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=canvas.yview)
        
        # 创建可滚动的框架
        self.scrollable_frame = ttk.Frame(canvas, style='TFrame')
        
        # 配置画布
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # 创建窗口
        canvas_frame = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=canvas.winfo_reqwidth())
        
        # 配置画布和滚动条
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 创建头部区域
        self.create_header()
        
        # 创建主要内容区域
        content_frame = ttk.Frame(self.scrollable_frame, style='TFrame')
        content_frame.pack(fill='both', expand=True)
        
        # 创建左侧边栏和右侧内容的容器
        nav_content_frame = ttk.Frame(content_frame, style='TFrame')
        nav_content_frame.pack(fill='both', expand=True)
        
        # 创建左侧边栏
        self.create_sidebar(nav_content_frame)
        
        # 创建右侧内容
        self.create_main_content(nav_content_frame)
        
        # 创建发帖按钮
        self.create_post_button()
        
        # 配置画布和滚动条
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 绑定窗口大小改变事件
        def _on_configure(event):
            canvas.itemconfig(canvas_frame, width=event.width)
        
        self.root.bind('<Configure>', _on_configure)
    
    def create_header(self):
        # 创建头部区域
        header_frame = ttk.Frame(self.scrollable_frame, style='Card.TFrame')
        header_frame.pack(fill='x', padx=30, pady=20)
        
        ttk.Label(
            header_frame,
            text="剧本杀社区",
            style='Title.TLabel'
        ).pack(anchor='w', padx=20, pady=10)
        
        ttk.Label(
            header_frame,
            text="分享你的剧本杀体验，结识志同道合的朋友",
            style='Subtitle.TLabel'
        ).pack(anchor='w', padx=20, pady=(0, 10))
    
    def create_sidebar(self, parent):
        # 创建左侧边栏
        sidebar_frame = ttk.Frame(parent, style='Card.TFrame')
        sidebar_frame.pack(side='left', fill='y', padx=(0, 20))
        
        # 搜索框
        search_frame = ttk.Frame(sidebar_frame, style='Card.TFrame')
        search_frame.pack(fill='x', pady=(0, 20))
        
        search_entry = ttk.Entry(search_frame, font=('Arial', 12))
        search_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        ttk.Button(
            search_frame,
            text="搜索",
            style='Primary.TButton',
            command=lambda: self.search_posts(search_entry.get())
        ).pack(side='right')
        
        # 分类导航
        category_frame = ttk.Frame(sidebar_frame, style='Card.TFrame')
        category_frame.pack(fill='x')
        
        ttk.Label(
            category_frame,
            text="分类",
            style='CardTitle.TLabel'
        ).pack(anchor='w', pady=(0, 10))
        
        categories = [
            ("全部", PostCategory.all),
            ("经验分享", PostCategory.experience),
            ("求助问答", PostCategory.question),
            ("剧本推荐", PostCategory.recommendation),
            ("店铺点评", PostCategory.review),
            ("组队交友", PostCategory.team)
        ]
        
        for text, category in categories:
            ttk.Button(
                category_frame,
                text=text,
                style='Category.TButton',
                command=lambda c=category: self.filter_posts(c)
            ).pack(fill='x', pady=2)
    
    def create_main_content(self, parent):
        # 创建右侧内容区域
        content_frame = ttk.Frame(parent, style='TFrame')
        content_frame.pack(side='left', fill='both', expand=True)
        
        # 帖子列表容器
        self.posts_frame = ttk.Frame(content_frame, style='TFrame')
        self.posts_frame.pack(fill='both', expand=True)
        
        # 分页控件
        pagination_frame = ttk.Frame(content_frame, style='TFrame')
        pagination_frame.pack(fill='x', pady=20)
        
        ttk.Button(
            pagination_frame,
            text="上一页",
            style='Outline.TButton',
            command=self.previous_page
        ).pack(side='left', padx=5)
        
        self.page_label = ttk.Label(
            pagination_frame,
            text="1",
            style='Info.TLabel'
        )
        self.page_label.pack(side='left', padx=10)
        
        ttk.Button(
            pagination_frame,
            text="下一页",
            style='Outline.TButton',
            command=self.next_page
        ).pack(side='left', padx=5)
    
    def create_post_button(self):
        # 创建发帖按钮
        post_button = ttk.Button(
            self.root,
            text="+",
            style='Primary.TButton',
            command=self.create_post
        )
        post_button.place(relx=0.95, rely=0.9, anchor='se')
    
    def create_post_card(self, post):
        # 创建帖子卡片
        card = ttk.Frame(self.posts_frame, style='Card.TFrame')
        card.pack(fill='x', pady=10)
        
        # 帖子头部
        header_frame = ttk.Frame(card, style='Card.TFrame')
        header_frame.pack(fill='x', pady=10)
        
        # 作者头像
        avatar_label = ttk.Label(header_frame, style='Card.TFrame')
        avatar_label.pack(side='left', padx=10)
        
        if post.author.avatar and os.path.exists(post.author.avatar):
            image = Image.open(post.author.avatar)
            image = image.resize((40, 40), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            avatar_label.configure(image=photo)
            avatar_label.image = photo
        else:
            avatar_label.configure(text="无头像")
        
        # 作者信息
        info_frame = ttk.Frame(header_frame, style='Card.TFrame')
        info_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(
            info_frame,
            text=post.author.username,
            style='CardTitle.TLabel'
        ).pack(anchor='w')
        
        ttk.Label(
            info_frame,
            text=f"{self.get_time_ago(post.created_at)} · {post.category.value}",
            style='Info.TLabel'
        ).pack(anchor='w')
        
        # 帖子内容
        content_frame = ttk.Frame(card, style='Card.TFrame')
        content_frame.pack(fill='x', pady=10)
        
        ttk.Label(
            content_frame,
            text=post.title,
            style='CardTitle.TLabel'
        ).pack(anchor='w')
        
        ttk.Label(
            content_frame,
            text=post.content,
            style='Info.TLabel',
            wraplength=600
        ).pack(anchor='w', pady=5)
        
        # 帖子操作
        actions_frame = ttk.Frame(card, style='Card.TFrame')
        actions_frame.pack(fill='x', pady=10)
        
        # 点赞
        likes_count = len(post.likes)
        ttk.Button(
            actions_frame,
            text=f"❤ {likes_count}",
            style='Outline.TButton',
            command=lambda: self.like_post(post)
        ).pack(side='left', padx=10)
        
        # 评论
        comments_count = len(post.comments)
        ttk.Button(
            actions_frame,
            text=f"💬 {comments_count}",
            style='Outline.TButton',
            command=lambda: self.show_comments(post)
        ).pack(side='left', padx=10)
        
        # 分享
        ttk.Button(
            actions_frame,
            text="分享",
            style='Outline.TButton',
            command=lambda: self.share_post(post)
        ).pack(side='left', padx=10)
    
    def load_posts(self, category=None, page=1):
        # 清空现有帖子
        for widget in self.posts_frame.winfo_children():
            widget.destroy()
        
        # 查询帖子
        query = self.session.query(Post)
        if category and category != PostCategory.all:
            query = query.filter_by(category=category)
        
        # 分页
        posts = query.order_by(Post.created_at.desc()).offset((page-1)*10).limit(10).all()
        
        # 显示帖子
        for post in posts:
            self.create_post_card(post)
        
        # 更新页码
        self.current_page = page
        self.page_label.configure(text=str(page))
    
    def search_posts(self, keyword):
        if not keyword:
            self.load_posts()
            return
        
        # 清空现有帖子
        for widget in self.posts_frame.winfo_children():
            widget.destroy()
        
        # 搜索帖子
        posts = self.session.query(Post).filter(
            (Post.title.like(f'%{keyword}%')) |
            (Post.content.like(f'%{keyword}%'))
        ).order_by(Post.created_at.desc()).all()
        
        # 显示帖子
        for post in posts:
            self.create_post_card(post)
    
    def filter_posts(self, category):
        self.load_posts(category)
    
    def previous_page(self):
        if self.current_page > 1:
            self.load_posts(page=self.current_page-1)
    
    def next_page(self):
        self.load_posts(page=self.current_page+1)
    
    def create_post(self):
        if not self.auth_manager.is_authenticated():
            messagebox.showwarning("警告", "请先登录")
            return
        
        create_post_window = CreatePostWindow(self.root, self.auth_manager)
        create_post_window.run()
        self.load_posts()
    
    def like_post(self, post):
        if not self.auth_manager.is_authenticated():
            messagebox.showwarning("警告", "请先登录")
            return
        
        user = self.auth_manager.get_current_user()
        existing_like = self.session.query(Like).filter_by(
            user_id=user.id,
            post_id=post.id
        ).first()
        
        if existing_like:
            self.session.delete(existing_like)
            messagebox.showinfo("成功", "取消点赞成功")
        else:
            like = Like(user_id=user.id, post_id=post.id)
            self.session.add(like)
            messagebox.showinfo("成功", "点赞成功")
        
        self.session.commit()
        self.load_posts()
    
    def show_comments(self, post):
        comments_window = CommentsWindow(self.root, self.auth_manager, post)
        comments_window.run()
        self.load_posts()
    
    def share_post(self, post):
        # TODO: 实现分享功能
        pass
    
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