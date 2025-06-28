"""
Goal model for the Rhiz application
"""
from datetime import datetime
from backend.app.core.database import db
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship

class Goal(db.Model):
    """Goal model for tracking user objectives and AI matching"""
    __tablename__ = 'goals'
    
    # Primary fields
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    
    # Goal content
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # AI processing
    embedding = Column(Text, nullable=True)  # JSON string of embedding vector
    
    # Status tracking
    is_active = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="goals")
    ai_suggestions = relationship("AISuggestion", back_populates="goal", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Goal {self.title}>'
    
    @classmethod
    def create_goal(cls, user_id, title, description, embedding=None):
        """Create a new goal"""
        import uuid
        goal = cls(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            description=description,
            embedding=embedding
        )
        db.session.add(goal)
        db.session.commit()
        return goal
    
    @classmethod
    def get_by_user(cls, user_id, active_only=True):
        """Get goals for a user"""
        query = cls.query.filter_by(user_id=user_id)
        if active_only:
            query = query.filter_by(is_active=True, is_completed=False)
        return query.order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_active_goals(cls, user_id):
        """Get active goals for a user"""
        return cls.query.filter_by(
            user_id=user_id,
            is_active=True,
            is_completed=False
        ).order_by(cls.updated_at.desc()).all()
    
    def update_embedding(self, embedding):
        """Update goal embedding for AI matching"""
        self.embedding = embedding
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def mark_completed(self):
        """Mark goal as completed"""
        self.is_completed = True
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def reactivate(self):
        """Reactivate a completed or inactive goal"""
        self.is_active = True
        self.is_completed = False
        self.completed_at = None
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convert goal to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'is_active': self.is_active,
            'is_completed': self.is_completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'has_embedding': bool(self.embedding)
        }