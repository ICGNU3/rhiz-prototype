"""
Interaction models for the Rhiz application
Includes ContactInteraction and AISuggestion models
"""
from datetime import datetime
from backend.app.core.database import db
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Float, Integer
from sqlalchemy.orm import relationship

class ContactInteraction(db.Model):
    """Model for tracking interactions with contacts"""
    __tablename__ = 'contact_interactions'
    
    # Primary fields
    id = Column(String, primary_key=True)
    contact_id = Column(String, ForeignKey('contacts.id'), nullable=False)
    
    # Interaction details
    interaction_type = Column(String(50), nullable=False)  # email, call, meeting, social, etc.
    direction = Column(String(20), nullable=False)  # inbound, outbound
    subject = Column(String(200), nullable=True)
    content = Column(Text, nullable=True)
    outcome = Column(String(100), nullable=True)
    
    # Context
    location = Column(String(100), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # Follow-up
    follow_up_required = Column(String(5), default='false')
    follow_up_notes = Column(Text, nullable=True)
    
    # Timestamps
    interaction_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    contact = relationship("Contact", back_populates="interactions")
    
    def __repr__(self):
        return f'<ContactInteraction {self.interaction_type} with {self.contact_id}>'
    
    @classmethod
    def create_interaction(cls, contact_id, interaction_type, direction, **kwargs):
        """Create a new contact interaction"""
        import uuid
        interaction = cls(
            id=str(uuid.uuid4()),
            contact_id=contact_id,
            interaction_type=interaction_type,
            direction=direction,
            **kwargs
        )
        db.session.add(interaction)
        db.session.commit()
        return interaction
    
    @classmethod
    def get_by_contact_id(cls, contact_id, limit=50):
        """Get interactions for a specific contact"""
        return cls.query.filter_by(contact_id=contact_id)\
                       .order_by(cls.interaction_date.desc())\
                       .limit(limit).all()
    
    @classmethod
    def get_recent(cls, user_id, limit=10):
        """Get recent interactions for user (through contacts)"""
        from .contact import Contact
        return cls.query.join(Contact)\
                       .filter(Contact.user_id == user_id)\
                       .order_by(cls.interaction_date.desc())\
                       .limit(limit).all()
    
    def to_dict(self):
        """Convert interaction to dictionary"""
        return {
            'id': self.id,
            'contact_id': self.contact_id,
            'interaction_type': self.interaction_type,
            'direction': self.direction,
            'subject': self.subject,
            'content': self.content,
            'outcome': self.outcome,
            'location': self.location,
            'duration_minutes': self.duration_minutes,
            'follow_up_required': self.follow_up_required,
            'follow_up_notes': self.follow_up_notes,
            'interaction_date': self.interaction_date.isoformat() if self.interaction_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AISuggestion(db.Model):
    """Model for AI-generated contact suggestions"""
    __tablename__ = 'ai_suggestions'
    
    # Primary fields
    id = Column(String, primary_key=True)
    contact_id = Column(String, ForeignKey('contacts.id'), nullable=False)
    goal_id = Column(String, ForeignKey('goals.id'), nullable=False)
    
    # AI-generated content
    suggestion = Column(Text, nullable=False)
    reasoning = Column(Text, nullable=True)
    confidence = Column(Float, nullable=False)
    
    # Suggestion metadata
    suggestion_type = Column(String(50), default='introduction')  # introduction, outreach, follow_up
    priority_score = Column(Float, default=0.5)
    
    # Action tracking
    is_viewed = Column(String(5), default='false')
    is_acted_upon = Column(String(5), default='false')
    action_taken = Column(String(100), nullable=True)
    action_result = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    viewed_at = Column(DateTime, nullable=True)
    acted_upon_at = Column(DateTime, nullable=True)
    
    # Relationships
    contact = relationship("Contact", back_populates="ai_suggestions")
    goal = relationship("Goal", back_populates="ai_suggestions")
    
    def __repr__(self):
        return f'<AISuggestion {self.suggestion_type} for {self.contact_id}>'
    
    @classmethod
    def create_suggestion(cls, contact_id, goal_id, suggestion, confidence, **kwargs):
        """Create a new AI suggestion"""
        import uuid
        ai_suggestion = cls(
            id=str(uuid.uuid4()),
            contact_id=contact_id,
            goal_id=goal_id,
            suggestion=suggestion,
            confidence=confidence,
            **kwargs
        )
        db.session.add(ai_suggestion)
        db.session.commit()
        return ai_suggestion
    
    @classmethod
    def get_by_contact_id(cls, contact_id):
        """Get AI suggestions for a specific contact"""
        return cls.query.filter_by(contact_id=contact_id)\
                       .order_by(cls.confidence.desc(), cls.created_at.desc()).all()
    
    @classmethod
    def get_by_goal_id(cls, goal_id, limit=20):
        """Get AI suggestions for a specific goal"""
        return cls.query.filter_by(goal_id=goal_id)\
                       .order_by(cls.confidence.desc(), cls.created_at.desc())\
                       .limit(limit).all()
    
    @classmethod
    def get_recent(cls, user_id, limit=10):
        """Get recent AI suggestions for user (through contacts)"""
        from .contact import Contact
        return cls.query.join(Contact)\
                       .filter(Contact.user_id == user_id)\
                       .order_by(cls.created_at.desc())\
                       .limit(limit).all()
    
    @classmethod
    def get_top_suggestions(cls, user_id, confidence_threshold=0.7, limit=10):
        """Get top AI suggestions for user based on confidence"""
        from .contact import Contact
        return cls.query.join(Contact)\
                       .filter(Contact.user_id == user_id, cls.confidence >= confidence_threshold)\
                       .order_by(cls.confidence.desc(), cls.priority_score.desc())\
                       .limit(limit).all()
    
    def mark_viewed(self):
        """Mark suggestion as viewed"""
        self.is_viewed = 'true'
        self.viewed_at = datetime.utcnow()
        db.session.commit()
    
    def mark_acted_upon(self, action_taken, action_result=None):
        """Mark suggestion as acted upon"""
        self.is_acted_upon = 'true'
        self.action_taken = action_taken
        self.action_result = action_result
        self.acted_upon_at = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convert AI suggestion to dictionary"""
        return {
            'id': self.id,
            'contact_id': self.contact_id,
            'goal_id': self.goal_id,
            'suggestion': self.suggestion,
            'reasoning': self.reasoning,
            'confidence': self.confidence,
            'suggestion_type': self.suggestion_type,
            'priority_score': self.priority_score,
            'is_viewed': self.is_viewed,
            'is_acted_upon': self.is_acted_upon,
            'action_taken': self.action_taken,
            'action_result': self.action_result,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'viewed_at': self.viewed_at.isoformat() if self.viewed_at else None,
            'acted_upon_at': self.acted_upon_at.isoformat() if self.acted_upon_at else None
        }