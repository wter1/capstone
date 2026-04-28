# capstone
This the final project for the Babson course, OIM3640.
I am the only member of my team.

## Minime App - Personal Profile

A simple Flask web app for creating and displaying a personalized self-marketing profile with unique avatars.

### Features (MVP)
- User input form to create profile (name, bio, skills, interests)
- Procedurally generated unique avatar based on profile data
- AI-generated talking points for personal branding and networking
- Static profile display with sections: About Me, Skills, Interests, Talking Points
- Professional styling and responsive design
- Session-based data storage
- Tabbed navigation
- Responsive design
- Printable profile

### Setup and Run Locally
1. Ensure Python 3.12+ is installed.
2. Install dependencies: `pip install -r requirements.txt`
3. Get an OpenAI API key from https://platform.openai.com/api-keys
4. Replace 'YOUR_OPENAI_API_KEY' in app.py with your actual API key
5. Run the app: `python app.py`
6. Open http://127.0.0.1:5000/ in your browser.
7. Click "Create My Profile" to fill out the form, then view your generated profile with AI talking points.

### Deploy to Render.com
1. Create a Git repository and push the code.
2. Sign up for Render.com.
3. Create a new Web Service, connect your Git repo.
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python app.py`
6. Deploy.

### Project Structure
- `app.py`: Flask application
- `templates/index.html`: Main template
- `static/styles.css`: Stylesheet
- `static/script.js`: JavaScript for tabs
- `requirements.txt`: Python dependencies
