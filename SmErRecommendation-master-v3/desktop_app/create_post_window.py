import tkinter as tk
from tkinter import ttk, messagebox
from database import Post, PostCategory, init_db

class CreatePostWindow:
    def __init__(self, parent, auth_manager):
        self.root = tk.Toplevel(parent)
        self.root.title("发布帖子")
        self.root.geometry("800x600")
        self.auth_manager = auth_manager
        self.session = init_db()
        self.init_styles()
        self.init_ui()
    
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
            text="发布帖子",
            style='Title.TLabel'
        ).pack(anchor='w', pady=(0, 20))
        
        # 创建表单
        form_frame = ttk.Frame(main_frame, style='Card.TFrame')
        form_frame.pack(fill='both', expand=True)
        
        # 标题输入
        ttk.Label(
            form_frame,
            text="标题",
            style='CardTitle.TLabel'
        ).pack(anchor='w', pady=(0, 5))
        
        self.title_entry = ttk.Entry(form_frame, font=('Arial', 12))
        self.title_entry.pack(fill='x', pady=(0, 20))
        
        # 分类选择
        ttk.Label(
            form_frame,
            text="分类",
            style='CardTitle.TLabel'
        ).pack(anchor='w', pady=(0, 5))
        
        self.category_var = tk.StringVar(value=PostCategory.all.value)
        category_frame = ttk.Frame(form_frame, style='Card.TFrame')
        category_frame.pack(fill='x', pady=(0, 20))
        
        categories = [
            ("全部", PostCategory.all),
            ("经验分享", PostCategory.experience),
            ("求助问答", PostCategory.question),
            ("剧本推荐", PostCategory.recommendation),
            ("店铺点评", PostCategory.review),
            ("组队交友", PostCategory.team)
        ]
        
        for text, category in categories:
            ttk.Radiobutton(
                category_frame,
                text=text,
                value=category.value,
                variable=self.category_var,
                style='Info.TLabel'
            ).pack(side='left', padx=10)
        
        # 内容输入
        ttk.Label(
            form_frame,
            text="内容",
            style='CardTitle.TLabel'
        ).pack(anchor='w', pady=(0, 5))
        
        self.content_text = tk.Text(form_frame, font=('Arial', 12), height=10)
        self.content_text.pack(fill='both', expand=True, pady=(0, 20))
        
        # 按钮区域
        button_frame = ttk.Frame(form_frame, style='Card.TFrame')
        button_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Button(
            button_frame,
            text="取消",
            style='Outline.TButton',
            command=self.root.destroy
        ).pack(side='right', padx=5)
        
        ttk.Button(
            button_frame,
            text="发布",
            style='Primary.TButton',
            command=self.create_post
        ).pack(side='right', padx=5)
    
    def create_post(self):
        title = self.title_entry.get().strip()
        content = self.content_text.get("1.0", "end-1c").strip()
        category = PostCategory(self.category_var.get())
        
        if not title:
            messagebox.showwarning("警告", "请输入标题")
            return
        
        if not content:
            messagebox.showwarning("警告", "请输入内容")
            return
        
        user = self.auth_manager.get_current_user()
        post = Post(
            title=title,
            content=content,
            category=category,
            author_id=user.id
        )
        
        self.session.add(post)
        self.session.commit()
        
        messagebox.showinfo("成功", "发布成功")
        self.root.destroy()
    
    def run(self):
        self.root.mainloop() 