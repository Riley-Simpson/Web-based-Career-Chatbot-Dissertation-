import logging
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
import requests
from datetime import datetime, timedelta
from PyPDF2 import PdfReader
import os
import json

"""
EDUCATION
University of Strathclyde 	Glasgow City Centre
Msc Artificial Intelligence and Applications , (2:1)	September 2023 - October2024
Masters Program  

University of Strathclyde 	Glasgow City Centre
Beng Electrical & Mechanical Engineering , (2:2)	August 2019 - August 2023
HonoursProgram 

WORK EXPERIENCE
Alloway Ltd Engineering 	    Bellshill, North Lanarkshire
Assembly Internship	  4 Day Internship
Assembly of control panels for an industrial Aerosol detection system. 
Design and prototyping of a Newton-Metre Assembly frame.
Calibration of laser detection system.

Scotts Bar & Restaurant 	    Troon , South Ayrshire
Bartender	   August 2023 - Present
Mixing and preparing a range of custom and classical cocktails for clients. 
Managing standard front of house duties ; taking bookings,  hosting, running food & drinks.
"""
app = Flask(__name__)
CORS(app)
app.secret_key = 'secret_key'

active_session = {
    'user': None,
    'expiry': None
}

logging.basicConfig(
    filename='/home/RileySimpson/career-chatbot-webapp/online_app_log.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)

file_handler = logging.FileHandler('/home/RileySimpson/career-chatbot-webapp/online_app_log.log')
app.logger.addHandler(file_handler)
logger = logging.getLogger(__name__)

class Chat:
    def __init__(self, local_api_url):
        self.local_api_url = local_api_url
        self.pre_prompt = "You are a Career Guidance Chatbot. Please follow the rules intensely and do not deviate from the following ruleset!\n"

    def query(self, query_str):
        try:
            if 'chat_history' not in session: #Checks if theres history with session. If not then assume chatbot needs reminded of role. 
                session['chat_history'] = self.pre_prompt
                logger.info("Reset past interactions")

            logger.info(session['chat_history'])
            context = (session['chat_history'], query_str)
            response = requests.post(self.local_api_url + "/chat", json={"context": context}) 
            
            try:
                response_data = response.json()
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON response: {e}")
                return "Invalid response from server"

            session['chat_history'] += f"\nUser: {query_str}\nChatBot: {response_data.get('response')}" #Updates chat history with response. 

            return response_data.get('response', 'No response content')

        except Exception as e:
            logger.error(f"Error communicating with local API: {e}")
            return "Sorry, something went wrong. Please try again."

    def upload_resume(self, file):
        try:
            if 'chat_history' not in session:
                session['chat_history'] = self.pre_prompt
                logger.info("Reset past interactions")

            pdf_reader = PdfReader(file)
            text = ''.join(page.extract_text() for page in pdf_reader.pages)
            response = requests.post(self.local_api_url + "/upload_resume", json={"resume": text})
            response_data = response.json()
            session['chat_history'] += f"\nUser: {text}\nBot: {response_data.get('response')}"

            logger.info(f"Past interactions set to: \n{session['chat_history']}")
            return response_data.get('response')

        except Exception as e:
            logger.error(f"Error communicating with local API: {e}")
            return "Sorry, something went wrong. Please try again."

def create_chat_instance():
    local_api_url = "url" 
    return Chat(local_api_url)

chat_instance = create_chat_instance()

def check_availability():
    if not active_session['user'] or active_session['expiry'] < datetime.now():
        active_session['user'] = request.remote_addr
        active_session['expiry'] = datetime.now() + timedelta(minutes=10)
        return jsonify({'sessionActive': False}), 200
    elif active_session['user'] != request.remote_addr:
        return jsonify({'response': 'Chat is currently in use by another user. Please wait your turn.'}), 403
    return jsonify({'sessionActive': True}), 200

@app.route("/")
def index():
    session.pop('chat_history', None)
    logger.info(f'------------------------------New Session------------------------------\n')
    return render_template("index.html")

@app.route('/startsession', methods=['POST'])
def start_session():
    return check_availability()

@app.route('/endsession', methods=['POST'])
def end_session():
    if active_session['user'] == request.remote_addr:
        active_session['user'] = None
        active_session['expiry'] = None
    return jsonify({'sessionEnded': True})

@app.route('/issessionactive', methods=['GET'])
def is_session_active():
    if active_session['user'] == request.remote_addr and active_session['expiry'] > datetime.now():
        return jsonify({'sessionActive': True})
    return jsonify({'sessionActive': False})

@app.route('/chat', methods=['POST'])
def chat():
    availability_response = check_availability()
    if availability_response[1] != 200:
        return availability_response

    try:
        data = request.get_json()
        user_input = data.get('context')

        if not user_input:
            return jsonify({"error": "No input provided"}), 400

        response = chat_instance.query(user_input)

        if isinstance(response, Exception):
            logger.error(f"Error from chat_instance.query: {response}")
            return jsonify({"error": "Something went wrong"}), 500

        logger.info(response)
        return jsonify({"response": response})

    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding failed: {e}")
        return jsonify({"error": "Invalid JSON received"}), 400

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": "Something went wrong on the backend"}), 500

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    availability_response = check_availability()
    if availability_response[1] != 200:
        return availability_response

    if 'resume' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'})

    file = request.files['resume']

    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'})

    try:
        response = chat_instance.upload_resume(file)
        return jsonify({"response": response})

    except Exception as e:
        logger.error(f"Error in /upload_resume: {e}")
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6666, threaded=True)
