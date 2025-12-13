# setup_database.py - FIXED VERSION

"""
Run this script to:
1. Create all database tables
2. Insert default roles
3. Create admin user
4. Add sample data (optional)

Usage: python setup_database.py
"""

def create_default_roles(db, Role):
    """Create default roles"""
    print("Creating default roles...")
    
    roles_data = [
        {'role_name': 'admin', 'description': 'Administrator with full access'},
        {'role_name': 'user', 'description': 'Regular user'},
        {'role_name': 'trainer', 'description': 'Fitness trainer'},
    ]
    
    for role_data in roles_data:
        existing = Role.query.filter_by(role_name=role_data['role_name']).first()
        if not existing:
            role = Role(**role_data)
            db.session.add(role)
            print(f"  ✓ Created role: {role_data['role_name']}")
        else:
            print(f"  - Role already exists: {role_data['role_name']}")
    
    db.session.commit()
    print("✓ Roles created successfully\n")


def create_admin_user(db, User, Role):
    """Create default admin user"""
    print("Creating admin user...")
    
    admin_role = Role.query.filter_by(role_name='admin').first()
    
    if not admin_role:
        print("  ✗ Admin role not found. Run create_default_roles() first.")
        return
    
    # Check if admin exists
    existing_admin = User.query.filter_by(email='admin@fitness.com').first()
    
    if not existing_admin:
        admin = User(
            username='admin',
            email='admin@fitness.com',
            mobile_number='1234567890',
            role_id=admin_role.id
        )
        admin.set_password('Admin@123')
        db.session.add(admin)
        db.session.commit()
        print("  ✓ Admin user created")
        print("    Email: admin@fitness.com")
        print("    Password: Admin@123")
    else:
        print("  - Admin user already exists")
    
    print("✓ Admin user setup complete\n")


def add_sample_yoga_data(db, Yoga):
    """Add sample yoga poses"""
    print("Adding sample yoga data...")
    
    yoga_data = [
        {
            'yoga_name': 'Downward Dog (Adho Mukha Svanasana)',
            'yoga_description': 'A foundational yoga pose that stretches the entire body while building strength.',
            'difficulty_level': 'beginner',
            'duration_minutes': 5,
            'benefits': 'Strengthens arms and legs, stretches spine, improves digestion, relieves back pain',
            'photo_url': None
        },
        {
            'yoga_name': 'Tree Pose (Vrksasana)',
            'yoga_description': 'A balancing pose that improves focus and strengthens legs.',
            'difficulty_level': 'beginner',
            'duration_minutes': 3,
            'benefits': 'Improves balance, strengthens legs, improves concentration, stretches hips',
            'photo_url': None
        },
        {
            'yoga_name': 'Warrior II (Virabhadrasana II)',
            'yoga_description': 'A powerful standing pose that builds strength and stamina.',
            'difficulty_level': 'intermediate',
            'duration_minutes': 4,
            'benefits': 'Strengthens legs and arms, opens hips and chest, improves endurance',
            'photo_url': None
        },
        {
            'yoga_name': 'Cobra Pose (Bhujangasana)',
            'yoga_description': 'A gentle backbend that opens the chest and strengthens the spine.',
            'difficulty_level': 'beginner',
            'duration_minutes': 3,
            'benefits': 'Strengthens spine, opens chest, reduces stress, improves flexibility',
            'photo_url': None
        },
        {
            'yoga_name': 'Crow Pose (Bakasana)',
            'yoga_description': 'An arm balance that requires strength and concentration.',
            'difficulty_level': 'advanced',
            'duration_minutes': 5,
            'benefits': 'Strengthens arms and wrists, builds core strength, improves balance',
            'photo_url': None
        }
    ]
    
    for data in yoga_data:
        existing = Yoga.query.filter_by(yoga_name=data['yoga_name']).first()
        if not existing:
            yoga = Yoga(**data)
            db.session.add(yoga)
            print(f"  ✓ Added: {data['yoga_name']}")
        else:
            print(f"  - Already exists: {data['yoga_name']}")
    
    db.session.commit()
    print("✓ Sample yoga data added\n")


def add_sample_workout_data(db, Workout):
    """Add sample workout exercises"""
    print("Adding sample workout data...")
    
    workout_data = [
        {
            'workout_name': 'Push-ups',
            'workout_description': 'Classic bodyweight exercise for upper body strength.',
            'category': 'strength',
            'difficulty_level': 'beginner',
            'duration_minutes': 5,
            'calories_burned': 30,
            'equipment_needed': 'None',
            'photo_url': None
        },
        {
            'workout_name': 'Squats',
            'workout_description': 'Fundamental lower body exercise targeting legs and glutes.',
            'category': 'strength',
            'difficulty_level': 'beginner',
            'duration_minutes': 5,
            'calories_burned': 35,
            'equipment_needed': 'None',
            'photo_url': None
        },
        {
            'workout_name': 'Burpees',
            'workout_description': 'Full-body cardio exercise that builds strength and endurance.',
            'category': 'cardio',
            'difficulty_level': 'intermediate',
            'duration_minutes': 10,
            'calories_burned': 100,
            'equipment_needed': 'None',
            'photo_url': None
        },
        {
            'workout_name': 'Plank',
            'workout_description': 'Core strengthening exercise that improves stability.',
            'category': 'strength',
            'difficulty_level': 'beginner',
            'duration_minutes': 3,
            'calories_burned': 20,
            'equipment_needed': 'None',
            'photo_url': None
        },
        {
            'workout_name': 'Jump Rope',
            'workout_description': 'High-intensity cardio exercise for fat burning.',
            'category': 'cardio',
            'difficulty_level': 'beginner',
            'duration_minutes': 10,
            'calories_burned': 120,
            'equipment_needed': 'Jump rope',
            'photo_url': None
        }
    ]
    
    for data in workout_data:
        existing = Workout.query.filter_by(workout_name=data['workout_name']).first()
        if not existing:
            workout = Workout(**data)
            db.session.add(workout)
            print(f"  ✓ Added: {data['workout_name']}")
        else:
            print(f"  - Already exists: {data['workout_name']}")
    
    db.session.commit()
    print("✓ Sample workout data added\n")


def initialize_database():
    """Main initialization function"""
    print("\n" + "="*50)
    print("  FITNESS TRACKER - DATABASE SETUP")
    print("="*50 + "\n")
    
    # Import here to avoid circular imports
    from app import create_app, db
    from app.models.role import Role
    from app.models.user import User
    from app.models.yoga import Yoga
    from app.models.workout import Workout
    
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        try:
            db.create_all()
            print("✓ Database tables created\n")
        except Exception as e:
            print(f"✗ Error creating tables: {e}")
            return
        
        # Create roles
        try:
            create_default_roles(db, Role)
        except Exception as e:
            print(f"✗ Error creating roles: {e}")
            db.session.rollback()
        
        # Create admin user
        try:
            create_admin_user(db, User, Role)
        except Exception as e:
            print(f"✗ Error creating admin user: {e}")
            db.session.rollback()
        
        # Add sample data
        try:
            response = input("Do you want to add sample data? (y/n): ").strip().lower()
            if response == 'y':
                add_sample_yoga_data(db, Yoga)
                add_sample_workout_data(db, Workout)
        except Exception as e:
            print(f"✗ Error adding sample data: {e}")
            db.session.rollback()
        
        print("="*50)
        print("  ✓ DATABASE SETUP COMPLETE!")
        print("="*50)
        print("\nYou can now start the server with:")
        print("  python run.py")
        print("\nDefault admin credentials:")
        print("  Email: admin@fitness.com")
        print("  Password: Admin@123")
        print("\n⚠️  IMPORTANT: Change the admin password before deploying to production!")
        print()


if __name__ == '__main__':
    try:
        initialize_database()
    except KeyboardInterrupt:
        print("\n\n✗ Setup cancelled by user")
    except Exception as e:
        print(f"\n\n✗ Setup failed: {e}")
        import traceback
        traceback.print_exc()