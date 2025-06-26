"""
Monica-Inspired CRM Features for OuRhizome
Handles reminders, journal entries, tasks, and file attachments
"""
import os
import uuid
import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from werkzeug.utils import secure_filename
from models import Database, Reminder, JournalEntry, Task, Attachment, Contact
from functools import wraps

def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def award_xp(user_id, action, points):
    """Simple XP tracking function"""
    try:
        import gamification
        gamification.award_xp(user_id, action, points)
    except ImportError:
        pass  # Skip XP if gamification module not available

# Create blueprint
monica_bp = Blueprint('monica', __name__, url_prefix='/crm')

# File upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database models
db = Database()
reminder_model = Reminder(db)
journal_model = JournalEntry(db)
task_model = Task(db)
attachment_model = Attachment(db)
contact_model = Contact(db)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Reminders Routes
@monica_bp.route('/reminders')
@require_login
def reminders():
    """Display all reminders for the user"""
    user_id = session.get('user_id')
    all_reminders = reminder_model.get_all(user_id)
    due_reminders = reminder_model.get_due_reminders(user_id, days_ahead=30)
    
    return render_template('monica/reminders.html', 
                         all_reminders=all_reminders,
                         due_reminders=due_reminders)

@monica_bp.route('/reminder/create', methods=['GET', 'POST'])
@require_login
def create_reminder():
    """Create a new reminder"""
    if request.method == 'POST':
        user_id = session.get('user_id')
        contact_id = request.form.get('contact_id')
        title = request.form.get('title')
        description = request.form.get('description', '')
        reminder_type = request.form.get('reminder_type', 'follow_up')
        due_date = request.form.get('due_date')
        is_recurring = bool(request.form.get('is_recurring'))
        recurrence_pattern = request.form.get('recurrence_pattern') if is_recurring else None
        
        if title and contact_id and due_date:
            reminder_id = reminder_model.create(
                user_id=user_id,
                contact_id=contact_id,
                title=title,
                description=description,
                reminder_type=reminder_type,
                due_date=due_date,
                is_recurring=is_recurring,
                recurrence_pattern=recurrence_pattern
            )
            
            if reminder_id:
                # Award XP for creating reminder
                award_xp(user_id, 'reminder_created', {
                    'action': 'reminder_created',
                    'xp_awarded': 5,
                    'reminder_type': reminder_type
                })
                flash('Reminder created successfully!', 'success')
                return redirect(url_for('monica.reminders'))
            else:
                flash('Failed to create reminder.', 'error')
        else:
            flash('Please fill in all required fields.', 'error')
    
    # Get contacts for dropdown
    user_id = session.get('user_id')
    contacts = contact_model.get_all(user_id)
    return render_template('monica/create_reminder.html', contacts=contacts)

@monica_bp.route('/reminder/<reminder_id>/complete', methods=['POST'])
@require_login
def complete_reminder(reminder_id):
    """Mark a reminder as completed"""
    reminder_model.mark_completed(reminder_id)
    
    # Award XP for completing reminder
    user_id = session.get('user_id')
    award_xp(user_id, 'reminder_completed', {
        'action': 'reminder_completed',
        'xp_awarded': 3
    })
    
    flash('Reminder marked as completed!', 'success')
    return redirect(url_for('monica.reminders'))

# Tasks Routes
@monica_bp.route('/tasks')
@require_login
def tasks():
    """Display all tasks for the user"""
    user_id = session.get('user_id')
    status_filter = request.args.get('status')
    
    all_tasks = task_model.get_all(user_id, status=status_filter)
    
    # Organize tasks by status for kanban view
    tasks_by_status = {
        'todo': [t for t in all_tasks if t['status'] == 'todo'],
        'in_progress': [t for t in all_tasks if t['status'] == 'in_progress'],
        'done': [t for t in all_tasks if t['status'] == 'done']
    }
    
    return render_template('monica/tasks.html', 
                         tasks_by_status=tasks_by_status,
                         status_filter=status_filter)

@monica_bp.route('/task/create', methods=['GET', 'POST'])
@require_login
def create_task():
    """Create a new task"""
    if request.method == 'POST':
        user_id = session.get('user_id')
        title = request.form.get('title')
        description = request.form.get('description', '')
        contact_id = request.form.get('contact_id') or None
        priority = request.form.get('priority', 'medium')
        due_date = request.form.get('due_date') or None
        
        if title:
            task_id = task_model.create(
                user_id=user_id,
                title=title,
                description=description,
                contact_id=contact_id,
                priority=priority,
                due_date=due_date
            )
            
            if task_id:
                # Award XP for creating task
                award_xp(user_id, 'task_created', {
                    'action': 'task_created',
                    'xp_awarded': 5,
                    'priority': priority
                })
                flash('Task created successfully!', 'success')
                return redirect(url_for('monica.tasks'))
            else:
                flash('Failed to create task.', 'error')
        else:
            flash('Please enter a task title.', 'error')
    
    # Get contacts for dropdown
    user_id = session.get('user_id')
    contacts = contact_model.get_all(user_id)
    return render_template('monica/create_task.html', contacts=contacts)

@monica_bp.route('/task/<task_id>/update', methods=['POST'])
@require_login
def update_task_status(task_id):
    """Update task status"""
    new_status = request.form.get('status')
    
    if new_status in ['todo', 'in_progress', 'done']:
        task_model.update_status(task_id, new_status)
        
        # Award XP for completing task
        if new_status == 'done':
            user_id = session.get('user_id')
            award_xp(user_id, 'task_completed', {
                'action': 'task_completed',
                'xp_awarded': 8
            })
            flash('Task completed! Well done!', 'success')
        else:
            flash('Task status updated!', 'success')
    else:
        flash('Invalid task status.', 'error')
    
    return redirect(url_for('monica.tasks'))

# Journal Entries Routes
@monica_bp.route('/contact/<contact_id>/journal')
@require_login
def contact_journal(contact_id):
    """Display journal entries for a contact"""
    user_id = session.get('user_id')
    contact = contact_model.get_by_id(contact_id)
    
    if not contact or contact['user_id'] != user_id:
        flash('Contact not found.', 'error')
        return redirect(url_for('dashboard'))
    
    entries = journal_model.get_by_contact(contact_id)
    return render_template('monica/contact_journal.html', 
                         contact=contact, entries=entries)

@monica_bp.route('/contact/<contact_id>/journal/create', methods=['POST'])
@require_login
def create_journal_entry(contact_id):
    """Create a new journal entry for a contact"""
    user_id = session.get('user_id')
    title = request.form.get('title', '')
    content = request.form.get('content')
    entry_type = request.form.get('entry_type', 'note')
    
    if content:
        entry_id = journal_model.create(
            user_id=user_id,
            contact_id=contact_id,
            content=content,
            title=title,
            entry_type=entry_type
        )
        
        if entry_id:
            # Award XP for creating journal entry
            award_xp(user_id, 'journal_entry_created', {
                'action': 'journal_entry_created',
                'xp_awarded': 3,
                'entry_type': entry_type
            })
            flash('Journal entry created successfully!', 'success')
        else:
            flash('Failed to create journal entry.', 'error')
    else:
        flash('Please enter some content for the journal entry.', 'error')
    
    return redirect(url_for('monica.contact_journal', contact_id=contact_id))

# File Attachments Routes
@monica_bp.route('/contact/<contact_id>/attachments')
@require_login
def contact_attachments(contact_id):
    """Display attachments for a contact"""
    user_id = session.get('user_id')
    contact = contact_model.get_by_id(contact_id)
    
    if not contact or contact['user_id'] != user_id:
        flash('Contact not found.', 'error')
        return redirect(url_for('dashboard'))
    
    attachments = attachment_model.get_by_contact(contact_id)
    return render_template('monica/contact_attachments.html', 
                         contact=contact, attachments=attachments)

@monica_bp.route('/contact/<contact_id>/attachments/upload', methods=['POST'])
@require_login
def upload_attachment(contact_id):
    """Upload a file attachment for a contact"""
    user_id = session.get('user_id')
    contact = contact_model.get_by_id(contact_id)
    
    if not contact or contact['user_id'] != user_id:
        flash('Contact not found.', 'error')
        return redirect(url_for('dashboard'))
    
    if 'file' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('monica.contact_attachments', contact_id=contact_id))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('monica.contact_attachments', contact_id=contact_id))
    
    if file and allowed_file(file.filename):
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            flash('File size too large. Maximum 16MB allowed.', 'error')
            return redirect(url_for('monica.contact_attachments', contact_id=contact_id))
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        try:
            file.save(file_path)
            
            # Save to database
            description = request.form.get('description', '')
            attachment_id = attachment_model.create(
                user_id=user_id,
                contact_id=contact_id,
                filename=filename,
                file_path=file_path,
                file_size=file_size,
                description=description
            )
            
            if attachment_id:
                # Award XP for uploading attachment
                award_xp(user_id, 'attachment_uploaded', {
                    'action': 'attachment_uploaded',
                    'xp_awarded': 5,
                    'file_type': filename.split('.')[-1].lower()
                })
                flash('File uploaded successfully!', 'success')
            else:
                os.remove(file_path)  # Clean up file if database save failed
                flash('Failed to save file information.', 'error')
                
        except Exception as e:
            flash(f'Failed to upload file: {str(e)}', 'error')
    else:
        flash('Invalid file type. Please check allowed formats.', 'error')
    
    return redirect(url_for('monica.contact_attachments', contact_id=contact_id))

@monica_bp.route('/attachment/<attachment_id>/download')
@require_login
def download_attachment(attachment_id):
    """Download an attachment file"""
    user_id = session.get('user_id')
    attachment = attachment_model.get_by_id(attachment_id)
    
    if not attachment or attachment['user_id'] != user_id:
        flash('Attachment not found.', 'error')
        return redirect(url_for('dashboard'))
    
    if os.path.exists(attachment['file_path']):
        return send_file(attachment['file_path'], as_attachment=True, 
                        download_name=attachment['filename'])
    else:
        flash('File not found on server.', 'error')
        return redirect(url_for('monica.contact_attachments', 
                              contact_id=attachment['contact_id']))

@monica_bp.route('/attachment/<attachment_id>/delete', methods=['POST'])
@require_login
def delete_attachment(attachment_id):
    """Delete an attachment"""
    user_id = session.get('user_id')
    attachment = attachment_model.get_by_id(attachment_id)
    
    if not attachment or attachment['user_id'] != user_id:
        flash('Attachment not found.', 'error')
        return redirect(url_for('dashboard'))
    
    contact_id = attachment['contact_id']
    
    # Delete file from filesystem
    if os.path.exists(attachment['file_path']):
        try:
            os.remove(attachment['file_path'])
        except Exception as e:
            print(f"Failed to delete file: {e}")
    
    # Delete from database
    if attachment_model.delete(attachment_id):
        flash('Attachment deleted successfully.', 'success')
    else:
        flash('Failed to delete attachment.', 'error')
    
    return redirect(url_for('monica.contact_attachments', contact_id=contact_id))

# API endpoints for AJAX updates
@monica_bp.route('/api/due-reminders')
@require_login
def api_due_reminders():
    """Get due reminders for dashboard widget"""
    user_id = session.get('user_id')
    reminders = reminder_model.get_due_reminders(user_id, days_ahead=7)
    return jsonify(reminders)

@monica_bp.route('/api/pending-tasks')
@require_login
def api_pending_tasks():
    """Get pending tasks for dashboard widget"""
    user_id = session.get('user_id')
    tasks = task_model.get_all(user_id, status='todo')
    return jsonify(tasks[:5])  # Return top 5 pending tasks