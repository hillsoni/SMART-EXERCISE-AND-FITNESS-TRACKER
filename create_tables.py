#!/usr/bin/env python3
"""Create all database tables"""

def main():
    print("\n" + "="*70)
    print("  📦 CREATING DATABASE TABLES")
    print("="*70 + "\n")
    
    from app import create_app, db
    
    app = create_app()
    
    with app.app_context():
        try:
            # Import all models to register them
            print("📋 Importing models...")
            from app.models.role import Role
            from app.models.user import User
            from app.models.yoga import Yoga
            from app.models.workout import Workout
            from app.models.diet_plan import DietPlan
            from app.models.exercise_plan import ExercisePlan
            from app.models.chatbot_query import ChatbotQuery
            print("✓ Models imported")
            
            # Create all tables
            print("\n🔨 Creating tables...")
            db.create_all()
            print("✓ Tables created successfully!")
            
            # Verify tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"\n✅ Created {len(tables)} tables:")
            for table in tables:
                print(f"   • {table}")
            
            print("\n" + "="*70)
            print("  ✓ SUCCESS!")
            print("="*70)
            print("\n💡 Next step: python seed_data.py\n")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)