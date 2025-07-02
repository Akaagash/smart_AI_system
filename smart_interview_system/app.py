import os
import requests
import json
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS # Required for cross-origin requests from frontend

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# --- Configuration ---
# IMPORTANT:
# If you are running this locally outside of the Canvas environment,
# you MUST replace "YOUR_GOOGLE_CLOUD_API_KEY" with your actual API key.
# In the Canvas environment, this will be automatically injected.
API_KEY = os.environ.get("GOOGLE_API_KEY", "AIzaSyAiR-Yu6h7LABnbCpUXrhR_WUkbrPbxU6Y")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

# --- Routes ---

@app.route('/')
def index():
    """Renders the main HTML page."""
    return render_template('index.html')

@app.route('/get_feedback', methods=['POST'])
def get_feedback():
    """
    Receives interview question and user's answer,
    sends them to the Gemini API, and returns AI feedback.
    """
    data = request.get_json()
    interview_question = data.get('question')
    user_answer = data.get('answer')

    if not interview_question or not user_answer:
        return jsonify({"error": "Missing question or answer"}), 400

    # --- Prompt Engineering for Gemini LLM ---
    # This is crucial! Craft a detailed prompt to guide the AI.
    # We ask for structured feedback points.
    prompt_text = f"""
    You are an AI interview coach designed to provide constructive and actionable feedback on interview answers.
    Analyze the user's answer in the context of the given interview question.

    Please provide feedback in the following structured format, covering each point:

    1.  **Relevance:** How well did the answer directly address the question? (Score 1-5, explain why)
    2.  **Clarity & Conciseness:** Was the answer easy to understand and to the point? (Score 1-5, explain why)
    3.  **Completeness:** Did the answer cover all necessary aspects? Were there any missed opportunities or points? (Score 1-5, explain why)
    4.  **Strengths:** What were the strong points of the user's answer?
    5.  **Areas for Improvement:** Provide specific, actionable suggestions for how the user could improve their answer.
    6.  **Example Improvement (Optional but highly recommended):** If possible, provide a brief example of how the answer could be rephrased or expanded for better impact.

    ---
    Interview Question: "{interview_question}"
    User's Answer: "{user_answer}"
    ---

    Your Feedback:
    """

    # Prepare the payload for the Gemini API
    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": prompt_text}]}
        ]
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        # Make the API call to Gemini
        response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        result = response.json()

        # Extract the bot's response
        if result.get("candidates") and len(result["candidates"]) > 0 and \
           result["candidates"][0].get("content") and \
           result["candidates"][0]["content"].get("parts") and \
           len(result["candidates"][0]["content"]["parts"]) > 0:
            ai_feedback = result["candidates"][0]["content"]["parts"][0].get("text", "No feedback generated.")
            return jsonify({"feedback": ai_feedback})
        else:
            print(f"API response: {result}") # Log the full response for debugging
            return jsonify({"error": "Could not get a valid response from the AI model. Unexpected structure."}), 500

    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Gemini API: {e}")
        return jsonify({"error": f"Failed to connect to AI service: {e}"}), 500
    except json.JSONDecodeError:
        print("Error: Could not decode JSON response from API.")
        return jsonify({"error": "Failed to parse AI response."}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": f"An internal server error occurred: {e}"}), 500

if __name__ == '__main__':
    # For local development, run with debug=True
    # For deployment, use a production-ready WSGI server like Gunicorn
    app.run(debug=True, port=5000)
