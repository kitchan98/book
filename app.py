#!/usr/bin/env python3
"""
Flask web application for the Book Advisor chatbot.
"""

from flask import Flask, render_template, request, jsonify, session
import uuid
import logging
from datetime import datetime
from mcp_client import SyncBookAdvisor
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize the book advisor
advisor = SyncBookAdvisor()

# Store chat histories (in production, use a database)
chat_histories = {}

@app.route('/')
def index():
    """Render the main chat interface."""
    # Create a new session ID if not exists
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        chat_histories[session['session_id']] = []
    
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    try:
        data = request.get_json()
        question = data.get('message', '').strip()
        
        if not question:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get session ID
        session_id = session.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
            chat_histories[session_id] = []
        
        # Get advice from the book advisor
        logger.info(f"Processing question: {question}")
        advice = advisor.get_advice(question)
        
        # Store in chat history
        chat_entry = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'answer': advice
        }
        
        if session_id not in chat_histories:
            chat_histories[session_id] = []
        chat_histories[session_id].append(chat_entry)
        
        # Keep only last 50 messages per session
        if len(chat_histories[session_id]) > 50:
            chat_histories[session_id] = chat_histories[session_id][-50:]
        
        return jsonify({
            'id': chat_entry['id'],
            'answer': advice,
            'timestamp': chat_entry['timestamp']
        })
        
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        return jsonify({'error': 'An error occurred processing your request'}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get chat history for the current session."""
    session_id = session.get('session_id')
    if not session_id or session_id not in chat_histories:
        return jsonify({'history': []})
    
    return jsonify({'history': chat_histories[session_id]})

@app.route('/api/clear', methods=['POST'])
def clear_history():
    """Clear chat history for the current session."""
    session_id = session.get('session_id')
    if session_id and session_id in chat_histories:
        chat_histories[session_id] = []
    
    return jsonify({'success': True})

@app.route('/api/examples', methods=['GET'])
def get_examples():
    """Get example questions."""
    examples = [
        "What would Steve Jobs do if he had to choose between a safe corporate job and a risky startup?",
        "How would Steve Jobs approach building a new product?",
        "What leadership advice would Steve Jobs give to a new manager?",
        "How can I make better decisions according to behavioral psychology?",
        "What can history's greatest innovators teach us about creativity?",
        "What does human history tell us about our future?",
        "How should I think about this difficult decision I'm facing?",
        "What would Steve Jobs say about work-life balance?"
    ]
    return jsonify({'examples': examples})

def start_app():
    """Start the Flask application."""
    try:
        # Start the MCP client
        logger.info("Starting MCP client...")
        advisor.start()
        logger.info("MCP client started successfully")
        
        # Run the Flask app
        app.run(debug=True, host='0.0.0.0', port=5001)
        
    except Exception as e:
        logger.error(f"Error starting app: {str(e)}")
    finally:
        # Stop the MCP client
        logger.info("Stopping MCP client...")
        advisor.stop()

if __name__ == '__main__':
    start_app()