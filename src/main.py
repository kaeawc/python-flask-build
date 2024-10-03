import os
import sys
from core.logging import logging
from flask import Flask, jsonify

# Create a Flask app
app = Flask(__name__)


# Status route, returns a JSON response
@app.route("/status", methods=["GET"])
def status():
    logging.debug("Status endpoint was accessed")
    return jsonify({"status": "OK", "message": "The application is running smoothly"})


# Function to get the port number
def get_port():
    # Check if a command-line argument is provided
    if len(sys.argv) > 1:
        return int(sys.argv[1])

    # Otherwise, check for the environment variable 'PORT'
    return int(os.getenv("PORT", 5000))


# Function to get the port number
def get_debug_flag():
    # Check if a command-line argument is provided
    if len(sys.argv) > 2:
        return int(sys.argv[2])

    # Otherwise, check for the environment variable 'DEBUG'
    return os.getenv("DEBUG", "false").lower() == "true"


# Start the app
if __name__ == "__main__":
    port = get_port()
    is_debug = get_debug_flag()
    logging.info(f"Starting the Flask app on port {port} with debug={is_debug}")
    app.run(host="0.0.0.0", port=port, debug=is_debug)
