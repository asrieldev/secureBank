import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from fraud_detection import FraudDetector
from flask import jsonify

# ---------------- CONFIG ----------------
load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')

database_url = os.getenv('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///banking_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
fraud_detector = FraudDetector()

# ---------------- MODELS ----------------
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
    upis = db.relationship('UPI', backref='owner', lazy=True)
    resolved_alerts = db.relationship('FraudAlert', backref='resolver',
                                      lazy=True, foreign_keys='FraudAlert.resolved_by')

    def update_profile(self, first_name=None, last_name=None, phone=None, email=None):
        if first_name:
            self.first_name = first_name
        if last_name:
            self.last_name = last_name
        if phone:
            self.phone = phone
        if email:
            self.email = email


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    account_type = db.Column(db.String(20), nullable=False)  # "savings" or "checking"
    balance = db.Column(db.Float, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    transactions = db.relationship('Transaction', backref='account', lazy=True, foreign_keys='Transaction.account_id')
    cards = db.relationship('Card', backref='account', lazy=True)
    subscriptions = db.relationship('Subscription', backref='account', lazy=True)



class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    recipient_account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=True)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscription.id'), nullable=True)
    upi_id = db.Column(db.Integer, db.ForeignKey('upi.id'), nullable=True)
    related_transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_fraudulent = db.Column(db.Boolean, default=False)
    fraud_score = db.Column(db.Float, default=0.0)
    location = db.Column(db.String(100))
    ip_address = db.Column(db.String(45))
    related_transaction = db.relationship('Transaction', remote_side=[id],
                                          backref='linked_transactions', lazy=True)
    card = db.relationship('Card', backref='transactions', lazy=True)
    subscription = db.relationship('Subscription', backref='transactions', lazy=True)
    upi = db.relationship('UPI', backref='transactions', lazy=True)
    fraud_alerts = db.relationship('FraudAlert', backref='transaction', lazy=True)


class FraudAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    is_resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String(16), unique=True, nullable=False)
    expiry_date = db.Column(db.String(5), nullable=False)
    cvv = db.Column(db.String(3), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)  # now required
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    blocked = db.Column(db.Boolean, default=False)



class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    billing_cycle = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=True)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="active")


class UPI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    upi_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---------------- LOGIN MANAGER ----------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------- ROUTES ----------------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or email already exists!", "danger")
            return redirect(url_for('register'))

        new_user = User(username=username, email=email,
                        password_hash=password, first_name=first_name, last_name=last_name)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for('dashboard'))
        flash("Invalid credentials!", "danger")
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have logged out.", "info")
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    recent_transactions = []
    for account in accounts:
        transactions = Transaction.query.filter_by(account_id=account.id)\
            .order_by(Transaction.timestamp.desc()).limit(5).all()
        recent_transactions.extend(transactions)
    recent_transactions.sort(key=lambda x: x.timestamp, reverse=True)
    recent_transactions = recent_transactions[:10]
    cards = Card.query.filter_by(user_id=current_user.id).all()
    upis = current_user.upis
    return render_template('dashboard.html', accounts=accounts, transactions=recent_transactions, cards=cards, upis=upis)

# ---------------- PROFILE ROUTES ----------------

@app.route('/profile')
@login_required
def profile():
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', accounts=accounts)


@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    current_user.update_profile(
        first_name=request.form.get('first_name'),
        last_name=request.form.get('last_name'),
        phone=request.form.get('phone'),
        email=request.form.get('email')
    )
    db.session.commit()
    flash("Profile updated successfully!", "success")
    return redirect(url_for('profile'))

@app.route('/profile/create_account', methods=['POST'])
@login_required
def create_account():
    account_number = request.form.get('account_number')
    account_type = request.form.get('account_type').strip().lower()

    # Standardize account types
    if account_type == "saving":
        account_type = "savings"

    allowed_account_types = ["savings", "checking"]
    if account_type not in allowed_account_types:
        flash("Invalid account type", "danger")
        return redirect(url_for("profile"))

    # Prevent duplicate account numbers
    if Account.query.filter_by(account_number=account_number).first():
        flash("Account number already exists!", "danger")
        return redirect(url_for('profile'))

    # Prevent duplicate account types
    existing_account = Account.query.filter(
        Account.user_id == current_user.id,
        db.func.lower(Account.account_type) == account_type
    ).first()

    if existing_account:
        flash(f"You already have a {account_type} account.", "warning")
        return redirect(url_for('profile'))

    # Create account
    new_account = Account(
        account_number=account_number,
        account_type=account_type,
        user_id=current_user.id,
        balance=0.0
    )
    db.session.add(new_account)
    db.session.commit()

    flash(f"{account_type.capitalize()} account created successfully!", "success")
    return redirect(url_for('profile'))
@app.route('/profile/delete_account/<int:account_id>', methods=['POST'])
@login_required
def delete_account(account_id):
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()

    if not account:
        flash("Account not found or unauthorized action.", "danger")
        return redirect(url_for('profile'))

    if len(accounts) <= 1:
        flash("You cannot delete your only account.", "warning")
        return redirect(url_for('profile'))

    if account.cards:
        flash("Cannot delete account with linked cards. Remove them first.", "danger")
        return redirect(url_for('profile'))

    if account.transactions:
        flash("Cannot delete account with existing transactions.", "danger")
        return redirect(url_for('profile'))

    db.session.delete(account)
    db.session.commit()

    flash(f"{account.account_type.capitalize()} account deleted successfully.", "success")
    return redirect(url_for('profile'))

@app.route('/account/<int:account_id>')
@login_required
def account_detail(account_id):
    account = Account.query.get_or_404(account_id)
    if account.user_id != current_user.id and not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    transactions = Transaction.query.filter_by(account_id=account.id).order_by(Transaction.timestamp.desc()).all()
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
            flash('Invalid source account', 'danger')
            return redirect(url_for('transfer'))
        if not to_account:
            flash('Recipient account not found', 'danger')
            return redirect(url_for('transfer'))
        if from_account.balance < amount:
            flash('Insufficient funds', 'danger')
            return redirect(url_for('transfer'))

        withdrawal = Transaction(
            transaction_type='transfer',
            amount=-amount,
            description=f"Transfer to {to_account.account_number}: {description}",
            account_id=from_account.id,
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

        from_account.balance -= amount
        to_account.balance += amount

        db.session.add(withdrawal)
        db.session.add(deposit)
        db.session.commit()
        flash('Transfer completed successfully', 'success')
        return redirect(url_for('dashboard'))

    accounts = Account.query.filter_by(user_id=current_user.id).all()
    return render_template('transfer.html', accounts=accounts)


@app.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    if request.method == 'POST':
        account_id = request.form.get('account_id')
        amount = float(request.form.get('amount'))
        description = request.form.get('description')
        account = Account.query.get(account_id)

        if not account or account.user_id != current_user.id:
            flash('Invalid account', 'danger')
            return redirect(url_for('deposit'))

        account.balance += amount
        transaction = Transaction(
            transaction_type='deposit',
            amount=amount,
            description=description or "Deposit",
            account_id=account.id,
            location=request.remote_addr,
            ip_address=request.remote_addr
        )
        db.session.add(transaction)
        db.session.commit()
        flash(f'Deposit of ${amount:.2f} successful!', 'success')
        return redirect(url_for('dashboard'))

    accounts = Account.query.filter_by(user_id=current_user.id).all()
    return render_template('deposit.html', accounts=accounts)


@app.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    if request.method == 'POST':
        account_id = request.form.get('account_id')
        amount = float(request.form.get('amount'))
        description = request.form.get('description')
        account = Account.query.get(account_id)

        if not account or account.user_id != current_user.id:
            flash('Invalid account', 'danger')
            return redirect(url_for('withdraw'))
        if account.balance < amount:
            flash('Insufficient funds', 'danger')
            return redirect(url_for('withdraw'))

        account.balance -= amount
        transaction = Transaction(
            transaction_type='withdrawal',
            amount=-amount,
            description=description or "Withdrawal",
            account_id=account.id,
            location=request.remote_addr,
            ip_address=request.remote_addr
        )
        db.session.add(transaction)
        db.session.commit()
        flash(f'Withdrawal of ₹{amount:.2f} successful!', 'success')
        return redirect(url_for('dashboard'))

    accounts = Account.query.filter_by(user_id=current_user.id).all()
    return render_template('withdraw.html', accounts=accounts)

from flask import jsonify

@app.route('/card/delete/<int:card_id>', methods=['POST'])
@login_required
def delete_card(card_id):
    card = Card.query.get_or_404(card_id)
    if card.user_id == current_user.id:
        db.session.delete(card)
        db.session.commit()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Access denied"}), 403
from flask import request

@app.route('/cards', methods=['GET', 'POST'])
@login_required
def cards():
    accounts = Account.query.filter_by(user_id=current_user.id).all()

    if request.method == 'POST':
        card_number = request.form.get('card_number')
        expiry_date = request.form.get('expiry_date')
        cvv = request.form.get('cvv')
        account_id = request.form.get('account_id')

        account = Account.query.get(account_id)

        if not account or account.user_id != current_user.id:
            flash('Invalid account selected.', 'danger')
            return redirect(url_for('cards'))

        allowed_account_types = ['savings', 'checking']
        if account.account_type.strip().lower() not in [a.lower() for a in allowed_account_types]:
            flash(f'Card can only be tied to {", ".join(allowed_account_types)} accounts.', 'danger')
            return redirect(url_for('cards'))

        new_card = Card(
            card_number=card_number,
            expiry_date=expiry_date,
            cvv=cvv,
            user_id=current_user.id,
            account_id=account.id
        )
        db.session.add(new_card)
        db.session.commit()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                "success": True,
                "card": {
                    "id": new_card.id,
                    "card_number": new_card.card_number,
                    "expiry_date": new_card.expiry_date,
                    "cvv": new_card.cvv,
                    "account_id": new_card.account.id,
                    "account_number": new_card.account.account_number,
                    "account_type": new_card.account.account_type,
                    "balance": new_card.account.balance,
                    "first_name": current_user.first_name,
                    "last_name": current_user.last_name,
                    "blocked": new_card.blocked,
                    "created_at": new_card.created_at.strftime("%b %Y"),
                    "transactions": [
                        {"is_fraudulent": t.is_fraudulent} for t in new_card.transactions
                    ]
                }
            })

        flash('Card added successfully!', 'success')
        return redirect(url_for('cards'))

    user_cards = Card.query.filter_by(user_id=current_user.id).all()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            "cards": [
                {
                    "id": card.id,
                    "card_number": card.card_number,
                    "expiry_date": card.expiry_date,
                    "cvv": card.cvv,
                    "account_id": card.account.id,
                    "account_number": card.account.account_number,
                    "account_type": card.account.account_type,
                    "balance": card.account.balance,
                    "first_name": current_user.first_name,
                    "last_name": current_user.last_name,
                    "blocked": card.blocked,
                    "created_at": card.created_at.strftime("%b %Y"),
                    "transactions": [
                        {"is_fraudulent": t.is_fraudulent} for t in card.transactions
                    ]
                }
                for card in user_cards
            ]
        })

    return render_template('cards.html', cards=user_cards, accounts=accounts)

@app.route('/toggle_card_view/<int:card_id>', methods=['POST'])
@login_required
def toggle_card_view(card_id):
    card = Card.query.get_or_404(card_id)

    # Ensure the card belongs to the logged-in user
    if card.user_id != current_user.id:
        return jsonify({"success": False, "error": "Access denied"}), 403

    # Toggle block status
    card.blocked = not card.blocked
    db.session.commit()

    return jsonify({
        "success": True,
        "blocked": card.blocked
    })



@app.route('/subscriptions', methods=['GET', 'POST'])
@login_required
def subscriptions():
    if request.method == 'POST':
        name = request.form.get('name')
        amount = request.form.get('amount')
        billing_cycle = request.form.get('billing_cycle')
        account_id = request.form.get('account_id')
        card_id = request.form.get('card_id')

        # Validation
        if not name or not amount or not billing_cycle:
            flash("Name, amount, and billing cycle are required.", "danger")
            return redirect(url_for('subscriptions'))

        try:
            amount = float(amount)
        except ValueError:
            flash("Invalid amount value.", "danger")
            return redirect(url_for('subscriptions'))

        # Create subscription
        subscription = Subscription(
            name=name,
            amount=amount,
            billing_cycle=billing_cycle,
            user_id=current_user.id,
            account_id=int(account_id) if account_id else None,
            card_id=int(card_id) if card_id else None
        )

        db.session.add(subscription)
        db.session.commit()
        flash('Subscription added successfully!', 'success')
        return redirect(url_for('subscriptions'))

    # GET: Load subscriptions, accounts, and cards
    user_subscriptions = Subscription.query.filter_by(user_id=current_user.id).all()
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    cards = Card.query.filter_by(user_id=current_user.id).all()

    return render_template(
        'subscriptions.html',
        subscriptions=user_subscriptions,
        accounts=accounts,
        cards=cards
    )


@app.route('/subscription/delete/<int:subscription_id>', methods=['POST'])
@login_required
def delete_subscription(subscription_id):
    subscription = Subscription.query.get_or_404(subscription_id)
    if subscription.user_id == current_user.id:
        db.session.delete(subscription)
        db.session.commit()
        flash('Subscription deleted successfully.', 'success')
    else:
        flash('Access denied.', 'danger')
    return redirect(url_for('subscriptions'))


@app.route('/subscription/activate/<int:subscription_id>', methods=['POST'])
@login_required
def activate_subscription(subscription_id):
    subscription = Subscription.query.get_or_404(subscription_id)
    if subscription.user_id == current_user.id:
        subscription.status = "active"
        db.session.commit()
        flash('Subscription activated successfully.', 'success')
    else:
        flash('Access denied.', 'danger')
    return redirect(url_for('subscriptions'))


@app.route('/subscription/deactivate/<int:subscription_id>', methods=['POST'])
@login_required
def deactivate_subscription(subscription_id):
    subscription = Subscription.query.get_or_404(subscription_id)
    if subscription.user_id == current_user.id:
        subscription.status = "canceled"
        db.session.commit()
        flash('Subscription canceled successfully.', 'success')
    else:
        flash('Access denied.', 'danger')
    return redirect(url_for('subscriptions'))


@app.route('/upis', methods=['GET', 'POST'])
@login_required
def upis():
    if request.method == 'POST':
        upi_id = request.form.get('upi_id')
        if not upi_id or UPI.query.filter_by(upi_id=upi_id).first():
            flash('Invalid or duplicate UPI ID.', 'danger')
            return redirect(url_for('upis'))
        new_upi = UPI(upi_id=upi_id, user_id=current_user.id)
        db.session.add(new_upi)
        db.session.commit()
        flash('UPI ID added successfully!', 'success')
        return redirect(url_for('upis'))
    user_upis = UPI.query.filter_by(user_id=current_user.id).all()
    return render_template('upis.html', upis=user_upis)


@app.route('/upi/delete/<int:upi_id>', methods=['POST'])
@login_required
def delete_upi(upi_id):
    upi = UPI.query.get_or_404(upi_id)
    if upi.user_id == current_user.id:
        db.session.delete(upi)
        db.session.commit()
        flash('UPI ID deleted successfully.', 'success')
    else:
        flash('Access denied.', 'danger')
    return redirect(url_for('upis'))


@app.route('/admin/alerts')
@login_required
def admin_alerts():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
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


# ---------------- MAIN ----------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
