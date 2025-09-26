#!/usr/bin/env python3
"""
Setup script for Banking Transaction System with Fraud Detection
Creates sample data for testing and demonstration
"""

import os
import sys
from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Account, Transaction, FraudAlert
from fraud_detection import FraudDetector

def create_sample_data():
    """Create sample users, accounts, and transactions"""
    
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        FraudAlert.query.delete()
        Transaction.query.delete()
        Account.query.delete()
        User.query.delete()
        
        # Create admin user
        print("Creating admin user...")
        admin = User(
            username='admin',
            email='admin@securebank.com',
            password_hash=generate_password_hash('admin123'),
            first_name='Admin',
            last_name='User',
            phone='555-0001',
            is_admin=True
        )
        db.session.add(admin)
        
        # Create regular users
        print("Creating sample users...")
        users = []
        user_data = [
            ('john_doe', 'john@example.com', 'John', 'Doe', '555-0002'),
            ('jane_smith', 'jane@example.com', 'Jane', 'Smith', '555-0003'),
            ('bob_wilson', 'bob@example.com', 'Bob', 'Wilson', '555-0004'),
            ('alice_brown', 'alice@example.com', 'Alice', 'Brown', '555-0005'),
            ('charlie_davis', 'charlie@example.com', 'Charlie', 'Davis', '555-0006')
        ]
        
        for username, email, first_name, last_name, phone in user_data:
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash('password123'),
                first_name=first_name,
                last_name=last_name,
                phone=phone
            )
            users.append(user)
            db.session.add(user)
        
        db.session.commit()
        
        # Create accounts for each user
        print("Creating sample accounts...")
        accounts = []
        account_types = ['savings', 'checking']
        
        for user in [admin] + users:
            for account_type in account_types:
                account = Account(
                    account_number=f"{random.randint(10000000, 99999999)}",
                    account_type=account_type,
                    balance=random.uniform(1000, 50000),
                    user_id=user.id
                )
                accounts.append(account)
                db.session.add(account)
        
        db.session.commit()
        
        # Create sample transactions
        print("Creating sample transactions...")
        transaction_types = ['transfer', 'deposit', 'withdrawal']
        descriptions = [
            'Grocery store purchase',
            'Online shopping',
            'Restaurant payment',
            'Gas station',
            'Utility bill payment',
            'Insurance premium',
            'Phone bill',
            'Internet service',
            'Movie tickets',
            'Coffee shop',
            'Bookstore purchase',
            'Clothing store',
            'Electronics purchase',
            'Home improvement',
            'Medical expenses'
        ]
        
        # Generate transactions over the last 30 days
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        fraud_detector = FraudDetector()
        
        for _ in range(200):  # Create 200 sample transactions
            # Random account
            account = random.choice(accounts)
            
            # Random transaction type
            transaction_type = random.choice(transaction_types)
            
            # Random amount based on type
            if transaction_type == 'deposit':
                amount = random.uniform(100, 5000)
            elif transaction_type == 'withdrawal':
                amount = -random.uniform(50, 2000)
            else:  # transfer
                amount = random.choice([random.uniform(50, 2000), -random.uniform(50, 2000)])
            
            # Random timestamp within last 30 days
            timestamp = start_date + timedelta(
                seconds=random.randint(0, int((end_date - start_date).total_seconds()))
            )
            
            # Random description
            description = random.choice(descriptions)
            
            # Create transaction
            transaction = Transaction(
                transaction_type=transaction_type,
                amount=amount,
                description=description,
                account_id=account.id,
                timestamp=timestamp,
                location=f"{random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'])}",
                ip_address=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
            )
            
            # Get fraud score
            fraud_score = fraud_detector.predict_fraud(transaction)
            transaction.fraud_score = fraud_score
            transaction.is_fraudulent = fraud_score > 0.7
            
            # Update account balance
            account.balance += amount
            
            db.session.add(transaction)
            db.session.commit()  # Commit so transaction.id is populated
            
            # Create fraud alert for high-risk transactions
            if transaction.is_fraudulent:
                alert = FraudAlert(
                    transaction_id=transaction.id,
                    alert_type='High Fraud Score',
                    severity='high' if fraud_score > 0.8 else 'medium',
                    description=f'Transaction flagged with fraud score: {fraud_score:.3f}'
                )
                db.session.add(alert)
                db.session.commit()
        
        db.session.commit()
        
        print("Sample data created successfully!")
        print(f"Created {len(users) + 1} users")
        print(f"Created {len(accounts)} accounts")
        print(f"Created 200 transactions")
        
        # Print login credentials
        print("\n" + "="*50)
        print("LOGIN CREDENTIALS")
        print("="*50)
        print("Admin User:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nRegular Users:")
        for user in users:
            print(f"  Username: {user.username}")
            print(f"  Password: password123")
        print("="*50)

def main():
    """Main setup function"""
    print("Banking Transaction System Setup")
    print("="*40)
    
    # Create database tables
    print("Creating database tables...")
    with app.app_context():
        db.create_all()
    
    # Create sample data
    create_sample_data()
    
    print("\nSetup completed successfully!")
    print("You can now run the application with: python app.py")

if __name__ == '__main__':
    main() 