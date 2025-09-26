from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from fraud_detection import FraudDetector
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Configure database for Vercel deployment
database_url = os.getenv('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Fallback to SQLite for local development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banking_system.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db and migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize fraud detector
fraud_detector = FraudDetector()

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    accounts = db.relationship('Account', backref='owner', lazy=True)
    cards = db.relationship('Card', backref='owner', lazy=True)
    subscriptions = db.relationship('Subscription', backref='owner', lazy=True)

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    account_type = db.Column(db.String(20), nullable=False)  # savings, checking, credit
    balance = db.Column(db.Float, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    transactions = db.relationship('Transaction', backref='account', lazy=True, foreign_keys='Transaction.account_id')

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(20), nullable=False)  # deposit, withdrawal, transfer
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    recipient_account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_fraudulent = db.Column(db.Boolean, default=False)
    fraud_score = db.Column(db.Float, default=0.0)
    location = db.Column(db.String(100))
    ip_address = db.Column(db.String(45))

class FraudAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
    description = db.Column(db.Text, nullable=False)
    is_resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String(16), unique=True, nullable=False)
    expiry_date = db.Column(db.String(5), nullable=False)  # MM/YY
    cvv = db.Column(db.String(3), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    blocked = db.Column(db.Boolean, default=False)  # Added blocked column to handle card blocking/unblocking

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    billing_cycle = db.Column(db.String(50), nullable=False)  # monthly, yearly, etc.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="active")  # active, canceled, expired # active, canceled, expired

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return render_template('register.html')
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    recent_transactions = []
    
    for account in accounts:
        transactions = Transaction.query.filter_by(account_id=account.id).order_by(Transaction.timestamp.desc()).limit(5).all()
        recent_transactions.extend(transactions)
    
    recent_transactions.sort(key=lambda x: x.timestamp, reverse=True)
    recent_transactions = recent_transactions[:10]
    
    return render_template('dashboard.html', accounts=accounts, transactions=recent_transactions)

@app.route('/account/<int:account_id>')
@login_required
def account_detail(account_id):
    account = Account.query.get_or_404(account_id)
    if account.user_id != current_user.id and not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    transactions = Transaction.query.filter_by(account_id=account_id).order_by(Transaction.timestamp.desc()).all()
    return render_template('account_detail.html', account=account, transactions=transactions)

@app.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    if request.method == 'POST':
        from_account_id = request.form.get('from_account')
        to_account_number = request.form.get('to_account')
        amount = float(request.form.get('amount'))
        description = request.form.get('description')
        
        from_account = Account.query.get(from_account_id)
        to_account = Account.query.filter_by(account_number=to_account_number).first()
        
        if not from_account or from_account.user_id != current_user.id:
            flash('Invalid source account')
            return render_template('transfer.html')
        
        if not to_account:
            flash('Recipient account not found')
            return render_template('transfer.html')
        
        if from_account.balance < amount:
            flash('Insufficient funds')
            return render_template('transfer.html')
        
        # Create transactions
        withdrawal = Transaction(
            transaction_type='transfer',
            amount=-amount,
            description=f"Transfer to {to_account.account_number}: {description}",
            account_id=from_account.id,
            recipient_account_id=to_account.id,
            location=request.remote_addr,
            ip_address=request.remote_addr
        )
        
        deposit = Transaction(
            transaction_type='transfer',
            amount=amount,
            description=f"Transfer from {from_account.account_number}: {description}",
            account_id=to_account.id,
            recipient_account_id=from_account.id,
            location=request.remote_addr,
            ip_address=request.remote_addr
        )
        
        # Fraud detection
        fraud_score = fraud_detector.predict_fraud(withdrawal)
        withdrawal.fraud_score = fraud_score
        withdrawal.is_fraudulent = fraud_score > 0.7
        
        if withdrawal.is_fraudulent:
            alert = FraudAlert(
                transaction_id=withdrawal.id,
                alert_type='High Fraud Score',
                severity='high',
                description=f'Transaction flagged with fraud score: {fraud_score:.3f}'
            )
            db.session.add(alert)
        
        # Update balances
        from_account.balance -= amount
        to_account.balance += amount
        
        db.session.add(withdrawal)
        db.session.add(deposit)
        db.session.commit()
        
        flash('Transfer completed successfully')
        return redirect(url_for('dashboard'))
    
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    return render_template('transfer.html', accounts=accounts)

@app.route('/api/transactions')
@login_required
def api_transactions():
    account_id = request.args.get('account_id')
    if account_id:
        transactions = Transaction.query.filter_by(account_id=account_id).order_by(Transaction.timestamp.desc()).all()
    else:
        accounts = Account.query.filter_by(user_id=current_user.id).all()
        account_ids = [acc.id for acc in accounts]
        transactions = Transaction.query.filter(Transaction.account_id.in_(account_ids)).order_by(Transaction.timestamp.desc()).all()
    
    return jsonify([{
        'id': t.id,
        'type': t.transaction_type,
        'amount': t.amount,
        'description': t.description,
        'timestamp': t.timestamp.isoformat(),
        'is_fraudulent': t.is_fraudulent,
        'fraud_score': t.fraud_score
    } for t in transactions])

@app.route('/admin/alerts')
@login_required
def admin_alerts():
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    alerts = FraudAlert.query.order_by(FraudAlert.created_at.desc()).all()
    return render_template('admin_alerts.html', alerts=alerts)

@app.route('/admin/resolve_alert/<int:alert_id>', methods=['POST'])
@login_required
def resolve_alert(alert_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    alert = FraudAlert.query.get_or_404(alert_id)
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    alert.resolved_by = current_user.id
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/cards', methods=['GET', 'POST'])
@login_required
def cards():
    if request.method == 'POST':
        card_number = request.form.get('card_number')
        expiry_date = request.form.get('expiry_date')
        cvv = request.form.get('cvv')
        
        # Create and save new card
        card = Card(
            card_number=card_number,
            expiry_date=expiry_date,
            cvv=cvv,
            user_id=current_user.id
        )
        db.session.add(card)
        db.session.commit()
        flash('Card added successfully!')
        return redirect(url_for('cards'))
    
    # Fetch all cards for the logged-in user
    user_cards = Card.query.filter_by(user_id=current_user.id).all()
    return render_template('cards.html', cards=user_cards)

@app.route('/card/delete/<int:card_id>', methods=['POST'])
@login_required
def delete_card(card_id):
    card = Card.query.get_or_404(card_id)
    if card.user_id == current_user.id:
        db.session.delete(card)
        db.session.commit()
        flash('Card deleted successfully.')
    else:
        flash('Access denied.')
    return redirect(url_for('cards'))

@app.route('/subscriptions', methods=['GET', 'POST'])
@login_required
def subscriptions():
    if request.method == 'POST':
        name = request.form.get('name')
        amount = float(request.form.get('amount'))
        billing_cycle = request.form.get('billing_cycle')
        
        # Create and save new subscription
        subscription = Subscription(
            name=name,
            amount=amount,
            billing_cycle=billing_cycle,
            user_id=current_user.id
        )
        db.session.add(subscription)
        db.session.commit()
        flash('Subscription added successfully!')
        return redirect(url_for('subscriptions'))
    
    # Fetch all subscriptions for the logged-in user
    user_subscriptions = Subscription.query.filter_by(user_id=current_user.id).all()
    return render_template('subscriptions.html', subscriptions=user_subscriptions)

@app.route('/subscription/delete/<int:subscription_id>', methods=['POST'])
@login_required
def delete_subscription(subscription_id):
    subscription = Subscription.query.get_or_404(subscription_id)
    if subscription.user_id == current_user.id:
        db.session.delete(subscription)
        db.session.commit()
        flash('Subscription deleted successfully.')
    else:
        flash('Access denied.')
    return redirect(url_for('subscriptions'))

@app.route('/subscription/activate/<int:subscription_id>', methods=['POST'])
@login_required
def activate_subscription(subscription_id):
    subscription = Subscription.query.get_or_404(subscription_id)
    if subscription.user_id == current_user.id:
        subscription.status = "active"
        db.session.commit()
        flash('Subscription activated successfully.')
    else:
        flash('Access denied.')
    return redirect(url_for('subscriptions'))

@app.route('/subscription/deactivate/<int:subscription_id>', methods=['POST'])
@login_required
def deactivate_subscription(subscription_id):
    subscription = Subscription.query.get_or_404(subscription_id)
    if subscription.user_id == current_user.id:
        subscription.status = "canceled"
        db.session.commit()
        flash('Subscription canceled successfully.')
    else:
        flash('Access denied.')
    return redirect(url_for('subscriptions'))

@app.route('/card/toggle/<int:card_id>', methods=['POST'])
@login_required
def toggle_card_view(card_id):
    card = Card.query.get_or_404(card_id)
    if card.user_id == current_user.id:
        card.blocked = not card.blocked  # Toggle the blocked status
        db.session.commit()
        flash(f"Card {card.card_number} {'blocked' if card.blocked else 'unblocked'} successfully.", 'success')
    else:
        flash('Access denied', 'danger')
    return redirect(url_for('cards'))



# Initialize the database with migrations
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
