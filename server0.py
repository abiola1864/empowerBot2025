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
import traceback
from assessments import (
    handle_business_size_selection,
    handle_financial_status_selection,
    handle_main_challenge_selection,
    handle_record_keeping_selection,
    handle_growth_goal_selection,
    handle_funding_need_selection
)

# Continue with the rest of your `server.py` code



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


# with open('data/quiz1.json') as f:
#     QUIZ_QUESTIONS = json.load(f)['questions']
   
 

 


def list_available_quizzes():
    quizzes = []
    for file in os.listdir('data'):
        if file.startswith('quiz') and file.endswith('.json'):
            quiz_number = file.split('.')[0].replace('quiz', '')
            quizzes.append(quiz_number)
    quizzes.sort(key=int)
    return quizzes
 
 
def load_quiz_data(quiz_name):
    try:
        with open(f'data/{quiz_name}.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Quiz file {quiz_name}.json not found")
        return None
     
     



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
                   GROUP_CONCAT(CASE WHEN responses.correct = 0 THEN responses.question_number ELSE NULL END) AS wrong_answers,
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
                'wrong_answers': row[3] or '',
                'quiz': row[4] or ''
            })
        return user_data
    except Exception as e:
        print(f"Error fetching user data: {e}")
        return []
    finally:
        conn.close()
       
       
       
       
# @app.route('/viewdata')
# def viewdata():
#     user_data = get_user_data()
#     return render_template('viewdata.html', user_data=user_data)

 
@app.route('/viewdata')
def viewdata():
    user_data = get_user_data()
    # Group user data by quiz
    grouped_data = {}
    for user in user_data:
        quiz = user['quiz'] or 'Unspecified'
        if quiz not in grouped_data:
            grouped_data[quiz] = []
        grouped_data[quiz].append(user)
    return render_template('viewdata.html', user_data=grouped_data)
   



def init_db():
    conn = get_db_connection()
    try:
        conn.executescript('''
            -- Users table
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL UNIQUE,
                name TEXT,
                random_number TEXT,
                state TEXT DEFAULT 'init',
                current_quiz TEXT DEFAULT '',
                previous_state TEXT DEFAULT ''
            );

            -- Records table (for image uploads)
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                media_url TEXT NOT NULL,
                upload_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            -- Quiz states table
            CREATE TABLE IF NOT EXISTS quiz_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                quiz_name TEXT NOT NULL,
                question_index INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            -- Responses table (for quiz answers)
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question_number INTEGER NOT NULL,
                response TEXT,
                correct INTEGER NOT NULL,
                quiz TEXT,
                upload_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            -- Processed messages table
            CREATE TABLE IF NOT EXISTS processed_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT NOT NULL UNIQUE
            );

            -- Questions table
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz TEXT NOT NULL,
                question TEXT NOT NULL
            );
        ''')
        conn.commit()
        logging.info("Database initialized successfully")
    except sqlite3.OperationalError as e:
        # Log the error, but don't raise it (allows for idempotent execution)
        logging.error(f"SQLite error during database initialization: {e}")
    finally:
        conn.close()

def get_db_connection():
    conn = sqlite3.connect('user_data.db')
    conn.row_factory = sqlite3.Row
    return conn
  
  

 
 
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

        if user is None:
            # This is a new user, let's create a record for them
            conn.execute('INSERT INTO users (phone_number, state) VALUES (?, ?)', (phone_number, 'awaiting_name'))
            conn.commit()
            user = conn.execute('SELECT * FROM users WHERE phone_number = ?', (phone_number,)).fetchone()
            send_message(phone_number, "Welcome to the Empowerment for Local People Foundation! What's your full name?")
            log_image_event(f"New user created for {phone_number}, awaiting name")
        else:
            if message_type == 'text':
                message_body = message['text']['body'].lower().strip()
                log_image_event(f"Received text message from {phone_number}: {message_body}")
                handle_text_message(phone_number, message_body, user, conn)
            elif message_type == 'interactive':
                interactive = message['interactive']
                if interactive['type'] == 'button_reply':
                    button_id = interactive['button_reply']['id']
                    button_text = interactive['button_reply']['title']
                    handle_button_response(phone_number, button_id, button_text, user, conn)
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
        log_image_event(traceback.format_exc())
        send_message(phone_number, "An error occurred. Please try again or contact support if the issue persists.")
    finally:
        conn.close()
       
     
def send_interactive_message(phone_number, message, buttons):
    url = f"https://graph.facebook.com/v11.0/{YOUR_PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": message
            },
            "action": {
                "buttons": buttons
            }
        }
    }
    response = requests.post(url, headers=headers, json=data)
    log_image_event(f"Sent interactive message to {phone_number} - Status: {response.status_code}")
    log_image_event(f"Response content: {response.text}")
   
    if response.status_code != 200:
        log_image_event(f"Error sending interactive message. Request data: {json.dumps(data)}")
        raise Exception(f"Failed to send interactive message. Status code: {response.status_code}")

    return response.status_code == 200
 
 
       
       

def generate_random_number(user_id):
    seed = f"user_{user_id}_seed"
    hash_object = hashlib.md5(seed.encode())
    random.seed(hash_object.hexdigest())
    return ''.join(random.choices(string.digits, k=6))

 
 
def handle_media_message(phone_number, message, message_type, user, conn):
    log_image_event(f"Handling media message for user {phone_number}")
   
    if user['state'] != 'records':
        log_image_event(f"User {phone_number} attempted to upload media while in state: {user['state']}")
        send_message(phone_number, "To upload a record, please select the 'Record Keeping' option first.")
        present_options(phone_number, user, conn)
        return

    media_id = message[message_type]['id']
    media_url = f"https://graph.facebook.com/v11.0/{media_id}"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}

    try:
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
            conn.execute('UPDATE users SET random_number = ?, state = ? WHERE id = ?', (random_number, 'awaiting_choice', user['id']))
            conn.execute('INSERT INTO records (user_id, media_url) VALUES (?, ?)', (user['id'], filename))
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
           
            # Update user object with new state
            user = conn.execute('SELECT * FROM users WHERE phone_number = ?', (phone_number,)).fetchone()
           
            # Present options after successful upload
            log_image_event(f"Presenting options after upload for user {phone_number}")
            present_options_after_upload(phone_number, user, conn)
        else:
            log_image_event(f"Error downloading media {media_id} for user {phone_number}: {response.status_code}")
            send_message(phone_number, "Sorry, there was an error processing your file. Please try again.")
            present_options(phone_number, user, conn)
    except requests.RequestException as e:
        log_image_event(f"Network error while processing media for user {phone_number}: {str(e)}")
        send_message(phone_number, "There was a network error while processing your file. Please try again later.")
        present_options(phone_number, user, conn)
    except sqlite3.Error as e:
        log_image_event(f"Database error while processing media for user {phone_number}: {str(e)}")
        send_message(phone_number, "There was a database error while saving your record. Please try again or contact support.")
        present_options(phone_number, user, conn)
    except IOError as e:
        log_image_event(f"File I/O error while saving media for user {phone_number}: {str(e)}")
        send_message(phone_number, "There was an error saving your file. Please try again or contact support.")
        present_options(phone_number, user, conn)
    except Exception as e:
        log_image_event(f"Unexpected error in handle_media_message for user {phone_number}: {str(e)}")
        log_image_event(traceback.format_exc())
        send_message(phone_number, "An unexpected error occurred while processing your upload. Please try again or contact support if the issue persists.")
        present_options(phone_number, user, conn)
       
       
       
       
def present_options_after_upload(phone_number, user, conn):
    try:
        log_image_event(f"Presenting options after upload for user {phone_number}")
        available_quizzes = list_available_quizzes()
        log_image_event(f"Available quizzes: {available_quizzes}")
       
        if not available_quizzes:
            log_image_event(f"No quizzes available for user {phone_number}")
            send_message(phone_number, "No quizzes are available. Would you like to upload another record?")
            buttons = [
                {"type": "reply", "reply": {"id": "records", "title": "Upload Record"}}
            ]
            send_interactive_message(phone_number, "Choose an option:", buttons)
            return

        completed_quizzes = conn.execute(
            'SELECT DISTINCT quiz FROM responses WHERE user_id = ?', (user['id'],)
        ).fetchall()
        completed_quizzes = [quiz[0] for quiz in completed_quizzes]
        log_image_event(f"Completed quizzes: {completed_quizzes}")
       
        uncompleted_quizzes = [quiz for quiz in available_quizzes if quiz not in completed_quizzes]
        log_image_event(f"Uncompleted quizzes: {uncompleted_quizzes}")
       
        if uncompleted_quizzes:
            buttons = [
                {"type": "reply", "reply": {"id": "quiz", "title": "Take Quiz"}},
                {"type": "reply", "reply": {"id": "records", "title": "Upload Record"}}
            ]
            message = "What would you like to do next? Type 'quiz' to take a quiz or 'records' to upload a record."
        else:
            buttons = [
                {"type": "reply", "reply": {"id": "records", "title": "Upload Record"}}
            ]
            message = "You've completed all quizzes. Would you like to upload another record? Type 'records' to upload."
       
        log_image_event(f"Sending interactive message to {phone_number} with options: {buttons}")
        result = send_interactive_message(phone_number, message, buttons)
        log_image_event(f"Result of send_interactive_message: {result}")
    except Exception as e:
        log_image_event(f"Error in present_options_after_upload: {str(e)}")
        log_image_event(traceback.format_exc())
        send_message(phone_number, "An error occurred. Please type 'records' to upload or 'quiz' to start a quiz.")
       
       
       
def present_options(phone_number, user, conn):
    buttons = [
        {"type": "reply", "reply": {"id": "records", "title": "Record Keeping"}},
        {"type": "reply", "reply": {"id": "quiz", "title": "Start Quiz"}},
        {"type": "reply", "reply": {"id": "settings", "title": "Settings"}}
    ]
    send_interactive_message(phone_number, "What would you like to do?", buttons)
    conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', ('awaiting_choice', phone_number))
    conn.commit()
    
    

 

def handle_text_message(phone_number, message_body, user, conn):
    log_image_event(f"Handling text message for {phone_number}: {message_body}")

    message_lower = message_body.lower().strip()

    try:
        if user['state'] == 'changing_name':
            new_name = message_body.strip()
            conn.execute('UPDATE users SET name = ?, state = ? WHERE phone_number = ?', 
                         (new_name, user['previous_state'], phone_number))
            conn.commit()
            send_message(phone_number, f"Your name has been updated to: {new_name}")
            user = conn.execute('SELECT * FROM users WHERE phone_number = ?', (phone_number,)).fetchone()
            present_options(phone_number, user, conn)
            return

        # Handle 'settings' command regardless of the current state
        if message_lower == 'settings':
            log_image_event(f"Accessing settings for {phone_number}")
            handle_settings_command(phone_number, user, conn)
            return

        # Handle other states
        if user['state'] == 'awaiting_name':
            log_image_event(f"User {phone_number} provided name: {message_body}")
            conn.execute('UPDATE users SET name = ?, state = ? WHERE phone_number = ?', 
                         (message_body, 'awaiting_choice', phone_number))
            conn.commit()
            send_message(phone_number, f"Nice to meet you, {message_body}! What would you like to do next?")
            present_options(phone_number, user, conn)
        elif user['state'] == 'awaiting_choice':
            send_message(phone_number, "Please choose 'Record Keeping' or 'Start Quiz'.")
            present_options(phone_number, user, conn)
        elif user['state'] == 'selecting_quiz':
            handle_quiz_selection(phone_number, message_body, user, conn)
        elif user['state'].startswith('quiz_'):
            handle_quiz_response(phone_number, message_body, user, conn)
        elif user['state'] == 'records':
            send_message(phone_number, "Please upload your business record as an image or PDF.")
        elif user['state'] == 'changing_name':
            new_name = message_body.strip()
            conn.execute('UPDATE users SET name = ?, state = ? WHERE phone_number = ?', 
                         (new_name, user['previous_state'], phone_number))
            conn.commit()
            send_message(phone_number, f"Your name has been updated to: {new_name}")
            user = conn.execute('SELECT * FROM users WHERE phone_number = ?', (phone_number,)).fetchone()
            if user['previous_state'].startswith('quiz_'):
                current_quiz = user['current_quiz']
                question_index = int(user['previous_state'].split('_')[1])
                send_quiz_question(phone_number, question_index, conn, current_quiz)
            else:
                present_options(phone_number, user, conn)
        else:
            send_message(phone_number, "Invalid input. Please type 'records' to begin record keeping or 'quiz' to start the quiz.")

        # Occasionally remind users about the quick switch option
        if random.random() < 0.2:  # 20% chance to show the reminder
            send_message(phone_number, "Remember, you can type 'records', 'quiz', or 'settings123' at any time to switch.")

    except Exception as e:
        log_image_event(f"Error in handle_text_message: {str(e)}")
        log_image_event(traceback.format_exc())
        send_message(phone_number, "An error occurred. Please try again or contact support if the issue persists.")
        present_options(phone_number, user, conn)

        
        
        
        
def handle_text_message(phone_number, message_body, user, conn):
    log_image_event(f"Handling text message for {phone_number}: {message_body}")
    message_lower = message_body.lower().strip()
    try:
        # Always allow switching to quiz, records, or settings
        if message_lower in ['quiz', 'start quiz', 'records', 'record keeping', 'settings']:
            if message_lower in ['quiz', 'start quiz']:
                handle_quiz_selection(phone_number, message_body, user, conn)
            elif message_lower in ['records', 'record keeping']:
                conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', ('records', phone_number))
                conn.commit()
                send_message(phone_number, f"Welcome {user['name']}, please upload your business record as an image or PDF.")
            elif message_lower == 'settings':
                handle_settings_command(phone_number, user, conn)
            return

        if user['state'] == 'removing_account':
            if message_lower == 'yes':
                remove_user_account(phone_number, conn)
            elif message_lower == 'no':
                handle_settings_command(phone_number, user, conn)
            else:
                send_message(phone_number, "Please respond with 'yes' to confirm account removal or 'no' to cancel.")
            return

        if user['state'] == 'changing_name':
            new_name = message_body.strip()
            conn.execute('UPDATE users SET name = ?, state = ? WHERE phone_number = ?',
                         (new_name, user['previous_state'], phone_number))
            conn.commit()
            send_message(phone_number, f"Your name has been updated to: {new_name}")
            user = conn.execute('SELECT * FROM users WHERE phone_number = ?', (phone_number,)).fetchone()
            present_options(phone_number, user, conn)
            return

        if user['state'] == 'awaiting_full_info':
            conn.execute('UPDATE users SET name = ?, state = ? WHERE phone_number = ?',
                         (message_body, 'awaiting_age', phone_number))
            conn.commit()
            send_message(phone_number, "Nice to meet you, {}! Please type your age in the chat".format(message_body))
        
        elif user['state'] == 'awaiting_age':
            conn.execute('UPDATE users SET age = ?, state = ? WHERE phone_number = ?',
                         (message_body, 'awaiting_gender', phone_number))
            conn.commit()
            send_message(phone_number, "Thank you! Please type your gender in the chat. (Please reply with 'male', 'female', or 'other')")
        
        elif user['state'] == 'awaiting_gender':
            conn.execute('UPDATE users SET gender = ?, state = ? WHERE phone_number = ?',
                         (message_body, 'awaiting_business_type', phone_number))
            conn.commit()
            send_message(phone_number, "Great! Please type in the chat the type of business or services you deal on?")
        
        elif user['state'] == 'awaiting_business_type':
            conn.execute('UPDATE users SET business_type = ?, state = ? WHERE phone_number = ?',
                         (message_body, 'awaiting_location', phone_number))
            conn.commit()
            send_message(phone_number, "Thank you! Type in the chat where your business is located?")
        
        elif user['state'] == 'awaiting_location':
            conn.execute('UPDATE users SET location = ?, state = ? WHERE phone_number = ?',
                         (message_body, 'awaiting_business_size', phone_number))
            conn.commit()
            # Send business size options using the settings-style list
            handle_business_size_selection(phone_number, user, conn)

        elif user['state'] == 'awaiting_business_size':
            conn.execute('UPDATE users SET business_size = ?, state = ? WHERE phone_number = ?',
                         (message_body, 'awaiting_financial_status', phone_number))
            conn.commit()
            handle_financial_status_selection(phone_number, user, conn)

        elif user['state'] == 'awaiting_financial_status':
            conn.execute('UPDATE users SET financial_status = ?, state = ? WHERE phone_number = ?',
                         (message_body, 'awaiting_main_challenge', phone_number))
            conn.commit()
            handle_main_challenge_selection(phone_number, user, conn)

        elif user['state'] == 'awaiting_main_challenge':
            conn.execute('UPDATE users SET main_challenge = ?, state = ? WHERE phone_number = ?',
                         (message_body, 'awaiting_record_keeping', phone_number))
            conn.commit()
            handle_record_keeping_selection(phone_number, user, conn)

        elif user['state'] == 'awaiting_record_keeping':
            conn.execute('UPDATE users SET record_keeping = ?, state = ? WHERE phone_number = ?',
                         (message_body, 'awaiting_growth_goal', phone_number))
            conn.commit()
            handle_growth_goal_selection(phone_number, user, conn)

        elif user['state'] == 'awaiting_growth_goal':
            conn.execute('UPDATE users SET growth_goal = ?, state = ? WHERE phone_number = ?',
                         (message_body, 'awaiting_funding_need', phone_number))
            conn.commit()
            handle_funding_need_selection(phone_number, user, conn)

        elif user['state'] == 'awaiting_funding_need':
            conn.execute('UPDATE users SET funding_need = ?, state = ? WHERE phone_number = ?',
                         (message_body, 'awaiting_choice', phone_number))
            conn.commit()
            send_message(phone_number, "Thank you! We now understand your business better. What would you like to do next?")
            present_options(phone_number, user, conn)

        elif user['state'] == 'awaiting_choice':
            send_message(phone_number, "Please choose 'Record Keeping' or 'Start Quiz'.")
            present_options(phone_number, user, conn)

        elif user['state'] in ['ai_chat', 'awaiting_followup', 'post_explanation', 'awaiting_action', 'awaiting_explanation']:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO followup_questions (user_id, question) VALUES (?, ?)',
                           (user['id'], message_body))
            conn.commit()
            handle_ai_chat(phone_number, message_body, conn)
            conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', ('ai_chat', phone_number))
            conn.commit()

        elif user['state'] == 'selecting_quiz':
            handle_quiz_selection(phone_number, message_body, user, conn)

        elif user['state'].startswith('quiz_'):
            handle_quiz_response(phone_number, message_body, user, conn)

        elif user['state'] == 'records':
            send_message(phone_number, f"Welcome {user['name']}, please upload your business record as an image or PDF.")

        else:
            send_message(phone_number, "Invalid input. Please type 'records' to begin record keeping or 'quiz' to start the quiz.")
       
        if random.random() < 0.2:
            send_message(phone_number, "Remember, you can type 'records', 'quiz', or 'settings' at any time to switch.")

    except Exception as e:
        log_image_event(f"Error in handle_text_message: {str(e)}")
        log_image_event(traceback.format_exc())
        send_message(phone_number, "Sorry, something went wrong. Please try again or contact support.")
        present_options(phone_number, user, conn)
        
        
        
       
def handle_records_command(phone_number, user, conn):
    message = f"Welcome to Record Keeping, {user['name']}! Please upload your business record as an image or PDF."
    send_message(phone_number, message)
    conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', ('records', phone_number))
    conn.commit()
    log_image_event(f"Switched to records mode for {phone_number}")

   
   

     

 

def check_quiz_state(conn, user_id, quiz_name):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quiz_states WHERE user_id = ? AND quiz_name = ?", (user_id, quiz_name))
    state = cursor.fetchone()
    logging.info(f"Current state for {quiz_name} for user {user_id}: {state}")
    return state
 
 


 
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

        if user is None:
            # This is a new user, let's create a record for them
            conn.execute('INSERT INTO users (phone_number, state) VALUES (?, ?)', (phone_number, 'awaiting_name'))
            conn.commit()
            user = conn.execute('SELECT * FROM users WHERE phone_number = ?', (phone_number,)).fetchone()
            send_message(phone_number, "Welcome to the Empowerment for Local People Foundation! What's your full name?")
            log_image_event(f"New user created for {phone_number}, awaiting name")
        else:
            if message_type == 'text':
                message_body = message['text']['body'].lower().strip()
                log_image_event(f"Received text message from {phone_number}: {message_body}")
                handle_text_message(phone_number, message_body, user, conn)
            elif message_type == 'interactive':
                interactive = message['interactive']
                if interactive['type'] == 'button_reply':
                    button_id = interactive['button_reply']['id']
                    button_text = interactive['button_reply']['title']
                    handle_button_response(phone_number, button_id, button_text, user, conn)
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
        log_image_event(traceback.format_exc())
        send_message(phone_number, "An error occurred. Please try again or contact support if the issue persists.")
    finally:
        conn.close()
        
        
        
def handle_text_message(phone_number, message_body, user, conn):
    log_image_event(f"Handling text message for {phone_number}: {message_body}")

    message_lower = message_body.lower().strip()

 

def handle_text_message(phone_number, message_body, user, conn):
    log_image_event(f"Handling text message for {phone_number}: {message_body}")

    message_lower = message_body.lower().strip()

    # Handle 'records' and 'quiz' commands regardless of the current state
    if message_lower in ['records', 'record keeping', 'upload record']:
        log_image_event(f"Switching to records mode for {phone_number}")
        handle_records_command(phone_number, user, conn)
        return
    elif message_lower in ['quiz', 'start quiz', 'take quiz']:
        log_image_event(f"Switching to quiz mode for {phone_number}")
        handle_quiz_command(phone_number, user, conn)
        return
        
       # Handle 'settings123' command regardless of the current state
    if message_lower == 'settings123':
        log_image_event(f"Accessing settings for {phone_number}")
        handle_settings_command(phone_number, user, conn)
        return

    # Handle other states
    if user['state'] == 'awaiting_name':
        log_image_event(f"User {phone_number} provided name: {message_body}")
        conn.execute('UPDATE users SET name = ?, state = ? WHERE phone_number = ?', (message_body, 'awaiting_choice', phone_number))
        conn.commit()
        send_message(phone_number, f"Nice to meet you, {message_body}! What would you like to do next?")
        present_options(phone_number, user, conn)
    elif user['state'] == 'changing_name':
        new_name = message_body.strip()
        conn.execute('UPDATE users SET name = ?, state = ? WHERE phone_number = ?', (new_name, 'awaiting_choice', phone_number))
        conn.commit()
        send_message(phone_number, f"Your name has been updated to: {new_name}")
        present_options(phone_number, user, conn)

        
        
    elif user['state'] == 'awaiting_choice':
        send_message(phone_number, "Please choose 'Record Keeping' or 'Start Quiz'.")
        present_options(phone_number, user, conn)
    elif user['state'] == 'selecting_quiz':
        handle_quiz_selection(phone_number, message_body, user, conn)
    elif user['state'].startswith('quiz_'):
        handle_quiz_response(phone_number, message_body, user, conn)
    elif user['state'] == 'records':
        send_message(phone_number, "Please upload your business record as an image or PDF.")
    else:
        send_message(phone_number, "Invalid input. Please type 'records' to begin record keeping or 'quiz' to start the quiz.")

    # Occasionally remind users about the quick switch option
    if random.random() < 0.2:  # 20% chance to show the reminder
        send_message(phone_number, "Remember, you can type 'records' or 'quiz' at any time to switch.")
       
       
       
def handle_button_response(phone_number, button_id, button_text, user, conn):
    log_image_event(f"Button response received: id={button_id}, text={button_text}")
    try:
        if button_id == "settings":
            log_image_event(f"Accessing settings for {phone_number}")
            handle_settings_command(phone_number, user, conn)
        elif button_id == "change_name":
            log_image_event(f"User {phone_number} initiated name change")
            conn.execute('UPDATE users SET state = ?, previous_state = ? WHERE phone_number = ?', 
                         ('changing_name', user['state'], phone_number))
            conn.commit()
            send_message(phone_number, "Please enter your new name:")
        elif button_id == "back":
            previous_state = conn.execute('SELECT previous_state FROM users WHERE phone_number = ?', (phone_number,)).fetchone()['previous_state']
            conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', (previous_state, phone_number))
            conn.commit()
            send_message(phone_number, "Returning to previous activity.")
            present_options(phone_number, user, conn)
        elif button_id in ["records", "quiz"]:
            handle_text_message(phone_number, button_text, user, conn)
        else:
            log_image_event(f"Unknown button response: {button_id} from {phone_number}")
            handle_text_message(phone_number, button_text, user, conn)
    except Exception as e:
        log_image_event(f"Error in handle_button_response: {str(e)}")
        log_image_event(traceback.format_exc())
        send_message(phone_number, "An error occurred. Please try again or type 'records', 'quiz', or 'settings' to switch.")

        
        
            
            
        
        
        
def handle_settings_command(phone_number, user, conn):
    buttons = [
        {"type": "reply", "reply": {"id": "change_name", "title": "Change Name"}},
        {"type": "reply", "reply": {"id": "back", "title": "Back"}}
    ]
    send_interactive_message(phone_number, "Settings:", buttons)
    
    # Store the previous state before entering settings
    previous_state = user['state']
    conn.execute('UPDATE users SET state = ?, previous_state = ? WHERE phone_number = ?', 
                 ('settings', previous_state, phone_number))
    conn.commit()
    log_image_event(f"User {phone_number} accessed settings")
    
    
    
    
def handle_records_command(phone_number, user, conn):
    message = f"Welcome to Record Keeping, {user['name']}! Please upload your business record as an image or PDF."
    send_message(phone_number, message)
    conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', ('records', phone_number))
    conn.commit()
    log_image_event(f"Switched to records mode for {phone_number}")
   
   


   
def handle_quiz_command(phone_number, user, conn):
    available_quizzes = list_available_quizzes()
   
    if not available_quizzes:
        send_message(phone_number, "No quizzes are available at the moment.")
        present_options(phone_number, user, conn)
        return

    quiz_statuses = {f"quiz{quiz}": get_quiz_status(conn, user['id'], f"quiz{quiz}") for quiz in available_quizzes}

    completed_quizzes = [quiz for quiz, status in quiz_statuses.items() if status == "completed"]
    in_progress_quizzes = [quiz for quiz, status in quiz_statuses.items() if status == "in_progress"]
    uncompleted_quizzes = [quiz for quiz, status in quiz_statuses.items() if status == "not_started"]

    message = "Quiz Status:\n"
    if completed_quizzes:
        message += "Completed: " + ", ".join(completed_quizzes) + "\n"
    if in_progress_quizzes:
        message += "In Progress: " + ", ".join(in_progress_quizzes) + "\n"
    if uncompleted_quizzes:
        message += "Available: " + ", ".join(uncompleted_quizzes) + "\n"

    send_message(phone_number, message)

    buttons = []
    if uncompleted_quizzes:
        buttons.append({"type": "reply", "reply": {"id": "new_quiz", "title": "Start New Quiz"}})
    if in_progress_quizzes:
        buttons.extend([
            {
                "type": "reply",
                "reply": {
                    "id": quiz,
                    "title": f"Continue {quiz}"
                }
            } for quiz in in_progress_quizzes[:2]  # Limit to 2 buttons
        ])
   
    if buttons:
        send_interactive_message(phone_number, "What would you like to do?", buttons)
    else:
        send_message(phone_number, "You've completed all available quizzes. Great job!")
        present_options(phone_number, user, conn)

    conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', ('selecting_quiz', phone_number))
    conn.commit()
    
    
    

def handle_quiz_selection(phone_number, message_body, user, conn):
    log_image_event(f"Quiz selection initiated for {phone_number} with message: {message_body}")
    try:
        available_quizzes = list_available_quizzes()
        selected_quiz = message_body.lower().replace(" ", "")
       
        quiz_statuses = {f"quiz{quiz}": get_quiz_status(conn, user['id'], f"quiz{quiz}") for quiz in available_quizzes}
       
        if selected_quiz in ["startnewquiz", "new_quiz"]:
            available_quizzes = [quiz for quiz, status in quiz_statuses.items() if status != "completed"]
            if available_quizzes:
                buttons = [
                    {
                        "type": "reply",
                        "reply": {
                            "id": quiz,
                            "title": f"{'Continue' if quiz_statuses[quiz] == 'in_progress' else 'Start'} {quiz}"
                        }
                    } for quiz in available_quizzes[:3]  # WhatsApp limits to 3 buttons
                ]
                send_interactive_message(phone_number, "Choose a quiz to start or continue:", buttons)
            else:
                send_message(phone_number, "You have completed all available quizzes. Great job!")
                present_options(phone_number, user, conn)
        else:
            quiz_number = ''.join(filter(str.isdigit, selected_quiz))
            selected_quiz = f"quiz{quiz_number}"
           
            if selected_quiz in quiz_statuses:
                status = quiz_statuses[selected_quiz]
                if status in ["in_progress", "not_started"]:
                    start_or_resume_quiz(phone_number, user, conn, selected_quiz)
                else:
                    send_message(phone_number, f"You've already completed {selected_quiz}. Choose another quiz or activity.")
                    handle_quiz_command(phone_number, user, conn)
            else:
                send_message(phone_number, "Invalid quiz selection. Please choose a quiz from the available options.")
                handle_quiz_command(phone_number, user, conn)
    except Exception as e:
        log_image_event(f"Error in handle_quiz_selection: {str(e)}")
        log_image_event(traceback.format_exc())
        send_message(phone_number, "An error occurred while selecting the quiz. Please try again.")
        present_options(phone_number, user, conn)

def start_or_resume_quiz(phone_number, user, conn, selected_quiz):
    quiz_state = check_quiz_state(conn, user['id'], selected_quiz)
    question_index = quiz_state['question_index'] if quiz_state else 0
   
    if not quiz_state:
        conn.execute('INSERT INTO quiz_states (user_id, quiz_name, question_index) VALUES (?, ?, ?)',
                     (user['id'], selected_quiz, question_index))
   
    conn.execute('UPDATE users SET current_quiz = ?, state = ? WHERE phone_number = ?',
                 (selected_quiz, f'quiz_{question_index}', phone_number))
    conn.commit()
   
    action = "Resuming" if quiz_state else "Starting"
    log_image_event(f"{action} {selected_quiz} for user {user['id']} at question {question_index}")
    start_quiz(phone_number, conn, selected_quiz, question_index)


   
def finish_quiz(phone_number, user, conn, current_quiz, num_questions):
    try:
        log_image_event(f"Finishing quiz {current_quiz} for user {user['id']}")
       
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
       
        log_image_event(f"Database updated for user {user['id']} after finishing quiz {current_quiz}")
       
        # Offer options to take another quiz or switch to records
        buttons = [
            {"type": "reply", "reply": {"id": "quiz", "title": "Take Another Quiz"}},
            {"type": "reply", "reply": {"id": "records", "title": "Switch to Records"}}
        ]
        success = send_interactive_message(phone_number, "What would you like to do next?", buttons)
       
        if not success:
            log_image_event(f"Failed to send interactive message for user {user['id']} after quiz completion")
            send_message(phone_number, "What would you like to do next? Type 'quiz' to take another quiz or 'records' to switch to record keeping.")
       
        log_image_event(f"Quiz {current_quiz} finished successfully for user {user['id']}")
       
    except Exception as e:
        log_image_event(f"Error in finish_quiz for user {user['id']}: {str(e)}")
        log_image_event(traceback.format_exc())
        send_message(phone_number, "An error occurred while finishing the quiz. Please type 'quiz' to start over or 'records' to switch to record keeping.")
   
    finally:
        # Ensure the user's state is reset even if an error occurs
        try:
            conn.execute("UPDATE users SET state='awaiting_choice', current_quiz='' WHERE phone_number=?", (phone_number,))
            conn.commit()
        except Exception as e:
            log_image_event(f"Error resetting user state in finish_quiz for user {user['id']}: {str(e)}")
           
           
       
def get_quiz_status(conn, user_id, quiz_name):
    state = conn.execute(
        "SELECT question_index FROM quiz_states WHERE user_id = ? AND quiz_name = ?",
        (user_id, quiz_name)
    ).fetchone()
   
    if state is None:
        return "not_started"
    elif state['question_index'] == -1:
        return "completed"
    else:
        return "in_progress"

def check_quiz_state(conn, user_id, quiz_name):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quiz_states WHERE user_id = ? AND quiz_name = ?", (user_id, quiz_name))
    state = cursor.fetchone()
    logging.info(f"Current state for {quiz_name} for user {user_id}: {state}")
    return state
 
 
       
       

def send_interactive_message(phone_number, message, buttons):
    url = f"https://graph.facebook.com/v11.0/{YOUR_PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": message
            },
            "action": {
                "buttons": buttons
            }
        }
    }
    response = requests.post(url, headers=headers, json=data)
    log_image_event(f"Sent interactive message to {phone_number} - Status: {response.status_code}")
    log_image_event(f"Response content: {response.text}")
   
    if response.status_code != 200:
        log_image_event(f"Error sending interactive message. Request data: {json.dumps(data)}")
        return False, f"Failed to send interactive message. Status code: {response.status_code}"

    return True, "Message sent successfully"
  
  
 
def handle_quiz_response(phone_number, response, user, conn):
    log_image_event(f"Handling quiz response for {phone_number}: {response}")
    
    if response.lower().strip() == 'settings123':
        handle_settings_command(phone_number, user, conn)
        return

    current_quiz = user['current_quiz']
    if not current_quiz:
        log_image_event(f"No current quiz for user {phone_number}")
        send_message(phone_number, "No active quiz. Type 'quiz' to start a new quiz.")
        return

    try:
        quiz_data = load_quiz_data(current_quiz)
        if not quiz_data:
            raise Exception(f"Quiz {current_quiz} not found")
        QUIZ_QUESTIONS = quiz_data['questions']
    except Exception as e:
        log_image_event(f"Error loading quiz data for {current_quiz}: {str(e)}")
        send_message(phone_number, "There was an error with the quiz. Please type 'quiz' to start over.")
        conn.execute("UPDATE users SET state = 'awaiting_choice', current_quiz = '' WHERE phone_number = ?", (phone_number,))
        conn.commit()
        return

    state = user['state']
    question_index = int(state.split('_')[1])
    question_number = question_index + 1

    if question_index < len(QUIZ_QUESTIONS):
        current_question = QUIZ_QUESTIONS[question_index]
        correct_answer = current_question['answer'].lower().strip()
        user_response = response.lower().strip()
        is_correct = user_response == correct_answer

        conn.execute(
            "INSERT INTO responses (user_id, question_number, response, correct, quiz) VALUES (?, ?, ?, ?, ?)",
            (user['id'], question_number, response, int(is_correct), current_quiz)
        )

        feedback = "Correct!" if is_correct else f"Wrong! The correct answer was {correct_answer.upper()}."
        send_message(phone_number, feedback)

        question_index += 1
        log_image_event(f"Moving to next question. New index: {question_index}")

        if question_index < len(QUIZ_QUESTIONS):
            conn.execute("UPDATE users SET state = ? WHERE phone_number = ?", (f'quiz_{question_index}', phone_number))
            conn.execute("UPDATE quiz_states SET question_index = ? WHERE user_id = ? AND quiz_name = ?",
                         (question_index, user['id'], current_quiz))
            conn.commit()
            send_quiz_question(phone_number, question_index, conn, current_quiz)
        else:
            try:
                finish_quiz(phone_number, user, conn, current_quiz, len(QUIZ_QUESTIONS))
            except Exception as e:
                log_image_event(f"Error in finish_quiz called from handle_quiz_response: {str(e)}")
                log_image_event(traceback.format_exc())
                send_message(phone_number, "An error occurred while finishing the quiz. Please type 'quiz' to start over or 'records' to switch to record keeping.")
    else:
        send_message(phone_number, "Invalid question number. Type 'quiz' to start a new quiz.")
        conn.execute("UPDATE users SET state = 'awaiting_choice', current_quiz = '' WHERE phone_number = ?", (phone_number,))
        conn.commit()
        
        
   
   
def truncate_text(text, max_length):
    return (text[:max_length-3] + '...') if len(text) > max_length else text

def send_quiz_question(phone_number, question_index, conn, quiz_name, retries=3):
    logging.info(f"Sending quiz question for {quiz_name}, question index: {question_index}")
    try:
        quiz_data = load_quiz_data(quiz_name)
        if not quiz_data:
            raise Exception(f"Quiz {quiz_name} not found")
        QUIZ_QUESTIONS = quiz_data['questions']
    except Exception as e:
        logging.error(f"Error loading quiz data for {quiz_name}: {str(e)}")
        logging.error(traceback.format_exc())
        send_message(phone_number, f"There was an error loading the quiz. Please type 'quiz' to try again.")
        conn.execute("UPDATE users SET state = 'awaiting_choice', current_quiz = '' WHERE phone_number = ?", (phone_number,))
        conn.commit()
        return


    if question_index < len(QUIZ_QUESTIONS):
      # Occasionally remind about quick switch
       # if random.random() < 0.1:  # 10% chance to show the reminder
         #   send_message(phone_number, "Remember, you can type 'records' at any time to switch to record keeping mode.")
        current_question = QUIZ_QUESTIONS[question_index]
        options = current_question['options']
        question_message = f"Question {question_index + 1} out of {len(QUIZ_QUESTIONS)}:\n\n{current_question['question']}\n\n"
        for option in options:
            question_message += f"{option}\n"
       
        buttons = [
            {
                "type": "reply",
                "reply": {
                    "id": f"option_{chr(65+i)}",
                    "title": f"{chr(65+i)}"
                }
            } for i in range(len(options))
        ]
       
        for attempt in range(retries):
            try:
                success = send_interactive_message(phone_number, question_message, buttons)
                if success:
                    logging.info(f"Successfully sent question for {quiz_name}, index {question_index}")
                    return
                else:
                    raise Exception("Failed to send interactive message")
            except Exception as e:
                logging.error(f"Error sending question (attempt {attempt + 1}): {str(e)}")
                logging.error(traceback.format_exc())
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
    url = f"https://graph.facebook.com/v11.0/{YOUR_PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "Welcome to the Empowerment for Local People Foundation! What would you like to do?"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "records",
                            "title": "Record Keeping"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "quiz",
                            "title": "Start Quiz"
                        }
                    }
                ]
            }
        }
    }
    response = requests.post(url, headers=headers, json=data)
    logging.info(f"Sent interactive message to {phone_number} - Status: {response.status_code}")
   
   
   

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
    logging.info(f"Starting quiz {quiz_name} for {phone_number} at question {question_index}")
    try:
        quiz_data = load_quiz_data(quiz_name)
        if not quiz_data:
            raise Exception(f"Quiz {quiz_name} not found")
        send_quiz_question(phone_number, question_index, conn, quiz_name)
    except Exception as e:
        logging.error(f"Error starting quiz {quiz_name}: {str(e)}")
        send_message(phone_number, f"There was an error starting the quiz. Please try again.")
        user = conn.execute("SELECT * FROM users WHERE phone_number = ?", (phone_number,)).fetchone()
        present_options(phone_number, user, conn)

       
       
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


# @app.route('/scoreboard')
# def scoreboard():
#     conn = get_db_connection()
#     try:
#         scores = conn.execute("""
#             SELECT
#                 users.phone_number,
#                 users.name,
#                 SUM(CASE WHEN responses.correct = 1 THEN 1 ELSE 0 END) as total_score,
#                 COUNT(DISTINCT responses.quiz) as quizzes_completed,
#                 MAX(responses.upload_date) as last_quiz_date,
#                 MAX(records.upload_date) as last_image_date,
#                 COUNT(records.id) as images_uploaded,
#                 COUNT(DISTINCT DATE(records.upload_date)) as unique_upload_days
#             FROM users
#             LEFT JOIN responses ON users.id = responses.user_id
#             LEFT JOIN records ON users.id = records.user_id
#             GROUP BY users.id
#             ORDER BY total_score DESC, quizzes_completed DESC
#         """).fetchall()
#         return render_template('scoreboard.html', scores=scores)
#     finally:
#         conn.close()


@app.route('/scoreboard')
def scoreboard():
    conn = get_db_connection()
    try:
        pass_percentage = request.args.get('pass_percentage', 60, type=int)
        min_quizzes = request.args.get('min_quizzes', 1, type=int)

        # Fetch all user data
        users = conn.execute("SELECT id, phone_number, name FROM users").fetchall()

        # Define quiz ranges
        quiz_ranges = ['all', '1-5', '6-10']
        user_scores = []

        for user in users:
            try:
                score_dict = {
                    'id': user['id'],
                    'name': user['name'],
                    'phone_number': user['phone_number'],
                    'all': {},
                    '1-5': {},
                    '6-10': {}
                }
                
                for range_key in quiz_ranges:
                    if range_key == 'all':
                        condition = "1=1"
                    elif range_key == '1-5':
                        condition = "quiz IN ('quiz1', 'quiz2', 'quiz3', 'quiz4', 'quiz5')"
                    else:  # '6-10'
                        condition = "quiz IN ('quiz6', 'quiz7', 'quiz8', 'quiz9', 'quiz10')"
                    
                    results = conn.execute(f"""
                        SELECT 
                            SUM(CASE WHEN correct = 1 THEN 1 ELSE 0 END) as total_correct_answers,
                            COUNT(*) as total_questions_attempted,
                            COUNT(DISTINCT quiz) as quizzes_taken,
                            MAX(upload_date) as last_quiz_date
                        FROM responses
                        WHERE user_id = ? AND {condition}
                    """, (user['id'],)).fetchone()

                    total_possible = conn.execute(f"SELECT COUNT(*) FROM questions WHERE {condition}").fetchone()[0]

                    score_dict[range_key] = {
                        'total_correct_answers': int(results['total_correct_answers'] or 0),
                        'total_questions_attempted': int(results['total_questions_attempted'] or 0),
                        'quizzes_taken': int(results['quizzes_taken'] or 0),
                        'total_possible': total_possible,
                        'last_quiz_date': results['last_quiz_date'] if results['last_quiz_date'] else 'N/A'
                    }

                    if score_dict[range_key]['total_questions_attempted'] > 0:
                        score_dict[range_key]['percentage'] = (score_dict[range_key]['total_correct_answers'] / score_dict[range_key]['total_questions_attempted']) * 100
                        score_dict[range_key]['pass_fail'] = 'Pass' if score_dict[range_key]['percentage'] >= pass_percentage and score_dict[range_key]['quizzes_taken'] >= min_quizzes else 'Fail'
                    else:
                        score_dict[range_key]['percentage'] = 0
                        score_dict[range_key]['pass_fail'] = 'N/A'

                additional_data = conn.execute("""
                    SELECT 
                        MAX(records.upload_date) as last_image_date,
                        COUNT(DISTINCT records.id) as images_uploaded,
                        COUNT(DISTINCT DATE(records.upload_date)) as unique_upload_days
                    FROM records
                    WHERE user_id = ?
                """, (user['id'],)).fetchone()

                score_dict.update({
                    'last_image_date': additional_data['last_image_date'] if additional_data['last_image_date'] else 'N/A',
                    'images_uploaded': additional_data['images_uploaded'] or 0,
                    'unique_upload_days': additional_data['unique_upload_days'] or 0
                })

                user_scores.append(score_dict)

            except Exception as user_error:
                app.logger.error(f"Error processing user {user['id']}: {str(user_error)}")

        # Sort user_scores by percentage in descending order
        user_scores.sort(key=lambda x: x['all']['percentage'], reverse=True)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'scores': user_scores,
                'pass_percentage': pass_percentage,
                'min_quizzes': min_quizzes
            })
        else:
            return render_template('scoreboard.html', 
                                   scores=user_scores,
                                   pass_percentage=pass_percentage, 
                                   min_quizzes=min_quizzes)

    except Exception as e:
        app.logger.error(f"An error occurred in scoreboard route: {str(e)}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': str(e)}), 500
        else:
            return f"An error occurred while loading the scoreboard: {str(e)}", 500

    finally:
        conn.close()
        
        
    
        
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
