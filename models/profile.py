"""
Profile model for user profile information.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app import db


class Profile(db.Model):
    """User profile model"""
    __tablename__ = 'profiles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    full_name = Column(String(100), nullable=False)
    mobile_number = Column(String(20))
    profile_picture = Column(String(255), default='default.png')
    bio = Column(Text)
    date_of_birth = Column(Date)
    address = Column(Text)
    city = Column(String(50))
    country = Column(String(50))
    timezone = Column(String(50), default='UTC')
    preferred_currency = Column(String(10), default='USD')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship('User', back_populates='profile')
    
    def __init__(self, user_id, full_name, **kwargs):
        """
        Initialize a new profile.
        
        Args:
            user_id: ID of the user
            full_name: User's full name
        """
        self.user_id = user_id
        self.full_name = full_name
        super().__init__(**kwargs)
    
    def get_age(self):
        """
        Calculate the user's age.
        
        Returns:
            int: Age in years or None if date of birth is not set
        """
        if not self.date_of_birth:
            return None
        
        today = datetime.now().date()
        age = today.year - self.date_of_birth.year
        
        # Adjust age if birthday hasn't occurred yet this year
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            age -= 1
        
        return age
    
    def to_dict(self):
        """
        Convert profile object to dictionary.
        
        Returns:
            dict: Profile data
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'mobile_number': self.mobile_number,
            'profile_picture': self.profile_picture,
            'bio': self.bio,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'age': self.get_age(),
            'address': self.address,
            'city': self.city,
            'country': self.country,
            'timezone': self.timezone,
            'preferred_currency': self.preferred_currency,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Profile {self.full_name}>'