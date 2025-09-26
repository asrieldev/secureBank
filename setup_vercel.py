#!/usr/bin/env python3
"""
Setup script for Vercel deployment
This script initializes the database and creates sample data for the banking system
"""

import os
import sys
from datetime import datetime, timedelta
import random
import string

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Account, Transaction, FraudAlert
from fraud_detection import FraudDetector

def generate_account_number():
    """Generate a random account number"""
    return ''.join(random.choices(string.digits, k=10))

def create_sample_data():
    """Create sample users, accounts, and transactions"""
    print("Creating sample data for Vercel deployment...")
    
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Check if admin user already exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            # Create admin user
            admin_user = User(
                username='admin',
                email='admin@banking.com',
                password_hash='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.i8m.',  # admin123
                first_name='Admin',
                last_name='User',
                phone='555-0001',
                is_admin=True,
                created_at=datetime.utcnow() - timedelta(days=30)
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Admin user created")
        
        # Create regular users
        users_data = [
            {
                'username': 'john_doe',
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'phone': '555-0002'
            },
            {
                'username': 'jane_smith',
                'email': 'jane@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'phone': '555-0003'
            },
            {
                'username': 'bob_wilson',
                'email': 'bob@example.com',
                'first_name': 'Bob',
                'last_name': 'Wilson',
                'phone': '555-0004'
            }
        ]
        
        created_users = []
        for user_data in users_data:
            user = User.query.filter_by(username=user_data['username']).first()
            if not user:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.i8m.',  # password123
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    phone=user_data['phone'],
                    created_at=datetime.utcnow() - timedelta(days=random.randint(10, 25))
                )
                db.session.add(user)
                created_users.append(user)
        
        db.session.commit()
        print(f"✅ {len(created_users)} regular users created")
        
        # Create accounts for users
        all_users = User.query.all()
        account_types = ['savings', 'checking', 'credit']
        
        for user in all_users:
            # Create 2-3 accounts per user
            num_accounts = random.randint(2, 3)
            for i in range(num_accounts):
                account_type = account_types[i % len(account_types)]
                account = Account(
                    account_number=generate_account_number(),
                    account_type=account_type,
                    balance=random.uniform(1000, 10000),
                    user_id=user.id,
                    created_at=datetime.utcnow() - timedelta(days=random.randint(5, 20))
                )
                db.session.add(account)
        
        db.session.commit()
        print("✅ Accounts created for all users")
        
        # Create sample transactions
        accounts = Account.query.all()
        transaction_types = ['deposit', 'withdrawal', 'transfer']
        
        for account in accounts:
            # Create 5-15 transactions per account
            num_transactions = random.randint(5, 15)
            for i in range(num_transactions):
                transaction_type = random.choice(transaction_types)
                amount = random.uniform(10, 500)
                
                if transaction_type == 'withdrawal':
                    amount = -amount
                elif transaction_type == 'transfer':
                    # Randomly choose another account for transfer
                    other_accounts = [acc for acc in accounts if acc.id != account.id]
                    if other_accounts:
                        recipient_account = random.choice(other_accounts)
                        # Create transfer transaction
                        transfer_out = Transaction(
                            transaction_type='transfer',
                            amount=-amount,
                            description=f"Transfer to {recipient_account.account_number}",
                            account_id=account.id,
                            recipient_account_id=recipient_account.id,
                            timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                            location='New York, NY',
                            ip_address='192.168.1.1'
                        )
                        db.session.add(transfer_out)
                        
                        transfer_in = Transaction(
                            transaction_type='transfer',
                            amount=amount,
                            description=f"Transfer from {account.account_number}",
                            account_id=recipient_account.id,
                            recipient_account_id=account.id,
                            timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                            location='New York, NY',
                            ip_address='192.168.1.1'
                        )
                        db.session.add(transfer_in)
                        
                        # Update balances
                        account.balance -= amount
                        recipient_account.balance += amount
                    continue
                
                transaction = Transaction(
                    transaction_type=transaction_type,
                    amount=amount,
                    description=f"{transaction_type.title()} transaction",
                    account_id=account.id,
                    timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                    location='New York, NY',
                    ip_address='192.168.1.1'
                )
                db.session.add(transaction)
                
                # Update account balance
                account.balance += amount
        
        db.session.commit()
        print("✅ Sample transactions created")
        
        # Create some fraud alerts
        high_risk_transactions = Transaction.query.filter(Transaction.amount > 1000).limit(5).all()
        
        for transaction in high_risk_transactions:
            alert = FraudAlert(
                transaction_id=transaction.id,
                alert_type='High Amount Transaction',
                severity='medium',
                description=f'Large transaction amount: ${abs(transaction.amount):.2f}',
                created_at=transaction.timestamp + timedelta(minutes=5)
            )
            db.session.add(alert)
        
        db.session.commit()
        print("✅ Sample fraud alerts created")
        
        print("\n🎉 Vercel deployment setup completed!")
        print("\n📋 Login Credentials:")
        print("Admin User:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nRegular Users:")
        print("  Username: john_doe, jane_smith, bob_wilson")
        print("  Password: password123")
        print("\n🌐 Access your application at your Vercel URL")

if __name__ == '__main__':
    create_sample_data() 