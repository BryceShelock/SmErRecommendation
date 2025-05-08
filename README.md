# Script Murder Mystery Room Booking and Recommendation System

一个基于 Django 的剧本杀房间预订和智能推荐系统，提供房间预订、用户评价和个性化推荐功能。

## 主要功能

- 房间预订管理
- 智能推荐系统（基于内容和协同过滤）
- 用户评价和情感分析
- 用户成就和积分系统
- 商家管理后台

## 技术栈

- Django 5.2
- Django REST Framework
- SQLite (开发) / PostgreSQL (生产)
- TextBlob (情感分析)
- Surprise (协同过滤)
- Pandas (数据处理)

## 快速开始

1. 克隆项目
```bash
git clone [项目地址]
cd SmErRecommendation
```

2. 创建并激活虚拟环境
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 初始化数据库
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

5. 运行开发服务器
```bash
python manage.py runserver
```

## API 文档

详细的 API 文档请参考 [API.md](API.md)

## 开发指南

- 代码风格遵循 PEP 8
- 使用 black 进行代码格式化
- 提交前请运行测试：`python manage.py test`

## 贡献指南

1. Fork 本仓库
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件 