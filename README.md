# Banking Transaction System with Fraud Detection

A comprehensive banking transaction system built with Python Flask and Scikit-learn, featuring real-time fraud detection using machine learning algorithms. This system provides a complete banking experience with secure user authentication, account management, transaction processing, and AI-powered fraud detection.

## 🚀 Features

### Core Banking Features

- **User Authentication & Registration** - Secure user management with password hashing
- **Account Management** - Multiple account types (savings, checking, credit) with real-time balance tracking
- **Transaction Processing** - Real-time money transfers between accounts with validation
- **Transaction History** - Complete audit trail of all transactions with detailed analytics
- **Dashboard Analytics** - Interactive charts showing transaction patterns and account performance

### Advanced Fraud Detection

- **Machine Learning Models** - Random Forest and Isolation Forest algorithms for comprehensive fraud detection
- **Real-time Analysis** - Instant fraud scoring for every transaction with risk assessment
- **Multi-factor Risk Assessment** - Location, time, amount, frequency, and behavioral analysis
- **Fraud Alerts** - Automated alerting system for suspicious activities with admin management
- **Model Persistence** - Trained models are saved and loaded automatically for consistent performance

### Admin Dashboard

- **Fraud Alert Management** - Monitor, investigate, and resolve fraud alerts
- **Analytics Dashboard** - Visual charts and statistics for system monitoring
- **Transaction Monitoring** - Real-time transaction oversight with detailed reporting
- **User Management** - View and manage user accounts and activities

### Security Features

- **Encrypted Sessions** - Secure user sessions with Flask-Login
- **Password Hashing** - Bcrypt-based password security
- **Input Validation** - Comprehensive form validation and sanitization
- **Access Control** - Role-based permissions for users and administrators

## 🛠️ Technology Stack

- **Backend**: Python Flask (Web Framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Machine Learning**: Scikit-learn (Random Forest, Isolation Forest)
- **Frontend**: Bootstrap 5, Chart.js, HTML5/CSS3
- **Authentication**: Flask-Login
- **Data Processing**: Pandas, NumPy
- **Development**: Python 3.8+

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Modern web browser (Chrome, Firefox, Safari, Edge)

## 🔧 Quick Start Installation

1. **Navigate to the project directory**

   ```bash
   cd "path/to/banking-transaction-system"
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database and create sample data**

   ```bash
   python setup.py
   ```

4. **Run the application**

   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser and go to `http://127.0.0.1:5000`
   - Login with the credentials provided by the setup script

## 👥 Default Users

After running the setup script, you'll have access to these accounts:

### Admin User

- **Username**: `admin`
- **Password**: `admin123`
- **Access**: Full admin privileges, fraud alert management, system analytics

### Regular Users

- **Username**: `john_doe`, `jane_smith`, `bob_wilson`, `alice_brown`, `charlie_davis`
- **Password**: `password123`
- **Access**: Standard banking features, account management, transfers

## 🎯 User Guide

### For Regular Users

#### 1. Getting Started

- **Login**: Use your credentials to access the system
- **Dashboard**: View your accounts, recent transactions, and account summaries
- **Navigation**: Use the top navigation bar to access different features

#### 2. Account Management

- **View Accounts**: See all your accounts with current balances
- **Account Details**: Click on any account to view detailed transaction history
- **Balance Tracking**: Real-time balance updates after transactions

#### 3. Making Transfers

- **Navigate**: Go to the "Transfer" page from the main menu
- **Select Account**: Choose your source account
- **Enter Details**: Provide recipient account number and amount
- **Fraud Check**: View real-time fraud detection analysis
- **Confirm**: Review and complete the transfer

#### 4. Transaction Monitoring

- **Recent Transactions**: View recent transactions on the dashboard
- **Fraud Scores**: Check fraud risk scores for each transaction
- **Transaction History**: Access complete transaction logs

### For Administrators

#### 1. Admin Access

- **Login**: Use admin credentials to access administrative features
- **Admin Menu**: Navigate to "Fraud Alerts" for administrative functions

#### 2. Fraud Alert Management

- **View Alerts**: See all active and resolved fraud alerts
- **Filter Options**: Filter by severity, type, date, and status
- **Investigation**: Review alert details and transaction information
- **Resolution**: Mark alerts as resolved with notes

#### 3. System Analytics

- **Fraud Statistics**: View fraud detection performance metrics
- **Alert Trends**: Monitor alert patterns over time
- **Transaction Analysis**: Analyze overall transaction patterns

## 🔍 Fraud Detection System

### How It Works

The fraud detection system employs a dual-model approach for comprehensive security:

#### 1. Random Forest Classifier

- **Purpose**: Primary fraud detection using supervised learning
- **Training**: Trained on synthetic transaction data with labeled fraud cases
- **Features**: Analyzes multiple transaction characteristics simultaneously
- **Output**: Provides probability scores for fraud likelihood

#### 2. Isolation Forest

- **Purpose**: Anomaly detection using unsupervised learning
- **Function**: Identifies unusual transaction patterns that don't fit normal behavior
- **Advantage**: Works alongside Random Forest for enhanced detection
- **Output**: Anomaly scores for transaction patterns

### Features Analyzed

- **Transaction Amount** - Unusually high or low amounts relative to account history
- **Time Patterns** - Transactions at unusual hours or rapid succession
- **Location Data** - Geographic risk assessment based on transaction location
- **IP Address** - Network-based risk factors and location verification
- **Transaction Frequency** - Rapid successive transactions indicating potential fraud
- **Account Age** - Risk assessment based on account establishment time
- **Day of Week** - Weekend vs. weekday transaction patterns
- **Amount Patterns** - Unusual transaction amounts compared to user history

### Risk Scoring System

- **Low Risk (0-30%)** - Normal transaction patterns, proceed normally
- **Medium Risk (30-70%)** - Some suspicious indicators, may require review
- **High Risk (70-100%)** - Multiple fraud indicators, immediate attention required

### Alert Management

- **Automatic Detection**: System automatically flags suspicious transactions
- **Manual Review**: Administrators can review and resolve alerts
- **Status Tracking**: Track alert status from detection to resolution
- **Notes System**: Add investigation notes and resolution details

## 📊 System Architecture

### File Structure

```
banking-transaction-system/
├── app.py                 # Main Flask application
├── fraud_detection.py     # Fraud detection models and logic
├── setup.py              # Database initialization and sample data
├── requirements.txt      # Python dependencies
├── models/               # SQLAlchemy database models
│   ├── __init__.py
│   ├── user.py
│   ├── account.py
│   ├── transaction.py
│   └── fraud_alert.py
├── templates/            # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── transfer.html
│   ├── account.html
│   └── admin/
│       └── alerts.html
└── instance/             # Database files
    └── banking_system.db
```

### Database Schema

#### Users Table

- User authentication and profile information
- Password hashing for security
- Role-based access control

#### Accounts Table

- Multiple account types per user
- Real-time balance tracking
- Account status management

#### Transactions Table

- Complete transaction records
- Fraud detection scores
- Audit trail for compliance

#### Fraud Alerts Table

- Alert management and tracking
- Investigation notes
- Resolution status

## 🔧 Configuration

### Environment Setup

The system uses default configurations suitable for development. For production deployment:

1. **Create environment file**

   ```bash
   # Create .env file
   echo "SECRET_KEY=your-production-secret-key" > .env
   echo "DATABASE_URL=sqlite:///banking_system.db" >> .env
   echo "FLASK_ENV=production" >> .env
   ```

2. **Database Configuration**
   - Default: SQLite (suitable for development)
   - Production: PostgreSQL or MySQL recommended
   - Update DATABASE_URL in .env file

### Model Configuration

Fraud detection models are automatically:

- **Trained**: During initial setup with synthetic data
- **Saved**: To disk for persistence across application restarts
- **Loaded**: Automatically when the application starts

## 🧪 Testing the System

### Manual Testing Scenarios

#### 1. Normal Transactions

- Login as a regular user
- Make small transfers (< $100)
- Verify normal fraud scores (0-30%)

#### 2. Suspicious Transactions

- Make large transfers (> $1000)
- Make transfers at unusual hours (2-5 AM)
- Create rapid successive transactions
- Verify elevated fraud scores (30-70%)

#### 3. High-Risk Transactions

- Combine multiple suspicious factors
- Verify high fraud scores (70-100%)
- Check admin alerts dashboard

#### 4. Admin Functions

- Login as admin user
- Monitor fraud alerts
- Resolve alerts with notes
- Verify alert status changes

### Expected Behaviors

- **Fraud Detection**: Should flag suspicious transactions automatically
- **Alert Generation**: High-risk transactions should create admin alerts
- **User Experience**: Normal transactions should proceed smoothly
- **Admin Dashboard**: Should show all alerts with proper filtering

## 📈 Performance Metrics

- **Response Time**: < 1 second for fraud detection analysis
- **Model Accuracy**: High precision fraud detection with low false positives
- **Scalability**: Handles multiple concurrent users and transactions
- **Memory Usage**: Optimized for efficient resource utilization

## 🔒 Security Features

### Data Protection

- **Password Security**: Bcrypt hashing for all user passwords
- **Session Management**: Secure session handling with Flask-Login
- **Input Validation**: Comprehensive form validation and sanitization
- **SQL Injection Protection**: SQLAlchemy ORM prevents injection attacks

### Fraud Prevention

- **Real-time Monitoring**: Every transaction is analyzed for fraud
- **Multi-factor Assessment**: Multiple risk factors considered simultaneously
- **Automated Alerts**: Immediate notification of suspicious activities
- **Manual Review**: Administrative oversight for complex cases

### Access Control

- **Role-based Permissions**: Different access levels for users and admins
- **Session Security**: Secure logout and session management
- **Authentication**: Required login for all protected routes

## 🚀 Deployment Options

### Development Deployment

```bash
# Current setup - suitable for development
python app.py
```

### Production Deployment

#### Option 1: Gunicorn

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Option 2: Docker

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Database Errors

- **Solution**: Run `python setup.py` to reinitialize the database
- **Check**: Ensure write permissions in the project directory

#### 2. Model Loading Errors

- **Solution**: Delete existing models and restart the application
- **Check**: Verify fraud_detection.py has proper error handling

#### 3. Import Errors

- **Solution**: Install all dependencies with `pip install -r requirements.txt`
- **Check**: Ensure Python 3.8+ is being used

#### 4. Port Already in Use

- **Solution**: Change port in app.py or kill existing process
- **Alternative**: Use `python app.py --port 5001`

### Performance Optimization

- **Database**: Consider using PostgreSQL for large datasets
- **Caching**: Implement Redis for session and model caching
- **Load Balancing**: Use multiple worker processes for high traffic

## 🔄 Maintenance

### Regular Tasks

- **Dependency Updates**: Keep packages updated for security
- **Model Retraining**: Retrain fraud detection models monthly
- **Database Backups**: Regular backups of transaction data
- **Security Reviews**: Periodic security assessments

### Model Maintenance

- **Accuracy Monitoring**: Track fraud detection accuracy
- **False Positive Analysis**: Review and adjust detection thresholds
- **Feature Engineering**: Update features based on new fraud patterns
- **Performance Tuning**: Optimize model parameters

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Check the troubleshooting section above
- Review the code comments for implementation details

## 📊 System Status

### Current Implementation Status

- ✅ User authentication and registration
- ✅ Account management and transactions
- ✅ Fraud detection with ML models
- ✅ Admin dashboard and alert management
- ✅ Interactive analytics and charts
- ✅ Database persistence and model saving
- ✅ Production-ready deployment options

### Future Enhancements

- 🔄 Real-time notifications
- 🔄 Advanced analytics dashboard
- 🔄 API endpoints for external integration
- 🔄 Mobile-responsive design improvements
- 🔄 Enhanced security features

---

**Note**: This is a demonstration system showcasing banking and fraud detection capabilities. For production use in financial institutions, implement additional security measures, proper logging, compliance with financial regulations (PCI DSS, SOX, etc.), and thorough testing procedures.

**Version**: 1.0.0  
**Last Updated**: December 2024  
**Python Version**: 3.8+  
**Flask Version**: 2.0+
