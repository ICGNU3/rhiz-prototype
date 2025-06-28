"""
Contact model for the Rhiz application
"""
from datetime import datetime
from backend.app.core.database import db
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

class Contact(db.Model):
    """Contact model for relationship management"""
    __tablename__ = 'contacts'
    
    # Primary fields
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    
    # Basic information
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Social profiles
    twitter = Column(String(100), nullable=True)
    linkedin = Column(String(200), nullable=True)
    handle = Column(String(50), nullable=True)
    
    # Professional information
    company = Column(String(100), nullable=True)
    title = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    
    # Relationship management
    relationship_type = Column(String(50), default='Contact')
    warmth_status = Column(Integer, default=1)
    warmth_label = Column(String(20), default='Cold')
    priority_level = Column(String(20), default='Medium')
    
    # Context and notes
    notes = Column(Text, nullable=True)
    narrative_thread = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)  # JSON string
    interests = Column(Text, nullable=True)
    introduced_by = Column(String(100), nullable=True)
    
    # Follow-up management
    follow_up_action = Column(String(200), nullable=True)
    follow_up_due_date = Column(DateTime, nullable=True)
    
    # Interaction tracking
    last_interaction_date = Column(DateTime, nullable=True)
    last_contact_method = Column(String(20), nullable=True)
    interaction_count = Column(Integer, default=0)
    
    # Source tracking for multi-source sync
    source = Column(String(20), default='manual')
    source_id = Column(String(100), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    
    # AI embeddings for matching
    embedding = Column(Text, nullable=True)  # JSON string
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="contacts")
    interactions = relationship("ContactInteraction", back_populates="contact", cascade="all, delete-orphan")
    ai_suggestions = relationship("AISuggestion", back_populates="contact", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Contact {self.name}>'
    
    @classmethod
    def create_contact(cls, user_id, name, **kwargs):
        """Create a new contact"""
        import uuid
        contact = cls(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=name,
            **kwargs
        )
        db.session.add(contact)
        db.session.commit()
        return contact
    
    @classmethod
    def get_by_user(cls, user_id, filters=None):
        """Get contacts for a user with optional filters"""
        query = cls.query.filter_by(user_id=user_id)
        
        if filters:
            if filters.get('warmth_status'):
                query = query.filter_by(warmth_status=filters['warmth_status'])
            if filters.get('relationship_type'):
                query = query.filter_by(relationship_type=filters['relationship_type'])
            if filters.get('source'):
                query = query.filter_by(source=filters['source'])
        
        return query.order_by(cls.updated_at.desc()).all()
    
    @classmethod
    def get_pipeline_view(cls, user_id):
        """Get contacts organized by warmth pipeline stages"""
        stages = ['Cold', 'Aware', 'Warm', 'Active', 'Contributor']
        pipeline = {}
        
        for stage in stages:
            contacts = cls.query.filter_by(
                user_id=user_id, 
                warmth_label=stage
            ).order_by(cls.updated_at.desc()).all()
            pipeline[stage] = [contact.to_dict() for contact in contacts]
        
        return pipeline
    
    @classmethod
    def get_follow_ups_due(cls, user_id, days_ahead=7):
        """Get contacts with follow-ups due"""
        from datetime import timedelta
        due_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        return cls.query.filter(
            cls.user_id == user_id,
            cls.follow_up_due_date.isnot(None),
            cls.follow_up_due_date <= due_date
        ).order_by(cls.follow_up_due_date).all()
    
    def update_interaction(self, method='Email'):
        """Update last interaction information"""
        self.last_interaction_date = datetime.utcnow()
        self.last_contact_method = method
        self.interaction_count += 1
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def update_warmth(self, status, label):
        """Update warmth status"""
        self.warmth_status = status
        self.warmth_label = label
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convert contact to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'twitter': self.twitter,
            'linkedin': self.linkedin,
            'handle': self.handle,
            'company': self.company,
            'title': self.title,
            'location': self.location,
            'relationship_type': self.relationship_type,
            'warmth_status': self.warmth_status,
            'warmth_label': self.warmth_label,
            'priority_level': self.priority_level,
            'notes': self.notes,
            'narrative_thread': self.narrative_thread,
            'tags': self.tags,
            'interests': self.interests,
            'introduced_by': self.introduced_by,
            'follow_up_action': self.follow_up_action,
            'follow_up_due_date': self.follow_up_due_date.isoformat() if self.follow_up_due_date else None,
            'last_interaction_date': self.last_interaction_date.isoformat() if self.last_interaction_date else None,
            'last_contact_method': self.last_contact_method,
            'interaction_count': self.interaction_count,
            'source': self.source,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def get_warmth_options():
        """Get available warmth status options"""
        return [
            (1, 'Cold'),
            (2, 'Aware'),
            (3, 'Warm'),
            (4, 'Active'),
            (5, 'Contributor')
        ]
    
    @staticmethod
    def get_relationship_types():
        """Get available relationship types"""
        return [
            'Colleague', 'Client', 'Advisor', 'Investor', 
            'Mentor', 'Friend', 'Acquaintance', 'Lead'
        ]