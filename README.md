# 🚨 Project No Longer Supported  

**Disclaimer:** This project is no longer being actively maintained or supported. While the code is available for reference, it may not function correctly due to outdated dependencies or missing external services.  

---

# AI-Powered Career Advice Chatbot  

## Overview  

This project is a web-based career advice chatbot designed to provide users with career guidance using natural language processing techniques. It integrates a frontend chat interface with a backend AI-powered chatbot that retrieves and processes relevant career-related documents. The chatbot can answer questions in real-time, analyze uploaded resumes, and provide personalized career advice.  

This chatbot was developed as part of a dissertation project for the **MSc in Artificial Intelligence and Applications at the University of Strathclyde**.  

## Features  

### Interactive Chatbot  
- Users can interact with the chatbot by typing career-related questions and receiving AI-generated responses.  
- Queries are processed using **Ollama** and **Sentence-Transformers**.  

### Resume Upload & Analysis  
- Users can upload their resumes in **PDF format**.  
- The chatbot will analyze the content to provide **tailored career advice**.  

### Document Retrieval & Processing  
- Stores and retrieves relevant career documents using **ChromaDB** and **LangChain**.  
- Uses **PDF processing tools (PyPDF2 & Fitz)** for extracting text from resumes and documents.  

### Session Management  
- Only **one user** can interact with the chatbot at a time.  
- Each session lasts for **10 minutes** before users are prompted for feedback.  

### Feedback Form  
- After the session ends, users can provide feedback on their experience.  

### Privacy & Security  
- All user interactions are stored securely on **encrypted cloud servers**.  
- No personal information is collected beyond necessary contact details.  

---

## Technologies Used  

### Frontend  
- **HTML, CSS, JavaScript** (User Interface)  

### Backend  
- **Python (Flask)** (API & session management)  
- **Ollama** (AI model for chat)  
- **Sentence-Transformers** (Text embeddings)  
- **ChromaDB & LangChain** (Document storage & retrieval)  
- **PyPDF2 & Fitz** (PDF processing)  
- **Python Logging Module** (Logging API interactions)  

---

## Installation  

### Prerequisites  
- **Python 3.x**  
- **Flask**  
- **PyPDF2**  
- **Requests**  

### Steps  

1. **Clone the repository:**  
   ```bash
   git clone https://github.com/yourusername/career-advice-chatbot.git
   cd career-advice-chatbot
   ```  

2. **Set up a virtual environment:**  
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use venv\Scripts\activate
   ```  

3. **Install dependencies:**  
   ```bash
   pip install -r requirements.txt
   ```  

4. **Run the Flask application:**  
   ```bash
   python online_app.py
   ```  

5. **Access the application:**  
   Open your browser and navigate to **http://localhost:6666**.  

---

## API Endpoints  

| Endpoint            | Method | Description |
|---------------------|--------|-------------|
| `/chat`            | POST   | Accepts user queries and returns AI-generated responses. |
| `/upload_resume`   | POST   | Accepts a resume and provides personalized career advice. |

---

## Usage  

### 1. Start a Session  
- When you access the chatbot, you must **read the Participant Information Sheet and provide consent**.  
- Once you agree, a **10-minute session** begins.  

### 2. Interact with the Chatbot  
- Type your **career-related questions** in the chatbox.  
- Click **"Send"** to receive AI-generated responses.  

### 3. Upload Resume for Analysis  
- Click the **"Upload Resume"** button.  
- Select a **PDF file** and upload it.  
- The chatbot will analyze your resume and provide **tailored career advice**.  

### 4. Provide Feedback  
- After the **10-minute session**, you will be redirected to a feedback form.  
- Share your experience and help improve the chatbot!  

---

## Project Structure  

```
career-advice-chatbot/
│── online_app.py        # Flask application (handles chat & resume processing)
│── app.py               # AI chatbot backend (query processing)
│── database_langchain_persist.py # Document retrieval & processing
│── static/
│   ├── styles.css       # Frontend styling
│   ├── scripts.js       # Client-side interaction handling
│── templates/
│   ├── index.html       # Chatbot interface
│── datasets/            # ChromaDB storage
│── PIS Form.pdf         # Participant Information Sheet
│── requirements.txt     # Required dependencies
│── README.md            # Project documentation
```

---

## Contributing  

Contributions are welcome! If you would like to contribute to this project, follow these steps:  

1. **Fork the repository**.  
2. **Create a new branch**:  
   ```bash
   git checkout -b feature/YourFeatureName
   ```  
3. **Commit your changes**:  
   ```bash
   git commit -m "Add some feature"
   ```  
4. **Push to your branch**:  
   ```bash
   git push origin feature/YourFeatureName
   ```  
5. **Open a pull request**.  

---

## License  

This project is licensed under the **MIT License**. See the **LICENSE** file for details.  

---

## Acknowledgments  

- **University of Strathclyde** – For providing resources and support.  
- **Flask** – For the web framework used in the backend.  
- **PyPDF2** – For PDF processing.  
- **Ollama** – For AI-powered responses.  
- **LangChain & ChromaDB** – For document storage and retrieval.  

---

## Contact  

📩 **Riley Simpson**  
📧 **riley.simpson@strath.ac.uk**  
🏩 **University of Strathclyde, Glasgow, UK**  

🔹 _Note: This project is for research purposes only. The chatbot runs on a small system, and response times may vary._  
