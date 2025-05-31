from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum

# 创建数据库引擎
engine = create_engine('sqlite:///script_killing.db')
Base = declarative_base()

# 用户角色枚举
class UserRole(enum.Enum):
    user = "user"
    merchant = "merchant"
    admin = "admin"

# 预约状态枚举
class BookingStatus(enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"

# 用户模型
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    password = Column(String(200), nullable=False)
    gender = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    reviews = relationship("Review", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")
    bookings = relationship("Booking", back_populates="user")

# 剧本模型
class Script(Base):
    __tablename__ = 'scripts'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)  # 推理、恐怖、情感、欢乐等
    difficulty = Column(String(20), nullable=False)  # 简单、中等、困难
    price = Column(Float, nullable=False)
    rating = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    reviews = relationship("Review", back_populates="script")
    favorites = relationship("Favorite", back_populates="script")
    bookings = relationship("Booking", back_populates="script")

# 店铺模型
class Store(Base):
    __tablename__ = 'stores'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    address = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=False)
    rating = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    bookings = relationship("Booking", back_populates="store")

# 评价模型
class Review(Base):
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    script_id = Column(Integer, ForeignKey('scripts.id'), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5星
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    user = relationship("User", back_populates="reviews")
    script = relationship("Script", back_populates="reviews")

# 收藏模型
class Favorite(Base):
    __tablename__ = 'favorites'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    script_id = Column(Integer, ForeignKey('scripts.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    user = relationship("User", back_populates="favorites")
    script = relationship("Script", back_populates="favorites")

# 预约模型
class Booking(Base):
    __tablename__ = 'bookings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    script_id = Column(Integer, ForeignKey('scripts.id'), nullable=False)
    store_id = Column(Integer, ForeignKey('stores.id'), nullable=False)
    booking_time = Column(DateTime, nullable=False)
    players = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String(20), nullable=False)  # 待确认、已确认、已完成、已取消
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    user = relationship("User", back_populates="bookings")
    script = relationship("Script", back_populates="bookings")
    store = relationship("Store", back_populates="bookings")

# 创建所有表
def init_db():
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()

# 创建会话
Session = sessionmaker(bind=engine) 