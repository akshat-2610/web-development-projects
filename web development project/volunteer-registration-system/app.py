import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from models import db, Volunteer, Opportunity, Application
from datetime import datetime
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key-volunteer-system-198234'
# Check if running on Vercel serverless
if os.environ.get('VERCEL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/volunteer.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///volunteer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
# Initialize database and seed opportunities automatically on startup
with app.app_context():
    db.create_all()
    if Opportunity.query.count() == 0:
        opportunities = [
            Opportunity(
                title="Green City Tree Planting",
                description="Join us for our annual reforestation drive. We will be planting native trees in the city park to increase green cover, combat local warming, and create beautiful natural spaces for the community. Wear comfortable clothing and bringing gardening gloves is recommended. Shovels, water, and lunch will be provided!",
                category="Environment",
                date="2026-06-25",
                time="09:00 AM - 01:00 PM",
                location="Central Park East Ground",
                required_skills="Physical endurance, Teamwork",
                max_slots=15,
                slots_filled=0
            ),
            Opportunity(
                title="Youth Math & Science Tutoring",
                description="Help middle school students from underserved communities catch up on critical STEM subjects. Tutors will work one-on-one or in small groups to explain core concepts, help with homework, and conduct fun science experiments. Educational materials and guidelines are fully provided.",
                category="Education",
                date="2026-06-28",
                time="04:00 PM - 06:30 PM",
                location="Downtown Public Library",
                required_skills="Patience, Strong STEM background, Communication",
                max_slots=8,
                slots_filled=0
            ),
            Opportunity(
                title="Community Food Bank Sorting",
                description="Help sort, package, and inventory incoming food donations for distribution to local shelters. This fast-paced, high-impact volunteer activity is perfect for teams or individuals looking to make a direct impact on hunger relief in our city.",
                category="Community",
                date="2026-07-02",
                time="10:00 AM - 02:00 PM",
                location="Metro Food Bank Depot",
                required_skills="Sorting, Attention to detail, Light lifting",
                max_slots=25,
                slots_filled=0
            ),
            Opportunity(
                title="Senior Tech Assist Workshop",
                description="Empower elder members of our community by teaching them how to use smartphones, tablets, video-call family members, and safely browse the internet. Your patience and kindness can help bridge the digital divide and reduce social isolation.",
                category="Community",
                date="2026-07-05",
                time="11:00 AM - 01:30 PM",
                location="Harmony Retirement Center",
                required_skills="Patience, Friendly demeanor, Digital literacy",
                max_slots=6,
                slots_filled=0
            ),
            Opportunity(
                title="Emergency Disaster Relief Drill",
                description="Participate in a preparedness drill organized by local rescue teams. Volunteers will roleplay as citizens requiring shelter and evacuation support, helping coordinators test emergency logistics, medical triage response, and shelter setups.",
                category="Disaster Relief",
                date="2026-07-12",
                time="08:00 AM - 03:00 PM",
                location="County Fairgrounds Arena",
                required_skills="Quick response, Teamwork, Calm under pressure",
                max_slots=40,
                slots_filled=0
            )
        ]
        db.session.bulk_save_objects(opportunities)
        db.session.commit()
        print("Database initialized and seeded successfully!")
# Context processor to expose log-in status to templates
@app.context_processor
def inject_user():
    user = None
    if 'volunteer_id' in session:
        user = Volunteer.query.get(session['volunteer_id'])
    return dict(current_user=user)
# ==================== VIEW ROUTES ====================
@app.route('/')
def home():
    # Fetch top statistics
    volunteers_count = Volunteer.query.count()
    opps_count = Opportunity.query.filter_by(status='Active').count()
    
    # Calculate total completed hours
    total_hours = db.session.query(db.func.sum(Application.hours_logged)).scalar() or 0
    total_hours = round(total_hours, 1)
    
    # Fetch 3 featured upcoming opportunities
    featured_opps = Opportunity.query.filter_by(status='Active').limit(3).all()
    
    return render_template('index.html', 
                           volunteers_count=volunteers_count + 120, # Add seed offset
                           opps_count=opps_count,
                           total_hours=total_hours + 840, # Add seed offset
                           featured_opps=featured_opps)
@app.route('/opportunities')
def opportunities():
    search_query = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    
    query = Opportunity.query.filter_by(status='Active')
    if search_query:
        query = query.filter(
            (Opportunity.title.ilike(f'%{search_query}%')) | 
            (Opportunity.description.ilike(f'%{search_query}%')) |
            (Opportunity.location.ilike(f'%{search_query}%'))
        )
    if category and category != 'All':
        query = query.filter_by(category=category)
        
    opps = query.order_by(Opportunity.date).all()
    categories = ['Environment', 'Education', 'Community', 'Disaster Relief', 'Healthcare']
    
    return render_template('opportunities.html', 
                           opportunities=opps, 
                           categories=categories, 
                           selected_category=category, 
                           search_query=search_query)
@app.route('/register')
def register():
    if 'volunteer_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('register.html')
@app.route('/dashboard')
def dashboard():
    if 'volunteer_id' not in session:
        return redirect(url_for('register'))
    
    volunteer = Volunteer.query.get(session['volunteer_id'])
    if not volunteer:
        session.clear()
        return redirect(url_for('register'))
        
    # Get active/past registrations
    apps = Application.query.filter_by(volunteer_id=volunteer.id).all()
    
    # Calculate stats
    completed_apps = [a for a in apps if a.status == 'Completed']
    total_hours = sum(a.hours_logged for a in completed_apps)
    upcoming_events = [a for a in apps if a.status in ['Pending', 'Approved']]
    
    return render_template('dashboard.html', 
                           volunteer=volunteer, 
                           applications=apps, 
                           total_hours=total_hours,
                           completed_count=len(completed_apps),
                           upcoming_count=len(upcoming_events))
@app.route('/admin')
def admin():
    # Simple open coordinator panel for the demo
    opportunities = Opportunity.query.order_by(Opportunity.date.desc()).all()
    applications = Application.query.order_by(Application.apply_date.desc()).all()
    
    # Admin stats
    total_volunteers = Volunteer.query.count()
    active_opps = Opportunity.query.filter_by(status='Active').count()
    pending_apps = Application.query.filter_by(status='Pending').count()
    
    # Calculate category share
    categories = ['Environment', 'Education', 'Community', 'Disaster Relief', 'Healthcare']
    cat_counts = []
    for cat in categories:
        count = Opportunity.query.filter_by(category=cat).count()
        cat_counts.append({'name': cat, 'count': count})
        
    return render_template('admin.html',
                           opportunities=opportunities,
                           applications=applications,
                           total_volunteers=total_volunteers,
                           active_opps=active_opps,
                           pending_apps=pending_apps,
                           categories_data=cat_counts)
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))
# ==================== API ENDPOINTS ====================
@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    
    # Validation
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    phone = data.get('phone', '').strip()
    age = data.get('age')
    skills = data.get('skills', [])
    interests = data.get('interests', [])
    availability = data.get('availability', [])
    
    if not name or not email or not password:
        return jsonify({'success': False, 'message': 'Name, email, and password are required.'}), 400
        
    if Volunteer.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': 'Email address already registered.'}), 400
        
    try:
        volunteer = Volunteer(
            name=name,
            email=email,
            phone=phone,
            age=int(age) if age else None,
            skills=','.join(skills) if isinstance(skills, list) else skills,
            interests=','.join(interests) if isinstance(interests, list) else interests,
            availability=','.join(availability) if isinstance(availability, list) else availability
        )
        volunteer.set_password(password)
        
        db.session.add(volunteer)
        db.session.commit()
        
        # Log in automatically
        session['volunteer_id'] = volunteer.id
        return jsonify({'success': True, 'message': 'Registration successful!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required.'}), 400
        
    volunteer = Volunteer.query.filter_by(email=email).first()
    if not volunteer or not volunteer.check_password(password):
        return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401
        
    session['volunteer_id'] = volunteer.id
    return jsonify({'success': True, 'message': 'Login successful!'})
@app.route('/api/apply/<int:opportunity_id>', methods=['POST'])
def api_apply(opportunity_id):
    if 'volunteer_id' not in session:
        return jsonify({'success': False, 'message': 'Please register or log in to apply.'}), 401
        
    volunteer_id = session['volunteer_id']
    opp = Opportunity.query.get(opportunity_id)
    if not opp:
        return jsonify({'success': False, 'message': 'Opportunity not found.'}), 404
        
    if opp.status != 'Active':
        return jsonify({'success': False, 'message': 'This opportunity is no longer active.'}), 400
        
    # Check duplicate application
    existing = Application.query.filter_by(volunteer_id=volunteer_id, opportunity_id=opportunity_id).first()
    if existing:
        return jsonify({'success': False, 'message': 'You have already applied for this opportunity.'}), 400
        
    # Check slots
    if opp.slots_filled >= opp.max_slots:
        return jsonify({'success': False, 'message': 'This opportunity is already full.'}), 400
        
    try:
        app_record = Application(
            volunteer_id=volunteer_id,
            opportunity_id=opportunity_id,
            status='Pending'
        )
        opp.slots_filled += 1
        db.session.add(app_record)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Application submitted successfully! Check your dashboard for status updates.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500
@app.route('/api/cancel-apply/<int:app_id>', methods=['POST'])
def api_cancel_apply(app_id):
    if 'volunteer_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized.'}), 401
        
    app_record = Application.query.get(app_id)
    if not app_record:
        return jsonify({'success': False, 'message': 'Application record not found.'}), 404
        
    if app_record.volunteer_id != session['volunteer_id']:
        return jsonify({'success': False, 'message': 'Unauthorized action.'}), 403
        
    try:
        opp = app_record.opportunity
        if opp and opp.slots_filled > 0:
            opp.slots_filled -= 1
            
        db.session.delete(app_record)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Registration cancelled successfully.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500
@app.route('/api/admin/opportunity', methods=['POST'])
def api_create_opportunity():
    # Simple mock authentication (open admin dashboard for demonstration)
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    category = data.get('category', '').strip()
    date = data.get('date', '').strip()
    time = data.get('time', '').strip()
    location = data.get('location', '').strip()
    required_skills = data.get('skills', '').strip()
    max_slots = data.get('max_slots', 10)
    
    if not title or not description or not category or not date or not time or not location:
        return jsonify({'success': False, 'message': 'All main fields are required.'}), 400
        
    try:
        opp = Opportunity(
            title=title,
            description=description,
            category=category,
            date=date,
            time=time,
            location=location,
            required_skills=required_skills,
            max_slots=int(max_slots)
        )
        db.session.add(opp)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Opportunity created successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500
@app.route('/api/admin/application/<int:app_id>/status', methods=['POST'])
def api_update_application_status(app_id):
    data = request.get_json() or {}
    new_status = data.get('status', '').strip() # Approved, Denied, Completed
    hours_logged = data.get('hours', 0.0)
    
    app_record = Application.query.get(app_id)
    if not app_record:
        return jsonify({'success': False, 'message': 'Application not found.'}), 404
        
    if new_status not in ['Approved', 'Denied', 'Completed', 'Pending']:
        return jsonify({'success': False, 'message': 'Invalid status.'}), 400
        
    try:
        app_record.status = new_status
        if new_status == 'Completed':
            app_record.hours_logged = float(hours_logged)
            
            # Recalculate volunteer level/badge based on total hours
            vol = app_record.volunteer
            completed_apps = Application.query.filter_by(volunteer_id=vol.id, status='Completed').all()
            total_hours = sum(a.hours_logged for a in completed_apps) + float(hours_logged)
            
            # Simple level/badge system
            if total_hours >= 50:
                vol.level = 4
                vol.badge = "Community Champion"
            elif total_hours >= 20:
                vol.level = 3
                vol.badge = "Local Hero"
            elif total_hours >= 5:
                vol.level = 2
                vol.badge = "Dedicated Helper"
            else:
                vol.level = 1
                vol.badge = "Newcomer"
                
        elif new_status == 'Denied':
            # Reclaim slot if denied
            opp = app_record.opportunity
            if opp and opp.slots_filled > 0:
                opp.slots_filled -= 1
                
        db.session.commit()
        return jsonify({'success': True, 'message': f'Application status updated to {new_status}.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500
# Run local dev server if executed directly
if __name__ == '__main__':
    app.run(debug=True, port=5000)
