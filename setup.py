import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from faker import Faker

fake = Faker()


def main():
    from app import app, db, User, Account, Transaction, FraudAlert, Card, Subscription, UPI, FraudDetector

    fraud_detector = FraudDetector()

    def generate_unique_upi(user, existing_upis):
        base_upi = f"{user.first_name.lower()}.{user.last_name.lower()}"
        suffix = random.randint(1, 999)
        upi_id = f"{base_upi}{suffix}@upi"

        while upi_id in existing_upis or UPI.query.filter_by(upi_id=upi_id).first():
            suffix = random.randint(1, 9999)
            upi_id = f"{base_upi}{suffix}@upi"

        return upi_id

    with app.app_context():
        print("Clearing existing data...")
        FraudAlert.query.delete()
        Transaction.query.delete()
        Account.query.delete()
        Card.query.delete()
        Subscription.query.delete()
        UPI.query.delete()
        User.query.delete()
        db.session.commit()

        print("Creating users...")
        users = []

        admin = User(
            username='admin',
            email='admin@securebank.com',
            password_hash=generate_password_hash('admin123'),
            first_name='Admin',
            last_name='User',
            phone='555-0001',
            is_admin=True
        )
        users.append(admin)

        for _ in range(50):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{first_name.lower()}{random.randint(100, 999)}"
            email = f"{username}@example.com"
            password_hash = generate_password_hash("password123")
            phone = fake.phone_number()
            users.append(User(
                username=username,
                email=email,
                password_hash=password_hash,
                first_name=first_name,
                last_name=last_name,
                phone=phone
            ))

        db.session.add_all(users)
        db.session.commit()

        print("Creating accounts...")
        accounts = []
        for user in users:
            savings = Account(
                account_number=f"ACC{random.randint(10000, 99999)}",
                account_type="savings",
                balance=round(random.uniform(1000, 50000), 2),
                user_id=user.id
            )
            checking = Account(
                account_number=f"ACC{random.randint(10000, 99999)}",
                account_type="checking",
                balance=round(random.uniform(1000, 50000), 2),
                user_id=user.id
            )
            accounts.extend([savings, checking])

        db.session.add_all(accounts)
        db.session.commit()

        print("Creating cards...")
        cards = []
        for account in accounts:
            if random.random() < 0.7:
                card_number = "".join(str(random.randint(0, 9)) for _ in range(16))
                expiry_date = f"{random.randint(1, 12):02d}/{random.randint(24, 30)}"
                cvv = f"{random.randint(100, 999)}"
                cards.append(Card(
                    card_number=card_number,
                    expiry_date=expiry_date,
                    cvv=cvv,
                    user_id=account.user_id,
                    account_id=account.id
                ))

        db.session.add_all(cards)
        db.session.commit()

        print("Creating UPI IDs...")
        upis = set()
        upi_objects = []
        for user in users:
            for _ in range(random.randint(0, 2)):
                upi_id = generate_unique_upi(user, upis)
                upis.add(upi_id)
                upi_objects.append(UPI(upi_id=upi_id, user_id=user.id))

        db.session.add_all(upi_objects)
        db.session.commit()

        print("Creating subscriptions...")
        subscriptions = []
        subscription_names = ["Netflix", "Spotify", "Amazon Prime", "YouTube Premium", "Disney+"]
        for user in users:
            for _ in range(random.randint(0, 2)):
                account = random.choice([a for a in accounts if a.user_id == user.id])
                name = random.choice(subscription_names)
                amount = round(random.uniform(50, 500), 2)
                billing_cycle = random.choice(["monthly", "yearly"])
                subscriptions.append(Subscription(
                    name=name,
                    amount=amount,
                    billing_cycle=billing_cycle,
                    user_id=user.id,
                    account_id=account.id
                ))

        db.session.add_all(subscriptions)
        db.session.commit()

        print("Creating transactions...")
        transactions = []
        for account in accounts:
            for _ in range(random.randint(5, 15)):
                transaction_type = random.choice(['deposit', 'withdrawal'])
                amount = round(random.uniform(10, 2000), 2)
                if transaction_type == 'withdrawal' and account.balance < amount:
                    amount = round(account.balance * 0.5, 2)

                transaction = Transaction(
                    transaction_type=transaction_type,
                    amount=amount if transaction_type == 'deposit' else -amount,
                    description=fake.sentence(nb_words=6),
                    account_id=account.id,
                    location=fake.city(),
                    ip_address=fake.ipv4(),
                    timestamp=datetime.utcnow() - timedelta(days=random.randint(0, 90))
                )

                fraud_score = random.uniform(0, 1)
                transaction.fraud_score = fraud_score
                transaction.is_fraudulent = fraud_score > 0.8

                transactions.append(transaction)
                account.balance += transaction.amount

                if transaction.is_fraudulent:
                    db.session.add(FraudAlert(
                        transaction=transaction,
                        alert_type="Suspicious Transaction",
                        severity="high",
                        description=f"Automatically generated fraud alert (score: {fraud_score:.2f})"
                    ))

        db.session.add_all(transactions)
        db.session.commit()

        print("Creating subscription transactions...")
        subscription_transactions = []
        for sub in subscriptions:
            account = Account.query.get(sub.account_id)
            if account.balance >= sub.amount:
                trans = Transaction(
                    transaction_type="subscription",
                    amount=-sub.amount,
                    description=f"Subscription payment: {sub.name}",
                    account_id=account.id,
                    subscription_id=sub.id,
                    location=fake.city(),
                    ip_address=fake.ipv4(),
                    timestamp=datetime.utcnow() - timedelta(days=random.randint(0, 30))
                )

                fraud_score = random.uniform(0, 1)
                trans.fraud_score = fraud_score
                trans.is_fraudulent = fraud_score > 0.8

                subscription_transactions.append(trans)
                account.balance -= sub.amount

                if trans.is_fraudulent:
                    db.session.add(FraudAlert(
                        transaction=trans,
                        alert_type="Suspicious Subscription",
                        severity="high",
                        description=f"Automatically generated fraud alert (score: {fraud_score:.2f})"
                    ))

        db.session.add_all(subscription_transactions)
        db.session.commit()

        print("Creating inter-user transfers...")
        transfer_transactions = []
        for _ in range(100):
            sender_account = random.choice(accounts)
            receiver_account = random.choice([a for a in accounts if a.user_id != sender_account.user_id])

            if sender_account.balance < 50:
                continue

            amount = round(random.uniform(20, min(500, sender_account.balance)), 2)

            withdrawal = Transaction(
                transaction_type='transfer',
                amount=-amount,
                description=f"Transfer to {receiver_account.account_number}",
                account_id=sender_account.id,
                recipient_account_id=receiver_account.id,
                location=fake.city(),
                ip_address=fake.ipv4(),
                timestamp=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            deposit = Transaction(
                transaction_type='transfer',
                amount=amount,
                description=f"Transfer from {sender_account.account_number}",
                account_id=receiver_account.id,
                recipient_account_id=sender_account.id,
                location=fake.city(),
                ip_address=fake.ipv4(),
                timestamp=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )

            fraud_score = random.uniform(0, 1)
            withdrawal.fraud_score = fraud_score
            withdrawal.is_fraudulent = fraud_score > 0.8
            deposit.fraud_score = fraud_score
            deposit.is_fraudulent = fraud_score > 0.8

            transfer_transactions.extend([withdrawal, deposit])

            sender_account.balance -= amount
            receiver_account.balance += amount

            if withdrawal.is_fraudulent:
                db.session.add(FraudAlert(
                    transaction=withdrawal,
                    alert_type="Suspicious Transfer",
                    severity="high",
                    description=f"Automatically generated fraud alert (score: {fraud_score:.2f})"
                ))

        db.session.add_all(transfer_transactions)
        db.session.commit()

        print("Setup complete! ✅")
        print(f"Created: {len(users)} users, {len(accounts)} accounts, {len(cards)} cards, {len(upis)} UPIs, {len(subscriptions)} subscriptions, {len(transactions) + len(subscription_transactions) + len(transfer_transactions)} transactions.")

        print("\nSample login credentials:")
        print(f"Admin -> username: admin | password: admin123")
        if len(users) > 1:
            sample_user = users[1]
            print(f"User -> username: {sample_user.username} | password: password123")


if __name__ == "__main__":
    main()
