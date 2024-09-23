from flask import Flask, render_template, request, jsonify
from custom_pandas_engine import create_custom_pandas_engine, run_query
import pandas as pd

app = Flask(__name__)

# Load your data
df = pd.read_csv('podcasts.csv')

# Define column descriptions
column_descriptions = {
    "podcast_name": "Name of the podcast show",
    "podcast_youtube_id": "Unique identifier for the podcast",
    "description": "Brief summary or description of the episode content",
    "podcast_number": "Number of the podcast episode",
    "published_at": "Date when the episode was published",
}

custom_engine = create_custom_pandas_engine(df, column_descriptions)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    user_query = request.json['query']
    try:
        response = run_query(custom_engine, user_query)
        
        if isinstance(response, dict):
            formatted_response = str(next(iter(response.values())))
        elif isinstance(response, str):
            formatted_response = response
        else:
            formatted_response = str(response)
        
        return jsonify({'response': formatted_response})
    except Exception as e:
        return jsonify({'error': f'An error occurred while processing your query: {str(e)}'}), 500

if __name__ == '__main__':
    app.run()