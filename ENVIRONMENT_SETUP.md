# 🔧 Environment Variables Setup Guide

This guide will help you set up environment variables for your Banking Transaction System.

## 📋 Required Environment Variables

### Essential Variables

```env
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=your-database-connection-string
FLASK_ENV=production
```

### Optional Variables

```env
DEBUG=False
LOG_LEVEL=INFO
```

## 🏠 Local Development Setup

### Step 1: Create .env File

Copy the example file and customize it:

```bash
# Copy the example file
cp env.example .env

# Edit the .env file with your values
```

### Step 2: Customize .env File

```env
# Flask Configuration
SECRET_KEY=my-super-secret-key-for-development
FLASK_ENV=development

# Database Configuration (SQLite for local development)
DATABASE_URL=sqlite:///banking_system.db

# Optional
DEBUG=True
LOG_LEVEL=DEBUG
```

### Step 3: Generate a Secure Secret Key

```python
# Run this in Python to generate a secure key
import secrets
print(secrets.token_hex(32))
```

## ☁️ Vercel Deployment Setup

### Method 1: Vercel Dashboard (Recommended)

1. **Go to Vercel Dashboard**

   - Visit [vercel.com/dashboard](https://vercel.com/dashboard)
   - Select your project

2. **Navigate to Settings**

   - Click on "Settings" tab
   - Go to "Environment Variables" section

3. **Add Environment Variables**

   ```
   Name: SECRET_KEY
   Value: your-super-secret-key-here
   Environment: Production, Preview, Development
   ```

   ```
   Name: DATABASE_URL
   Value: postgresql://username:password@host:port/database
   Environment: Production, Preview, Development
   ```

   ```
   Name: FLASK_ENV
   Value: production
   Environment: Production, Preview, Development
   ```

### Method 2: Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Set environment variables
vercel env add SECRET_KEY
vercel env add DATABASE_URL
vercel env add FLASK_ENV

# Deploy with environment variables
vercel --prod
```

### Method 3: During Project Creation

When creating a new Vercel project:

1. Import your repository
2. In the configuration step, add environment variables
3. Deploy the project

## 🗄️ Database Connection Strings

### Vercel Postgres

```env
DATABASE_URL=postgresql://postgres:password@db.vercel.com:5432/banking_system
```

### Supabase

```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
```

### Neon

```env
DATABASE_URL=postgresql://username:password@ep-cool-name-123456.us-east-2.aws.neon.tech/banking_system
```

### Railway

```env
DATABASE_URL=postgresql://postgres:password@containers-us-west-1.railway.app:5432/railway
```

### Local PostgreSQL

```env
DATABASE_URL=postgresql://username:password@localhost:5432/banking_system
```

## 🔐 Generating Secure Keys

### Python Method

```python
import secrets
import string

# Generate a secure secret key
secret_key = secrets.token_hex(32)
print(f"SECRET_KEY={secret_key}")

# Generate a random password
password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
print(f"Password: {password}")
```

### Online Generators

- [Random.org](https://www.random.org/passwords/)
- [LastPass Password Generator](https://www.lastpass.com/features/password-generator)

## 🧪 Testing Environment Variables

### Local Testing

```bash
# Test if .env file is loaded
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('SECRET_KEY:', os.getenv('SECRET_KEY', 'Not set'))"
```

### Vercel Testing

```python
# Add this to your app.py temporarily for testing
@app.route('/test-env')
def test_env():
    return {
        'SECRET_KEY_SET': bool(os.getenv('SECRET_KEY')),
        'DATABASE_URL_SET': bool(os.getenv('DATABASE_URL')),
        'FLASK_ENV': os.getenv('FLASK_ENV', 'Not set')
    }
```

## 🔒 Security Best Practices

### 1. Never Commit Sensitive Data

```bash
# Add .env to .gitignore
echo ".env" >> .gitignore
echo "*.db" >> .gitignore
```

### 2. Use Strong Keys

- Generate keys with at least 32 characters
- Use a mix of letters, numbers, and symbols
- Never reuse keys across projects

### 3. Rotate Keys Regularly

- Change production keys every 3-6 months
- Update all environments when rotating keys
- Keep a secure backup of current keys

### 4. Environment-Specific Keys

- Use different keys for development, staging, and production
- Never use production keys in development

## 🚨 Troubleshooting

### Common Issues

#### 1. "SECRET_KEY not set" Error

**Solution**: Ensure SECRET_KEY is set in your environment variables

#### 2. Database Connection Errors

**Solution**:

- Check DATABASE_URL format
- Verify database credentials
- Ensure database is accessible

#### 3. Environment Variables Not Loading

**Solution**:

- Check file permissions on .env file
- Verify .env file is in project root
- Restart your application

#### 4. Vercel Environment Variables Not Working

**Solution**:

- Check environment variable names (case-sensitive)
- Ensure variables are set for correct environments
- Redeploy after adding variables

### Debug Commands

```bash
# Check if .env file exists
ls -la .env

# Check environment variables
python -c "import os; print(os.environ.get('SECRET_KEY', 'Not found'))"

# Test database connection
python -c "from app import app; print(app.config['SQLALCHEMY_DATABASE_URI'])"
```

## 📝 Environment Variables Reference

| Variable       | Required | Description                   | Example                               |
| -------------- | -------- | ----------------------------- | ------------------------------------- |
| `SECRET_KEY`   | Yes      | Flask secret key for sessions | `my-super-secret-key-123`             |
| `DATABASE_URL` | Yes      | Database connection string    | `postgresql://user:pass@host:port/db` |
| `FLASK_ENV`    | No       | Flask environment             | `production` or `development`         |
| `DEBUG`        | No       | Enable debug mode             | `True` or `False`                     |
| `LOG_LEVEL`    | No       | Logging level                 | `INFO`, `DEBUG`, `WARNING`            |

## 🎯 Quick Setup Checklist

- [ ] Create `.env` file for local development
- [ ] Generate secure `SECRET_KEY`
- [ ] Set up database connection string
- [ ] Add `.env` to `.gitignore`
- [ ] Configure Vercel environment variables
- [ ] Test environment variables locally
- [ ] Deploy and test on Vercel

## 🆘 Need Help?

### Local Development

- Check if `.env` file exists and is readable
- Verify environment variable names
- Restart your Flask application

### Vercel Deployment

- Check Vercel dashboard for environment variables
- Review deployment logs for errors
- Test with Vercel CLI locally

Your environment variables are now properly configured! 🚀
