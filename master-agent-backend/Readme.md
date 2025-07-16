# Master Agent - Complete Deployment Guide

## Overview

This guide provides complete instructions for deploying your Master Agent system, which includes a Python/Flask backend, React frontend, and voice notes functionality for task management, goal tracking, note-taking, and chat capabilities.

## System Architecture

### Backend (Python/Flask)
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: SQLite (development) / PostgreSQL (production)
- **Features**: RESTful API, CORS enabled, voice note transcription
- **Dependencies**: Flask, Flask-CORS, SQLAlchemy, SpeechRecognition, pydub

### Frontend (React)
- **Framework**: React with Vite
- **UI Library**: shadcn/ui components with Tailwind CSS
- **Features**: Responsive design, real-time chat, voice recording
- **Dependencies**: React, Tailwind CSS, Lucide icons, shadcn/ui

### Core Functionalities
1. **Chat Interface**: Natural language interaction with the Master Agent
2. **Task Management**: Create, update, delete, and track tasks with priorities and due dates
3. **Goal Tracking**: Set goals with progress tracking and target dates
4. **Note Taking**: Both text and voice notes with automatic transcription
5. **Dashboard**: Overview of all activities with statistics and recent items

## Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- pnpm package manager

### Backend Setup
1. Extract the backend package:
   ```bash
   tar -xzf master-agent-backend-complete.tar.gz
   cd master-agent-backend
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the Flask server:
   ```bash
   python src/main.py
   ```
   The backend will be available at `http://localhost:5000`

### Frontend Setup
1. Extract the frontend package:
   ```bash
   tar -xzf master-agent-frontend-complete.tar.gz
   cd master-agent-frontend
   ```

2. Install dependencies:
   ```bash
   pnpm install
   ```

3. Start the development server:
   ```bash
   pnpm run dev --host
   ```
   The frontend will be available at `http://localhost:5173`

## Google Cloud Platform (GCP) Deployment

### Prerequisites for GCP Deployment

#### Required GCP Services
Enable the following services in your GCP project:

```bash
# Enable required APIs
gcloud services enable compute.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sql-component.googleapis.com
gcloud services enable storage-component.googleapis.com
gcloud services enable appengine.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
gcloud services enable iam.googleapis.com
```

#### Set up gcloud CLI
```bash
# Install gcloud CLI (if not already installed)
# Follow instructions at: https://cloud.google.com/sdk/docs/install

# Initialize and authenticate
gcloud init
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### Backend Deployment (App Engine)

1. **Create app.yaml for App Engine**:
   ```yaml
   runtime: python311
   
   env_variables:
     FLASK_ENV: production
     DATABASE_URL: postgresql://username:password@/dbname?host=/cloudsql/PROJECT_ID:REGION:INSTANCE_NAME
   
   automatic_scaling:
     min_instances: 1
     max_instances: 10
   ```

2. **Set up Cloud SQL (PostgreSQL)**:
   ```bash
   # Create Cloud SQL instance
   gcloud sql instances create master-agent-db \
     --database-version=POSTGRES_14 \
     --tier=db-f1-micro \
     --region=us-central1
   
   # Create database
   gcloud sql databases create masteragent --instance=master-agent-db
   
   # Create user
   gcloud sql users create masteragent-user \
     --instance=master-agent-db \
     --password=YOUR_SECURE_PASSWORD
   ```

3. **Update Flask configuration for production**:
   ```python
   # In src/main.py, update database configuration
   import os
   
   if os.environ.get('FLASK_ENV') == 'production':
       app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
   else:
       app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
   ```

4. **Deploy to App Engine**:
   ```bash
   cd master-agent-backend
   gcloud app deploy
   ```

### Frontend Deployment (Cloud Storage + CDN)

1. **Build the React application**:
   ```bash
   cd master-agent-frontend
   pnpm run build
   ```

2. **Create Cloud Storage bucket**:
   ```bash
   # Create bucket for static hosting
   gsutil mb gs://YOUR_BUCKET_NAME
   
   # Make bucket publicly readable
   gsutil iam ch allUsers:objectViewer gs://YOUR_BUCKET_NAME
   
   # Enable website configuration
   gsutil web set -m index.html -e index.html gs://YOUR_BUCKET_NAME
   ```

3. **Upload built files**:
   ```bash
   gsutil -m rsync -r -d dist/ gs://YOUR_BUCKET_NAME
   ```

4. **Update API endpoint in frontend**:
   ```javascript
   // In src/App.jsx, update API_BASE_URL
   const API_BASE_URL = 'https://YOUR_PROJECT_ID.appspot.com/api'
   ```

### Domain Configuration (Optional)

1. **Set up custom domain**:
   ```bash
   # For App Engine backend
   gcloud app domain-mappings create api.yourdomain.com
   
   # For Cloud Storage frontend
   gcloud compute url-maps create web-map \
     --default-backend-bucket=YOUR_BUCKET_NAME
   ```

## Environment Variables

### Backend Environment Variables
```bash
FLASK_ENV=production
DATABASE_URL=postgresql://username:password@host:port/database
SECRET_KEY=your-secret-key-here
GOOGLE_CLOUD_PROJECT=your-project-id
```

### Frontend Environment Variables
```bash
VITE_API_BASE_URL=https://your-backend-url.com/api
```

## Security Considerations

### Backend Security
- Use environment variables for sensitive data
- Enable HTTPS in production
- Implement rate limiting for API endpoints
- Validate all user inputs
- Use secure session management

### Frontend Security
- Implement Content Security Policy (CSP)
- Use HTTPS for all communications
- Sanitize user inputs
- Implement proper authentication

## Monitoring and Logging

### GCP Monitoring Setup
```bash
# Enable monitoring
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com
```

### Application Logging
- Flask backend logs are automatically captured by GCP
- Frontend errors can be monitored using Google Analytics or custom logging

## Cost Estimation

### Monthly Costs (Estimated)
- **App Engine**: $20-50 (depending on usage)
- **Cloud SQL**: $15-30 (db-f1-micro instance)
- **Cloud Storage**: $1-5 (for static files)
- **Cloud Build**: $0-10 (free tier covers most usage)
- **Total**: $36-95 per month

### Cost Optimization Tips
- Use App Engine automatic scaling
- Choose appropriate Cloud SQL tier
- Enable Cloud CDN for better performance and lower costs
- Monitor usage with GCP billing alerts

## Troubleshooting

### Common Issues

1. **Database Connection Issues**:
   - Verify Cloud SQL instance is running
   - Check connection string format
   - Ensure proper IAM permissions

2. **CORS Issues**:
   - Verify Flask-CORS is properly configured
   - Check frontend API endpoint URLs

3. **Voice Notes Not Working**:
   - Ensure microphone permissions are granted
   - Check SpeechRecognition dependencies are installed
   - Verify audio file upload size limits

4. **Build Failures**:
   - Check all dependencies are listed in requirements.txt
   - Verify Python version compatibility
   - Ensure all environment variables are set

### Debugging Commands
```bash
# Check App Engine logs
gcloud app logs tail -s default

# Check Cloud SQL status
gcloud sql instances describe master-agent-db

# Test API endpoints
curl -X GET https://YOUR_PROJECT_ID.appspot.com/api/dashboard?user_id=1
```

## Maintenance

### Regular Tasks
- Monitor application performance
- Update dependencies regularly
- Backup database regularly
- Review and rotate API keys
- Monitor costs and usage

### Database Backups
```bash
# Create database backup
gcloud sql backups create --instance=master-agent-db

# List backups
gcloud sql backups list --instance=master-agent-db
```

## API Documentation

### Core Endpoints

#### Chat
- `POST /api/chat` - Send message to Master Agent

#### Tasks
- `GET /api/tasks` - Get all tasks
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

#### Goals
- `GET /api/goals` - Get all goals
- `POST /api/goals` - Create new goal
- `PUT /api/goals/{id}` - Update goal
- `DELETE /api/goals/{id}` - Delete goal

#### Notes
- `GET /api/notes` - Get all notes
- `POST /api/notes` - Create text note
- `POST /api/notes/voice` - Upload voice note
- `PUT /api/notes/{id}` - Update note
- `DELETE /api/notes/{id}` - Delete note

#### Dashboard
- `GET /api/dashboard` - Get dashboard statistics

## Support and Updates

### Getting Help
- Check the troubleshooting section above
- Review GCP documentation for specific services
- Monitor application logs for error details

### Future Enhancements
- Integration with external calendar services
- Email and SMS notifications
- Advanced AI capabilities with LLM integration
- Mobile app development
- Multi-user support with authentication

## Conclusion

Your Master Agent system is now ready for deployment! This comprehensive system provides a solid foundation for personal productivity management with modern web technologies and cloud infrastructure.

For any issues or questions, refer to the troubleshooting section or check the application logs for detailed error information.