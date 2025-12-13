#!/usr/bin/env python3
"""Add height, weight columns to users table and create challenge tables"""

from app import create_app, db
from sqlalchemy import text

def main():
    print("\n" + "="*70)
    print("  📦 ADDING NEW COLUMNS AND TABLES")
    print("="*70 + "\n")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Add height and weight columns to users table
            print("📋 Adding height and weight columns to users table...")
            try:
                db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS height FLOAT"))
                db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS weight FLOAT"))
                db.session.commit()
                print("✓ Height and weight columns added successfully!")
            except Exception as e:
                print(f"⚠️  Note: {e}")
                db.session.rollback()
            
            # Import challenge models to register them
            print("\n📋 Importing challenge models...")
            from app.models.challenge import Challenge, UserChallenge, ChallengeProgress
            print("✓ Challenge models imported")
            
            # Create challenge tables
            print("\n🔨 Creating challenge tables...")
            try:
                Challenge.__table__.create(db.engine, checkfirst=True)
                UserChallenge.__table__.create(db.engine, checkfirst=True)
                ChallengeProgress.__table__.create(db.engine, checkfirst=True)
                print("✓ Challenge tables created successfully!")
            except Exception as e:
                print(f"⚠️  Note: {e}")
            
            # Verify tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"\n✅ Database now has {len(tables)} tables:")
            for table in sorted(tables):
                print(f"   • {table}")
            
            # Check users table columns
            print("\n📋 Checking users table columns...")
            columns = inspector.get_columns('users')
            column_names = [col['name'] for col in columns]
            print(f"   Users table columns: {', '.join(column_names)}")
            
            if 'height' in column_names and 'weight' in column_names:
                print("✓ Height and weight columns exist in users table")
            else:
                print("⚠️  Warning: Height or weight columns missing!")
            
            print("\n" + "="*70)
            print("  ✓ MIGRATION COMPLETE!")
            print("="*70 + "\n")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False
    
    return True

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)

