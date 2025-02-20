import sys
import pandas as pd
import logging
from datetime import datetime
from flask import Flask, request, Response, jsonify, stream_with_context
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader
import time
from database_langchain_persist import Dataset
import ollama

class Chat:
    def __init__(self, ollama_model="llama3"):
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.database = Dataset(predefined_directory_path=r'G:\My Drive\Dissertation_Database')
        self.database.load_data()
        self.ollama_model = ollama_model
        self.logs_df = pd.DataFrame(columns=['Date', 'Query', 'Relevant Documents', 'Generated Response', 'Response Time (s)', 'Model'])
        self.rules = ("\nPlease answer the QUESTION with these RULES, do not break these rules. They must be strictly followed:\n---\n"
                      "[DOC_CONTEXT] - USE THIS FOR CONTEXTUALLY AWARE ANSWERS FROM DOCUMENTS. THIS IS NOT FROM THE USER.\n"
                      "[RESUME_CONTEXT] - USE THIS TO PROVIDE GUIDANCE SPECIFICALLY ON THE USER'S RESUME.\n"
                      "[QUESTION] - User submitted query.\n"
                      "[History] - previous interactions with the Guidance Chatbot. Use this information to answer the current query.\n"
                      "[Additional Information] - information submitted by the user.\n"
                      "PLEASE RESPOND IN STANDARD MARKDOWN FORMAT, do not include JSON files or any other text representation in your response.\n"
                      "Do not include the following words in square brackets in your response: [DOC_CONTEXT][RESUME_CONTEXT][Additional Information][History][User Query]")

    def save_logs(self):
        self.logs_df.to_csv('api_requests_log.csv', index=False)
    
    def generate_response(self, context):
        print("\nGenerating Response...")
        try:
            start_time = time.time()
            response = ollama.chat(
                model=self.ollama_model,
                messages=[
                    {
                        'role': 'user',
                        'content': context
                    }  
                ]
            )
            response_time = time.time() - start_time
            response_content = response['message']['content']
            print(response_content)
            return response_content, response_time
        except Exception as e:
            logging.error(f"Error generating response: {e}")
            return f"Sorry, something went wrong. Please try again. {e}", 0
      
    def query(self, user_input=[], extra_info=None, relevancy_threshold=1.3):
        try:
            context = self.rules
            query_str = user_input[1]
            chat_history = user_input[0]
            retrieved_docs = self.database.retrieve_documents(query_str, relevancy_threshold=relevancy_threshold)

            if "[RESUME]" in query_str:
                context += f"\n[History]:\n{chat_history}"
                context += f"\n[RESUME_CONTEXT]:\n{query_str}"
            else:
                context += f"\n[History]:\n{chat_history}"
                context += f"\n[DOC_CONTEXT]: \n{retrieved_docs}"
                context += f"\nQUESTION:{query_str}"

            if extra_info:
                context += f"\n[Additional Information]:\n{extra_info}"

            print(f"\nContext:\n{context}")
            generated_response, response_time = self.generate_response(context)
            
            # Log response
            log_entry = {
                'Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Query': [query_str],
                'Relevant Documents': [retrieved_docs],
                'Generated Response': [generated_response],
                'Response Time (s)': [response_time],
                'Model': [self.ollama_model]
            }
            new_rows = pd.DataFrame(log_entry)
            self.logs_df = pd.concat([self.logs_df, new_rows], ignore_index=True)
            self.save_logs()  
            
            return generated_response
        except Exception as e:
            print(f"ERROR:root:Error retrieving documents: {e}")
        
chat_instance = Chat(ollama_model="gemma2:latest")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chatbot'
app.config['SESSION_TYPE'] = 'career-bot'

CORS(app)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('context')
    if not user_input:
        logging.error("No input provided")
        return jsonify({"error": "No input provided"}), 400

    try:
        response = chat_instance.query(user_input)
        return jsonify({"response": response})

    except Exception as e:
        logging.error(f"Error with query function : {e}")
        return jsonify({'success': False, 'message': str(e)})
    
@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    data = request.json
    resume = data.get("resume")
    try:
        response = chat_instance.query(user_input= "[RESUME] Read the following resume and provide advise to the user(assume the resume belongs to the user, use first person.)",
                                       extra_info= (f"User Resume: \n{resume}"))
        return jsonify({'success': True, 'response': response})
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(threaded=True, use_reloader=False)