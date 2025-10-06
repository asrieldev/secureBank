## `(secureBankm)-> world := make(chan string, 1) ; world <- "Banking with AI/ML Security"`


## `Project Discription`

**Secure Bank** is a **Python Flask** web application with **real-time fraud detection** powered by **machine learning (Random Forest & Isolation Forest)**. It offers a full banking experience, including secure user authentication, account management, transaction processing, and advanced admin oversight.

The system is designed for **security, transparency, and scalability**, ensuring financial operations are protected while delivering detailed transaction analytics and fraud prevention.

---

### `Key Features`

* **Secure User Authentication** – Password hashing, encrypted sessions, and role-based access control.
* **Account Management** – Support for savings, checking, and credit accounts with real-time balance tracking.
* **Transaction Processing** – Instant, validated fund transfers.
* **Transaction History** – Full audit trail with analytics.
* **Fraud Detection** – Real-time risk scoring with machine learning models.
* **Admin Dashboard** – Manage fraud alerts, monitor transactions, and handle user accounts.

---

### `Fraud Detection Highlights`

* **Machine Learning Models** – Random Forest & Isolation Forest for supervised and anomaly detection.
* **Real-time Risk Analysis** – Instant scoring of every transaction.
* **Multi-factor Assessment** – Amount, time, location, frequency, and behavioral patterns.
* **Automated Alerts** – Suspicious transactions trigger immediate notifications.
* **Persistent Models** – Models stored and loaded automatically for consistent accuracy.

---

### `Technical Stack`

* **Programming & Scripting:** Python, SQL, Bash
* **Frameworks:** Flask, Scikit-learn
* **Machine Learning:** Supervised & Unsupervised Learning, Fraud Detection Models
* **Data & Database:** SQLite (development), PostgreSQL/MySQL (production)
* **Security:** Bcrypt, Flask-Login, Role-based Access Control
---

### `Project Structure`

```
securBank/
├── app.py
├── fraud_detection.py
├── requirements.txt
├── setup.py
├── api/
│   └── init-db.py
├── instance/
│   └── banking_system.db
├── migrations
├── models/
│   ├── encoders.pkl
│   ├── fraud_detection_model.pkl
│   ├── isolation_forest.pkl
│   └── scaler.pkl
├── static
├── templates/
│   ├── account_detail.html
│   ├── admin_alerts.html
│   ├── base.html
│   ├── cards.html
│   ├── dashboard.html
│   ├── deposit.html
│   ├── index.html
│   ├── login.html
│   ├── profile.html
│   ├── register.html
│   ├── statements.html
│   ├── subscriptions.html
│   ├── transfer.html
│   ├── upis.html
│   ├── verify_statement_otp.html
│   └── withdraw.html
├── README.md

```

---

### `Setup Instructions`

```bash
# Clone repo
git clone <repo-url>
cd secureBank

# Install dependencies
pip install -r requirements.txt

# Initialize database
python api/init-db.py

# Run app
flask run/ python app.py

# Visit:
http://127.0.0.1:5000](http://127.0.0.1:5000)
```
---

### `Testing Scenarios`

* **Normal Transactions:** Processed without alerts (Risk Score: 0–30%)
* **Suspicious Transactions:** Trigger medium alerts (Risk Score: 30–70%)
* **High-Risk Transactions:** Immediate admin alerts (Risk Score: 70–100%)

---

### `Future Enhancements`

* Mobile-responsive banking dashboard
* Real-time fraud notifications
* API integration with external banking services
* Deep learning-based fraud detection
* Biometric authentication for transactions

---

### `Developers & Contributors`

* *By Ashriel & Danielle & Abdul*
---

