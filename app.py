from flask import Flask, render_template, send_file, session, request, redirect, url_for

from PIL import Image, ImageDraw

import hashlib

import io

from openai import OpenAI

from dotenv import load_dotenv

import os

load_dotenv()

api_key = os.environ['OPENAI_API_KEY']
if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Check your .env file.")

client = OpenAI(api_key=api_key)


app = Flask(__name__)

app.secret_key = "dev-secret-key"

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

    prompt = f"Based on this person's profile: Name: {profile['name']}, Bio: {profile['bio']}, Skills: {', '.join(profile['skills'])}, Interests: {', '.join(profile['interests'])}, generate 3-5 concise talking points for personal branding and networking conversations. Do NOT include bold text."

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

@app.route('/create', methods=['GET', 'POST'])
def create():

    if request.method == 'POST':

        skills = request.form['skills'].split(',')

        interests = request.form['interests'].split(',')

        profile = {

            'name': request.form['name'],

            'bio': request.form['bio'],

            'skills': [s.strip() for s in skills],

            'interests': [i.strip() for i in interests]

        }

        profile['talking_points'] = generate_talking_points(profile)

        profile['brand_headlines'] = generate_brand_headlines(profile)

        profile['value_prop'] = generate_value_prop(profile)

        session['profile'] = profile

        return redirect(url_for('profile'))

    return render_template('create.html')

@app.route('/profile')
def profile():

    profile = session.get('profile', {

        'name': 'John Doe',

        'bio': 'Born in Idaho and currently a student at Bentley University majoring in business administration. I have a passion for fishing and long walks on the beach.',

        'skills': ['Proficient in Excel', 'R', 'SQL', 'Python'],

        'interests': ['Tech', 'Food', 'Parks', 'Franchises'],

        'talking_points': ['Highlight your technical skills in data analysis.', 'Share your passion for outdoor activities to connect personally.', 'Discuss your business administration background.']

    })

    return render_template('index.html', profile=profile)

@app.route('/avatar')
def avatar():

    profile = session.get('profile', {

        'name': 'John Doe',

        'bio': 'Born in Idaho and currently a student at Bentley University majoring in business administration. I have a passion for fishing and long walks on the beach.',

        'skills': ['Proficient in Excel', 'R', 'SQL', 'Python'],

        'interests': ['Tech', 'Food', 'Parks', 'Franchises'],

        'talking_points': ['Highlight your technical skills in data analysis.', 'Share your passion for outdoor activities to connect personally.', 'Discuss your business administration background.']

    })

    img = generate_avatar(profile)

    img_io = io.BytesIO()

    img.save(img_io, 'PNG')

    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':

    app.run(debug=True)