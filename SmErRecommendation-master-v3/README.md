# 剧本杀推荐系统

一个基于PyQt6的桌面应用程序，用于推荐和管理剧本杀游戏。

## 功能特点

- 用户注册和登录
- 剧本列表浏览和搜索
- 店铺信息查看
- 收藏喜欢的剧本
- 在线预约剧本
- 评价和评分系统

## 安装要求

- Python 3.8+
- PyQt6
- SQLAlchemy
- Werkzeug

## 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/script-killing-recommendation.git
cd script-killing-recommendation
```

2. 创建虚拟环境（可选但推荐）：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

# run django server
```
python manage.py runserver 8001
```

## 运行应用

```bash
python desktop_app/main.py
```

## 使用说明

1. 首次使用需要注册账号
2. 登录后可以浏览剧本和店铺信息
3. 可以收藏喜欢的剧本
4. 选择剧本和店铺进行预约
5. 可以评价已完成的剧本

## 项目结构

```
desktop_app/
├── main.py              # 主程序入口
├── login_window.py      # 登录窗口
├── main_window.py       # 主窗口
├── auth_manager.py      # 认证管理
└── database.py          # 数据库模型
```

## 贡献

欢迎提交问题和功能请求！

## 许可证

MIT License 