import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os
from datetime import datetime, timedelta
import random

class FraudDetector:
    def __init__(self):
        self.rf_model = None
        self.isolation_model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = [
            'amount', 'hour_of_day', 'day_of_week', 'is_weekend',
            'amount_category', 'transaction_frequency', 'location_risk',
            'ip_risk', 'time_since_last_transaction', 'account_age_days'
        ]
        self.model_path = 'models/fraud_detection_model.pkl'
        self.scaler_path = 'models/scaler.pkl'
        self.encoders_path = 'models/encoders.pkl'
        
        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)
        
        # Load or train models
        self._load_or_train_models()
    
    def _load_or_train_models(self):
        """Load existing models or train new ones if they don't exist"""
        try:
            if os.path.exists(self.model_path) and os.path.exists('models/isolation_forest.pkl'):
                self.rf_model = joblib.load(self.model_path)
                self.isolation_model = joblib.load('models/isolation_forest.pkl')
                self.scaler = joblib.load(self.scaler_path)
                self.label_encoders = joblib.load(self.encoders_path)
                print("Loaded existing fraud detection models")
            else:
                print("Training new fraud detection models...")
                self._train_models()
        except Exception as e:
            print(f"Error loading models: {e}")
            print("Training new fraud detection models...")
            self._train_models()
    
    def _generate_synthetic_data(self, n_samples=10000):
        """Generate synthetic transaction data for training"""
        np.random.seed(42)
        
        data = []
        
        for i in range(n_samples):
            # Generate normal transaction patterns
            amount = np.random.exponential(100) + 10  # Most transactions are small
            hour = np.random.randint(0, 24)
            day_of_week = np.random.randint(0, 7)
            is_weekend = 1 if day_of_week >= 5 else 0
            
            # Amount categories
            if amount < 50:
                amount_category = 'small'
            elif amount < 500:
                amount_category = 'medium'
            else:
                amount_category = 'large'
            
            # Transaction frequency (simulated)
            transaction_frequency = np.random.poisson(3)  # Average 3 transactions per day
            
            # Location risk (simulated)
            location_risk = np.random.beta(2, 5)  # Most locations are low risk
            
            # IP risk (simulated)
            ip_risk = np.random.beta(1, 10)  # Most IPs are low risk
            
            # Time since last transaction (hours)
            time_since_last = np.random.exponential(8)  # Average 8 hours between transactions
            
            # Account age (days)
            account_age = np.random.exponential(365) + 30  # Average 1 year old account
            
            # Determine if this is fraudulent (based on risk factors)
            fraud_probability = (
                (amount > 1000) * 0.3 +
                (hour < 6 or hour > 22) * 0.2 +
                (location_risk > 0.8) * 0.4 +
                (ip_risk > 0.8) * 0.4 +
                (transaction_frequency > 10) * 0.3 +
                (time_since_last < 1) * 0.2
            )
            
            is_fraudulent = np.random.random() < fraud_probability
            
            data.append({
                'amount': amount,
                'hour_of_day': hour,
                'day_of_week': day_of_week,
                'is_weekend': is_weekend,
                'amount_category': amount_category,
                'transaction_frequency': transaction_frequency,
                'location_risk': location_risk,
                'ip_risk': ip_risk,
                'time_since_last_transaction': time_since_last,
                'account_age_days': account_age,
                'is_fraudulent': is_fraudulent
            })
        
        return pd.DataFrame(data)
    
    def _train_models(self):
        """Train the fraud detection models"""
        # Generate synthetic training data
        df = self._generate_synthetic_data(20000)
        
        # Prepare features
        X = df[self.feature_columns].copy()
        y = df['is_fraudulent']
        
        # Encode categorical variables
        for col in ['amount_category']:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col])
            self.label_encoders[col] = le
        
        # Scale numerical features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train Random Forest model
        self.rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        self.rf_model.fit(X_train, y_train)
        
        # Train Isolation Forest for anomaly detection
        self.isolation_model = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        self.isolation_model.fit(X_scaled)
        
        # Evaluate model
        y_pred = self.rf_model.predict(X_test)
        print("Random Forest Model Performance:")
        print(classification_report(y_test, y_pred))
        
        # Save models
        joblib.dump(self.rf_model, self.model_path)
        joblib.dump(self.isolation_model, 'models/isolation_forest.pkl')
        joblib.dump(self.scaler, self.scaler_path)
        joblib.dump(self.label_encoders, self.encoders_path)
        print("Models saved successfully")
    
    def _extract_features(self, transaction):
        """Extract features from a transaction for fraud detection"""
        # Basic transaction features
        amount = abs(transaction.amount)
        timestamp = transaction.timestamp
        hour_of_day = timestamp.hour
        day_of_week = timestamp.weekday()
        is_weekend = 1 if day_of_week >= 5 else 0
        
        # Amount categories
        if amount < 50:
            amount_category = 'small'
        elif amount < 500:
            amount_category = 'medium'
        else:
            amount_category = 'large'
        
        # Simulate transaction frequency (in real system, this would be calculated from database)
        transaction_frequency = random.randint(1, 20)
        
        # Location risk (simulated - in real system, this would be based on known risky locations)
        location_risk = random.betavariate(2, 5)
        
        # IP risk (simulated - in real system, this would be based on IP reputation)
        ip_risk = random.betavariate(1, 10)
        
        # Time since last transaction (simulated)
        time_since_last = random.expovariate(1/8)
        
        # Account age (simulated - in real system, this would be calculated from account creation date)
        account_age = random.expovariate(1/365) + 30
        
        return {
            'amount': amount,
            'hour_of_day': hour_of_day,
            'day_of_week': day_of_week,
            'is_weekend': is_weekend,
            'amount_category': amount_category,
            'transaction_frequency': transaction_frequency,
            'location_risk': location_risk,
            'ip_risk': ip_risk,
            'time_since_last_transaction': time_since_last,
            'account_age_days': account_age
        }
    
    def predict_fraud(self, transaction):
        """Predict fraud probability for a transaction"""
        try:
            # Extract features
            features = self._extract_features(transaction)
            
            # Create feature vector as DataFrame for correct feature names
            feature_vector = []
            for col in self.feature_columns:
                if col == 'amount_category':
                    # Encode categorical variable
                    le = self.label_encoders[col]
                    feature_vector.append(le.transform([features[col]])[0])
                else:
                    feature_vector.append(features[col])
            feature_df = pd.DataFrame([feature_vector], columns=self.feature_columns)
            
            # Scale features
            feature_vector_scaled = self.scaler.transform(feature_df)
            
            # Get fraud probability from Random Forest
            fraud_probability = self.rf_model.predict_proba(feature_vector_scaled)[0][1]
            
            # Get anomaly score from Isolation Forest
            anomaly_score = self.isolation_model.decision_function(feature_vector_scaled)[0]
            
            # Combine both scores (higher values indicate more suspicious)
            combined_score = (fraud_probability + (1 - anomaly_score)) / 2
            
            return combined_score
            
        except Exception as e:
            print(f"Error in fraud prediction: {e}")
            return 0.5  # Default to medium risk if error occurs
    
    def get_fraud_indicators(self, transaction):
        """Get detailed fraud indicators for a transaction"""
        features = self._extract_features(transaction)
        indicators = []
        
        # High amount indicator
        if features['amount'] > 1000:
            indicators.append({
                'type': 'high_amount',
                'severity': 'medium',
                'description': f'Transaction amount (${features["amount"]:.2f}) is unusually high'
            })
        
        # Unusual time indicator
        if features['hour_of_day'] < 6 or features['hour_of_day'] > 22:
            indicators.append({
                'type': 'unusual_time',
                'severity': 'low',
                'description': f'Transaction at unusual hour: {features["hour_of_day"]}:00'
            })
        
        # High location risk
        if features['location_risk'] > 0.8:
            indicators.append({
                'type': 'high_location_risk',
                'severity': 'high',
                'description': 'Transaction from high-risk location'
            })
        
        # High IP risk
        if features['ip_risk'] > 0.8:
            indicators.append({
                'type': 'high_ip_risk',
                'severity': 'high',
                'description': 'Transaction from high-risk IP address'
            })
        
        # High transaction frequency
        if features['transaction_frequency'] > 10:
            indicators.append({
                'type': 'high_frequency',
                'severity': 'medium',
                'description': f'High transaction frequency: {features["transaction_frequency"]} transactions'
            })
        
        # Rapid successive transactions
        if features['time_since_last_transaction'] < 1:
            indicators.append({
                'type': 'rapid_transactions',
                'severity': 'medium',
                'description': 'Transaction occurred within 1 hour of previous transaction'
            })
        
        return indicators
    
    def retrain_models(self, new_data=None):
        """Retrain models with new data"""
        print("Retraining fraud detection models...")
        self._train_models()
        print("Models retrained successfully") 