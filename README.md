# Language Learning Chatbot

An AI-powered language learning chatbot that engages users in target language conversations, detects and logs language mistakes, and provides tailored feedback. Built with Flask, Bootstrap, SQLite, and LangChain with OpenAI's GPT-3.5-turbo.

## Setup

1. **Clone the Repository:**
   
bash
   git clone https://github.com/yourusername/language-learning-chatbot.git
   cd language-learning-chatbot
Create & Activate a Virtual Environment:

bash
Copy
python -m venv venv
source venv/bin/activate  # For Linux/Mac
venv\Scripts\activate     # For Windows
Install Dependencies:

bash
Copy
pip install -r requirements.txt
Configure API Key:

Set your OPENAI_API_KEY in your environment or in a config file (ensure you remove it before public submission).

Run the Application:

bash
Copy
python main.py
Then, open http://127.0.0.1:5000/ in your browser.

Usage
Enter your target language, known language, and proficiency level.

Chat with the bot, which detects mistakes in your input.

End the session with "exit" or "quit" to view a summary of logged mistakes.

License
This project is licensed under the MIT License.

markdown
Copy

1. **Replace** `yourusername` in the clone URL with your actual GitHub username or repository URL.  
2. **Commit** this updated README.md and **push** it to GitHub.  

Now it should display properly on your repository’s main page!
