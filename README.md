# ProPrelims – Competitive Exam Quiz Platform

ProPrelims is a full–featured AI-driven exam preparation platform for SSC & UPSC aspirants built with Django, supporting multiple quiz types, Google OAuth login, paginated quiz navigation, blog system, user profiles with attempt history, and reporting functionality. It is live at https://proprelims.com

## Features
- Multiple Quiz Modes: Standard, Advance, Super quizzes
- Google OAuth and email login via Django-Allauth
- Interactive paginated quiz flow with HTMX
- Detailed result analytics and score tracking
- Blogs and recommended books section
- Real-time issue reporting via Telegram Bot API
- Search, filter, bookmarking, like system
- Responsive UI with Bootstrap
- Rate limiting & security enhancements

## Tech Stack
| Technology | Description |
|-----------|-------------|
| Backend | Django 5.2 |
| Auth | Django-Allauth, Google OAuth2 |
| DB | PostgreSQL |
| Frontend | HTMX + Bootstrap + Javascript + General HTML+CSS |
| Deployment | Fly.io |

## Installation Instructions
### Clone Repo
git clone https://github.com/yourusername/proprelims.git  
cd proprelims

### Create Environment
python3 -m venv venv  
source venv/bin/activate  

### Install Requirements
pip install -r requirements.txt  

### Environment Variables
Create .env file:  
SECRET=your-secret-key  
GOOGLE_OAUTH2_CLIENT_ID=xxxx.apps.googleusercontent.com  
GOOGLE_OAUTH2_CLIENT_SECRET=xxxx  
HOST1=localhost  
PASSWORD1=postgres_password  

### Run Migrations
python manage.py migrate  

### Run Server
python manage.py runserver

## Deployment (Example Fly.io)
flyctl launch
flyctl deploy
