#!/usr/bin/env python3
"""
🏋️‍♂️ Shiba Tales Workout Tracker with Improved Equipment Categorization
- Uses specific equipment types (Barbell, Dumbbell, etc.) instead of vague "Free Weight"
- Enhanced substitution system with equipment category intelligence
- Advanced filtering by equipment category, mobility, and resistance type
- Professional UI with comprehensive exercise information
"""

from flask import Flask, render_template_string, jsonify, request, session, redirect, url_for
from functools import wraps
import json
import os

app = Flask(__name__)
app.secret_key = 'workout_tracker_secret_key_2024'

# Password protection
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'N1ppl3$':
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template_string(LOGIN_TEMPLATE, error="Invalid password")
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/robots.txt')
def robots_txt():
    return """User-agent: *
Disallow: /
"""

# Enhanced Workout Database Class
class UltimateWorkoutDatabase:
    """Ultimate workout database with improved equipment categorization"""
    
    def __init__(self):
        # Load the correct JSON database (main exercises only)
        with open('workout_database.json', 'r') as f:
            self.database = json.load(f)
        
        print(f"🚀 Loaded Ultimate Workout Database:")
        print(f"   • Muscles: {len(self.database.get('muscles', {}))}")
        print(f"   • Equipment: {len(self.database.get('equipment', {}))}")
        print(f"   • Exercises: {len(self.database.get('exercises', []))}")
    
    def get_exercise_by_id(self, exercise_id):
        """Get exercise by ID - returns first match for duplicate IDs"""
        if isinstance(self.database['exercises'], dict):
            return self.database['exercises'].get(exercise_id)
        else:
            for exercise in self.database['exercises']:
                if exercise['id'] == exercise_id:
                    return exercise
        return None
    
    def get_all_exercises(self):
        """Get all exercises"""
        if isinstance(self.database['exercises'], list):
            return self.database['exercises']
        elif isinstance(self.database['exercises'], dict):
            return list(self.database['exercises'].values())
        return []
    
    def get_exercises_for_workout(self, week, workout_type):
        """Get exercises for a specific week and workout type"""
        exercises = []
        all_exercises = self.get_all_exercises()
        for exercise in all_exercises:
            if exercise.get('week') == week and exercise.get('workout_type') == workout_type:
                exercises.append(exercise)
        return exercises
    
    def get_workout_types_by_week(self, week):
        """Get available workout types for a specific week"""
        workout_types = set()
        all_exercises = self.get_all_exercises()
        for exercise in all_exercises:
            if exercise.get('week') == week:
                workout_types.add(exercise.get('workout_type'))
        return sorted(list(workout_types))
    
    def get_equipment_categories(self):
        """Get all equipment categories for filtering"""
        categories = set()
        for equipment in self.database['equipment'].values():
            categories.add(equipment['category'])
        return sorted(list(categories))
    
    def get_equipment_by_category(self, category):
        """Get equipment by category"""
        equipment_list = []
        for eq_id, equipment in self.database['equipment'].items():
            if equipment['category'] == category:
                equipment_list.append({
                    'id': eq_id,
                    'name': equipment['name'],
                    'subcategory': equipment['subcategory'],
                    'mobility': equipment['mobility'],
                    'resistance_type': equipment['resistance_type']
                })
        return equipment_list
    
    def substitute_exercise(self, original_exercise_id, substitution_exercise_id):
        """
        Substitute an exercise and return the substitution exercise data
        Works with substitution objects that have their own IDs and properties
        """
        # Find the original exercise
        original_exercise = self.get_exercise_by_id(original_exercise_id)
        if not original_exercise:
            return None
        
        # If substitution_exercise_id is the same as original, return original (reset case)
        if substitution_exercise_id == original_exercise_id:
            return original_exercise
        
        # Look for the substitution in the original exercise's substitutions
        for sub in original_exercise.get('substitutions', []):
            if isinstance(sub, dict) and sub.get('id') == substitution_exercise_id:
                # Return the substitution exercise data
                return {
                    'id': sub['id'],
                    'name': sub['name'],
                    'muscle': sub['muscle'],
                    'equipment': sub['equipment'],
                    'body_part': sub['body_part'],
                    'week': original_exercise['week'],
                    'workout_type': original_exercise['workout_type'],
                    'working_sets': original_exercise['working_sets'],
                    'reps': original_exercise['reps'],
                    'rest': original_exercise['rest'],
                    'notes': original_exercise.get('notes', ''),
                    'substitutions': original_exercise['substitutions']  # Keep substitution options
                }
        
        return None
    
    def get_smart_substitutions(self, exercise_id):
        """
        Get smart substitutions based on equipment category and muscle group
        """
        original_exercise = self.get_exercise_by_id(exercise_id)
        if not original_exercise:
            return []
        
        # Get the original substitutions (list of substitution objects)
        original_substitutions = original_exercise.get('substitutions', [])
        
        # Return substitutions directly since they're already in the correct format
        enhanced_substitutions = []
        for sub_obj in original_substitutions:
            if isinstance(sub_obj, dict):
                enhanced_sub = {
                    'id': sub_obj.get('id', ''),
                    'name': sub_obj.get('name', ''),
                    'muscle': sub_obj.get('muscle', ''),
                    'equipment': sub_obj.get('equipment', ''),
                    'equipment_name': sub_obj.get('equipment', ''),
                    'body_part': sub_obj.get('body_part', '')
                }
                enhanced_substitutions.append(enhanced_sub)
        
        return enhanced_substitutions
    
    def generate_comprehensive_tags(self, exercise):
        """Generate comprehensive tags including equipment categories"""
        tags = []
        
        # Muscle tags
        muscle = exercise.get('muscle', '').lower()
        if muscle:
            tags.append(muscle)
        
        # Equipment tags
        equipment = exercise.get('equipment', '').lower()
        if equipment:
            tags.append(equipment.replace(' ', '-'))
        
        # Body part tags
        body_part = exercise.get('body_part', '').lower()
        if body_part:
            tags.append(body_part.replace(' ', '-'))
        
        # Training focus tags
        training_focus = exercise.get('training_focus', '').lower()
        if 'strength' in training_focus:
            tags.append('strength')
        elif 'hypertrophy' in training_focus:
            tags.append('hypertrophy')
        
        # Movement pattern tags based on exercise name
        exercise_name = exercise.get('name', '').lower()
        if any(word in exercise_name for word in ['press', 'push']):
            tags.append('pressing')
        if any(word in exercise_name for word in ['pull', 'row', 'pulldown']):
            tags.append('pulling')
        if any(word in exercise_name for word in ['squat', 'lunge']):
            tags.append('squatting')
        if any(word in exercise_name for word in ['curl']):
            tags.append('curling')
        if any(word in exercise_name for word in ['extension', 'extend']):
            tags.append('extending')
        if any(word in exercise_name for word in ['raise', 'lateral', 'fly', 'flye']):
            tags.append('raising')
        
        return list(set(tags))  # Remove duplicates

# Initialize database
db = UltimateWorkoutDatabase()

def build_enhanced_workout_templates():
    """Build workout templates with enhanced equipment information"""
    templates = {}
    
    # Get all unique weeks
    weeks = set()
    for exercise in db.database['exercises']:
        weeks.add(exercise['week'])
    
    for week in sorted(weeks, key=lambda x: (isinstance(x, str), x)):
        templates[str(week)] = {'days': {}}
        
        # Get workout types for this week
        workout_types = db.get_workout_types_by_week(week)
        
        for workout_type in workout_types:
            exercises = db.get_exercises_for_workout(week, workout_type)
            
            if exercises:
                # Convert to the format expected by the frontend
                formatted_exercises = []
                for exercise in exercises:
                    formatted_exercise = {
                        'id': exercise['id'],
                        'name': exercise['name'],
                        'muscle': exercise['muscle'],
                        'equipment': exercise['equipment'],
                        'body_part': exercise['body_part'],
                        'training_focus': exercise['training_focus'],
                        'reps': exercise['reps'],
                        'early_rpe': exercise['early_rpe'],
                        'last_rpe': exercise['last_rpe'],
                        'warmup_sets': exercise['warmup_sets'],
                        'working_sets': exercise['working_sets'],
                        'rest': exercise['rest'],
                        'notes': exercise.get('notes', ''),
                        'tutorial_url': exercise.get('tutorial_url', ''),
                        'substitutions': exercise.get('substitutions', [])
                    }
                    formatted_exercises.append(formatted_exercise)
                
                templates[str(week)]['days'][workout_type] = {
                    'exercises': formatted_exercises
                }
    
    return templates

# Build enhanced workout templates
# workout_templates = build_enhanced_workout_templates()

def generate_comprehensive_tags(exercise):
    """Generate comprehensive tags for an exercise"""
    tags = []
    
    # Add muscle tag
    if exercise.get('muscle'):
        tags.append(exercise['muscle'])
    
    # Add equipment tag
    if exercise.get('equipment'):
        tags.append(exercise['equipment'])
    
    # Add body part tag
    if exercise.get('body_part'):
        tags.append(exercise['body_part'])
    
    return tags

@app.route('/api/exercises')
@login_required
def get_exercises():
    """API endpoint to get exercises filtered by week and workout_type or all exercises"""
    week = request.args.get('week')
    workout_type = request.args.get('workout_type')
    
    if week and workout_type:
        # Filter exercises by week and workout_type
        exercises = db.get_exercises_for_workout(int(week), workout_type)
    else:
        # Return all exercises (for Exercise Database)
        exercises = db.get_all_exercises()
    
    # Add comprehensive tags for each exercise
    for exercise in exercises:
        exercise['tags'] = generate_comprehensive_tags(exercise)
    
    return jsonify(exercises)

@app.route('/api/exercises/<exercise_id>')
@login_required
def get_exercise_by_id(exercise_id):
    """API endpoint to get a specific exercise by ID"""
    exercise = db.get_exercise_by_id(exercise_id)
    if exercise:
        return jsonify(exercise)
    else:
        return jsonify({'error': 'Exercise not found'}), 404

@app.route('/api/substitutions/<exercise_id>')
@login_required
def get_substitutions(exercise_id):
    """API endpoint to get smart substitutions for an exercise"""
    substitutions = db.get_smart_substitutions(exercise_id)
    return jsonify(substitutions)

@app.route('/api/substitute', methods=['POST'])
@login_required
def substitute_exercise():
    """API endpoint to substitute an exercise with enhanced equipment info"""
    data = request.get_json()
    original_id = data.get('original_id')
    substitution_id = data.get('substitution_id')
    
    if not original_id or not substitution_id:
        return jsonify({'error': 'Missing exercise IDs'}), 400
    
    substitution_exercise = db.substitute_exercise(original_id, substitution_id)
    if substitution_exercise:
        return jsonify(substitution_exercise)
    else:
        return jsonify({'error': 'Substitution not found'}), 404

@app.route('/api/equipment-categories')
def get_equipment_categories():
    """API endpoint to get all equipment categories"""
    categories = db.get_equipment_categories()
    return jsonify(categories)

@app.route('/api/equipment/<category>')
def get_equipment_by_category(category):
    """API endpoint to get equipment by category"""
    equipment = db.get_equipment_by_category(category)
    return jsonify(equipment)

@app.route('/api/workout-types/<int:week>')
def get_workout_types(week):
    """API endpoint to get workout types for a specific week"""
    workout_types = db.get_workout_types_by_week(week)
    # Return the full workout type names with focus keywords
    return jsonify(workout_types)

# Progress tracking and workout history endpoints
@app.route('/api/workout-history', methods=['POST'])
def save_workout_session():
    """Save a completed workout session"""
    data = request.get_json()
    
    # Basic validation
    required_fields = ['week', 'workout_type', 'date', 'exercises']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # In a real application, this would save to a database
    # For now, we'll return success to indicate the endpoint works
    return jsonify({'success': True, 'message': 'Workout session saved'})

@app.route('/api/workout-history')
def get_workout_history():
    """Get workout history for progress tracking"""
    # In a real application, this would query a database
    # For now, return empty history
    return jsonify([])

@app.route('/api/progress/<exercise_name>')
def get_exercise_progress(exercise_name):
    """Get progress data for a specific exercise"""
    # In a real application, this would analyze historical data
    # For now, return empty progress data
    return jsonify({
        'exercise': exercise_name,
        'sessions': [],
        'max_weight': 0,
        'total_volume': 0,
        'avg_rpe': 0
    })

@app.route('/api/export-data')
def export_workout_data():
    """Export all workout data as JSON"""
    # This would typically export from a database
    # For now, return a template for the export format
    return jsonify({
        'export_date': datetime.now().isoformat(),
        'workout_sessions': [],
        'exercise_progress': {},
        'user_preferences': {}
    })

# Enhanced HTML Template with improved equipment categorization
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ultimate Workout Tracker - Login</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .login-container {
            background: white;
            padding: 3rem;
            border-radius: 16px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 400px;
            text-align: center;
            margin: 0 1rem; /* Add horizontal margin for mobile */
        }
        
        @media (max-width: 768px) {
            .login-container {
                padding: 2rem 1rem; /* Reduce padding but ensure good spacing */
                margin: 0 1.5rem; /* More margin on mobile */
                max-width: none; /* Allow container to use available width */
            }
        }
        
        .login-title {
            font-size: 2rem;
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 0.5rem;
        }
        
        .login-subtitle {
            color: #718096;
            margin-bottom: 2rem;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
            text-align: left;
        }
        
        .form-label {
            display: block;
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 0.5rem;
        }
        
        .form-input {
            width: 100%;
            padding: 0.75rem 1rem;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 16px; /* Prevent mobile zoom */
            transition: border-color 0.2s;
        }
        
        .form-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .login-btn {
            width: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .login-btn:hover {
            transform: translateY(-2px);
        }
        
        .error-message {
            background: #fed7d7;
            color: #c53030;
            padding: 0.75rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            font-size: 0.875rem;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h1 class="login-title">🏋️‍♂️ Ultimate Workout Tracker</h1>
        <p class="login-subtitle">Enter password to access your workout tracker</p>
        
        {% if error %}
        <div class="error-message">{{ error }}</div>
        {% endif %}
        
        <form method="POST">
            <div class="form-group">
                <label for="password" class="form-label">Password</label>
                <input type="password" id="password" name="password" class="form-input" required>
            </div>
            <button type="submit" class="login-btn">Access Tracker</button>
        </form>
    </div>
</body>
</html>
'''

HTML_TEMPLATE = r'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏋️‍♂️ Shiba Tales Workout Tracker</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #2d3748;
            line-height: 1.6;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.98);
            backdrop-filter: blur(10px);
            padding: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 1.25rem;
            font-weight: 700;
            color: #2d3748;
        }
        
        .nav {
            display: flex;
            gap: 0.5rem;
            flex-wrap: nowrap;
            align-items: center;
        }
        
        .nav-btn {
            padding: 0.75rem 1.25rem;
            border: none;
            border-radius: 8px;
            background: #4299e1;
            color: white;
            text-decoration: none;
            font-weight: 500;
            font-size: 0.875rem;
            transition: all 0.2s ease;
            cursor: pointer;
        }
        
        .nav-btn:hover {
            background: #3182ce;
            transform: translateY(-1px);
        }
        
        .nav-btn.active {
            background: #2b6cb0;
            box-shadow: 0 4px 12px rgba(43, 108, 176, 0.4);
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem 1.5rem;
        }
        
        .page {
            display: none;
        }
        
        .page.active {
            display: block;
        }
        
        .workout-controls {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        
        .controls-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            align-items: end;
        }
        
        .control-group {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .control-group label {
            font-weight: 600;
            color: #4a5568;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .control-group select {
            padding: 0.75rem 1rem;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            background: white;
            font-size: 1rem;
            transition: all 0.2s ease;
        }
        
        .control-group select:focus {
            outline: none;
            border-color: #4299e1;
            box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
        }
        
        .workout-header {
            background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
            color: white;
            padding: 2rem;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(66, 153, 225, 0.3);
        }
        
        .workout-header h2 {
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
        }
        
        .workout-header p {
            font-size: 1.125rem;
            opacity: 0.9;
        }
        
        .exercise-container {
            background: white;
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 2rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border: 1px solid #e2e8f0;
        }
        
        .exercise-container > .exercise-header {
            background: #f8f9fa;
            margin: -1.5rem -1.5rem 2rem -1.5rem;
            padding: 1rem;
            border-radius: 12px 12px 0 0;
            border-bottom: 2px solid #e2e8f0;
        }
        
        .exercise-container .calculator-section,
        .exercise-container .sets-section {
            background: #fafbfc;
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1.5rem;
            border: 1px solid #e2e8f0;
        }
        
        .exercise-card {
            background: white;
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border: 1px solid #e2e8f0;
            transition: all 0.3s ease;
        }
        
        .exercise-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }
        
           .exercise-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1rem;
            flex-wrap: wrap;
            gap: 1rem;
        }
        
        .exercise-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: #2d3748;
            margin: 0;
            flex: 1;
            min-width: 200px;
        }
        
        .exercise-meta {
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
            align-items: center;
        }
        
        .meta-tag {
            background: #edf2f7;
            color: #4a5568;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        .meta-tag.muscle {
            background: #e6fffa;
            color: #234e52;
        }
        
        .meta-tag.equipment {
            background: #fef5e7;
            color: #744210;
        }
        
        .exercise-actions {
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
        }
        
        .original-badge {
            background: #48bb78;
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: bold;
            margin-right: 0.5rem;
        }
        
        .original-exercise {
            border: 2px solid #48bb78 !important;
            background: #f0fff4 !important;
        }
        
        .modal-actions {
            padding: 1rem;
            border-top: 1px solid #e2e8f0;
            text-align: center;
            margin-top: 1rem;
        }
        
        .btn-reset {
            background: #ed8936;
            color: white;
            border: none;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s ease;
        }
        
        .btn-reset:hover {
            background: #dd6b20;
            transform: translateY(-1px);
        }
        
            .btn {
            padding: 0.75rem 1rem;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.875rem;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }
        
        .btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        .substitute-btn {
            background: linear-gradient(135deg, #ff7b54 0%, #ff6b35 100%);
            color: white;
            padding: 0.75rem 1rem;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.875rem;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }
        
        .substitute-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(255, 123, 84, 0.3);
        }
        
        .tutorial-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 0.75rem 1rem;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.875rem;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }
        
        .tutorial-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        
        .btn-add-set {
            background: linear-gradient(135deg, #4299e1, #3182ce);
            color: white;
            margin-bottom: 1rem;
        }
        
        .btn-add-set:hover {
            background: linear-gradient(135deg, #3182ce, #2c5282);
        }
        
        .btn-log-warmup, .btn-log-working {
            background: linear-gradient(135deg, #48bb78, #38a169);
            color: white;
            font-size: 0.75rem;
            padding: 0.5rem 1rem;
        }
        
        .btn-log-warmup:hover, .btn-log-working:hover {
            background: linear-gradient(135deg, #38a169, #2f855a);
        }
        
        .btn-remove {
            background: linear-gradient(135deg, #f56565, #e53e3e);
            color: white;
            padding: 0.5rem 1rem;
            font-size: 0.75rem;
        }
        
        .btn-remove:hover {
            background: linear-gradient(135deg, #e53e3e, #c53030);
        }
        
        /* Input field improvements */
        input[type="number"], input[type="text"] {
            padding: 0.75rem 1rem;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 16px; /* Prevent mobile zoom */
            transition: all 0.2s ease;
            background: white;
        }
        
        input[type="number"]:focus, input[type="text"]:focus {
            outline: none;
            border-color: #4299e1;
            box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
        }
        
        /* Set container improvements */
        .set-item {
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 1rem;
            flex-wrap: wrap;
        }
        
        .set-item:hover {
            background: #edf2f7;
        }
        
        select {
            padding: 0.75rem 2.5rem 0.75rem 1rem;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 1rem;
            background: white;
            appearance: none;
            background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
            background-position: right 0.75rem center;
            background-repeat: no-repeat;
            background-size: 1.5em 1.5em;
        }
        
        .set-row {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 0.75rem;
            padding: 0.75rem;
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }
        
        .set-inputs {
            display: flex;
            gap: 0.5rem;
            flex: 1;
            align-items: center;
            max-width: 300px;
        }
        
        .set-inputs input {
            width: 100px;
            min-width: 80px;
            padding: 0.5rem;
            border: 1px solid #cbd5e0;
            border-radius: 4px;
            font-size: 0.9rem;
            text-align: center;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }
        
        .btn-secondary {
            background: #ed8936;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #dd6b20;
        }
        
        .btn-danger {
            background: #e53e3e;
            color: white;
        }
        
        .btn-danger:hover {
            background: #c53030;
        }
        
        .exercise-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .stat-item {
            text-align: center;
            padding: 1rem;
            background: #f7fafc;
            border-radius: 8px;
        }
        
        .stat-label {
            font-size: 0.75rem;
            font-weight: 600;
            color: #718096;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.25rem;
        }
        
        .stat-value {
            font-size: 1.125rem;
            font-weight: 700;
            color: #2d3748;
            line-height: 1.2;
        }
        
        .equipment-details {
            background: #edf2f7;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
        }
        
        .equipment-details h4 {
            color: #4a5568;
            margin-bottom: 0.5rem;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .equipment-tags {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }
        
        .equipment-tag {
            background: #4299e1;
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        
        .equipment-tag.category {
            background: #48bb78;
        }
        
        .equipment-tag.mobility {
            background: #ed8936;
        }
        
        .equipment-tag.resistance {
            background: #9f7aea;
        }
        
        .exercise-notes {
            background: #edf2f7;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
            font-style: italic;
            color: #4a5568;
        }
        
        /* Modal Styles */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
            backdrop-filter: blur(5px);
        }
        
        .modal.active {
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .modal-content {
            background: white;
            padding: 2rem;
            border-radius: 16px;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }
        
        .modal-header h3 {
            font-size: 1.25rem;
            font-weight: 700;
            color: #2d3748;
        }
        
        .close-btn {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #718096;
            padding: 0.25rem;
        }
        
        .close-btn:hover {
            color: #2d3748;
        }
        
        .substitution-list {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .substitution-item {
            padding: 1rem;
            background: #f7fafc;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            border: 2px solid transparent;
        }
        
        .substitution-item:hover {
            background: #edf2f7;
            border-color: #4299e1;
            transform: translateX(4px);
        }
        
        .substitution-item.selected {
            background: #e6fffa;
            border-color: #38b2ac;
            box-shadow: 0 0 0 3px rgba(56, 178, 172, 0.1);
        }
        
        .substitution-item.selected:hover {
            background: #b2f5ea;
            border-color: #319795;
        }
        
        .substitution-name {
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 0.5rem;
        }
        
        .substitution-details {
            font-size: 0.875rem;
            color: #718096;
            margin-bottom: 0.5rem;
        }
        
        .substitution-equipment {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin-top: 0.5rem;
        }
        
        .substitution-equipment .equipment-tag {
            font-size: 0.625rem;
        }
        
        /* Success message */
        .success-message {
            background: #48bb78;
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            text-align: center;
            display: none;
        }
        
        .success-message.show {
            display: block;
            animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Workout Tracking Styles */
        .calculator-section, .sets-section {
            margin-top: 1.5rem;
            padding: 1rem;
            background: #f8fafc;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }
        
        .section-title {
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 0.75rem;
            font-size: 0.9rem;
        }
        
        .calculator-grid {
            display: flex;
            gap: 1rem;
            align-items: end;
            flex-wrap: wrap;
        }
        
        .input-group {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }
        
        .input-group label {
            font-size: 0.8rem;
            font-weight: 500;
            color: #4a5568;
        }
        
        .input-group input {
            padding: 0.5rem;
            border: 1px solid #cbd5e0;
            border-radius: 4px;
            font-size: 16px; /* Prevent mobile zoom */
            width: 120px;
        }
        
        .btn-calculate {
            background: #48bb78;
            color: white;
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 4px;
            font-size: 0.9rem;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .btn-calculate:hover {
            background: #38a169;
        }
        
        .btn-add-set {
            background: #4299e1;
            color: white;
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 4px;
            font-size: 0.9rem;
            cursor: pointer;
            margin-bottom: 1rem;
            transition: background 0.2s;
        }
        
        .btn-add-set:hover {
            background: #3182ce;
        }
        
        .warmup-results {
            margin-top: 1rem;
            padding: 0.75rem;
            background: white;
            border-radius: 4px;
            border: 1px solid #e2e8f0;
        }
        
        .warmup-set {
            display: flex;
            justify-content: space-between;
            padding: 0.25rem 0;
            font-size: 0.9rem;
        }
        
        .warmup-set:not(:last-child) {
            border-bottom: 1px solid #f1f5f9;
        }
        
        .sets-container {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .set-row {
            display: grid;
            grid-template-columns: 60px 110px 110px 45px;
            gap: 0.4rem;
            align-items: center;
            padding: 0.75rem;
            background: white;
            border-radius: 4px;
            border: 1px solid #e2e8f0;
            max-width: 100%;
            overflow: hidden;
        }
        
        .set-number {
            font-weight: 600;
            color: #4a5568;
            font-size: 0.9rem;
            min-width: 50px;
        }
        
        .set-input {
            padding: 0.5rem;
            border: 1px solid #cbd5e0;
            border-radius: 4px;
            font-size: 16px; /* Prevent mobile zoom */
            text-align: center;
        }
        
        .set-inputs {
            display: contents; /* Make inputs part of the parent grid */
        }
        
        .set-inputs input {
            padding: 0.5rem;
            border: 1px solid #cbd5e0;
            border-radius: 4px;
            font-size: 16px; /* Prevent mobile zoom */
            text-align: center;
        }
        
        .set-input:focus {
            outline: none;
            border-color: #4299e1;
            box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
        }
        
        .remove-link {
            color: #e53e3e;
            text-decoration: none;
            font-size: 1.1rem;
            font-weight: 500;
            padding: 0.4rem;
            border-radius: 4px;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            min-width: 35px;
            max-width: 35px;
            height: 35px;
            background: #fed7d7;
            border: 1px solid #feb2b2;
            box-sizing: border-box;
        }
        
        .remove-link:hover {
            color: #c53030;
            background: #fbb6ce;
            border-color: #f687b3;
            text-decoration: none;
            transform: scale(1.05);
        }
        
        .btn-remove {
            background: #e53e3e;
            color: white;
            padding: 0.4rem 0.8rem;
            border: none;
            border-radius: 4px;
            font-size: 0.8rem;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .btn-remove:hover {
            background: #c53030;
        }
        
        .rest-timer {
            margin-top: 1rem;
            padding: 1rem;
            background: white;
            border-radius: 4px;
            border: 1px solid #e2e8f0;
            text-align: left;
        }
        
        .rest-status {
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 0.5rem;
        }
        
        .btn-rest {
            background: #ed8936;
            color: white;
            padding: 0.75rem 1rem;
            border: none;
            border-radius: 4px;
            font-size: 0.9rem;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .btn-rest:hover {
            background: #dd6b20;
        }
        
        .timer-display {
            font-size: 2rem;
            font-weight: bold;
            color: #ed8936;
            margin-top: 0.5rem;
            text-align: left; /* Ensure left alignment */
        }
        
        .timer-presets {
            display: flex !important;
            gap: 1rem !important;
            margin-top: 0.5rem;
            flex-wrap: wrap;
            justify-content: flex-start;
            align-items: center;
        }
        
        /* Force flex display even when set via JavaScript */
        .timer-presets[style*="display: block"] {
            display: flex !important;
        }
        
        /* Ensure rest timer container maintains consistent layout */
        .rest-timer {
            display: flex;
            flex-direction: column;
            align-items: flex-start; /* Left align all children */
            margin-top: 1rem;
        }
        
        /* Ensure timer display and stop button are left aligned */
        .rest-timer .timer-display,
        .rest-timer .btn-stop {
            align-self: flex-start; /* Force left alignment */
        }
        
        .btn-preset {
            background: #4299e1;
            color: white;
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 4px;
            font-size: 0.8rem;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .btn-preset:hover {
            background: #3182ce;
        }
        
        .btn-stop {
            background: #e53e3e;
            color: white;
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 4px;
            font-size: 0.875rem;
            cursor: pointer;
            transition: background 0.2s;
            margin-top: 0.5rem;
            display: inline-block;
            text-align: center;
            float: left; /* Force left alignment */
            clear: both; /* Clear any floats */
        }
        
        .btn-stop:hover {
            background: #c53030;
        }
        
        .btn-log-warmup, .btn-log-working {
            background: #38a169;
            color: white;
            padding: 0.25rem 0.5rem;
            border: none;
            border-radius: 4px;
            font-size: 0.8rem;
            cursor: pointer;
            margin-left: 0.5rem;
            transition: background 0.2s;
        }
        
        .btn-log-warmup:hover, .btn-log-working:hover {
            background: #2f855a;
        }
        
        .working-set-suggestion {
            margin-top: 1rem;
            padding: 0.75rem;
            background: #f7fafc;
            border-radius: 4px;
            border: 1px solid #e2e8f0;
        }
        
        .suggestion-title {
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 0.5rem;
        }
        
        .suggestion-details {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        /* Progress Page Styles */
        .progress-controls {
            display: flex;
            gap: 2rem;
            margin-bottom: 2rem;
            align-items: end;
            flex-wrap: wrap;
        }
        
        .progress-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.95);
            padding: 1rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .stat-card h3 {
            font-size: 0.9rem;
            color: #4a5568;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: #2d3748;
        }
        
        #exercise-progress-chart {
            background: rgba(255, 255, 255, 0.95);
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            min-height: 300px;
        }
        
        .progress-sessions {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .session-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 1rem;
        }
        
        .session-header {
            margin-bottom: 0.75rem;
            color: #2d3748;
        }
        
        .session-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 1rem;
            margin-bottom: 0.75rem;
        }
        
        .session-stat {
            display: flex;
            justify-content: space-between;
            font-size: 0.9rem;
        }
        
        .session-stat span:first-child {
            color: #4a5568;
        }
        
        .session-stat span:last-child {
            font-weight: 600;
            color: #2d3748;
        }
        
        .session-sets {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        
        .set-badge {
            background: #4299e1;
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 500;
        }

        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }
            
            .controls-grid {
                grid-template-columns: 1fr;
            }
            
            .exercise-header {
                flex-direction: column;
                align-items: flex-start;
            }
            
            .exercise-stats {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .calculator-grid {
                flex-direction: column;
                align-items: stretch;
            }
            
            .input-group input {
                width: 100%;
            }
            
            .set-row {
                grid-template-columns: 45px 75px 75px 35px;
                gap: 0.2rem;
                padding: 0.4rem;
                max-width: 100%;
                overflow: hidden;
            }
            
            .set-inputs {
                display: contents; /* Make inputs part of the grid */
            }
            
            .set-inputs input {
                font-size: 16px; /* Prevent mobile zoom */
                padding: 0.3rem;
                min-width: 0; /* Allow inputs to shrink */
                width: 100%;
            }
            
            .remove-set {
                font-size: 14px !important;
                padding: 0.2rem 0.4rem !important;
                min-width: 30px !important;
                width: 30px !important;
            }
            
            .remove-link {
                padding: 0.25rem;
                font-size: 0.9rem;
                min-width: 30px;
                max-width: 30px;
                height: 30px;
                white-space: nowrap;
            }
            
            /* Expandable Exercise Cards */
        .exercise-card {
            transition: all 0.3s ease;
            background: white;
            border-radius: 12px;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .exercise-card.collapsed .exercise-content {
            display: none !important;
        }
        
        .exercise-card.collapsed .exercise-header {
            cursor: pointer;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 0;
        }
        
        .exercise-card.collapsed.completed .exercise-header {
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        }
        
        .exercise-card.collapsed .exercise-header:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        }
        
        .exercise-card.collapsed.completed .exercise-header:hover {
            box-shadow: 0 8px 25px rgba(72, 187, 120, 0.3);
        }
        
        .exercise-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: nowrap;
        }
        
        .exercise-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: white;
            flex: 1;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .completion-status {
            font-size: 1.5rem;
            margin-right: 0.5rem;
        }
        
        .expand-icon {
            font-size: 1.5rem;
            color: white;
            transition: transform 0.3s ease;
        }
        
        .exercise-card:not(.collapsed) .expand-icon {
            transform: rotate(180deg);
        }
        
        .exercise-card:not(.collapsed) .exercise-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px 12px 0 0;
            padding: 1rem;
            margin-bottom: 0;
        }
        
        .exercise-card:not(.collapse        .exercise-content {
            padding: 0.5rem;
            border-radius: 0 0 12px 12px;
        }    
        .completion-checkbox-container {
            margin-top: 1rem;
            padding: 1rem;
            border-top: 2px solid #e2e8f0;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .completion-checkbox {
            width: 20px;
            height: 20px;
            cursor: pointer;
        }
        
        .completion-label {
            font-weight: 600;
            color: #2d3748;
            cursor: pointer;
        }ments */
            .modal-content {
                width: 95%;
                max-height: 90vh;
                margin: 1rem;
                padding: 1rem;
            }
            
            .modal-header {
                margin-bottom: 1rem;
            }
            
            .modal-header h3 {
                font-size: 1.1rem;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="logo">
                🏋️‍♂️ Shiba Tales Workout Tracker
            </div>
            <nav class="nav">
                <div id="online-status" style="
                    background: rgba(0,0,0,0.8);
                    color: white;
                    padding: 8px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: bold;
                    margin-right: 1rem;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    white-space: nowrap;
                ">🟢 Online</div>
                <a href="#" class="nav-btn active" onclick="showPage('workout')">Workout</a>
                <a href="#" class="nav-btn" onclick="showPage('database')">Exercise DB</a>
            </nav>
        </div>
    </div>

    <div class="container">
        <!-- Workout Page -->
        <div id="workout-page" class="page active">
            <div class="workout-controls">
                <div class="controls-grid">
                    <div class="control-group">
                        <label for="week-select">Training Week</label>
                        <select id="week-select" onchange="updateWorkout()">
                            {% for i in range(1, 13) %}
                            <option value="{{ i }}">Week {{ i }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="control-group">
                        <label for="day-select">Workout Type</label>
                        <select id="day-select" onchange="updateWorkout()">
                            <!-- Options will be populated dynamically -->
                        </select>
                    </div>
                </div>
            </div>
            
            <div id="workout-content">
                <!-- Workout content will be populated by JavaScript -->
            </div>
        </div>

        <!-- Exercise Database Page -->
        <div id="database-page" class="page">
            <!-- Database content will be added here -->
        </div>
    </div>

    <!-- Enhanced Substitution Modal -->
    <div id="substitution-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Smart Exercise Substitutions</h3>
                <button class="close-btn" onclick="closeModal('substitution-modal')">&times;</button>
            </div>
            <div class="success-message" id="substitution-success">
                Exercise substituted successfully! Equipment and details updated.
            </div>
            <div id="substitution-list" class="substitution-list">
                <!-- Substitutions will be populated by JavaScript -->
            </div>
        </div>
    </div>

    <script>
        // Global variables
        const workoutTemplates = {};
        let currentExerciseId = null;
        let workoutData = {};
        let cachedWorkoutData = null; // Store all workout data for offline use
        let restTimers = {};

        // Load workout data from localStorage
        function loadWorkoutData() {
            try {
                const saved = localStorage.getItem('workoutData');
                if (saved) {
                    workoutData = JSON.parse(saved);
                    console.log('✅ Workout data loaded from localStorage:', Object.keys(workoutData).length, 'workouts');
                } else {
                    workoutData = {};
                    console.log('ℹ️ No saved workout data found, starting fresh');
                }
            } catch (error) {
                console.error('❌ Error loading workout data:', error);
                workoutData = {};
            }
        }

        // Save workout data to localStorage
        function saveWorkoutData() {
            try {
                localStorage.setItem('workoutData', JSON.stringify(workoutData));
                console.log('✅ Workout data saved to localStorage:', Object.keys(workoutData).length, 'workouts');
            } catch (error) {
                console.error('❌ Error saving workout data:', error);
            }
        }

        // Load saved sets when displaying workout
        function loadSavedSets(exerciseId, workoutKey) {
            if (workoutData[workoutKey] && workoutData[workoutKey].sets) {
                const setsContainer = document.getElementById(`sets-container-${exerciseId}`);
                if (setsContainer) {
                    setsContainer.innerHTML = generateSetsHTML(workoutData[workoutKey].sets, exerciseId, workoutKey);
                }
            }
        }

        // Initialize the application
        document.addEventListener('DOMContentLoaded', function() {
            // Load workout data first
            loadWorkoutData();
            
            // Set default week to 1 (now that all weeks have data)
            document.getElementById('week-select').value = '1';
            updateWorkoutTypes();
            updateWorkout();
            loadExerciseDatabase();
        });

        // Page navigation
        function showPage(pageId) {
            // Hide all pages
            document.querySelectorAll('.page').forEach(page => {
                page.classList.remove('active');
            });
            
            // Remove active class from all nav buttons
            document.querySelectorAll('.nav-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Show selected page
            document.getElementById(pageId + '-page').classList.add('active');
            
            // Add active class to clicked nav button
            event.target.classList.add('active');
            
            // Load page-specific content
            if (pageId === 'database') {
                loadExerciseDatabase();
            }
        }

        // Exercise Database functionality
        async function loadExerciseDatabase() {
            try {
                const response = await fetch('/api/exercises', {
                    credentials: 'same-origin'
                });
                
                if (!response.ok) {
                    throw new Error('Failed to load exercises');
                }
                
                const exercises = await response.json();
                
                // Filter to get only unique exercises by name
                const uniqueExercises = [];
                const seenNames = new Set();
                
                exercises.forEach(exercise => {
                    if (!seenNames.has(exercise.name)) {
                        seenNames.add(exercise.name);
                        uniqueExercises.push(exercise);
                    }
                });
                
                console.log(`📊 Exercise Database: Showing ${uniqueExercises.length} unique exercises (filtered from ${exercises.length} total)`);
            
            const databasePage = document.getElementById('database-page');
                
                let html = `
                    <div class="workout-controls">
                        <div class="controls-grid">
                            <div class="control-group">
                                <label>Search Exercises</label>
                                <input type="text" id="exercise-search" placeholder="Search by name..." 
                                       onkeyup="filterExercises()" style="padding: 0.75rem 1rem; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 1rem;">
                            </div>
                            <div class="control-group">
                                <label>Sort by Name</label>
                                <select id="name-sort" onchange="sortAndFilterExercises()" style="padding: 0.75rem 1rem; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 1rem;">
                                    <option value="">Default Order</option>
                                    <option value="asc">A-Z</option>
                                    <option value="desc">Z-A</option>
                                </select>
                            </div>
                            <div class="control-group">
                                <label>Filter by Muscle Group</label>
                                <select id="muscle-filter" onchange="filterExercises()" style="padding: 0.75rem 1rem; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 1rem;">
                                    <option value="">All Muscles</option>
                                    <option value="Chest">Chest</option>
                                    <option value="Back">Back</option>
                                    <option value="Quadriceps">Quadriceps</option>
                                    <option value="Hamstrings">Hamstrings</option>
                                    <option value="Glutes">Glutes</option>
                                    <option value="Adductors">Adductors</option>
                                    <option value="Calves">Calves</option>
                                    <option value="Biceps">Biceps</option>
                                    <option value="Triceps">Triceps</option>
                                    <option value="Abs">Abs</option>
                                </select>
                            </div>
                            <div class="control-group">
                                <label>Filter by Equipment</label>
                                <select id="equipment-filter" onchange="filterExercises()" style="padding: 0.75rem 1rem; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 1rem;">
                                    <option value="">All Equipment</option>
                                    <option value="Barbell">Barbell</option>
                                    <option value="Dumbbell">Dumbbell</option>
                                    <option value="Cable Machine">Cable Machine</option>
                                    <option value="Weight Machine">Weight Machine</option>
                                    <option value="Bodyweight">Bodyweight</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div id="exercise-results">
                `;
                
                uniqueExercises.forEach((exercise, index) => {
                    html += `
                        <div class="exercise-card exercise-db-item" data-name="${exercise.name.toLowerCase()}" data-equipment="${exercise.equipment}" data-muscle="${exercise.muscle}">
                            <div class="exercise-header">
                                <div>
                                    <h3 class="exercise-title">${exercise.name}</h3>
                                </div>
                            </div>
                            
                            <div class="exercise-stats">
                                <div class="stat-item">
                                    <div class="stat-label">Muscle</div>
                                    <div class="stat-value">${exercise.muscle}</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-label">Equipment</div>
                                    <div class="stat-value">${exercise.equipment}</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-label">Reps</div>
                                    <div class="stat-value">${exercise.reps}</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-label">Sets</div>
                                    <div class="stat-value">${exercise.warmup_sets} + ${exercise.working_sets}</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-label">Rest</div>
                                    <div class="stat-value">${exercise.rest}</div>
                                </div>
                            </div>
                            
                            ${exercise.notes ? `<div class="exercise-notes">
                                <strong>Notes:</strong> ${exercise.notes}
                            </div>` : ''}
                            
                            <div class="exercise-actions">
                                <a href="${exercise.tutorial_url || '#'}" target="_blank" class="btn btn-secondary">
                                    📺 Watch Tutorial
                                </a>
                            </div>
                        </div>
                    `;
                });
                
                html += '</div>';
                databasePage.innerHTML = html;
                
            } catch (error) {
                console.error('Error loading exercise database:', error);
            }
        }

        // Filter exercises in database
        function filterExercises() {
            const searchTerm = document.getElementById('exercise-search').value.toLowerCase();
            const equipmentFilter = document.getElementById('equipment-filter').value;
            const muscleFilter = document.getElementById('muscle-filter').value;
            const exercises = document.querySelectorAll('.exercise-db-item');
            
            exercises.forEach(exercise => {
                const name = exercise.getAttribute('data-name');
                const equipment = exercise.getAttribute('data-equipment');
                const muscle = exercise.getAttribute('data-muscle');
                
                const matchesSearch = name.includes(searchTerm);
                const matchesEquipment = !equipmentFilter || equipment === equipmentFilter;
                const matchesMuscle = !muscleFilter || muscle === muscleFilter;
                
                if (matchesSearch && matchesEquipment && matchesMuscle) {
                    exercise.style.display = 'block';
                } else {
                    exercise.style.display = 'none';
                }
            });
        }

        // Sort and filter exercises
        function sortAndFilterExercises() {
            const sortOrder = document.getElementById('name-sort').value;
            const exerciseResults = document.getElementById('exercise-results');
            const exercises = Array.from(document.querySelectorAll('.exercise-db-item'));
            
            if (sortOrder) {
                exercises.sort((a, b) => {
                    const nameA = a.getAttribute('data-name');
                    const nameB = b.getAttribute('data-name');
                    
                    if (sortOrder === 'asc') {
                        return nameA.localeCompare(nameB);
                    } else if (sortOrder === 'desc') {
                        return nameB.localeCompare(nameA);
                    }
                    return 0;
                });
                
                // Re-append sorted exercises
                exercises.forEach(exercise => {
                    exerciseResults.appendChild(exercise);
                });
            }
            
            // Apply filters after sorting
            filterExercises();
        }

        // Update workout types based on selected week
        async function updateWorkoutTypes(desiredSelection = null) {
            const week = document.getElementById('week-select').value;
            const daySelect = document.getElementById('day-select');
            const currentSelection = desiredSelection || daySelect.value; // Use desired selection if provided
            
            try {
                const response = await fetch(`/api/workout-types/${week}`);
                const workoutTypes = await response.json();
                
                daySelect.innerHTML = '';
                workoutTypes.forEach(type => {
                    const option = document.createElement('option');
                    option.value = type;
                    option.textContent = type;
                    daySelect.appendChild(option);
                });
                
                // Restore previous selection if it exists in the new options
                if (currentSelection && workoutTypes.includes(currentSelection)) {
                    daySelect.value = currentSelection;
                    console.log('🔄 Restored workout type selection:', currentSelection);
                } else {
                    console.log('⚠️ Could not restore workout type:', currentSelection, 'Available:', workoutTypes);
                }
                
                updateWorkout();
            } catch (error) {
                console.error('Error loading workout types:', error);
            }
        }

        // Workout functionality
        async function updateWorkout() {
            const week = document.getElementById('week-select').value;
            const workoutType = document.getElementById('day-select').value;
            
            if (!week || !workoutType) {
                return;
            }
            
            try {
                const response = await fetch(`/api/exercises?week=${week}&workout_type=${encodeURIComponent(workoutType)}`);
                const exercises = await response.json();
                
                if (exercises && exercises.length > 0) {
                    displayWorkout(exercises, week, workoutType);
                } else {
                    document.getElementById('workout-content').innerHTML = '<p>No exercises found for this week and workout type.</p>';
                }
            } catch (error) {
                console.error('Error loading exercises:', error);
                
                // Try to load from cached data if available
                if (typeof cachedWorkoutData !== 'undefined' && cachedWorkoutData) {
                    console.log('🔄 Loading from cached data due to network error');
                    const cachedExercises = cachedWorkoutData.filter(ex => 
                        ex.week == week && ex.workout_type === workoutType
                    );
                    
                    if (cachedExercises.length > 0) {
                        displayWorkout(cachedExercises, week, workoutType);
                        return;
                    }
                }
                
                document.getElementById('workout-content').innerHTML = `
                    <div style="text-align: center; padding: 2rem; color: #666;">
                        <p>Unable to load exercises. Please check your connection and try again.</p>
                        <button onclick="loadWorkout()" style="margin-top: 1rem; padding: 0.5rem 1rem; background: #4299e1; color: white; border: none; border-radius: 8px; cursor: pointer;">Retry</button>
                    </div>
                `;
            }
        }

        function displayWorkout(exercises, week, workoutType) {
            const content = document.getElementById('workout-content');
            
            // Parse the workout type to get focus
            const focus = workoutType.split('(')[1]?.replace(')', '') || '';
            
            let html = ``;
            
            exercises.forEach((exercise, index) => {
                const exerciseId = exercise.id || `ex_${index}`;
                const workoutKey = `${week}-${workoutType}-${exerciseId}`;
                const savedSets = workoutData[workoutKey]?.sets || [];
                const exerciseIndex = index + 1;
                
                html += `
                    <div class="exercise-card collapsed" id="exercise-${exerciseId}" data-exercise-id="${exerciseId}">
                        <div class="exercise-header" onclick="toggleExerciseCard('${exerciseId}')">
                            <div class="exercise-title" style="flex: 1; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-right: 1rem;">${exerciseIndex}. ${exercise.name}</div>
                            <div class="completion-status" id="completion-status-${exerciseId}" style="flex-shrink: 0;"></div>
                            <div class="expand-icon" style="flex-shrink: 0;">▼</div>
                        </div>
                        <div class="exercise-content">
                            <div class="exercise-actions">
                                <button class="substitute-btn" onclick="showSubstitutions('${exerciseId}')">🔄 Substitute</button>
                                <a href="${exercise.tutorial_url}" target="_blank" class="tutorial-btn">📺 Tutorial</a>
                            </div>
                        
                        <div class="exercise-stats">
                            <div class="stat-item">
                                <div class="stat-label">Muscle</div>
                                <div class="stat-value" id="muscle-${exerciseId}">${exercise.muscle}</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-label">Equipment</div>
                                <div class="stat-value" id="equipment-${exerciseId}">${exercise.equipment}</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-label">Lift Type</div>
                                <div class="stat-value">${exercise.body_part}</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-label">Reps</div>
                                <div class="stat-value">${exercise.reps}</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-label">RPE</div>
                                <div class="stat-value">${exercise.early_rpe} → ${exercise.last_rpe}</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-label">Rest</div>
                                <div class="stat-value">${exercise.rest}</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-label">Sets</div>
                                <div class="stat-value">${exercise.warmup_sets} + ${exercise.working_sets}</div>
                            </div>
                        </div>
                        
                        ${exercise.notes ? `<div class="exercise-notes">${exercise.notes}</div>` : ''}
                        
                        <div class="calculator-section">
                            <div class="section-title">Weight Calculator (${exercise.warmup_sets} sets)</div>
                            <div class="calculator-grid">
                                <div class="input-group">
                                    <label for="target-weight-${exerciseId}">Target Weight:</label>
                                    <input type="number" id="target-weight-${exerciseId}" placeholder="Enter weight" step="2.5">
                                </div>
                                <button class="btn btn-calculate" onclick="calculateWarmup('${exerciseId}')">Calculate</button>
                            </div>
                            <div id="warmup-results-${exerciseId}"></div>
                        </div>
                        
                        <div class="sets-section">
                            <div class="section-title">Working Sets (${exercise.working_sets} sets)</div>
                            <button class="btn btn-add-set" onclick="addSet('${workoutKey}', '${exerciseId}')">+ Add Set</button>
                            <div id="sets-container-${exerciseId}" class="sets-container">
                                ${generateSetsHTML(savedSets, exerciseId, workoutKey)}
                            </div>
                            <div class="rest-timer">
                                <div class="rest-status">Rest Timer</div>
                                <div class="timer-presets">
                                    ${generateRestTimerButtons(exercise.rest, exerciseId)}
                                </div>
                                <div id="timer-display-${exerciseId}" class="timer-display" style="display: none;"></div>
                                <button id="stop-timer-${exerciseId}" class="btn btn-stop" onclick="stopRestTimer('${exerciseId}')" style="display: none;">Stop Timer</button>
                            </div>
                        </div>
                        
                        <div class="completion-checkbox-container">
                            <input type="checkbox" id="completion-${exerciseId}" class="completion-checkbox" 
                                   onchange="toggleExerciseCompletion('${exerciseId}', '${workoutKey}')">
                            <label for="completion-${exerciseId}" class="completion-label">Mark as Completed</label>
                        </div>
                        </div>
                    </div>
                `;
            });
            
            content.innerHTML = html;
            
            // Apply stored substitutions after a short delay to ensure DOM is ready
            setTimeout(() => {
                applyStoredSubstitutions();
                // Restore the previously open card
                restoreOpenCard();
                // Apply completion status
                applyCompletionStatus();
            }, 100);
        }
        
        // Global variable to track modal close timeout
        let modalCloseTimeout = null;
        
        // Expandable exercise cards functionality
        function toggleExerciseCard(exerciseId) {
            const card = document.getElementById(`exercise-${exerciseId}`);
            const isCollapsed = card.classList.contains('collapsed');
            
            // Close all other cards first
            document.querySelectorAll('.exercise-card').forEach(otherCard => {
                if (otherCard.id !== `exercise-${exerciseId}`) {
                    otherCard.classList.add('collapsed');
                }
            });
            
            // Toggle current card
            if (isCollapsed) {
                card.classList.remove('collapsed');
                // Save the open card position to cookie
                const cardIndex = Array.from(document.querySelectorAll('.exercise-card')).indexOf(card);
                setCookie('openExerciseCard', cardIndex, 1); // 1 day expiry
            } else {
                card.classList.add('collapsed');
                // Clear the cookie when closing
                setCookie('openExerciseCard', '', -1);
            }
        }
        
        // Cookie management functions
        function setCookie(name, value, days) {
            const expires = new Date();
            expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
            document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/`;
        }
        
        function getCookie(name) {
            const nameEQ = name + "=";
            const ca = document.cookie.split(';');
            for (let i = 0; i < ca.length; i++) {
                let c = ca[i];
                while (c.charAt(0) === ' ') c = c.substring(1, c.length);
                if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
            }
            return null;
        }
        
        // Restore open card from cookie
        function restoreOpenCard() {
            const openCardIndex = getCookie('openExerciseCard');
            const cards = document.querySelectorAll('.exercise-card');
            
            // First, ensure all cards are collapsed
            cards.forEach(card => {
                card.classList.add('collapsed');
            });
            
            // Then open only the saved card if it exists
            if (openCardIndex !== null && openCardIndex !== '' && cards[openCardIndex]) {
                cards[openCardIndex].classList.remove('collapsed');
            }
        }
        
        // Close all cards when week or workout type changes
        function closeAllCards() {
            setCookie('openExerciseCard', '', -1);
        }
        
        // Exercise completion tracking
        function toggleExerciseCompletion(exerciseId, workoutKey) {
            const checkbox = document.getElementById(`completion-${exerciseId}`);
            const card = document.getElementById(`exercise-${exerciseId}`);
            const completionStatus = document.getElementById(`completion-status-${exerciseId}`);
            
            const isCompleted = checkbox.checked;
            
            // Update visual state
            if (isCompleted) {
                card.classList.add('completed');
                completionStatus.textContent = '✅';
            } else {
                card.classList.remove('completed');
                completionStatus.textContent = '';
            }
            
            // Save completion status to localStorage
            saveExerciseCompletion(workoutKey, exerciseId, isCompleted);
        }
        
        function saveExerciseCompletion(workoutKey, exerciseId, isCompleted) {
            let completionData = JSON.parse(localStorage.getItem('exerciseCompletions') || '{}');
            const completionKey = `${workoutKey}-${exerciseId}`;
            
            if (isCompleted) {
                completionData[completionKey] = {
                    completed: true,
                    timestamp: new Date().toISOString()
                };
            } else {
                delete completionData[completionKey];
            }
            
            localStorage.setItem('exerciseCompletions', JSON.stringify(completionData));
            console.log(`💾 Saved completion status for ${exerciseId}: ${isCompleted}`);
        }
        
        function loadExerciseCompletion(workoutKey, exerciseId) {
            const completionData = JSON.parse(localStorage.getItem('exerciseCompletions') || '{}');
            const completionKey = `${workoutKey}-${exerciseId}`;
            return completionData[completionKey]?.completed || false;
        }
        
        function applyCompletionStatus() {
            const week = document.getElementById('week-select').value;
            const workoutType = document.getElementById('day-select').value;
            
            document.querySelectorAll('.exercise-card').forEach(card => {
                const exerciseId = card.getAttribute('data-exercise-id');
                const workoutKey = `${week}-${workoutType}-${exerciseId}`;
                const isCompleted = loadExerciseCompletion(workoutKey, exerciseId);
                
                const checkbox = document.getElementById(`completion-${exerciseId}`);
                const completionStatus = document.getElementById(`completion-status-${exerciseId}`);
                
                if (checkbox) {
                    checkbox.checked = isCompleted;
                    
                    if (isCompleted) {
                        card.classList.add('completed');
                        completionStatus.textContent = '✅';
                    } else {
                        card.classList.remove('completed');
                        completionStatus.textContent = '';
                    }
                }
            });
        }
        
        // Exercise substitution functionality
        async function showSubstitutions(exerciseId) {
            // Clear any existing modal close timeout
            if (modalCloseTimeout) {
                clearTimeout(modalCloseTimeout);
                modalCloseTimeout = null;
            }
            try {
                const response = await fetch(`/api/substitutions/${exerciseId}`, {
                    credentials: 'same-origin'
                });
                
                if (!response.ok) {
                    throw new Error('Failed to load substitutions');
                }
                
                const substitutions = await response.json();
                
                const modal = document.getElementById('substitution-modal');
                const list = document.getElementById('substitution-list');
                
                if (substitutions.length === 0) {
                    list.innerHTML = '<p style="text-align: center; color: #718096;">No substitutions available for this exercise.</p>';
                } else {
                    // Get current selection to highlight it
                    const currentSubstitution = getStoredSubstitution(exerciseId);
                    
                    // Add original exercise option first
                    const originalExercise = await getOriginalExercise(exerciseId);
                    let html = '';
                    
                    if (originalExercise) {
                        const isCurrentlyOriginal = !currentSubstitution || currentSubstitution === originalExercise.id;
                        html += `
                            <div class="substitution-item original-exercise ${isCurrentlyOriginal ? 'selected' : ''}" onclick="selectSubstitution('${exerciseId}', '${originalExercise.id}', true)">
                                <div class="substitution-name">
                                    <span class="original-badge">ORIGINAL</span>
                                    ${originalExercise.name}
                                </div>
                                <div class="substitution-details">Muscle: ${originalExercise.muscle}</div>
                                <div class="substitution-equipment">
                                    <span class="equipment-tag">${originalExercise.equipment}</span>
                                </div>
                            </div>
                        `;
                    }
                    
                    // Add substitution options
                    html += substitutions.map(sub => {
                        const isCurrentlySelected = currentSubstitution === sub.id;
                        return `
                            <div class="substitution-item ${isCurrentlySelected ? 'selected' : ''}" onclick="selectSubstitution('${exerciseId}', '${sub.id}')">
                                <div class="substitution-name">${sub.name}</div>
                                <div class="substitution-details">Muscle: ${sub.muscle}</div>
                                <div class="substitution-equipment">
                                    <span class="equipment-tag">${sub.equipment_name}</span>
                                </div>
                            </div>
                        `;
                    }).join('');
                    
                    // Add reset button
                    html += `
                        <div class="modal-actions">
                            <button class="btn btn-reset" onclick="resetToOriginal('${exerciseId}')">
                                🔄 Reset to Original
                            </button>
                        </div>
                    `;
                    
                    list.innerHTML = html;
                }
                
                modal.classList.add('active');
            } catch (error) {
                console.error('Error loading substitutions:', error);
            }
        }

        // Get original exercise data
        async function getOriginalExercise(exerciseId) {
            try {
                const response = await fetch(`/api/exercises/${exerciseId}`);
                if (response.ok) {
                    return await response.json();
                }
            } catch (error) {
                console.error('Error getting original exercise:', error);
            }
            return null;
        }

        // Reset exercise to original
        async function resetToOriginal(exerciseId) {
            const originalExercise = await getOriginalExercise(exerciseId);
            if (originalExercise) {
                await selectSubstitution(exerciseId, originalExercise.id, true);
            }
        }

        async function selectSubstitution(originalId, substitutionId, isReset = false) {
            try {
                const response = await fetch('/api/substitute', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify({
                        original_id: originalId,
                        substitution_id: substitutionId
                    })
                });
                
                const substitutionExercise = await response.json();
                
                if (response.ok) {
                    // Update the exercise card with comprehensive new information
                    updateExerciseCard(originalId, substitutionExercise);
                    
                    // Store substitution in localStorage for persistence
                    storeSubstitution(originalId, substitutionId, isReset);
                    
                    // Show success message
                    const successMsg = document.getElementById('substitution-success');
                    successMsg.classList.add('show');
                    setTimeout(() => {
                        successMsg.classList.remove('show');
                    }, 3000);
                    
                    // Close modal after a short delay
                    modalCloseTimeout = setTimeout(() => {
                        closeModal('substitution-modal');
                        modalCloseTimeout = null;
                    }, 1500);
                } else {
                    alert('Error: ' + substitutionExercise.error);
                }
            } catch (error) {
                console.error('Error substituting exercise:', error);
                alert('Error substituting exercise');
            }
        }

        function updateExerciseCard(exerciseId, newExercise) {
            // Update the exercise title
            const titleElement = document.querySelector(`#exercise-${exerciseId} .exercise-title`);
            if (titleElement) {
                const exerciseNumber = titleElement.textContent.split('.')[0];
                titleElement.textContent = `${exerciseNumber}. ${newExercise.name}`;
            }
            
            // Update muscle
            const muscleElement = document.getElementById(`muscle-${exerciseId}`);
            if (muscleElement) {
                muscleElement.textContent = newExercise.muscle;
            }
            
            // Update equipment (this is the key feature!)
            const equipmentElement = document.getElementById(`equipment-${exerciseId}`);
            if (equipmentElement) {
                equipmentElement.textContent = newExercise.equipment;
            }
            
            // Close modal
            closeModal('substitution-modal');
        }
        
        function closeModal(modalId) {
            // Clear any pending modal close timeout
            if (modalCloseTimeout) {
                clearTimeout(modalCloseTimeout);
                modalCloseTimeout = null;
            }
            document.getElementById(modalId).classList.remove('active');
        }

        // Close modals when clicking outside
        document.addEventListener('click', function(event) {
            if (event.target.classList.contains('modal')) {
                event.target.classList.remove('active');
            }
        });

        // Workout tracking functions
        function generateSetsHTML(sets, exerciseId, workoutKey) {
            let html = '';
            sets.forEach((set, index) => {
                html += `
                    <div class="set-row">
                        <div class="set-number">Set ${index + 1}</div>
                        <div class="set-inputs">
                            <input type="number" placeholder="Weight" value="${set.weight || ''}" 
                                   onchange="updateSet('${workoutKey}', ${index}, 'weight', this.value)">
                            <input type="number" placeholder="Reps" value="${set.reps || ''}" 
                                   onchange="updateSet('${workoutKey}', ${index}, 'reps', this.value)">
                        </div>
                        <a href="#" class="remove-link" onclick="removeSet('${workoutKey}', ${index}, '${exerciseId}'); return false;">×</a>
                    </div>
                `;
            });
            return html;
        }

        // Generate rest timer buttons based on exercise rest time
        function generateRestTimerButtons(restTime, exerciseId) {
            if (!restTime) {
                // Default buttons if no rest time specified
                return `
                    <button class="btn btn-preset" onclick="startRestTimer('${exerciseId}', 60)">1 min</button>
                    <button class="btn btn-preset" onclick="startRestTimer('${exerciseId}', 120)">2 min</button>
                    <button class="btn btn-preset" onclick="startRestTimer('${exerciseId}', 180)">3 min</button>
                `;
            }
            
            // Parse rest time (e.g., "1-2 min", "2-3 min", "3-5 min")
            const restMatch = restTime.match(/(\d+)-(\d+)\s*min/);
            if (restMatch) {
                const minRest = parseInt(restMatch[1]);
                const maxRest = parseInt(restMatch[2]);
                
                let buttons = '';
                for (let i = minRest; i <= maxRest; i++) {
                    buttons += `<button class="btn btn-preset" onclick="startRestTimer('${exerciseId}', ${i * 60})">${i} min</button>`;
                }
                return buttons;
            }
            
            // Single value rest time (e.g., "2 min")
            const singleMatch = restTime.match(/(\d+)\s*min/);
            if (singleMatch) {
                const restMinutes = parseInt(singleMatch[1]);
                return `
                    <button class="btn btn-preset" onclick="startRestTimer('${exerciseId}', ${(restMinutes - 1) * 60})">${restMinutes - 1} min</button>
                    <button class="btn btn-preset" onclick="startRestTimer('${exerciseId}', ${restMinutes * 60})">${restMinutes} min</button>
                    <button class="btn btn-preset" onclick="startRestTimer('${exerciseId}', ${(restMinutes + 1) * 60})">${restMinutes + 1} min</button>
                `;
            }
            
            // Fallback to default
            return `
                <button class="btn btn-preset" onclick="startRestTimer('${exerciseId}', 60)">1 min</button>
                <button class="btn btn-preset" onclick="startRestTimer('${exerciseId}', 120)">2 min</button>
                <button class="btn btn-preset" onclick="startRestTimer('${exerciseId}', 180)">3 min</button>
            `;
        }

        // Calculate warmup sets
        function calculateWarmup(exerciseId) {
            const targetWeight = parseFloat(document.getElementById(`target-weight-${exerciseId}`).value);
            if (!targetWeight) return;
            
            // Round target weight to nearest 5
            const roundedTargetWeight = Math.round(targetWeight / 5) * 5;
            
            const warmupSets = [
                { percentage: 40, reps: 8 },
                { percentage: 60, reps: 5 },
                { percentage: 80, reps: 3 }
            ];
            
            let html = '<div class="warmup-results">';
            warmupSets.forEach((set, index) => {
                const weight = Math.round((roundedTargetWeight * (set.percentage / 100)) / 5) * 5; // Round to nearest 5
                html += `
                    <div class="warmup-set">
                        <span>Warmup Set ${index + 1}:</span>
                        <span>${weight} lbs × ${set.reps} reps (${set.percentage}%)</span>
                        <button class="btn btn-log-warmup" onclick="logWarmupSet('${exerciseId}', ${weight}, ${set.reps})">Log Set</button>
                    </div>
                `;
            });
            
            // Add working set suggestion
            html += `
                <div class="working-set-suggestion">
                    <div class="suggestion-title">Suggested Working Set:</div>
                    <div class="suggestion-details">
                        <span>${roundedTargetWeight} lbs × target reps</span>
                        <button class="btn btn-log-working" onclick="logWorkingSet('${exerciseId}', ${roundedTargetWeight})">Log Working Set</button>
                    </div>
                </div>
            `;
            
            html += '</div>';
            
            document.getElementById(`warmup-results-${exerciseId}`).innerHTML = html;
        }

        // Log warmup set to working sets
        function logWarmupSet(exerciseId, weight, reps) {
            // Find the workout key for this exercise
            const week = document.getElementById('week-select').value;
            const day = document.getElementById('day-select').value;
            const workoutKey = `${week}-${day}-${exerciseId}`;
            
            if (!workoutData[workoutKey]) {
                workoutData[workoutKey] = { sets: [] };
            }
            
            workoutData[workoutKey].sets.push({
                weight: weight.toString(),
                reps: reps.toString()
            });
            
            saveWorkoutData();
            
            // Refresh sets display
            const setsContainer = document.getElementById(`sets-container-${exerciseId}`);
            setsContainer.innerHTML = generateSetsHTML(workoutData[workoutKey].sets, exerciseId, workoutKey);
        }

        // Log working set to working sets
        function logWorkingSet(exerciseId, weight) {
            // Find the workout key for this exercise
            const week = document.getElementById('week-select').value;
            const day = document.getElementById('day-select').value;
            const workoutKey = `${week}-${day}-${exerciseId}`;
            
            if (!workoutData[workoutKey]) {
                workoutData[workoutKey] = { sets: [] };
            }
            
            workoutData[workoutKey].sets.push({
                weight: weight.toString(),
                reps: '' // User will fill in actual reps
            });
            
            saveWorkoutData();
            
            // Refresh sets display
            const setsContainer = document.getElementById(`sets-container-${exerciseId}`);
            setsContainer.innerHTML = generateSetsHTML(workoutData[workoutKey].sets, exerciseId, workoutKey);
        }

        // Add set
        function addSet(workoutKey, exerciseId) {
            if (!workoutData[workoutKey]) {
                workoutData[workoutKey] = { sets: [] };
            }
            
            workoutData[workoutKey].sets.push({
                weight: '',
                reps: ''
            });
            
            saveWorkoutData();
            
            // Refresh sets display
            const setsContainer = document.getElementById(`sets-container-${exerciseId}`);
            setsContainer.innerHTML = generateSetsHTML(workoutData[workoutKey].sets, exerciseId, workoutKey);
        }

        // Update set
        function updateSet(workoutKey, setIndex, field, value) {
            if (!workoutData[workoutKey]) {
                workoutData[workoutKey] = { sets: [] };
            }
            
            if (!workoutData[workoutKey].sets[setIndex]) {
                workoutData[workoutKey].sets[setIndex] = {};
            }
            
            workoutData[workoutKey].sets[setIndex][field] = value;
            saveWorkoutData();
        }

        // Remove set
        function removeSet(workoutKey, setIndex, exerciseId) {
            if (workoutData[workoutKey] && workoutData[workoutKey].sets) {
                workoutData[workoutKey].sets.splice(setIndex, 1);
                saveWorkoutData();
                
                // Refresh sets display
                const setsContainer = document.getElementById(`sets-container-${exerciseId}`);
                setsContainer.innerHTML = generateSetsHTML(workoutData[workoutKey].sets, exerciseId, workoutKey);
            }
        }

        // Start rest timer
        function startRestTimer(exerciseId, seconds) {
            // If seconds is a string (old format), parse it
            if (typeof seconds === 'string') {
                const restMatch = seconds.match(/(\d+)(?:-\d+)?\s*min/);
                if (!restMatch) return;
                const minutes = parseInt(restMatch[1]);
                seconds = minutes * 60;
            }
            
            const timerDisplay = document.getElementById(`timer-display-${exerciseId}`);
            const restStatus = timerDisplay.parentElement.querySelector('.rest-status');
            const presetButtons = timerDisplay.parentElement.querySelector('.timer-presets');
            const stopButton = document.getElementById(`stop-timer-${exerciseId}`);
            
            timerDisplay.style.display = 'block';
            presetButtons.style.setProperty('display', 'none', 'important');
            stopButton.style.display = 'block';
            restStatus.textContent = 'Resting...';
            
            const timer = setInterval(() => {
                const mins = Math.floor(seconds / 60);
                const secs = seconds % 60;
                timerDisplay.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;
                
                if (seconds <= 0) {
                    clearInterval(timer);
                    timerDisplay.style.display = 'none';
                    presetButtons.style.setProperty('display', 'flex', 'important');
                    stopButton.style.display = 'none';
                    restStatus.textContent = 'Rest Complete!';
                    
                    // Reset after 3 seconds
                    setTimeout(() => {
                        restStatus.textContent = 'Rest Timer';
                    }, 3000);
                    
                    delete restTimers[exerciseId];
                    return;
                }
                seconds--;
            }, 1000);
            
            restTimers[exerciseId] = timer;
        }

        // Stop rest timer
        function stopRestTimer(exerciseId) {
            if (restTimers[exerciseId]) {
                clearInterval(restTimers[exerciseId]);
                delete restTimers[exerciseId];
                
                const timerDisplay = document.getElementById(`timer-display-${exerciseId}`);
                const restStatus = timerDisplay.parentElement.querySelector('.rest-status');
                const presetButtons = timerDisplay.parentElement.querySelector('.timer-presets');
                const stopButton = document.getElementById(`stop-timer-${exerciseId}`);
                
                timerDisplay.style.display = 'none';
                presetButtons.style.setProperty('display', 'flex', 'important');
                stopButton.style.display = 'none';
                restStatus.textContent = 'Rest Timer';
            }
        }

        // Progress tracking functions
        
        function loadProgressPage() {
            // Load exercise list for progress tracking
            fetch('/api/exercises')
                .then(response => response.json())
                .then(exercises => {
                    const select = document.getElementById('exercise-select');
                    select.innerHTML = '<option value="">Choose an exercise...</option>';
                    
                    // Get unique exercise names
                    const uniqueExercises = [...new Set(exercises.map(ex => ex.name))];
                    uniqueExercises.sort().forEach(exerciseName => {
                        const option = document.createElement('option');
                        option.value = exerciseName;
                        option.textContent = exerciseName;
                        select.appendChild(option);
                    });
                })
                .catch(error => console.error('Error loading exercises:', error));
            
            // Update progress statistics
            updateProgressStats();
        }
        
        function updateProgressStats() {
            // Calculate statistics from workout data
            let totalWorkouts = 0;
            let weekWorkouts = 0;
            let totalVolume = 0;
            
            const currentWeek = document.getElementById('week-select')?.value || '1';
            
            for (const [key, workout] of Object.entries(workoutData)) {
                if (workout.sets && workout.sets.length > 0) {
                    totalWorkouts++;
                    
                    // Check if this workout is from current week
                    if (key.startsWith(`${currentWeek}-`)) {
                        weekWorkouts++;
                    }
                    
                    // Calculate volume
                    workout.sets.forEach(set => {
                        if (set.weight && set.reps) {
                            totalVolume += parseFloat(set.weight) * parseInt(set.reps);
                        }
                    });
                }
            }
            
            // Update display
            document.getElementById('total-workouts').textContent = totalWorkouts;
            document.getElementById('week-workouts').textContent = weekWorkouts;
            document.getElementById('total-volume').textContent = `${Math.round(totalVolume)} lbs`;
            document.getElementById('avg-sets').textContent = totalWorkouts > 0 ? Math.round(Object.values(workoutData).reduce((sum, w) => sum + (w.sets ? w.sets.length : 0), 0) / totalWorkouts) : '0';
        }
        
        function loadExerciseProgress() {
            const exerciseName = document.getElementById('exercise-select').value;
            if (!exerciseName) {
                document.getElementById('exercise-progress-chart').innerHTML = 
                    '<p style="text-align: center; color: #718096; margin: 2rem 0;">Select an exercise to view progress charts</p>';
                return;
            }
            
            // Find all workout sessions for this exercise
            const exerciseSessions = [];
            for (const [key, workout] of Object.entries(workoutData)) {
                if (key.includes(exerciseName) && workout.sets && workout.sets.length > 0) {
                    const [week, day] = key.split('-');
                    exerciseSessions.push({
                        week: parseInt(week),
                        day: day,
                        sets: workout.sets,
                        date: new Date().toISOString() // In real app, this would be stored
                    });
                }
            }
            
            if (exerciseSessions.length === 0) {
                document.getElementById('exercise-progress-chart').innerHTML = 
                    '<p style="text-align: center; color: #718096; margin: 2rem 0;">No data available for this exercise</p>';
                return;
            }
            
            // Sort by week
            exerciseSessions.sort((a, b) => a.week - b.week);
            
            // Generate progress chart HTML
            let chartHTML = `
                <h3 style="margin-bottom: 1rem;">${exerciseName} Progress</h3>
                <div class="progress-sessions">
            `;
            
            exerciseSessions.forEach((session, index) => {
                const maxWeight = Math.max(...session.sets.map(set => parseFloat(set.weight) || 0));
                const totalVolume = session.sets.reduce((sum, set) => 
                    sum + (parseFloat(set.weight) || 0) * (parseInt(set.reps) || 0), 0);
                
                chartHTML += `
                    <div class="session-card">
                        <div class="session-header">
                            <strong>Week ${session.week} - ${session.day}</strong>
                        </div>
                        <div class="session-stats">
                            <div class="session-stat">
                                <span>Max Weight:</span>
                                <span>${maxWeight} lbs</span>
                            </div>
                            <div class="session-stat">
                                <span>Volume:</span>
                                <span>${Math.round(totalVolume)} lbs</span>
                            </div>
                            <div class="session-stat">
                                <span>Sets:</span>
                                <span>${session.sets.length}</span>
                            </div>
                        </div>
                        <div class="session-sets">
                            ${session.sets.map((set, i) => 
                                `<span class="set-badge">${set.weight || 0}×${set.reps || 0}</span>`
                            ).join('')}
                        </div>
                    </div>
                `;
            });
            
            chartHTML += '</div>';
            document.getElementById('exercise-progress-chart').innerHTML = chartHTML;
        }
        
        function exportWorkoutData() {
            const dataToExport = {
                export_date: new Date().toISOString(),
                workout_data: workoutData,
                total_sessions: Object.keys(workoutData).length
            };
            
            const blob = new Blob([JSON.stringify(dataToExport, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `workout-data-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
        
        function clearAllData() {
            if (confirm('Are you sure you want to clear all workout data? This cannot be undone.')) {
                workoutData = {};
                saveWorkoutData();
                updateProgressStats();
                loadExerciseProgress();
                // Clear substitutions as well
                localStorage.removeItem('exerciseSubstitutions');
                alert('All workout data has been cleared.');
            }
        }

        // Substitution persistence functions
        function storeSubstitution(originalId, substitutionId, isReset = false) {
            let substitutions = JSON.parse(localStorage.getItem('exerciseSubstitutions') || '{}');
            
            if (isReset) {
                // Remove the substitution (reset to original)
                delete substitutions[originalId];
            } else {
                // Store the substitution
                substitutions[originalId] = substitutionId;
            }
            
            localStorage.setItem('exerciseSubstitutions', JSON.stringify(substitutions));
            console.log('💾 Stored substitution:', originalId, '->', substitutionId, isReset ? '(reset)' : '');
        }

        function getStoredSubstitution(originalId) {
            const substitutions = JSON.parse(localStorage.getItem('exerciseSubstitutions') || '{}');
            return substitutions[originalId] || null;
        }

        function clearStoredSubstitutions() {
            localStorage.removeItem('exerciseSubstitutions');
            console.log('🗑️ Cleared all stored substitutions');
        }

        // Apply stored substitutions when loading workout
        async function applyStoredSubstitutions() {
            const substitutions = JSON.parse(localStorage.getItem('exerciseSubstitutions') || '{}');
            console.log('🔍 All stored substitutions:', substitutions);
            
            for (const [originalId, substitutionId] of Object.entries(substitutions)) {
                try {
                    // Check if the exercise card exists on current page
                    const exerciseCard = document.querySelector(`[data-exercise-id="${originalId}"]`);
                    if (exerciseCard) {
                        console.log('🔄 Applying stored substitution:', originalId, '->', substitutionId);
                        
                        // Apply the substitution silently (without showing success message)
                        const response = await fetch('/api/substitute', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            credentials: 'same-origin',
                            body: JSON.stringify({
                                original_id: originalId,
                                substitution_id: substitutionId
                            })
                        });
                        
                        if (response.ok) {
                            const substitutionExercise = await response.json();
                            console.log('✅ Substitution loaded:', substitutionExercise.name);
                            updateExerciseCard(originalId, substitutionExercise);
                        } else {
                            const error = await response.json();
                            console.error('❌ Substitution failed:', error);
                        }
                    } else {
                        console.log('⚠️ Exercise card not found for:', originalId);
                    }
                } catch (error) {
                    console.error('Error applying stored substitution:', error);
                }
            }
        }

        // Update workout types when week changes
        document.getElementById('week-select').addEventListener('change', function() {
            closeAllCards(); // Close all cards when week changes
            updateWorkoutTypes();
            saveCurrentSelections();
        });
        
        // Save workout type selection when changed
        document.getElementById('day-select').addEventListener('change', function() {
            closeAllCards(); // Close all cards when workout type changes
            saveCurrentSelections();
        });
        
        // Save current selections to localStorage
        function saveCurrentSelections() {
            const week = document.getElementById('week-select').value;
            const workoutType = document.getElementById('day-select').value;
            
            if (week && workoutType) {
                const selections = { week, workoutType };
                localStorage.setItem('currentSelections', JSON.stringify(selections));
                console.log('💾 Saved selections:', selections);
            }
        }
        
        // Load saved selections from localStorage
        function loadSavedSelections() {
            const saved = localStorage.getItem('currentSelections');
            if (saved) {
                try {
                    const selections = JSON.parse(saved);
                    console.log('🔄 Loading saved selections:', selections);
                    
                    // Set week selection
                    const weekSelect = document.getElementById('week-select');
                    if (weekSelect && selections.week) {
                        weekSelect.value = selections.week;
                        // Pass the desired workout type to updateWorkoutTypes
                        updateWorkoutTypes(selections.workoutType);
                    }
                    
                } catch (error) {
                    console.error('Error loading saved selections:', error);
                }
            }
        }
        
        // Load saved selections when page loads
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(loadSavedSelections, 200); // Small delay to ensure DOM is ready
        });

        // Register Service Worker for offline functionality
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', function() {
                navigator.serviceWorker.register('/service-worker.js')
                    .then(function(registration) {
                        console.log('ServiceWorker registration successful');
                        
                        // Pre-cache all workout data for offline use
                        setTimeout(preCacheWorkoutData, 2000);
                    })
                    .catch(function(err) {
                        console.log('ServiceWorker registration failed: ', err);
                    });
            });
        }

        // Pre-cache all workout data for offline use
        async function preCacheWorkoutData() {
            console.log('Pre-caching workout data for offline use...');
            
            try {
                // Load and cache all exercise data
                const response = await fetch('/api/exercises', { credentials: 'same-origin' });
                if (response.ok) {
                    cachedWorkoutData = await response.json();
                    console.log(`✅ Cached ${cachedWorkoutData.length} exercises for offline use`);
                }
                
                // Cache all week/workout type combinations
                for (let week = 1; week <= 12; week++) {
                    const workoutTypes = ['Upper (Strength)', 'Lower (Strength)', 'Pull (Hypertrophy)', 'Push (Hypertrophy)', 'Legs (Hypertrophy)'];
                    
                    for (const workoutType of workoutTypes) {
                        const url = `/api/exercises?week=${week}&workout_type=${encodeURIComponent(workoutType)}`;
                        try {
                            await fetch(url, { credentials: 'same-origin' });
                        } catch (e) {
                            console.log(`Failed to cache: ${url}`);
                        }
                    }
                }
                
                // Cache exercise database
                try {
                    await fetch('/api/exercises', { credentials: 'same-origin' });
                } catch (e) {
                    console.log('Failed to cache exercise database');
                }
                
                console.log('✅ Workout data cached for offline use!');
                
                // Show offline ready notification
                showOfflineReadyNotification();
                
            } catch (error) {
                console.log('Error pre-caching workout data:', error);
            }
        }

        // Show offline ready notification
        function showOfflineReadyNotification() {
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: #4CAF50;
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                z-index: 10000;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                animation: slideIn 0.3s ease-out;
            `;
            notification.innerHTML = '📱 App ready for offline use at the gym!';
            
            // Add slide-in animation
            const style = document.createElement('style');
            style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(style);
            
            document.body.appendChild(notification);
            
            // Remove notification after 4 seconds
            setTimeout(() => {
                notification.style.animation = 'slideIn 0.3s ease-out reverse';
                setTimeout(() => notification.remove(), 300);
            }, 4000);
        }

        // Check online/offline status
        function updateOnlineStatus() {
            const statusIndicator = document.getElementById('online-status') || createStatusIndicator();
            
            if (navigator.onLine) {
                statusIndicator.innerHTML = '🟢 Online';
                statusIndicator.style.color = '#4CAF50';
            } else {
                statusIndicator.innerHTML = '🔴 Offline (Gym Mode)';
                statusIndicator.style.color = '#f44336';
            }
        }

        function createStatusIndicator() {
            // Return the existing status indicator in the header
            return document.getElementById('online-status');
        }

        // Listen for online/offline events
        window.addEventListener('online', updateOnlineStatus);
        window.addEventListener('offline', updateOnlineStatus);
        
        // Initial status check
        updateOnlineStatus();
    </script>
</body>
</html>
'''

@app.route('/')
@login_required
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/service-worker.js')
def service_worker():
    """Serve the service worker file"""
    with open('service-worker.js', 'r') as f:
        content = f.read()
    response = app.response_class(
        content,
        mimetype='application/javascript'
    )
    return response

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

