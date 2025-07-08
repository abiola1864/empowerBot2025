import os
import logging
import requests
import sqlite3
import time
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import json
import random
import string
import hashlib
from flask import Flask, request, render_template, jsonify, send_from_directory
import time
import shutil
import json
import csv
from logging.handlers import RotatingFileHandler
import datetime
from datetime import timedelta





app = Flask(__name__)
load_dotenv()

#os.remove('user_data.db') if os.path.exists('user_data.db') else None


# Configure logging to write to a file
log_file = 'app.log'
log_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024 * 5, backupCount=5)
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)
app.logger.addHandler(log_handler)
app.logger.setLevel(logging.INFO)


# Log image-related events
def log_image_event(message):
    app.logger.info(f"IMAGE EVENT: {message}")
   
   

   
def get_logs_and_data():
    two_minutes_ago = datetime.datetime.now() - timedelta(minutes=2)

    with open('app.log', 'r') as log_file:
        logs = [log for log in log_file.readlines() if "IMAGE EVENT" in log and datetime.datetime.strptime(log.split(' - ')[0], '%Y-%m-%d %H:%M:%S,%f') > two_minutes_ago]

    conn = get_db_connection()
    try:
        users = conn.execute("SELECT id, phone_number, name FROM users").fetchall()
        records = conn.execute("""
            SELECT users.phone_number, users.name, records.media_url, records.upload_date
            FROM records
            JOIN users ON records.user_id = users.id
            ORDER BY records.upload_date DESC
        """).fetchall()
        return logs, list(users), list(records)
    except Exception as e:
        app.logger.error(f"Error fetching data: {e}")
        return [], [], []
    finally:
        conn.close()
       

     


@app.route('/stream_logs')
def stream_logs():
    def generate():
        with open('app.log', 'r') as log_file:
            while True:
                line = log_file.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                yield f"data: {line}\n\n"

    return Response(generate(), mimetype='text/event-stream')
@app.route('/dashboard')


def dashboard():
    logs, users, records = get_logs_and_data()
    return render_template('dashboard.html', initial_logs=logs, initial_users=users, initial_records=records)
 
       
       

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
WHATSAPP_TOKEN = os.getenv('GRAPH_API_TOKEN')
WEBHOOK_VERIFY_TOKEN = os.getenv('WEBHOOK_VERIFY_TOKEN')
YOUR_PHONE_NUMBER_ID = os.getenv('YOUR_PHONE_NUMBER_ID')
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


with open('data/quiz1.json') as f:
    QUIZ_QUESTIONS = json.load(f)['questions']
   
 

 


def list_available_quizzes():
    quizzes = []
    for file in os.listdir('data'):
        if file.startswith('quiz') and file.endswith('.json'):
            quiz_number = file.split('.')[0].replace('quiz', '')
            quizzes.append(quiz_number)
    quizzes.sort(key=int)
    return quizzes
 




def get_db_connection(retries=5):
    attempt = 0
    while attempt < retries:
        try:
            conn = sqlite3.connect('user_data.db')
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.OperationalError as e:
            if 'database is locked' in str(e):
                attempt += 1
                time.sleep(0.1)
            else:
                raise
    raise sqlite3.OperationalError("Max retries exceeded: database is locked")
   
     
# def get_db_data():
#     conn = get_db_connection()
#     try:
#         data = {}
#         for table in conn.execute("SELECT name FROM sqlite_master WHERE type='table'"):
#             table_name = table[0]
#             data[table_name] = []
#             cursor = conn.execute(f"SELECT * FROM {table_name}")
#             rows = cursor.fetchall()
#             column_names = [description[0] for description in cursor.description]
#             for row in rows:
#                 data[table_name].append(dict(zip(column_names, row)))
#         return data
#     except Exception as e:
#         print(f"Error fetching database data: {e}")
#         return {}
#     finally:
#         conn.close()
       
# @app.route('/viewdata')
# def viewdata():
#     data = get_db_data()
#     return render_template('viewdata.html', data=json.dumps(data))
 
 
 
def get_user_data():
    conn = get_db_connection()
    try:
        user_data = []
        cursor = conn.cursor()
        cursor.execute("""
            SELECT users.phone_number, users.name,
                   COUNT(CASE WHEN responses.correct = 1 THEN 1 END) AS correct_answers,
                   responses.quiz
            FROM users
            LEFT JOIN responses ON users.id = responses.user_id
            GROUP BY users.id, users.name, users.phone_number, responses.quiz
            ORDER BY users.name
        """)
        rows = cursor.fetchall()
        for row in rows:
            user_data.append({
                'phone_number': row[0],
                'name': row[1],
                'correct_answers': row[2] or 0,
                'quiz': row[3] or ''
            })
        return user_data
    except Exception as e:
        print(f"Error fetching user data: {e}")
        return []
    finally:
        conn.close()
       
       
@app.route('/viewdata')
def viewdata():
    user_data = get_user_data()
    return render_template('viewdata.html', user_data=user_data)
 
 
   
def init_db():
    conn = get_db_connection()
    try:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL UNIQUE,
                name TEXT,
                random_number TEXT,
                state TEXT DEFAULT 'init',
                current_quiz TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                media_url TEXT NOT NULL,
                upload_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            CREATE TABLE IF NOT EXISTS quiz_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                quiz_name TEXT NOT NULL,
                question_index INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question_number INTEGER NOT NULL,
                response TEXT,
                correct INTEGER NOT NULL,
                quiz TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            CREATE TABLE IF NOT EXISTS processed_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT NOT NULL UNIQUE
            );
        ''')
        conn.commit()
    finally:
        conn.close()
       

     
     

 
 
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    logging.info(f"Received webhook: {data}")
    if data['object'] == 'whatsapp_business_account':
        for entry in data['entry']:
            for change in entry['changes']:
                if change['field'] == 'messages' and 'messages' in change['value']:
                    for message in change['value']['messages']:
                        handle_message(message)
    return 'OK', 200

def handle_message(message):
    message_id = message.get('id')
    phone_number = message['from']
    message_type = message['type']

    log_image_event(f"Received message of type '{message_type}' from {phone_number}")

    conn = get_db_connection()
    try:
        if conn.execute('SELECT 1 FROM processed_messages WHERE message_id = ?', (message_id,)).fetchone():
            log_image_event(f"Message {message_id} already processed, skipping")
            return

        user = conn.execute('SELECT * FROM users WHERE phone_number = ?', (phone_number,)).fetchone()
        log_image_event(f"Processing message {message_id} for user: {user}")

        if message_type == 'text':
            message_body = message['text']['body'].lower().strip()
            log_image_event(f"Received text message from {phone_number}: {message_body}")
            handle_text_message(phone_number, message_body, user, conn)
        elif message_type in ['image', 'document']:
            log_image_event(f"Received {message_type} message from {phone_number}")
            handle_media_message(phone_number, message, message_type, user, conn)
        else:
            log_image_event(f"Unsupported message type '{message_type}' from {phone_number}")
            send_message(phone_number, "Unsupported message type. Please send text, image, or document.")

        conn.execute('INSERT INTO processed_messages (message_id) VALUES (?)', (message_id,))
        conn.commit()
    except Exception as e:
        log_image_event(f"Error processing message {message_id}: {str(e)}")
    finally:
        conn.close()
       
       
       
       

def generate_random_number(user_id):
    seed = f"user_{user_id}_seed"
    hash_object = hashlib.md5(seed.encode())
    random.seed(hash_object.hexdigest())
    return ''.join(random.choices(string.digits, k=6))

 
 
def handle_media_message(phone_number, message, message_type, user, conn):
    if not user or user['state'] != 'records':
        log_image_event(f"User {phone_number} attempted to upload media without being in 'records' state.")
        send_message(phone_number, "Please type 'records' to begin record keeping before uploading.")
        return

    media_id = message[message_type]['id']
    media_url = f"https://graph.facebook.com/v11.0/{media_id}"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}

    log_image_event(f"User {phone_number} requested to upload {message_type}. Downloading media {media_id}...")
    response = requests.get(media_url, headers=headers)
    if response.status_code == 200:
        log_image_event(f"Successfully downloaded media {media_id} for user {phone_number}")
        file_url = response.json()['url']
        log_image_event(f"Retrieving media file from {file_url}")
        file_content = requests.get(file_url, headers=headers).content

        filename = secure_filename(f"{user['id']}_{media_id}.{'jpg' if message_type == 'image' else 'pdf'}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        log_image_event(f"Saving media file as {filename} to {file_path}")
        with open(file_path, 'wb') as f:
            f.write(file_content)

        random_number = generate_random_number(user['id'])
        log_image_event(f"Generating random number {random_number} for user {user['id']}")
        conn.execute('UPDATE users SET random_number = ? WHERE id = ?', (random_number, user['id']))
        conn.execute('INSERT INTO records (user_id, media_url) VALUES (?, ?)', (user['id'], filename))
        conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', ('awaiting_choice', phone_number))
        conn.commit()
        log_image_event(f"Stored media {filename} for user {phone_number} in database")

        base_url = "https://glitter-dynamic-taxicab.glitch.me"  # Replace with your actual base URL
        user_url = f"{base_url}/user/{user['id']}/{random_number}"

        thank_you_message = (
             f"Thank you {user['name']}! Your record has been uploaded successfully. "
            f"You can view your records here: {user_url}"
        )
        log_image_event(f"Sending success message to user {phone_number}")
        send_message(phone_number, thank_you_message)
    else:
        log_image_event(f"Error downloading media {media_id} for user {phone_number}: {response.status_code}")
        send_message(phone_number, "Sorry, there was an error processing your file. Please try again.")
       
       
def handle_text_message(phone_number, message_body, user, conn):
    logging.info(f"Handling text message for {phone_number}: {message_body}")
    log_image_event(f"Handling text message for {phone_number}: {message_body}")

    message_body = message_body.lower().strip()

    if message_body == 'records':
        log_image_event(f"User {phone_number} requested to begin record keeping")
        handle_records_command(phone_number, user, conn)
        return
    elif message_body == 'quiz':
        log_image_event(f"User {phone_number} requested to start a quiz")
        handle_quiz_command(phone_number, user, conn)
        return

    try:
        if not user:
            log_image_event(f"New user {phone_number}, sending intro message")
            send_intro_message(phone_number)
            conn.execute('INSERT INTO users (phone_number, state) VALUES (?, ?)', (phone_number, 'awaiting_name'))
            conn.commit()
            log_image_event(f"User {phone_number} state set to 'awaiting_name'")
            send_message(phone_number, "What's your full name?")
            return

        if user['state'] == 'awaiting_name':
            log_image_event(f"User {phone_number} provided name: {message_body}")
            conn.execute('UPDATE users SET name = ?, state = ? WHERE phone_number = ?', (message_body, 'awaiting_choice', phone_number))
            conn.commit()
            log_image_event(f"User {phone_number} state set to 'awaiting_choice'")
            send_message(phone_number, f"Nice to meet you, {message_body}! Please type 'records' to begin record keeping or 'quiz' to start the quiz.")
        elif user['state'] == 'awaiting_choice':
            log_image_event(f"User {phone_number} provided invalid input in 'awaiting_choice' state")
            send_message(phone_number, "Invalid input. Please type 'records' to begin record keeping or 'quiz' to start the quiz.")
        elif user['state'] == 'selecting_quiz':
            log_image_event(f"User {phone_number} provided input in 'selecting_quiz' state: {message_body}")
            handle_quiz_selection(phone_number, message_body, user, conn)
        elif user['state'].startswith('quiz_'):
            log_image_event(f"User {phone_number} provided response in 'quiz' state: {message_body}")
            handle_quiz_response(phone_number, message_body, user, conn)
        else:
            log_image_event(f"User {phone_number} provided invalid input in state '{user['state']}'")
            send_message(phone_number, "Invalid input. Please type 'records' to begin record keeping or 'quiz' to start the quiz.")
    except Exception as e:
        log_image_event(f"Error in handle_text_message for {phone_number}: {str(e)}")
    finally:
        log_image_event(f"Final state for {phone_number}: {conn.execute('SELECT state FROM users WHERE phone_number = ?', (phone_number,)).fetchone()['state']}")      
       
       
       
def handle_records_command(phone_number, user, conn):
    send_message(phone_number, f"Welcome {user['name']}! Please upload your business record as an image or PDF.")
    conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', ('records', phone_number))
    conn.commit()
   
   
def handle_quiz_command(phone_number, user, conn):
    available_quizzes = list_available_quizzes()
    if not available_quizzes:
        send_message(phone_number, "No quizzes are available at the moment.")
        return

    uncompleted_quizzes = [quiz for quiz in available_quizzes if not conn.execute('SELECT 1 FROM quiz_states WHERE user_id = ? AND quiz_name = ? AND question_index = -1',
                                          (user['id'], f"quiz{quiz}")).fetchone()]
   
    if uncompleted_quizzes:
        quiz_list_message = "Please choose a quiz by typing the corresponding number:\n" + "\n".join([f"{i+1}. quiz{quiz}" for i, quiz in enumerate(uncompleted_quizzes)])
        send_message(phone_number, quiz_list_message)
        conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', ('selecting_quiz', phone_number))
        conn.commit()
    else:
        send_message(phone_number, "You have completed all available quizzes. Great job! Type 'records' to begin record keeping.")

    # If there are completed quizzes, inform the user
    completed_quizzes = set(available_quizzes) - set(uncompleted_quizzes)
    if completed_quizzes:
        completed_message = "You have completed the following quizzes:\n" + "\n".join([f"- quiz{quiz}" for quiz in completed_quizzes])
        send_message(phone_number, completed_message)

       
   
   
def handle_quiz_selection(phone_number, message_body, user, conn):
    available_quizzes = list_available_quizzes()
    uncompleted_quizzes = [quiz for quiz in available_quizzes if not conn.execute('SELECT 1 FROM quiz_states WHERE user_id = ? AND quiz_name = ? AND question_index = -1',
                                          (user['id'], f"quiz{quiz}")).fetchone()]
   
    if message_body.isdigit():
        selected_index = int(message_body) - 1
        if 0 <= selected_index < len(uncompleted_quizzes):
            selected_quiz = f"quiz{uncompleted_quizzes[selected_index]}"
           
            existing_state = conn.execute('SELECT question_index FROM quiz_states WHERE user_id = ? AND quiz_name = ?',
                                          (user['id'], selected_quiz)).fetchone()
           
            question_index = existing_state['question_index'] if existing_state else 0
           
            if not existing_state:
                conn.execute('INSERT INTO quiz_states (user_id, quiz_name, question_index) VALUES (?, ?, ?)',
                             (user['id'], selected_quiz, question_index))
           
            conn.execute('UPDATE users SET current_quiz = ?, state = ? WHERE phone_number = ?',
                         (selected_quiz, f'quiz_{question_index}', phone_number))
            conn.commit()
            start_quiz(phone_number, conn, selected_quiz, question_index)
        else:
            send_message(phone_number, f"Invalid quiz number. Please choose a number between 1 and {len(uncompleted_quizzes)}.")
    else:
        send_message(phone_number, "Invalid input. Please type a number corresponding to the quiz you want to choose.")

       
       

       
def handle_quiz_response(phone_number, message_body, user, conn):
    logging.info(f"Handling quiz response for {phone_number}: {message_body}")

    current_quiz = user['current_quiz']
    if not current_quiz:
        logging.error(f"No current quiz for user {phone_number}")
        send_message(phone_number, "No active quiz. Type 'quiz' to start a new quiz.")
        return

    try:
        with open(f"data/{current_quiz}.json", 'r') as f:
            quiz_data = json.load(f)
        QUIZ_QUESTIONS = quiz_data['questions']
    except Exception as e:
        logging.error(f"Error loading quiz data for {current_quiz}: {str(e)}")
        send_message(phone_number, "There was an error with the quiz. Please type 'quiz' to start over.")
        conn.execute("UPDATE users SET state = 'awaiting_choice', current_quiz = '' WHERE phone_number = ?", (phone_number,))
        conn.commit()
        return

    num_questions = len(QUIZ_QUESTIONS)
    question_index = int(user['state'].split('_')[1])
    question_number = question_index + 1

    logging.info(f"Current quiz: {current_quiz}, Question index: {question_index}, Total questions: {num_questions}")

    if message_body.lower() in ['records', 'quiz']:
        handle_text_message(phone_number, message_body, user, conn)
        return

    if 0 <= question_index < num_questions:
        current_question = QUIZ_QUESTIONS[question_index]

        if message_body.lower() not in ['a', 'b', 'c']:
            send_message(phone_number, "Please answer with A, B, or C only.")
            send_quiz_question(phone_number, question_index, conn, current_quiz)
            return

        user_response_letter = message_body.lower()
        correct_answer = current_question['answer'].lower()
        is_correct = user_response_letter == correct_answer

        conn.execute(
            "INSERT INTO responses (user_id, question_number, response, correct, quiz) VALUES (?, ?, ?, ?, ?)",
            (user['id'], question_number, user_response_letter, int(is_correct), current_quiz)
        )

        feedback = "Correct!" if is_correct else f"Wrong! The correct answer was {correct_answer.upper()}."
        send_message(phone_number, feedback)

        question_index += 1
        logging.info(f"Moving to next question. New index: {question_index}")

        if question_index < num_questions:
            conn.execute("UPDATE users SET state='quiz_' || ? WHERE phone_number=?", (question_index, phone_number))
            conn.execute("UPDATE quiz_states SET question_index = ? WHERE user_id = ? AND quiz_name = ?",
                         (question_index, user['id'], current_quiz))
            conn.commit()
            send_quiz_question(phone_number, question_index, conn, current_quiz)
        else:
            finish_quiz(phone_number, user, conn, current_quiz, num_questions)
    else:
        send_message(phone_number, "Invalid question number. Type 'quiz' to start a new quiz.")
        conn.execute("UPDATE users SET state = 'awaiting_choice', current_quiz = '' WHERE phone_number = ?", (phone_number,))
        conn.commit()
       
       
       
       
def finish_quiz(phone_number, user, conn, current_quiz, num_questions):
    total_correct = conn.execute(
        "SELECT COUNT(*) AS total_correct FROM responses WHERE user_id = ? AND quiz = ? AND correct = 1",
        (user['id'], current_quiz)
    ).fetchone()['total_correct']
   
    congratulations_message = f"Congratulations! You've completed the quiz. You scored {total_correct} out of {num_questions} questions correctly."
    send_message(phone_number, congratulations_message)
   
    conn.execute("UPDATE users SET state='awaiting_choice', current_quiz='' WHERE phone_number=?", (phone_number,))
    conn.execute("UPDATE quiz_states SET question_index = -1 WHERE user_id = ? AND quiz_name = ?",
                 (user['id'], current_quiz))
    conn.commit()
    send_message(phone_number, "Type 'quiz' to see other available quizzes or 'records' for record keeping.")

   
   
def send_quiz_question(phone_number, question_index, conn, quiz_name, retries=3):
    logging.info(f"Sending quiz question for {quiz_name}, question index: {question_index}")
    try:
        with open(f"data/{quiz_name}.json", 'r') as f:
            quiz_data = json.load(f)
        QUIZ_QUESTIONS = quiz_data['questions']
    except Exception as e:
        logging.error(f"Error loading quiz data for {quiz_name}: {str(e)}")
        send_message(phone_number, f"There was an error loading the quiz. Please type 'quiz' to try again.")
        conn.execute("UPDATE users SET state = 'awaiting_choice', current_quiz = '' WHERE phone_number = ?", (phone_number,))
        conn.commit()
        return

    if question_index < len(QUIZ_QUESTIONS):
        current_question = QUIZ_QUESTIONS[question_index]
        question_message = f"Question {question_index + 1} out of {len(QUIZ_QUESTIONS)}: {current_question['question']}"
        options_message = "\n".join([f"{chr(65+i)}) {option[3:]}" for i, option in enumerate(current_question['options'])])


        full_message = f"{question_message}\n\n{options_message}\n\nType A, B, or C to choose."
       
        for attempt in range(retries):
            try:
                send_message(phone_number, full_message)
                return
            except Exception as e:
                logging.error(f"Error sending question (attempt {attempt + 1}): {str(e)}")
                if attempt == retries - 1:
                    send_message(phone_number, "There was an error sending the question. Please type 'quiz' to try again.")
                    conn.execute("UPDATE users SET state = 'awaiting_choice', current_quiz = '' WHERE phone_number = ?", (phone_number,))
                    conn.commit()
                else:
                    time.sleep(2 ** attempt)  # Exponential backoff
    else:
        logging.warning(f"Question index {question_index} out of range for {quiz_name}")
        finish_quiz(phone_number, conn.execute("SELECT * FROM users WHERE phone_number = ?", (phone_number,)).fetchone(), conn, quiz_name, len(QUIZ_QUESTIONS))  
       
   
def send_intro_message(phone_number):
    emoji_bulb = "\U0001F4A1"  # Light bulb emoji
    emoji_question = "\U00002753"  # Question mark emoji

    intro_message = (
        f"🌟 Welcome to the Empowerment for Local People Foundation! 🌟\n\n"
        f"{emoji_bulb}This service offer two main features:\n\n"
        f"1. Record Keeping: Type 'records' to begin.\n"
        f"2. Quizzes: Type 'quiz' to start.\n\n"
        f"You can switch between them anytime and continue any quiz from where you left off.\n\n"
        f"Quiz 1 is Record-keeping. Quiz 2 is Digital Marketing for Sales.\n\n"
        f"Before you begin... {emoji_question}"
    )
    send_message(phone_number, intro_message)

def send_message(phone_number, message):
    url = f"https://graph.facebook.com/v11.0/{YOUR_PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "text": {"body": message}
    }
    response = requests.post(url, headers=headers, json=data)
    logging.info(f"Sent message to {phone_number}: {message} - Status: {response.status_code}")

def start_quiz(phone_number, conn, quiz_name, question_index):
    with open(f"data/{quiz_name}.json", 'r') as f:
        quiz_data = json.load(f)
    QUIZ_QUESTIONS = quiz_data['questions']
   
    if question_index < len(QUIZ_QUESTIONS):
        send_quiz_question(phone_number, question_index, conn, quiz_name)
    else:
        send_message(phone_number, f"You've already completed {quiz_name}. Type 'quiz' to see other available quizzes.")
        conn.execute("UPDATE users SET state = 'completed', current_quiz = '' WHERE phone_number = ?", (phone_number,))
        conn.commit()
       
@app.route('/images')
def images():
    conn = get_db_connection()
    try:
        records = conn.execute("""
            SELECT users.phone_number, users.name, records.media_url, records.upload_date
            FROM records
            JOIN users ON records.user_id = users.id
            ORDER BY records.upload_date DESC
        """).fetchall()
       
        return render_template('images.html', records=records)
    except Exception as e:
        logging.error(f"Error fetching records: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()

@app.route('/users')
def users():
    conn = get_db_connection()
    try:
        users = conn.execute("SELECT id, phone_number, name, random_number FROM users").fetchall()
        return render_template('users.html', users=users)
    except Exception as e:
        logging.error(f"Error fetching users: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()
       
       

       
@app.route('/user/<int:user_id>', defaults={'random_number': None})
@app.route('/user/<int:user_id>/<random_number>')
def user_details(user_id, random_number=None):
    conn = get_db_connection()
    try:
        user = conn.execute("SELECT phone_number, name, random_number FROM users WHERE id=?", (user_id,)).fetchone()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        if random_number and user['random_number'] != random_number:
            return jsonify({'status': 'error', 'message': 'Invalid random number'}), 403

        records = conn.execute("SELECT media_url, upload_date FROM records WHERE user_id=?", (user_id,)).fetchall()
        return render_template('user_details.html', user=user, records=records)
    except Exception as e:
        logging.error(f"Error fetching user details: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()
       
       

@app.route('/uploads/<path:filename>')
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def handle_token_error(error_data):
    error = error_data.get('error', {})
    message = error.get('message', 'Unknown error')
    error_type = error.get('type')
    code = error.get('code')
    subcode = error.get('error_subcode')
    logging.error(f"Token error: {message}, Type: {error_type}, Code: {code}, Subcode: {subcode}")

   
if __name__ == '__main__':
    init_db()
    app.run(port=5000, debug=True)
