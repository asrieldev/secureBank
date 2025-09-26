# Vercel Deployment Guide for Banking Transaction System

This guide will help you deploy your Banking Transaction System with fraud detection on Vercel.

## 🚀 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub/GitLab Repository**: Your code should be in a Git repository
3. **Database**: You'll need a PostgreSQL database (Vercel Postgres or external)

## 📋 Deployment Steps

### Step 1: Prepare Your Repository

Your repository should now contain these Vercel-specific files:

- `vercel.json` - Vercel configuration
- `runtime.txt` - Python version specification
- `requirements.txt` - Updated with PostgreSQL support
- `setup_vercel.py` - Database initialization script

### Step 2: Set Up Database

#### Option A: Vercel Postgres (Recommended)

1. Go to your Vercel dashboard
2. Create a new project or select existing
3. Go to "Storage" tab
4. Create a new Postgres database
5. Copy the connection string

#### Option B: External PostgreSQL

Use services like:

- [Supabase](https://supabase.com) (Free tier available)
- [Neon](https://neon.tech) (Free tier available)
- [Railway](https://railway.app) (Free tier available)

### Step 3: Configure Environment Variables

In your Vercel project settings, add these environment variables:

```env
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://username:password@host:port/database
FLASK_ENV=production
```

### Step 4: Deploy to Vercel

#### Method 1: Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Follow the prompts to connect your repository
```

#### Method 2: GitHub Integration

1. Connect your GitHub repository to Vercel
2. Vercel will automatically deploy on every push
3. Set up environment variables in Vercel dashboard

#### Method 3: Manual Upload

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your Git repository
3. Configure environment variables
4. Deploy

### Step 5: Initialize Database

After deployment, you need to initialize the database:

#### Option A: Vercel Functions

Create a new file `api/init-db.py`:

```python
from http.server import BaseHTTPRequestHandler
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from setup_vercel import create_sample_data

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            create_sample_data()
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('Database initialized successfully!'.encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f'Error: {str(e)}'.encode())
```

Then visit: `https://your-app.vercel.app/api/init-db`

#### Option B: Local Setup

```bash
# Clone your repository
git clone <your-repo-url>
cd <your-repo>

# Set environment variables
export DATABASE_URL="your-postgres-connection-string"
export SECRET_KEY="your-secret-key"

# Run setup
python setup_vercel.py
```

## 🔧 Configuration Details

### vercel.json

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ],
  "env": {
    "FLASK_ENV": "production"
  },
  "functions": {
    "app.py": {
      "maxDuration": 30
    }
  }
}
```

### Database Configuration

The app automatically detects and configures the database:

- Uses PostgreSQL if `DATABASE_URL` is provided
- Falls back to SQLite for local development
- Handles connection string format conversion

## 🧪 Testing Your Deployment

### 1. Check Application Status

Visit your Vercel URL to ensure the app loads

### 2. Test User Registration/Login

- Try registering a new user
- Login with sample credentials:
  - Admin: `admin` / `admin123`
  - User: `john_doe` / `password123`

### 3. Test Core Features

- Create accounts
- Make transactions
- Check fraud detection
- Access admin dashboard

### 4. Monitor Logs

Check Vercel function logs for any errors:

```bash
vercel logs your-app-name
```

## 🔒 Security Considerations

### Environment Variables

- Never commit sensitive data to your repository
- Use Vercel's environment variable system
- Rotate secrets regularly

### Database Security

- Use strong database passwords
- Enable SSL connections
- Restrict database access

### Application Security

- The app uses bcrypt for password hashing
- Sessions are managed securely
- Input validation is implemented

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Connection Errors

**Error**: `psycopg2.OperationalError`
**Solution**:

- Check your `DATABASE_URL` format
- Ensure database is accessible from Vercel
- Verify SSL settings

#### 2. Import Errors

**Error**: `ModuleNotFoundError`
**Solution**:

- Check `requirements.txt` includes all dependencies
- Ensure Python version compatibility
- Verify file paths

#### 3. Function Timeout

**Error**: `Function execution timeout`
**Solution**:

- Increase `maxDuration` in `vercel.json`
- Optimize database queries
- Consider caching strategies

#### 4. Model Loading Issues

**Error**: `FileNotFoundError` for model files
**Solution**:

- Ensure model files are in the repository
- Check file paths in `fraud_detection.py`
- Consider using environment variables for model paths

### Debug Commands

```bash
# Check Vercel logs
vercel logs

# Test locally with Vercel
vercel dev

# Check function status
vercel ls
```

## 📊 Performance Optimization

### Database Optimization

- Use connection pooling
- Implement caching for frequently accessed data
- Optimize database queries

### Application Optimization

- Enable gzip compression
- Use CDN for static assets
- Implement caching strategies

### Vercel-Specific

- Use edge functions for simple operations
- Implement proper error handling
- Monitor function execution times

## 🔄 Continuous Deployment

### Automatic Deployments

1. Connect your Git repository to Vercel
2. Every push to main branch triggers deployment
3. Set up preview deployments for pull requests

### Environment Management

- Use different databases for staging/production
- Set up environment-specific variables
- Implement proper testing before deployment

## 📈 Monitoring and Analytics

### Vercel Analytics

- Monitor function performance
- Track error rates
- Analyze user behavior

### Application Monitoring

- Implement logging for fraud detection
- Monitor database performance
- Track user activity

## 🎯 Best Practices

### Code Organization

- Keep functions small and focused
- Implement proper error handling
- Use environment variables for configuration

### Database Management

- Use migrations for schema changes
- Implement proper backup strategies
- Monitor database performance

### Security

- Regularly update dependencies
- Implement rate limiting
- Use HTTPS for all connections

## 🆘 Support

### Vercel Support

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Community](https://github.com/vercel/vercel/discussions)
- [Vercel Support](https://vercel.com/support)

### Application Support

- Check the main README.md for application-specific help
- Review error logs in Vercel dashboard
- Test locally before deploying

---

## 🎉 Success Checklist

- [ ] Repository contains all Vercel configuration files
- [ ] Database is set up and accessible
- [ ] Environment variables are configured
- [ ] Application deploys successfully
- [ ] Database is initialized with sample data
- [ ] All features work correctly
- [ ] Security measures are in place
- [ ] Monitoring is set up

Your Banking Transaction System is now ready for production use on Vercel! 🚀
