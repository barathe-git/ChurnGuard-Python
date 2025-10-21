"""
Database CRUD operations module
Centralized CRUD operations for all database entities
"""
from .user_crud import UserCRUD
from .analytics_crud import AnalyticsCRUD
from .csv_crud import CSVRUD
from .chat_crud import ChatCRUD
from .campaign_crud import CampaignCRUD

__all__ = [
    'UserCRUD',
    'AnalyticsCRUD',
    'CSVRUD',
    'ChatCRUD',
    'CampaignCRUD'
]

