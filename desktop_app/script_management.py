import tkinter as tk
from tkinter import ttk, messagebox
from database import Script, init_db

class AddScriptDialog:
    def __init__(self, parent=None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("添加剧本")
        self.dialog.geometry("400x500")
        self.result = None
        self.init_ui()
        
        # 设置模态窗口
        self.dialog.transient(parent)
        self.dialog.grab_set()
    
    def init_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 剧本名称
        name_label = ttk.Label(main_frame, text="剧本名称:")
        name_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_input = ttk.Entry(main_frame, width=30)
        self.name_input.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # 难度
        difficulty_label = ttk.Label(main_frame, text="难度(1-5):")
        difficulty_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.difficulty_var = tk.StringVar(value="3.0")
        difficulty_spin = ttk.Spinbox(
            main_frame,
            from_=1.0,
            to=5.0,
            increment=0.5,
            textvariable=self.difficulty_var,
            width=5
        )
        difficulty_spin.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 时长
        duration_label = ttk.Label(main_frame, text="时长(分钟):")
        duration_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        self.duration_var = tk.StringVar(value="120")
        duration_spin = ttk.Spinbox(
            main_frame,
            from_=30,
            to=300,
            textvariable=self.duration_var,
            width=5
        )
        duration_spin.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # 描述
        desc_label = ttk.Label(main_frame, text="描述:")
        desc_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        self.desc_input = tk.Text(main_frame, height=10, width=30)
        self.desc_input.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
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
            "title": self.name_input.get(),
            "difficulty": float(self.difficulty_var.get()),
            "duration": int(self.duration_var.get()),
            "description": self.desc_input.get("1.0", tk.END).strip()
        }
        self.dialog.destroy()
    
    def on_cancel(self):
        self.dialog.destroy()

class ScriptManagementWindow:
    def __init__(self, auth_manager):
        self.root = tk.Toplevel()
        self.root.title("剧本管理")
        self.root.geometry("800x600")
        self.auth_manager = auth_manager
        self.session = init_db()
        self.init_ui()
    
    def init_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加剧本按钮
        add_button = ttk.Button(
            main_frame,
            text="添加剧本",
            command=self.add_script,
            style="Action.TButton"
        )
        add_button.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # 剧本列表
        self.script_tree = ttk.Treeview(
            main_frame,
            columns=("title", "difficulty", "duration", "description", "created_at"),
            show="headings"
        )
        self.script_tree.heading("title", text="剧本名称")
        self.script_tree.heading("difficulty", text="难度")
        self.script_tree.heading("duration", text="时长")
        self.script_tree.heading("description", text="描述")
        self.script_tree.heading("created_at", text="创建时间")
        self.script_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.script_tree.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.script_tree.configure(yscrollcommand=scrollbar.set)
        
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
        self.load_scripts()
    
    def load_scripts(self):
        # 清空现有数据
        for item in self.script_tree.get_children():
            self.script_tree.delete(item)
        
        scripts = self.session.query(Script).all()
        for script in scripts:
            item = self.script_tree.insert(
                "",
                tk.END,
                values=(
                    script.title,
                    str(script.difficulty),
                    f"{script.duration}分钟",
                    script.description,
                    str(script.created_at)
                ),
                tags=(str(script.id),)
            )
            
            # 添加编辑和删除按钮
            edit_button = ttk.Button(
                self.script_tree,
                text="编辑",
                command=lambda s=script: self.edit_script(s),
                style="Action.TButton"
            )
            delete_button = ttk.Button(
                self.script_tree,
                text="删除",
                command=lambda s=script: self.delete_script(s),
                style="Action.TButton"
            )
            
            self.script_tree.set(item, "edit_button", edit_button)
            self.script_tree.set(item, "delete_button", delete_button)
    
    def add_script(self):
        dialog = AddScriptDialog(self.root)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            script = Script(
                title=dialog.result["title"],
                difficulty=dialog.result["difficulty"],
                duration=dialog.result["duration"],
                description=dialog.result["description"]
            )
            self.session.add(script)
            self.session.commit()
            self.load_scripts()
    
    def edit_script(self, script):
        dialog = AddScriptDialog(self.root)
        dialog.name_input.insert(0, script.title)
        dialog.difficulty_var.set(str(script.difficulty))
        dialog.duration_var.set(str(script.duration))
        dialog.desc_input.insert("1.0", script.description)
        
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            script.title = dialog.result["title"]
            script.difficulty = dialog.result["difficulty"]
            script.duration = dialog.result["duration"]
            script.description = dialog.result["description"]
            self.session.commit()
            self.load_scripts()
    
    def delete_script(self, script):
        if messagebox.askyesno("确认删除", f'确定要删除剧本 "{script.title}" 吗？'):
            self.session.delete(script)
            self.session.commit()
            self.load_scripts() 