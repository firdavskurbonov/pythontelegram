"""
Telegram API Message Sender

A simple Flask API to handle sending messages and media to Telegram.
"""

import os
import logging
from typing import Dict, Any, Optional, Union
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Get bot token from environment or use as parameter
DEFAULT_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')


def send_telegram_request(
    method: str,
    token: str,
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Send a request to the Telegram API.

    Args:
        method: Telegram API method name
        token: Telegram bot token
        params: Request parameters

    Returns:
        Response from Telegram API as dictionary
    """
    url = f"https://api.telegram.org/bot{token}/{method}"

    try:
        response = requests.post(url, json=params, timeout=10)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Telegram API request failed: {e}")
        # Re-raise with more context
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.text
            status_code = e.response.status_code
            raise Exception(
                f"Telegram API error ({status_code}): {error_detail}")
        raise Exception(f"Request to Telegram API failed: {str(e)}")


@app.route('/health', methods=['GET'])
def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return jsonify({"status": "ok"})


@app.route('/api/telegram/sendMessage', methods=['POST'])
def send_message() -> Dict[str, Any]:
    """
    Send a text message via Telegram API.

    Expected JSON body:
    {
        "bot_token": "YOUR_BOT_TOKEN", (optional if set in environment)
        "chat_id": "123456789",
        "text": "Hello from API!",
        "parse_mode": "HTML" (optional)
    }
    """
    data = request.json

    # Validate required fields
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if 'chat_id' not in data:
        return jsonify({"error": "Missing required field: chat_id"}), 400

    if 'text' not in data:
        return jsonify({"error": "Missing required field: text"}), 400

    # Get bot token from request or use default
    bot_token = data.pop('bot_token', DEFAULT_BOT_TOKEN)
    if not bot_token:
        return jsonify({
            "error": "No bot token provided and TELEGRAM_BOT_TOKEN environment variable not set"
        }), 400

    try:
        response = send_telegram_request('sendMessage', bot_token, data)
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/telegram/sendPhoto', methods=['POST'])
def send_photo() -> Dict[str, Any]:
    """
    Send a photo via Telegram API.

    Expected JSON body:
    {
        "bot_token": "YOUR_BOT_TOKEN", (optional if set in environment)
        "chat_id": "123456789",
        "photo": "https://example.com/image.jpg",
        "caption": "Check out this photo!" (optional)
    }
    """
    data = request.json

    # Validate required fields
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if 'chat_id' not in data:
        return jsonify({"error": "Missing required field: chat_id"}), 400

    if 'photo' not in data:
        return jsonify({"error": "Missing required field: photo"}), 400

    # Get bot token from request or use default
    bot_token = data.pop('bot_token', DEFAULT_BOT_TOKEN)
    if not bot_token:
        return jsonify({
            "error": "No bot token provided and TELEGRAM_BOT_TOKEN environment variable not set"
        }), 400

    try:
        response = send_telegram_request('sendPhoto', bot_token, data)
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error sending photo: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/telegram/sendDocument', methods=['POST'])
def send_document() -> Dict[str, Any]:
    """
    Send a document via Telegram API.

    Expected JSON body:
    {
        "bot_token": "YOUR_BOT_TOKEN", (optional if set in environment)
        "chat_id": "123456789",
        "document": "https://example.com/file.pdf",
        "caption": "Here's the document" (optional)
    }
    """
    data = request.json

    # Validate required fields
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if 'chat_id' not in data:
        return jsonify({"error": "Missing required field: chat_id"}), 400

    if 'document' not in data:
        return jsonify({"error": "Missing required field: document"}), 400

    # Get bot token from request or use default
    bot_token = data.pop('bot_token', DEFAULT_BOT_TOKEN)
    if not bot_token:
        return jsonify({
            "error": "No bot token provided and TELEGRAM_BOT_TOKEN environment variable not set"
        }), 400

    try:
        response = send_telegram_request('sendDocument', bot_token, data)
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error sending document: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(e) -> tuple[Dict[str, str], int]:
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(e) -> tuple[Dict[str, str], int]:
    """Handle 500 errors."""
    logger.error(f"Server error: {str(e)}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))

    # Run app with debug mode in development
    debug_mode = os.environ.get('FLASK_ENV') == 'development'

    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
