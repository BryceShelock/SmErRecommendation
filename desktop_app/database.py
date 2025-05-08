from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import enum
from datetime import datetime

Base = declarative_base()

class UserRole(enum.Enum):
    user = "user"
    merchant = "merchant"
    admin = "admin"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.user)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # 用户资料
    nickname = Column(String(50))
    phone = Column(String(20))
    avatar = Column(String(200))
    
    # 关系
    scripts = relationship("Script", back_populates="merchant")
    reviews = relationship("Review", back_populates="user")
    orders = relationship("Order", back_populates="user")

class Script(Base):
    __tablename__ = "scripts"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    difficulty = Column(Integer, nullable=False)  # 1-5
    duration = Column(Integer, nullable=False)  # 分钟
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # 商家信息
    merchant_id = Column(Integer, ForeignKey("users.id"))
    merchant = relationship("User", back_populates="scripts")
    
    # 剧本详情
    price = Column(Float, nullable=False, default=0.0)
    min_players = Column(Integer, nullable=False, default=4)
    max_players = Column(Integer, nullable=False, default=8)
    location = Column(String(200))
    status = Column(String(20), nullable=False, default="pending")  # pending, active, inactive, deleted
    
    # 关系
    reviews = relationship("Review", back_populates="script")
    orders = relationship("Order", back_populates="script")

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    script_id = Column(Integer, ForeignKey("scripts.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    content = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="reviews")
    script = relationship("Script", back_populates="reviews")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    script_id = Column(Integer, ForeignKey("scripts.id"), nullable=False)
    order_time = Column(DateTime, nullable=False)
    player_count = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String(20), nullable=False, default="pending")  # pending, confirmed, completed, cancelled
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="orders")
    script = relationship("Script", back_populates="orders")

def init_db():
    engine = create_engine("sqlite:///script_recommendation.db")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session() 