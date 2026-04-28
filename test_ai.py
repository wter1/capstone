import os
from dotenv import load_dotenv
import openai

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('api_key')
client = openai.OpenAI()

def generate_talking_points(profile):
    prompt = f"Based on this person's profile: Name: {profile['name']}, Bio: {profile['bio']}, Skills: {', '.join(profile['skills'])}, Interests: {', '.join(profile['interests'])}, generate 3-5 concise talking points for personal branding and networking conversations."
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        points = response.choices[0].message.content.strip().split('\n')
        return [point.strip('- ').strip() for point in points if point.strip()]
    except Exception as e:
        return ["Error: " + str(e)]

# Test
profile = {
    'name': 'Alex Johnson',
    'bio': 'A creative marketing professional with 5 years of experience in digital campaigns and brand strategy.',
    'skills': ['Digital Marketing', 'SEO', 'Content Creation', 'Analytics'],
    'interests': ['Photography', 'Travel', 'Technology Trends', 'Coffee Culture']
}

points = generate_talking_points(profile)
print(points)