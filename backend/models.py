# models.py - FIXED VERSION

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
from discount_decorators import DiscountFactory, BasePriceCalculator
from werkzeug.security import generate_password_hash, check_password_hash
import json

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(200), nullable=False)
    role = Column(String(20), default='user')  # 'user' or 'admin'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships - Use simple backref for now
    orders = relationship('Order', backref='customer', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    price = Column(Float, nullable=False)
    rating = Column(Float, default=0.0)
    reviews = Column(Integer, default=0)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    image = Column(String(500), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'price': self.price,
            'rating': self.rating,
            'reviews': self.reviews,
            'description': self.description,
            'image': self.image,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CartItem(Base):
    __tablename__ = 'cart_items'
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    session_id = Column(String(100), nullable=False, index=True)
    quantity = Column(Integer, default=1)
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Use simple relationship
    product = relationship('Product')
    
    def to_dict(self):
        """Convert cart item to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'added_at': self.added_at.isoformat() if self.added_at else None,
            'product': self.product.to_dict() if self.product else None
        }

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    session_id = Column(String(100), nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String(50), default='pending')
    shipping_info = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Simple relationship without back_populates
    items = relationship('OrderItem', backref='order_rel', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'total_amount': self.total_amount,
            'status': self.status,
            'shipping_info': json.loads(self.shipping_info) if self.shipping_info else {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'item_count': self.items.count() if hasattr(self, 'items') else 0
        }

class OrderItem(Base):
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, default=1)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Simple relationships
    product = relationship('Product')
    # order_rel is created by backref in Order model
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product': self.product.to_dict() if self.product else None,
            'quantity': self.quantity,
            'price': self.price,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }