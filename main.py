import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate
# LangChain imports
from langchain_community.chat_models import ChatOpenAI

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a secure key

# Set your OpenAI API key 
os.environ["OPENAI_API_KEY"] = "YOUR_API_HERE"

# Database file name
DB_NAME = "mistakes.db"

def init_database():
    """Initialize SQLite database and create mistakes table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mistakes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_input TEXT NOT NULL,
            detected_mistakes TEXT,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def log_mistake(user_input, detected_mistakes):
    """Log a user input and detected mistakes to the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat(timespec='seconds')
    cursor.execute("""
        INSERT INTO mistakes (user_input, detected_mistakes, timestamp)
        VALUES (?, ?, ?)
    """, (user_input, detected_mistakes, timestamp))
    conn.commit()
    conn.close()

def detect_mistakes_llm(user_input, target_language):
    """
    Use LangChain's ChatOpenAI to detect language mistakes in the user input.
    This function builds a proper prompt message list using ChatPromptTemplate.
    """
    # prompt template for mistake detection
    prompt_template = ChatPromptTemplate.from_messages([
        HumanMessagePromptTemplate.from_template(
            "Please review the following sentence written in {target_language} and list any grammatical or usage mistakes, or say 'No mistakes' if the sentence is correct.\n\nSentence: \"{user_input}\"\n\nAnswer:"
        )
    ])
    
    # Format the messages
    messages = prompt_template.format_messages(target_language=target_language, user_input=user_input)
    
    # Instantiate the LLM
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.0)
    
    # Get the response
    response = llm(messages)
    return response.content.strip()

def generate_bot_response_llm(user_message, target_language, known_language, level, scene, conversation_history):
    """
    Use LangChain's ChatOpenAI along with a ChatPromptTemplate to generate a chatbot response.
    The system prompt includes the conversation history as well as context about the user's known language and level.
    """
    # Build the system message that includes context and prior conversation
    system_msg = (
        f"You are a language tutor chatbot helping a user learn {target_language}. "
        f"The user is a native speaker of {known_language} and is currently at a {level} level in {target_language}. "
        f"Set the scene as follows: {scene}. "
        "Engage in conversation entirely in the target language and gently correct mistakes when necessary.\n"
        "Conversation so far:"
    )
    for msg in conversation_history:
        role = "User" if msg["role"] == "user" else "Bot"
        system_msg += f"\n{role}: {msg['content']}"
    
    # Create a prompt template with system and human messages
    chat_prompt = ChatPromptTemplate.from_messages([
        #SystemMessagePromptTemplate.from_template(system_msg),
        HumanMessagePromptTemplate.from_template("{user_message}")
    ])

    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
    # Use format_messages() to get the list of message objects
    messages = chat_prompt.format_messages(user_message=user_message)
    response = llm(messages)
    return response.content.strip()



@app.route("/", methods=["GET", "POST"])
def index():
    """
    Landing page where user provides initial parameters:
    target language, known language, and proficiency level.
    """
    if request.method == "POST":
        session["target_language"] = request.form["target_language"].strip()
        session["known_language"] = request.form["known_language"].strip()
        session["level"] = request.form["level"].strip()
        session["scene"] = f"You are in a casual coffee shop setting, engaging in a friendly conversation in {session['target_language']}."
        # Initialize conversation history in session
        session["conversation_history"] = []
        return redirect(url_for("chat"))
    return render_template("index.html")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    """
    Chat interface where the conversation takes place.
    """
    if "target_language" not in session:
        return redirect(url_for("index"))
    
    target_language = session["target_language"]
    known_language = session["known_language"]
    level = session["level"]
    scene = session["scene"]
    conversation_history = session.get("conversation_history", [])
    bot_response = None

    if request.method == "POST":
        user_message = request.form["user_message"].strip()
        if user_message.lower() in ["exit", "quit"]:
            flash("Chat session ended. See summary below.", "info")
            return redirect(url_for("summary"))
        
        # Detect mistakes in the user's message using LangChain
        mistakes_feedback = detect_mistakes_llm(user_message, target_language)
        if mistakes_feedback and mistakes_feedback.lower() != "no mistakes":
            log_mistake(user_message, mistakes_feedback)
        
        bot_response = generate_bot_response_llm(
            user_message, target_language, known_language, level, scene, conversation_history
        )
        
        conversation_history.append({"role": "user", "content": user_message})
        conversation_history.append({"role": "assistant", "content": bot_response})
        session["conversation_history"] = conversation_history

    return render_template("chat.html", conversation=conversation_history, bot_response=bot_response)

@app.route("/summary")
def summary():
    """
    Displays a summary of all mistakes logged during the session.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, user_input, detected_mistakes FROM mistakes ORDER BY id")
    records = cursor.fetchall()
    conn.close()
    return render_template("summary.html", records=records)

if __name__ == "__main__":
    init_database()
    app.run(debug=True)
