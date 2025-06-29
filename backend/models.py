"""
SQLAlchemy Models for Rhiz Backend
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, Float, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .extensions import db


class User(db.Model):
    """User model for authentication and profile management"""
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    google_id = Column(String(255))
    magic_link_token = Column(String(255))
    magic_link_expires = Column(DateTime)
    subscription_tier = Column(String(50), default='free')
    stripe_customer_id = Column(String(255))
    stripe_subscription_id = Column(String(255))
    subscription_status = Column(String(50))
    subscription_expires = Column(DateTime)
    goals_count = Column(Integer, default=0)
    contacts_count = Column(Integer, default=0)
    ai_suggestions_used = Column(Integer, default=0)
    is_guest = Column(Boolean, default=False)
    guest_actions_count = Column(Integer, default=0)
    onboarding_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    contacts = relationship('Contact', back_populates='user', cascade='all, delete-orphan')
    goals = relationship('Goal', back_populates='user', cascade='all, delete-orphan')
    ai_suggestions = relationship('AISuggestion', back_populates='user', cascade='all, delete-orphan')
    journal_entries = relationship('JournalEntry', back_populates='user', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'email': self.email,
            'google_id': self.google_id,
            'subscription_tier': self.subscription_tier,
            'stripe_customer_id': self.stripe_customer_id,
            'stripe_subscription_id': self.stripe_subscription_id,
            'subscription_status': self.subscription_status,
            'subscription_expires': self.subscription_expires.isoformat() if self.subscription_expires else None,
            'goals_count': self.goals_count,
            'contacts_count': self.contacts_count,
            'ai_suggestions_used': self.ai_suggestions_used,
            'is_guest': self.is_guest,
            'guest_actions_count': self.guest_actions_count,
            'onboarding_completed': self.onboarding_completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Contact(db.Model):
    """Contact model for relationship management"""
    __tablename__ = 'contacts'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    
    # Basic information
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    twitter = Column(String(255))
    linkedin = Column(String(500))
    handle = Column(String(255))
    relationship_type = Column(String(100))
    
    # Warmth tracking
    warmth_status = Column(Integer, default=0)
    warmth_label = Column(String(50))
    warmth_level = Column(String(20), default='cold')
    
    # Interaction tracking
    last_interaction_date = Column(DateTime)
    last_contact_method = Column(String(100))
    interaction_count = Column(Integer, default=0)
    
    # Organization and metadata
    priority_level = Column(String(20))
    notes = Column(Text)
    narrative_thread = Column(Text)
    follow_up_action = Column(Text)
    follow_up_due_date = Column(DateTime)
    tags = Column(Text)
    introduced_by = Column(String(255))
    location = Column(String(255))
    company = Column(String(255))
    title = Column(String(255))
    interests = Column(Text)
    source = Column(String(50), default='manual')
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='contacts')
    interactions = relationship('ContactInteraction', back_populates='contact', cascade='all, delete-orphan')
    ai_suggestions = relationship('AISuggestion', back_populates='contact', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'twitter': self.twitter,
            'linkedin': self.linkedin,
            'handle': self.handle,
            'relationship_type': self.relationship_type,
            'warmth_status': self.warmth_status,
            'warmth_label': self.warmth_label,
            'warmth_level': self.warmth_level,
            'last_interaction_date': self.last_interaction_date.isoformat() if self.last_interaction_date else None,
            'last_contact_method': self.last_contact_method,
            'interaction_count': self.interaction_count,
            'priority_level': self.priority_level,
            'notes': self.notes,
            'narrative_thread': self.narrative_thread,
            'follow_up_action': self.follow_up_action,
            'follow_up_due_date': self.follow_up_due_date.isoformat() if self.follow_up_due_date else None,
            'tags': self.tags,
            'introduced_by': self.introduced_by,
            'location': self.location,
            'company': self.company,
            'title': self.title,
            'interests': self.interests,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Goal(db.Model):
    """Goal model for tracking user objectives"""
    __tablename__ = 'goals'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    goal_type = Column(String(100))  # fundraising, hiring, partnerships, etc.
    timeline = Column(String(100))
    status = Column(String(50), default='active')  # active, paused, completed
    priority_level = Column(String(50), default='medium')  # low, medium, high
    metrics = Column(Text)
    progress_percentage = Column(Integer, default=0)
    
    # AI processing
    embedding = Column(Text)  # Store vector embeddings for matching
    target_contact_types = Column(Text)
    preferred_interaction_style = Column(Text)
    context_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='goals')
    ai_suggestions = relationship('AISuggestion', back_populates='goal', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'title': self.title,
            'description': self.description,
            'goal_type': self.goal_type,
            'timeline': self.timeline,
            'status': self.status,
            'priority_level': self.priority_level,
            'metrics': self.metrics,
            'progress_percentage': self.progress_percentage,
            'embedding': self.embedding,
            'target_contact_types': self.target_contact_types,
            'preferred_interaction_style': self.preferred_interaction_style,
            'context_notes': self.context_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ContactInteraction(db.Model):
    """Track interactions with contacts"""
    __tablename__ = 'contact_interactions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_id = Column(UUID(as_uuid=True), ForeignKey('contacts.id'), nullable=False)
    
    interaction_type = Column(String(50), nullable=False)  # email, call, meeting, message
    direction = Column(String(20), default='outbound')  # inbound, outbound
    content = Column(Text)
    sentiment = Column(Float, default=0.5)  # 0.0 to 1.0
    
    created_at = Column(DateTime, default=datetime.utcnow)
    interaction_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    contact = relationship('Contact', back_populates='interactions')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'contact_id': str(self.contact_id),
            'interaction_type': self.interaction_type,
            'direction': self.direction,
            'content': self.content,
            'sentiment': self.sentiment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'interaction_date': self.interaction_date.isoformat() if self.interaction_date else None
        }


class AISuggestion(db.Model):
    """AI-generated suggestions for user actions"""
    __tablename__ = 'ai_suggestions'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    goal_id = Column(String, ForeignKey('goals.id'))
    contact_id = Column(String, ForeignKey('contacts.id'))
    
    suggestion_type = Column(String(50), nullable=False)  # contact_match, outreach, follow_up
    confidence = Column(Float, default=0.0)
    reasoning = Column(Text)
    suggested_action = Column(Text)
    outreach_message = Column(Text)
    
    # Status tracking
    status = Column(String(20), default='pending')  # pending, viewed, acted, dismissed
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='ai_suggestions')
    goal = relationship('Goal', back_populates='ai_suggestions')
    contact = relationship('Contact', back_populates='ai_suggestions')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'goal_id': str(self.goal_id) if self.goal_id else None,
            'contact_id': str(self.contact_id) if self.contact_id else None,
            'suggestion_type': self.suggestion_type,
            'confidence': self.confidence,
            'reasoning': self.reasoning,
            'suggested_action': self.suggested_action,
            'outreach_message': self.outreach_message,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AuthToken(db.Model):
    """Authentication tokens for magic link login"""
    __tablename__ = 'user_auth_tokens'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), nullable=False)
    token = Column(String(255), nullable=False, unique=True)
    expires = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    used_at = Column(DateTime)
    
    def is_expired(self):
        return datetime.utcnow() > self.expires
    
    def mark_used(self):
        self.used_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'email': self.email,
            'token': self.token,
            'expires': self.expires.isoformat() if self.expires else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'used_at': self.used_at.isoformat() if self.used_at else None
        }


class JournalEntry(db.Model):
    """Journal entries for reflection and insights"""
    __tablename__ = 'journal_entries'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    title = Column(String(255))
    content = Column(Text, nullable=False)
    tags = Column(JSON)  # Store as JSON array
    
    # AI analysis
    ai_reflection = Column(Text)
    sentiment_score = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='journal_entries')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'title': self.title,
            'content': self.content,
            'tags': self.tags,
            'ai_reflection': self.ai_reflection,
            'sentiment_score': self.sentiment_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }