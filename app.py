import openai
import mysql.connector
from flask import Flask, request, jsonify
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Configure OpenAI API key
openai.api_key = "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"

# MySQL Database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "mysql",
    "database": "faq_system"
}

def connect_db():
    """Connect to the MySQL database."""
    return mysql.connector.connect(**DB_CONFIG)

# Helper function to interact with ChatGPT API
def get_chatgpt_response(question):
    """Send question to ChatGPT and get a response."""
    prompt = f"You are a support assistant. Answer the following question in one paragraph: {question}"
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error: {e}"

# Helper function to log query and response
def log_query(question, response):
    """Log the question, response, and timestamp into the database."""
    conn = connect_db()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    query = "INSERT INTO logs (question, response, timestamp) VALUES (%s, %s, %s)"
    cursor.execute(query, (question, response, timestamp))
    conn.commit()
    conn.close()

# Flask route to handle FAQ queries
@app.route('/ask', methods=['POST'])
def ask_question():
    """Handle user question and return ChatGPT response."""
    data = request.json
    question = data.get('question')
    
    if not question:
        return jsonify({"error": "Question is required"}), 400
    
    # Get response from ChatGPT
    response = get_chatgpt_response(question)
    
    # Log question and response
    log_query(question, response)
    
    return jsonify({"question": question, "response": response})

# Flask route to fetch logs
@app.route('/logs', methods=['GET'])
def get_logs():
    """Fetch all logged questions and responses."""
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    conn.close()
    return jsonify(logs)

if __name__ == '__main__':
    app.run(debug=True)
