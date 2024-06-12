from flask import Flask, request, jsonify, session
import openai
import yaml

# Load the config.yaml file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

#Extract keys from YAML
openai_api_key = config['openaiapikey']
flask_secret_key = config['flask_secret_key']

#Initialize OpenAI API key
openai.api_key = openai_api_key

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

    response = openai.Completion.create(
        model="text-davinci-004",
        prompt=context + "\n" + query_text,
        max_tokens=150
    )

    return jsonify({'response': response.choices[0].text.strip()}), 200

if __name__ == '__main__':
    app.run(debug=True)
