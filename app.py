from flask import Flask, render_template, send_file, session, request, redirect, url_for
from PIL import Image, ImageDraw
import hashlib
import io
import json
import base64
import os
import uuid
from openai import OpenAI
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from PyPDF2 import PdfReader

load_dotenv()

api_key = os.environ.get('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Check your .env file.")

client = OpenAI(api_key=api_key)
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key')

USER_STORE_FILE = os.path.join(os.path.dirname(__file__), 'user_store.json')
USER_KEYS = {}

if not os.path.exists(USER_STORE_FILE):
    with open(USER_STORE_FILE, 'w', encoding='utf-8') as store_file:
        json.dump({}, store_file)


def load_user_store():
    with open(USER_STORE_FILE, 'r', encoding='utf-8') as store_file:
        return json.load(store_file)


def save_user_store(store):
    with open(USER_STORE_FILE, 'w', encoding='utf-8') as store_file:
        json.dump(store, store_file, indent=2)


def derive_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 200_000).hex()


def encrypt_profile(profile, key):
    payload = json.dumps(profile).encode('utf-8')
    return Fernet(key).encrypt(payload).decode('utf-8')


def decrypt_profile(token, key):
    payload = Fernet(key).decrypt(token.encode('utf-8'))
    return json.loads(payload.decode('utf-8'))


def extract_resume_text(file_storage):
    filename = file_storage.filename or ''
    data = file_storage.read()
    if filename.lower().endswith('.txt'):
        return data.decode('utf-8', errors='ignore').strip()
    if filename.lower().endswith('.pdf'):
        reader = PdfReader(io.BytesIO(data))
        text = []
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text.append(content)
        return '\n'.join(text).strip()
    return None


def generate_talking_points_from_resume(resume_text):
    prompt = f"Based on this resume text, generate 3-5 concise talking points for personal branding and networking conversations. Return each point as plain text without any numbering, bullets, dashes, or prefixes. Just the talking point text. Resume text: {resume_text}"
    try:
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=400
        )
        points = response.choices[0].message.content.strip().split('\n')
        return [point.strip('- ').strip() for point in points if point.strip()]
    except Exception as e:
        return [f"Error generating talking points: {e}"]


def generate_suggestions_from_resume(resume_text):
    prompt = f"Based on this resume text, generate 3-5 actionable suggestions for what to add to their resume and next career steps. Focus on skills to develop, experiences to gain, and career advancement opportunities. Return each suggestion as plain text without any numbering, bullets, dashes, or prefixes. Just the suggestion text. Resume text: {resume_text}"
    try:
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=400
        )
        suggestions = response.choices[0].message.content.strip().split('\n')
        return [suggestion.strip('- ').strip() for suggestion in suggestions if suggestion.strip()]
    except Exception as e:
        return [f"Error generating suggestions: {e}"]


def generate_brand_headlines_from_resume(resume_text):
    prompt = f"""
Based on this resume text:
{resume_text}

Generate 3 memorable LinkedIn-style personal brand headlines.

Rules:
- Use a format like: Skill | Identity | Interest
- Make them distinct, concise, and professional
- Do not use bold text
- Do not explain anything
- Each headline should be one line
"""
    try:
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=200
        )
        headlines = response.choices[0].message.content.strip().split('\n')
        return [headline.strip('- ').strip() for headline in headlines if headline.strip()]
    except Exception as e:
        return [f"Error generating brand headlines: {e}"]


def generate_value_prop_from_resume(resume_text):
    prompt = f"""
Based on this resume text:
{resume_text}

Write ONE clear personal value proposition.

Rules:
- Start with \"I help...\" or \"I bring...\"
- Be specific and professional
- Keep it under 20 words
- Do not use bold text
- Do not explain anything
"""
    try:
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating value proposition: {e}"


def generate_resume_outputs(resume_text):
    return {
        'talking_points': generate_talking_points_from_resume(resume_text),
        'brand_headlines': generate_brand_headlines_from_resume(resume_text),
        'value_prop': generate_value_prop_from_resume(resume_text),
        'suggestions': generate_suggestions_from_resume(resume_text)
    }


def get_current_user_record():
    store = load_user_store()
    user_id = session.get('user_id')
    return store.get(user_id), store, user_id


def get_user_key():
    token = session.get('session_token')
    return USER_KEYS.get(token)


def generate_avatar(profile):

    data = str(profile)

    hash_obj = hashlib.md5(data.encode())

    seed = int(hash_obj.hexdigest(), 16) % 1000000

    img = Image.new('RGB', (100, 100), color='white')

    draw = ImageDraw.Draw(img)

    r = (seed % 256)

    g = ((seed // 256) % 256)

    b = ((seed // 65536) % 256)

    draw.ellipse([10, 10, 90, 90], fill=(r, g, b))

    initial = profile['name'][0].upper()

    draw.text((45, 45), initial, fill='white')

    return img

def generate_talking_points(profile):

    prompt = f"Based on this person's profile: Name: {profile['name']}, Bio: {profile['bio']}, Skills: {', '.join(profile['skills'])}, Interests: {', '.join(profile['interests'])}, generate 3-5 concise talking points for personal branding and networking conversations. Return each point as plain text without any numbering, bullets, dashes, or prefixes. Just the talking point text."

    try:

        response = client.chat.completions.create(

            model="gpt-4o-mini",

            messages=[{"role": "user", "content": prompt}],

            max_tokens=400

        )

        points = response.choices[0].message.content.strip().split('\n')

        return [point.strip('- ').strip() for point in points if point.strip()]

    except Exception as e:

        return ["Error generating talking points: " + str(e)]

def generate_suggestions(profile):

    prompt = f"Based on this person's profile: Name: {profile['name']}, Bio: {profile['bio']}, Skills: {', '.join(profile['skills'])}, Interests: {', '.join(profile['interests'])}, generate 3-5 actionable suggestions for what to add to their resume and next career steps. Focus on skills to develop, experiences to gain, and career advancement opportunities. Return each suggestion as plain text without any numbering, bullets, dashes, or prefixes. Just the suggestion text."

    try:

        response = client.chat.completions.create(

            model="gpt-4o-mini",

            messages=[{"role": "user", "content": prompt}],

            max_tokens=400

        )

        suggestions = response.choices[0].message.content.strip().split('\n')

        return [suggestion.strip('- ').strip() for suggestion in suggestions if suggestion.strip()]

    except Exception as e:

        return ["Error generating suggestions: " + str(e)]

def generate_brand_headlines(profile):

    prompt = f"""
Based on this person's profile:
Name: {profile['name']}
Bio: {profile['bio']}
Skills: {', '.join(profile['skills'])}
Interests: {', '.join(profile['interests'])}

Generate 3 memorable LinkedIn-style personal brand headlines.

Rules:
- Use a format like: Skill | Identity | Interest
- Make them distinct, concise, and professional
- Do not use bold text
- Do not explain anything
- Each headline should be one line
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )

        headlines = response.choices[0].message.content.strip().split('\n')

        return [headline.strip('- ').strip() for headline in headlines if headline.strip()]

    except Exception as e:
        return ["Error generating brand headlines: " + str(e)]

def generate_value_prop(profile):

    prompt = f"""
Based on this person's profile:
Name: {profile['name']}
Bio: {profile['bio']}
Skills: {', '.join(profile['skills'])}
Interests: {', '.join(profile['interests'])}

Write ONE clear personal value proposition.

Rules:
- Start with "I help..." or "I bring..."
- Be specific and professional
- Keep it under 20 words
- Do not use bold text
- Do not explain anything
"""

    try:

        response = client.chat.completions.create(

            model="gpt-4o-mini",

            messages=[{"role": "user", "content": prompt}],

            max_tokens=100

        )

        return response.choices[0].message.content.strip()

    except Exception as e:

        return "Error generating value proposition: " + str(e)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        if not email or not password:
            error = 'Enter both email and password.'
        else:
            store = load_user_store()
            user_id = hashlib.sha256(email.encode('utf-8')).hexdigest()
            if store.get(user_id):
                error = 'An account already exists. Please sign in.'
            else:
                salt = os.urandom(16)
                key = derive_key(password, salt)
                record = {
                    'email': email,
                    'password_hash': hash_password(password, salt),
                    'salt': base64.b64encode(salt).decode('utf-8'),
                    'encrypted_profile': None,
                    'encrypted_resume': None,
                    'encrypted_resume_outputs': None
                }
                store[user_id] = record
                save_user_store(store)
                session['user_id'] = user_id
                session['email'] = email
                session['session_token'] = str(uuid.uuid4())
                USER_KEYS[session['session_token']] = key
                return redirect(url_for('create'))
    return render_template('signup.html', error=error)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        if not email or not password:
            error = 'Enter both email and password.'
        else:
            store = load_user_store()
            user_id = hashlib.sha256(email.encode('utf-8')).hexdigest()
            record = store.get(user_id)
            if not record:
                error = 'No account found. Please create a new account.'
            else:
                salt = base64.b64decode(record['salt'])
                if record['password_hash'] != hash_password(password, salt):
                    error = 'Email or password is incorrect.'
                else:
                    key = derive_key(password, salt)
                    session['user_id'] = user_id
                    session['email'] = email
                    session['session_token'] = str(uuid.uuid4())
                    USER_KEYS[session['session_token']] = key
                    if record.get('encrypted_profile'):
                        return redirect(url_for('profile'))
                    return redirect(url_for('create'))
    return render_template('signin.html', error=error)


@app.route('/signout')
def signout():
    token = session.pop('session_token', None)
    if token:
        USER_KEYS.pop(token, None)
    session.clear()
    return redirect(url_for('home'))


@app.route('/upload_resume', methods=['GET', 'POST'])
def upload_resume():
    key = get_user_key()
    if 'user_id' not in session or not key:
        return redirect(url_for('home'))

    record, store, user_id = get_current_user_record()
    if not record:
        return redirect(url_for('home'))

    error = None
    if request.method == 'POST':
        resume_file = request.files.get('resume')
        if not resume_file or resume_file.filename == '':
            error = 'Please select a resume file to upload.'
        else:
            resume_text = extract_resume_text(resume_file)
            if not resume_text:
                error = 'Upload failed. Supported file types: .txt, .pdf'
            else:
                record['encrypted_resume'] = encrypt_profile({'text': resume_text}, key)
                record['encrypted_resume_outputs'] = encrypt_profile(generate_resume_outputs(resume_text), key)
                store[user_id] = record
                save_user_store(store)
                session['output_mode'] = 'resume'
                return redirect(url_for('profile'))
    return render_template('upload_resume.html', error=error, resume_exists=bool(record.get('encrypted_resume')))


@app.route('/use_resume')
def use_resume():
    key = get_user_key()
    if 'user_id' not in session or not key:
        return redirect(url_for('home'))
    record, store, user_id = get_current_user_record()
    if not record or not record.get('encrypted_resume'):
        return redirect(url_for('profile'))

    if not record.get('encrypted_resume_outputs'):
        resume_text = decrypt_profile(record['encrypted_resume'], key)['text']
        record['encrypted_resume_outputs'] = encrypt_profile(generate_resume_outputs(resume_text), key)
        store[user_id] = record
        save_user_store(store)

    session['output_mode'] = 'resume'
    return redirect(url_for('profile'))


@app.route('/use_form')
def use_form():
    key = get_user_key()
    if 'user_id' not in session or not key:
        return redirect(url_for('home'))
    session['output_mode'] = 'form'
    return redirect(url_for('profile'))


@app.route('/create', methods=['GET', 'POST'])
def create():
    key = get_user_key()
    if 'user_id' not in session or not key:
        return redirect(url_for('home'))

    if request.method == 'POST':
        skills = request.form.get('skills', '').split(',')
        interests = request.form.get('interests', '').split(',')
        profile = {
            'name': request.form.get('name', '').strip(),
            'bio': request.form.get('bio', '').strip(),
            'skills': [s.strip() for s in skills if s.strip()],
            'interests': [i.strip() for i in interests if i.strip()]
        }
        profile['talking_points'] = generate_talking_points(profile)
        profile['brand_headlines'] = generate_brand_headlines(profile)
        profile['value_prop'] = generate_value_prop(profile)
        profile['suggestions'] = generate_suggestions(profile)

        record, store, user_id = get_current_user_record()
        if not record:
            return redirect(url_for('home'))
        record['encrypted_profile'] = encrypt_profile(profile, key)
        store[user_id] = record
        save_user_store(store)
        return redirect(url_for('profile'))

    return render_template('create.html', email=session.get('email'))

@app.route('/profile')
def profile():
    key = get_user_key()
    if 'user_id' not in session or not key:
        return redirect(url_for('home'))

    record, store, user_id = get_current_user_record()
    if not record:
        return redirect(url_for('home'))

    output_mode = session.get('output_mode', 'form')
    has_form = bool(record.get('encrypted_profile'))
    has_resume = bool(record.get('encrypted_resume'))

    if output_mode == 'resume' and not has_resume:
        output_mode = 'form'
        session['output_mode'] = 'form'

    profile = None
    talking_points = []
    brand_headlines = []
    value_prop = ''

    if has_form:
        try:
            profile = decrypt_profile(record['encrypted_profile'], key)
        except Exception:
            return redirect(url_for('home'))
    else:
        profile = {
            'name': session.get('email', 'User').split('@')[0].title(),
            'bio': 'Profile information is not available. Resume-based outputs are shown below.',
            'skills': [],
            'interests': []
        }

    if output_mode == 'resume' and has_resume:
        if record.get('encrypted_resume_outputs'):
            resume_outputs = decrypt_profile(record['encrypted_resume_outputs'], key)
        else:
            resume_text = decrypt_profile(record['encrypted_resume'], key)['text']
            resume_outputs = generate_resume_outputs(resume_text)
            record['encrypted_resume_outputs'] = encrypt_profile(resume_outputs, key)
            store[user_id] = record
            save_user_store(store)
        talking_points = resume_outputs.get('talking_points', [])
        brand_headlines = resume_outputs.get('brand_headlines', [])
        value_prop = resume_outputs.get('value_prop', '')
        suggestions = resume_outputs.get('suggestions', [])
    else:
        talking_points = profile.get('talking_points', [])
        brand_headlines = profile.get('brand_headlines', [])
        value_prop = profile.get('value_prop', '')
        suggestions = profile.get('suggestions', [])

    return render_template(
        'index.html',
        profile=profile,
        output_mode=output_mode,
        has_resume=has_resume,
        has_form=has_form,
        talking_points=talking_points,
        brand_headlines=brand_headlines,
        value_prop=value_prop,
        suggestions=suggestions
    )

@app.route('/avatar')
def avatar():
    key = get_user_key()
    if 'user_id' not in session or not key:
        return redirect(url_for('home'))

    record, _, _ = get_current_user_record()
    if not record or not record.get('encrypted_profile'):
        return redirect(url_for('create'))

    profile = decrypt_profile(record['encrypted_profile'], key)
    img = generate_avatar(profile)
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':

    app.run(debug=True)