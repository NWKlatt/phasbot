from flask import Flask, request, jsonify, session
from openai import OpenAI
import yaml
import os

# Load the config.yaml file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

#Extract keys from YAML
openai_api_key = config['openaiapikey']
flask_secret_key = config['flask_secret_key']

#Initialize OpenAI API key
# openai.api_key = openai_api_key

app = Flask(__name__)
app.secret_key = flask_secret_key  # Use the secret key from YAML

# Route to initialize context
@app.route('/initialize_context', methods=['POST'])
def initialize_context():
    context = request.json.get('context', '')
    session['context'] = context
    return jsonify({'message': 'Context initialized'}), 200

# Route to handle queries
@app.route('/query', methods=['POST'])
def query():
    query_text = request.json.get('query', '')
    context = session.get('context', '')

    if not context:
        return jsonify({'error': 'Context not initialized'}), 400

    client = OpenAI(
        api_key = openai_api_key
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        max_tokens=150,
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": query_text}
        ]
    )
    
    return jsonify({'response': response.choices[0].message.content}), 200

if __name__ == '__main__':
    app.run(debug=True)
