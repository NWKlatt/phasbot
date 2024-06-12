from flask import Flask, request, jsonify, session
from flask_cors import CORS
from openai import OpenAI
import yaml
import os
import logging
import uuid

# Load the config.yaml file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Extract keys from YAML
openai_api_key = config['openaiapikey']
flask_secret_key = config['flask_secret_key']

# initialize logger:
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI API key
# openai.api_key = openai_api_key

app = Flask(__name__)
app.secret_key = flask_secret_key  # Use the secret key from YAML
CORS(app)  # Allow cross-origin requests

# Global dictionary to store context keyed by session ID
contexts = {}

# Route to initialize context
@app.route('/initialize_context', methods=['POST'])
def initialize_context():
    session_id = request.cookies.get('session')
    if not session_id:
        # log error
        logger.error('Session ID not found')
        # assign new session ID
        session_id = "default" # change this to uuid.uuid4()
        # return jsonify({'error': 'Session ID not found'}), 400

    with open('context.txt', 'r') as context_file:
        context = context_file.read()
        contexts[session_id] = context

    return jsonify({'message': 'Context initialized'}), 200

# Route to handle queries
@app.route('/query', methods=['POST'])
def query():
    session_id = request.cookies.get('session')
    if not session_id:
        # log error
        logger.error('Session ID not found')
        # assign new session ID
        session_id = "default" # change this to uuid.uuid4() but read from initial context
        # return jsonify({'error': 'Session ID not found'}), 400

    # query_text = request.json.get('query', '')
    context = contexts.get(session_id, '')

    if not context:
        return jsonify({'error': 'Context not initialized'}), 400
    behaviors = request.json.get('behaviors', '')
    query_text = 'The ghost exhibits the following behaviors:'
    for behavior in behaviors:
        query_text += f'\n- {behavior}'
    query_text += '\n\nWhat is the ghost type? Only respond with the ghost type.'
    client = OpenAI(
        api_key = openai_api_key
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=150,
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": query_text}
        ]
    )
    
    return jsonify({'response': response.choices[0].message.content}), 200

if __name__ == '__main__':
    app.run(debug=True)
