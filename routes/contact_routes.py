"""
Contact management routes module
Handles contact CRUD operations, pipeline management, and interactions
"""

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
from . import RouteBase, login_required, get_current_user_id
from utils.import.csv_import import CSVContactImporter
from utils.import.linkedin_importer import LinkedInContactImporter
from services.email.simple_email import SimpleEmailSender
from features.intelligence.contact_intelligence import ContactNLP
import logging
import json

# Create blueprint
contact_bp = Blueprint('contact_routes', __name__)

class ContactRoutes(RouteBase):
    def __init__(self):
        super().__init__()
        try:
            self.csv_importer = CSVContactImporter(self.db)
        except Exception:
            self.csv_importer = None
        
        try:
            self.linkedin_importer = LinkedInContactImporter()
        except Exception:
            self.linkedin_importer = None
        
        try:
            self.email_sender = SimpleEmailSender(self.db)
        except Exception:
            self.email_sender = None

contact_routes = ContactRoutes()

@contact_bp.route('/contacts')
@login_required
def contacts():
    """Display all contacts with search and filtering"""
    user_id = get_current_user_id()
    
    # Get query parameters
    search = request.args.get('search', '')
    warmth_filter = request.args.get('warmth', '')
    company_filter = request.args.get('company', '')
    
    try:
        if search or warmth_filter or company_filter:
            # Apply filters
            all_contacts = contact_routes.contact_model.search_contacts(
                user_id=user_id,
                search_term=search,
                warmth_status=warmth_filter,
                company=company_filter
            )
        else:
            all_contacts = contact_routes.contact_model.get_all(user_id)
        
        # Get filter options for dropdowns  
        from models import Contact
        warmth_options = Contact.get_warmth_options()
        company_options = contact_routes.contact_model.get_company_options(user_id)
        
        return render_template('contacts.html', 
                             contacts=all_contacts,
                             search=search,
                             warmth_filter=warmth_filter,
                             company_filter=company_filter,
                             warmth_options=warmth_options,
                             company_options=company_options)
                             
    except Exception as e:
        logging.error(f"Error loading contacts: {e}")
        contact_routes.flash_error('Failed to load contacts')
        return render_template('contacts.html', contacts=[])

@contact_bp.route('/contacts/create', methods=['GET', 'POST'])
@login_required
def create_contact():
    """Create a new contact"""
    if request.method == 'POST':
        user_id = get_current_user_id()
        
        # Extract form data
        contact_data = {
            'name': request.form.get('name', '').strip(),
            'email': request.form.get('email', '').strip(),
            'phone': request.form.get('phone', '').strip(),
            'company': request.form.get('company', '').strip(),
            'title': request.form.get('title', '').strip(),
            'linkedin': request.form.get('linkedin', '').strip(),
            'twitter': request.form.get('twitter', '').strip(),
            'location': request.form.get('location', '').strip(),
            'relationship_type': request.form.get('relationship_type', 'Contact'),
            'warmth_status': int(request.form.get('warmth_status', 1)),
            'warmth_label': request.form.get('warmth_label', 'Cold'),
            'priority_level': request.form.get('priority_level', 'Medium'),
            'notes': request.form.get('notes', '').strip(),
            'tags': request.form.get('tags', '').strip(),
            'interests': request.form.get('interests', '').strip()
        }
        
        # Validate required fields
        if not contact_data['name']:
            contact_routes.flash_error('Contact name is required')
            return render_template('contact_form.html', **contact_data)
        
        try:
            contact_id = contact_routes.contact_model.create(user_id, **contact_data)
            
            if contact_id:
                # Award XP for adding contact
                contact_routes.award_xp('contact_added', 5, {
                    'contact_id': contact_id,
                    'contact_name': contact_data['name']
                })
                
                contact_routes.flash_success('Contact created successfully!')
                return redirect(url_for('contact_routes.contact_detail', contact_id=contact_id))
            else:
                contact_routes.flash_error('Failed to create contact')
                
        except Exception as e:
            logging.error(f"Error creating contact: {e}")
            contact_routes.flash_error(f'Error creating contact: {str(e)}')
        
        return render_template('contact_form.html', **contact_data)
    
    # GET request - show form
    return render_template('contact_form.html')

@contact_bp.route('/contacts/<contact_id>')
@login_required
def contact_detail(contact_id):
    """Display contact details and interaction history"""
    user_id = get_current_user_id()
    
    try:
        contact = contact_routes.contact_model.get_by_id(contact_id)
        
        if not contact or contact['user_id'] != user_id:
            contact_routes.flash_error('Contact not found')
            return redirect(url_for('contact_routes.contacts'))
        
        # Get interaction history
        interactions = contact_routes.interaction_model.get_by_contact_id(contact_id)
        
        # Get AI suggestions for this contact
        ai_suggestions = contact_routes.ai_suggestion_model.get_by_contact_id(contact_id)
        
        return render_template('contact_detail.html', 
                             contact=contact,
                             interactions=interactions,
                             ai_suggestions=ai_suggestions)
                             
    except Exception as e:
        logging.error(f"Error loading contact detail: {e}")
        contact_routes.flash_error('Failed to load contact details')
        return redirect(url_for('contact_routes.contacts'))

@contact_bp.route('/contacts/<contact_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_contact(contact_id):
    """Edit contact information"""
    user_id = get_current_user_id()
    
    try:
        contact = contact_routes.contact_model.get_by_id(contact_id)
        
        if not contact or contact['user_id'] != user_id:
            contact_routes.flash_error('Contact not found')
            return redirect(url_for('contact_routes.contacts'))
        
        if request.method == 'POST':
            # Extract updated data
            update_data = {
                'name': request.form.get('name', '').strip(),
                'email': request.form.get('email', '').strip(),
                'phone': request.form.get('phone', '').strip(),
                'company': request.form.get('company', '').strip(),
                'title': request.form.get('title', '').strip(),
                'linkedin': request.form.get('linkedin', '').strip(),
                'twitter': request.form.get('twitter', '').strip(),
                'location': request.form.get('location', '').strip(),
                'relationship_type': request.form.get('relationship_type', 'Contact'),
                'warmth_status': int(request.form.get('warmth_status', 1)),
                'warmth_label': request.form.get('warmth_label', 'Cold'),
                'priority_level': request.form.get('priority_level', 'Medium'),
                'notes': request.form.get('notes', '').strip(),
                'tags': request.form.get('tags', '').strip(),
                'interests': request.form.get('interests', '').strip()
            }
            
            if not update_data['name']:
                contact_routes.flash_error('Contact name is required')
                return render_template('contact_form.html', contact=contact, **update_data)
            
            success = contact_routes.contact_model.update(contact_id, **update_data)
            
            if success:
                contact_routes.flash_success('Contact updated successfully!')
                return redirect(url_for('contact_routes.contact_detail', contact_id=contact_id))
            else:
                contact_routes.flash_error('Failed to update contact')
        
        return render_template('contact_form.html', contact=contact, edit_mode=True)
        
    except Exception as e:
        logging.error(f"Error editing contact: {e}")
        contact_routes.flash_error('Failed to edit contact')
        return redirect(url_for('contact_routes.contacts'))

@contact_bp.route('/contacts/<contact_id>/interaction', methods=['POST'])
@login_required
def add_interaction(contact_id):
    """Add new interaction with contact"""
    user_id = get_current_user_id()
    
    try:
        # Verify contact ownership
        contact = contact_routes.contact_model.get_by_id(contact_id)
        if not contact or contact['user_id'] != user_id:
            return jsonify({'error': 'Contact not found'}), 404
        
        interaction_data = {
            'interaction_type': request.form.get('type', 'note'),
            'notes': request.form.get('notes', '').strip(),
            'follow_up_date': request.form.get('follow_up_date', None),
            'outcome': request.form.get('outcome', 'completed')
        }
        
        if not interaction_data['notes']:
            return jsonify({'error': 'Interaction notes are required'}), 400
        
        interaction_id = contact_routes.interaction_model.create(
            user_id=user_id,
            contact_id=contact_id,
            **interaction_data
        )
        
        if interaction_id:
            # Award XP for interaction
            contact_routes.award_xp('interaction_logged', 3, {
                'contact_id': contact_id,
                'interaction_type': interaction_data['interaction_type']
            })
            
            return jsonify({'success': True, 'interaction_id': interaction_id})
        else:
            return jsonify({'error': 'Failed to create interaction'}), 500
            
    except Exception as e:
        logging.error(f"Error adding interaction: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@contact_bp.route('/contacts/import', methods=['GET', 'POST'])
@login_required
def import_contacts():
    """Import contacts from CSV or LinkedIn"""
    if request.method == 'POST':
        user_id = get_current_user_id()
        import_type = request.form.get('import_type', 'csv')
        
        try:
            if import_type == 'csv' and 'csv_file' in request.files:
                file = request.files['csv_file']
                if file.filename and file.filename.endswith('.csv'):
                    results = contact_routes.csv_importer.import_contacts(user_id, file)
                    
                    if results['success']:
                        # Award XP for import
                        contact_routes.award_xp('contacts_imported', 
                                               min(results['imported_count'] * 2, 50), {
                            'count': results['imported_count'],
                            'source': 'csv'
                        })
                        
                        contact_routes.flash_success(
                            f"Successfully imported {results['imported_count']} contacts!"
                        )
                    else:
                        contact_routes.flash_error(f"Import failed: {results['error']}")
                else:
                    contact_routes.flash_error('Please upload a valid CSV file')
                    
            elif import_type == 'linkedin':
                contact_routes.flash_error('LinkedIn import not yet implemented')
            
        except Exception as e:
            logging.error(f"Import error: {e}")
            contact_routes.flash_error('Import failed due to an error')
    
    return render_template('import_contacts.html')

@contact_bp.route('/contacts/pipeline')
@login_required
def contact_pipeline():
    """Display contacts in pipeline view (Kanban style)"""
    user_id = get_current_user_id()
    
    try:
        # Get contacts grouped by warmth status
        pipeline_data = contact_routes.contact_model.get_pipeline_view(user_id)
        
        return render_template('contact_pipeline.html', pipeline=pipeline_data)
        
    except Exception as e:
        logging.error(f"Error loading pipeline: {e}")
        contact_routes.flash_error('Failed to load contact pipeline')
        return redirect(url_for('contact_routes.contacts'))

@contact_bp.route('/api/contacts/<contact_id>/warmth', methods=['POST'])
@login_required
def update_contact_warmth(contact_id):
    """API endpoint to update contact warmth status"""
    user_id = get_current_user_id()
    
    try:
        # Verify ownership
        contact = contact_routes.contact_model.get_by_id(contact_id)
        if not contact or contact['user_id'] != user_id:
            return jsonify({'error': 'Contact not found'}), 404
        
        warmth_status = request.json.get('warmth_status')
        warmth_label = request.json.get('warmth_label', '')
        
        if warmth_status is None:
            return jsonify({'error': 'Warmth status is required'}), 400
        
        success = contact_routes.contact_model.update_warmth(
            contact_id, warmth_status, warmth_label
        )
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to update warmth'}), 500
            
    except Exception as e:
        logging.error(f"Error updating warmth: {e}")
        return jsonify({'error': 'Internal server error'}), 500