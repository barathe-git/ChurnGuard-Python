"""
MongoDB Document Models for ChurnGuard
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId
from pydantic import BaseModel, Field
from enum import Enum

class AccountStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    CHURNED = "churned"

class TransactionType(str, Enum):
    PURCHASE = "purchase"
    REFUND = "refund"
    SUBSCRIPTION = "subscription"
    CANCELLATION = "cancellation"

class TransactionStatus(str, Enum):
    COMPLETED = "completed"
    PENDING = "pending"
    FAILED = "failed"
    CANCELLED = "cancelled"

class SentimentLabel(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class CampaignType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    CALL = "call"
    PUSH = "push"

class CampaignStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class EventType(str, Enum):
    SENT = "sent"
    OPENED = "opened"
    CLICKED = "clicked"
    CONVERTED = "converted"
    BOUNCED = "bounced"
    UNSUBSCRIBED = "unsubscribed"

class Organization(BaseModel):
    """Organization document model"""
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    name: str = Field(..., max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Customer(BaseModel):
    """Customer document model"""
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    org_id: ObjectId = Field(...)
    customer_external_id: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    signup_date: Optional[datetime] = None
    last_activity_date: Optional[datetime] = None
    account_status: AccountStatus = Field(default=AccountStatus.ACTIVE)
    lifetime_value: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Transaction(BaseModel):
    """Transaction document model"""
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    customer_id: ObjectId = Field(...)
    transaction_date: datetime = Field(...)
    amount: float = Field(...)
    transaction_type: Optional[TransactionType] = None
    product_category: Optional[str] = Field(None, max_length=100)
    status: TransactionStatus = Field(default=TransactionStatus.COMPLETED)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Feedback(BaseModel):
    """Customer feedback document model"""
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    customer_id: ObjectId = Field(...)
    feedback_text: Optional[str] = None
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[SentimentLabel] = None
    feedback_date: datetime = Field(default_factory=datetime.utcnow)
    source: Optional[str] = Field(None, max_length=50)  # email, survey, chat, etc.
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ChurnScore(BaseModel):
    """Churn prediction scores document model"""
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    customer_id: ObjectId = Field(...)
    churn_probability: float = Field(...)
    risk_level: RiskLevel = Field(...)
    prediction_date: datetime = Field(default_factory=datetime.utcnow)
    features_used: Optional[Dict[str, Any]] = None
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Campaign(BaseModel):
    """Engagement campaign document model"""
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    org_id: ObjectId = Field(...)
    name: str = Field(..., max_length=255)
    campaign_type: Optional[CampaignType] = None
    status: CampaignStatus = Field(default=CampaignStatus.DRAFT)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    scheduled_date: Optional[datetime] = None
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class CampaignEvent(BaseModel):
    """Campaign execution events document model"""
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    campaign_id: ObjectId = Field(...)
    customer_id: ObjectId = Field(...)
    event_type: EventType = Field(...)
    event_date: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
