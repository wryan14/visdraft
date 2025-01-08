from app import create_app
from models import db  # Add this import
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the Library Viz application')
    parser.add_argument('--reset-db', action='store_true', 
                       help='Reset the database (WARNING: This will delete all data)')
    args = parser.parse_args()

    app = create_app()
    
    if args.reset_db:
        with app.app_context():
            print("Resetting database...")
            db.drop_all()
            db.create_all()
            print("Database reset complete")
    
    app.run(debug=True, port=5000)