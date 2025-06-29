"""
Contact Routes - Contact management and CSV upload functionality
"""
import json
import uuid
import pandas as pd
import io
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from backend.models import Contact, ContactInteraction, User
from backend.extensions import db
from backend.services.contact_sync_engine import ContactSyncEngine
from backend.services.contact_intelligence import ContactIntelligence

contact_bp = Blueprint('contact', __name__)


@contact_bp.route('', methods=['GET'])
def get_contacts():
    """Get all contacts for the current user"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        contacts = Contact.query.filter_by(user_id=user_id).all()
        return jsonify([contact.to_dict() for contact in contacts])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@contact_bp.route('', methods=['POST'])
def create_contact():
    """Create a new contact"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    
    try:
        contact = Contact(
            user_id=user_id,
            name=data['name'],
            email=data.get('email'),
            phone=data.get('phone'),
            company=data.get('company'),
            title=data.get('title'),
            linkedin=data.get('linkedin'),
            twitter=data.get('twitter'),
            notes=data.get('notes'),
            warmth_level=data.get('warmth_level', 'cold'),
            source=data.get('source', 'manual')
        )
        
        db.session.add(contact)
        db.session.commit()
        
        return jsonify(contact.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@contact_bp.route('/<contact_id>', methods=['GET'])
def get_contact(contact_id):
    """Get a specific contact"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        contact = Contact.query.filter_by(id=contact_id, user_id=user_id).first()
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
        
        return jsonify(contact.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@contact_bp.route('/<contact_id>', methods=['PUT'])
def update_contact(contact_id):
    """Update a contact"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        contact = Contact.query.filter_by(id=contact_id, user_id=user_id).first()
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
        
        # Update fields
        for field in ['name', 'email', 'phone', 'company', 'title', 'linkedin', 'twitter', 'notes', 'warmth_level']:
            if field in data:
                setattr(contact, field, data[field])
        
        db.session.commit()
        return jsonify(contact.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@contact_bp.route('/<contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    """Delete a contact"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        contact = Contact.query.filter_by(id=contact_id, user_id=user_id).first()
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
        
        db.session.delete(contact)
        db.session.commit()
        return jsonify({'message': 'Contact deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@contact_bp.route('/upload', methods=['POST'])
def upload_contacts():
    """Upload and parse CSV contacts file"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Handle JSON data from frontend (parsed CSV)
        if request.is_json:
            data = request.get_json()
            contacts_data = data.get('contacts', [])
            
            if not contacts_data:
                return jsonify({'error': 'No contacts provided'}), 400
            
            # Process parsed contacts
            sync_engine = ContactSyncEngine()
            result = sync_engine.process_parsed_contacts(user_id, contacts_data)
            
            return jsonify(result)
        
        # Handle file upload (legacy support)
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.csv'):
            return jsonify({'error': 'Only CSV files are allowed'}), 400
        
        # Process CSV file
        sync_engine = ContactSyncEngine()
        result = sync_engine.import_csv_file(user_id, file)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@contact_bp.route('/sync/<source_type>', methods=['POST'])
def sync_contacts(source_type):
    """Trigger contact sync from external sources"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        sync_engine = ContactSyncEngine()
        
        if source_type == 'google':
            result = sync_engine.sync_google_contacts(user_id)
        elif source_type == 'linkedin':
            result = sync_engine.sync_linkedin_contacts(user_id)
        else:
            return jsonify({'error': 'Unsupported sync source'}), 400
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@contact_bp.route('/sync-status', methods=['GET'])
def get_sync_status():
    """Get status of contact sync operations"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        sync_engine = ContactSyncEngine()
        status = sync_engine.get_sync_status(user_id)
        return jsonify(status)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@contact_bp.route('/<contact_id>/interactions', methods=['GET'])
def get_contact_interactions(contact_id):
    """Get interactions for a specific contact"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Verify contact belongs to user
        contact = Contact.query.filter_by(id=contact_id, user_id=user_id).first()
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
        
        interactions = ContactInteraction.query.filter_by(contact_id=contact_id).order_by(
            ContactInteraction.interaction_date.desc()
        ).all()
        
        return jsonify([interaction.to_dict() for interaction in interactions])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@contact_bp.route('/<contact_id>/interactions', methods=['POST'])
def add_contact_interaction(contact_id):
    """Add new interaction with contact"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    if not data or not data.get('interaction_type'):
        return jsonify({'error': 'Interaction type is required'}), 400
    
    try:
        # Verify contact belongs to user
        contact = Contact.query.filter_by(id=contact_id, user_id=user_id).first()
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
        
        interaction = ContactInteraction(
            contact_id=contact_id,
            interaction_type=data['interaction_type'],
            direction=data.get('direction', 'outbound'),
            content=data.get('content'),
            sentiment=data.get('sentiment', 0.5)
        )
        
        db.session.add(interaction)
        
        # Update contact's last interaction
        contact.last_interaction = interaction.interaction_date
        
        db.session.commit()
        
        return jsonify(interaction.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500