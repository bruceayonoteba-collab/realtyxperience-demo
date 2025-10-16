# database.py
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv('/Users/bruceayonotejr/Desktop/RX CODE/.env')

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine
engine = create_engine(DATABASE_URL)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# ==================== MODELS ====================

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    phone = Column(String)
    user_type = Column(String)
    test_group = Column(String)
    created_date = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Subscription fields
    subscription_tier = Column(String, default='free')
    subscription_status = Column(String, default='inactive')
    subscription_start_date = Column(DateTime)
    subscription_end_date = Column(DateTime)
    payment_reference = Column(String)
    
    # Relationships
    properties = relationship("Property", back_populates="owner")
    lands = relationship("Land", back_populates="owner")
    messages = relationship("Message", back_populates="user")
    inquiries_sent = relationship("Inquiry", foreign_keys="Inquiry.sender_id", back_populates="sender")
    inquiries_received = relationship("Inquiry", foreign_keys="Inquiry.receiver_id", back_populates="receiver")


class Property(Base):
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic Info
    title = Column(String, nullable=False)
    description = Column(Text)
    property_type = Column(String)
    listing_type = Column(String)
    
    # Location
    address = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String, default='Nigeria')
    
    # Details
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    square_feet = Column(Float)
    
    # Pricing
    price = Column(Float)
    currency = Column(String, default='NGN')
    
    # Status
    status = Column(String, default='available')
    is_published = Column(Boolean, default=True)
    
    # Metadata
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, onupdate=datetime.utcnow)
    views_count = Column(Integer, default=0)
    
    # Relationships
    owner = relationship("User", back_populates="properties")
    inquiries = relationship("Inquiry", back_populates="property")


class Land(Base):
    __tablename__ = "lands"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic Info
    title = Column(String, nullable=False)
    description = Column(Text)
    land_type = Column(String)
    
    # Location
    address = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String, default='Nigeria')
    
    # Details
    size_sqm = Column(Float)
    
    # Pricing
    price = Column(Float)
    currency = Column(String, default='NGN')
    
    # Status
    status = Column(String, default='available')
    is_published = Column(Boolean, default=True)
    
    # Metadata
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, onupdate=datetime.utcnow)
    views_count = Column(Integer, default=0)
    
    # Relationships
    owner = relationship("User", back_populates="lands")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Message details
    assistant_type = Column(String)
    role = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="messages")


class Inquiry(Base):
    __tablename__ = "inquiries"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id"))
    
    # Inquiry details
    message = Column(Text)
    sender_name = Column(String)
    sender_phone = Column(String)
    sender_email = Column(String)
    
    # Status
    status = Column(String, default='new')
    
    # Metadata
    created_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], back_populates="inquiries_sent")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="inquiries_received")
    property = relationship("Property", back_populates="inquiries")


# ==================== DATABASE FUNCTIONS ====================

def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully!")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_user(db, username, email, password, phone=None, user_type=None, test_group=None):
    """Create a new user"""
    user = User(
        username=username,
        email=email,
        password=password,
        phone=phone,
        user_type=user_type,
        test_group=test_group
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_username(db, username):
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db, email):
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def create_property(db, owner_id, **property_data):
    """Create a new property"""
    property = Property(owner_id=owner_id, **property_data)
    db.add(property)
    db.commit()
    db.refresh(property)
    return property


def get_user_properties(db, user_id):
    """Get all properties for a user"""
    return db.query(Property).filter(Property.owner_id == user_id).all()


def get_all_properties(db, limit=100):
    """Get all published properties"""
    return db.query(Property).filter(Property.is_published == True).limit(limit).all()


def update_property(db, property_id, **updates):
    """Update a property"""
    property = db.query(Property).filter(Property.id == property_id).first()
    if property:
        for key, value in updates.items():
            setattr(property, key, value)
        db.commit()
        db.refresh(property)
    return property


def delete_property(db, property_id):
    """Delete a property"""
    property = db.query(Property).filter(Property.id == property_id).first()
    if property:
        db.delete(property)
        db.commit()
        return True
    return False


if __name__ == "__main__":
    print("Testing database connection...")
    init_db()
    print("Database setup complete!")
