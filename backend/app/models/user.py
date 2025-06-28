"""
User model for the Rhiz application
"""
from datetime import datetime
from backend.app.core.database import db
from sqlalchemy import Column, String, DateTime, Text, Integer
from sqlalchemy.orm import relationship

class User(db.Model):
    """User model with authentication and subscription management"""
    __tablename__ = 'users'
    
    # Primary fields
    id = Column(String, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    
    # Profile information
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    profile_image_url = Column(String(255), nullable=True)
    
    # Authentication
    google_id = Column(String, nullable=True)
    subscription_tier = Column(String(20), default='explorer')
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    
    # Usage tracking
    goals_count = Column(Integer, default=0)
    contacts_count = Column(Integer, default=0)
    ai_suggestions_count = Column(Integer, default=0)
    
    # Gamification
    xp_points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    title = Column(String(50), default='Contact Seeker')
    badges = Column(Text, nullable=True)  # JSON string
    
    # Preferences
    motivation_style = Column(String(20), default='Motivated')
    email_notifications = Column(String(5), default='true')
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    contacts = relationship("Contact", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    @classmethod
    def create_user(cls, email, google_id=None, subscription_tier='explorer'):
        """Create a new user"""
        import uuid
        user = cls(
            id=str(uuid.uuid4()),
            email=email,
            google_id=google_id,
            subscription_tier=subscription_tier
        )
        db.session.add(user)
        db.session.commit()
        return user
    
    @classmethod
    def get_by_email(cls, email):
        """Get user by email"""
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_by_id(cls, user_id):
        """Get user by ID"""
        return cls.query.get(user_id)
    
    def update_usage_count(self, field, increment=1):
        """Update usage count for specific field"""
        current_value = getattr(self, f"{field}_count", 0)
        setattr(self, f"{field}_count", current_value + increment)
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def award_xp(self, points, action_description=""):
        """Award XP points to user"""
        self.xp_points += points
        
        # Level up logic
        new_level = min((self.xp_points // 100) + 1, 10)
        if new_level > self.level:
            self.level = new_level
            self._update_title()
        
        self.updated_at = datetime.utcnow()
        db.session.commit()
        
        return {
            'points_awarded': points,
            'total_points': self.xp_points,
            'level': self.level,
            'title': self.title
        }
    
    def _update_title(self):
        """Update user title based on level"""
        titles = {
            1: 'Contact Seeker',
            2: 'Network Builder',
            3: 'Connection Maker',
            4: 'Relationship Cultivator',
            5: 'Community Weaver',
            6: 'Network Architect',
            7: 'Connection Master',
            8: 'Relationship Strategist',
            9: 'Network Virtuoso',
            10: 'Connection Sage'
        }
        self.title = titles.get(self.level, 'Network Sage')
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'profile_image_url': self.profile_image_url,
            'subscription_tier': self.subscription_tier,
            'goals_count': self.goals_count,
            'contacts_count': self.contacts_count,
            'ai_suggestions_count': self.ai_suggestions_count,
            'xp_points': self.xp_points,
            'level': self.level,
            'title': self.title,
            'motivation_style': self.motivation_style,
            'email_notifications': self.email_notifications,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }