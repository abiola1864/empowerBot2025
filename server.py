import os
import logging
import base64

# Decode base64 and save as a temp file
b64_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_B64")
if not b64_creds:
    raise ValueError("Missing Google credentials in environment!")

creds_path = "/tmp/google_creds.json"
with open(creds_path, "wb") as f:
    f.write(base64.b64decode(b64_creds))

# Set the path for Google SDK to use
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path


import requests
import sqlite3
import json
import random
import string
import hashlib
import time
import inspect
import shutil
import csv
import re
import threading
from datetime import datetime, timedelta
from collections import defaultdict
from contextlib import contextmanager
from dotenv import load_dotenv
from flask import Flask, request, render_template, jsonify, send_from_directory
from functools import lru_cache
from logging.handlers import RotatingFileHandler
from fuzzywuzzy import fuzz, process
import pytz
import schedule
from werkzeug.utils import secure_filename
import traceback




app = Flask(__name__)
load_dotenv()







# Simple ping endpoint
@app.route('/ping')
def ping():
    return 'OK'

def keep_alive():
    while True:
        try:
            # Ping your specific Glitch URL
            requests.get('https://glitter-dynamic-taxicab.glitch.me/ping')
            print("Ping successful")
        except Exception as e:
            print(f"Ping failed: {str(e)}")
        
        # Wait 4 minutes before next ping
        time.sleep(240)  # 240 seconds = 4 minutes

# Start the keep-alive thread when your app starts
def start_keep_alive():
    keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
    keep_alive_thread.start()
    print("Keep-alive service started")
    
    
    




# from assessments import (handle_product_selection,
#     handle_business_size_selection,
#     handle_financial_status_selection,
#     handle_main_challenge_selection,
#     handle_record_keeping_selection,
#     handle_growth_goal_selection,
#     handle_funding_need_selection
# )







def generate_product_options(business_type, current_products):
    # Define the context for the AI
    location = "Nigeria"  # This can be made dynamic based on user input
    prompt = (
        f"Generate five product options for a business that sells {business_type} "
        f"in {location}. The options should be relevant and popular in the local market. "
        f"Exclude the following products: {', '.join(current_products)}."
    )
    
    # Call the generate_text function to get product options
    generated_text = generate_text(prompt)
    
    # Assuming the generated_text will return a comma-separated string of products
    if generated_text:
        # Split the generated text into a list and clean up any whitespace
        product_options = [product.strip() for product in generated_text.split(',')]
        # Filter out already selected products from the generated options
        filtered_options = [product for product in product_options if product not in current_products]
        return filtered_options[:5]  # Return the first five new options
    else:
        # Fallback in case of an error
        return []

      
 
  
# Function to handle business size selection
def handle_business_size_selection(phone_number, user, conn):
    list_message = {
        "type": "list",
        "header": {"type": "text", "text": "Business Size"},
        "body": {"text": "How many work in your business?"},
        "footer": {"text": "Select an option below"},
        "action": {
            "button": "Select size",
            "sections": [{
                "title": "Choose an option",
                "rows": [
                    {"id": "me", "title": "Just me"},
                    {"id": "micro", "title": "1-5 workers"},
                    {"id": "very_small", "title": "6-15 workers"},
                    {"id": "small", "title": "16-30 workers"},
                    {"id": "medium", "title": "31-50 workers"},
                    {"id": "large", "title": "51-100 workers"},
                    {"id": "very_large", "title": "Over 100 workers"}
                ]
            }]
        }
    }
    return send_interactive_message(phone_number, list_message)


# Function to handle financial status selection
def handle_financial_status_selection(phone_number, user, conn):
    list_message = {
        "type": "list",
        "header": {"type": "text", "text": "Financial Status"},
        "body": {"text": "How is your business doing?"},
        "footer": {"text": "Select an option below"},
        "action": {
            "button": "Select status",
            "sections": [{
                "title": "Choose an option",
                "rows": [
                    {"id": "loss", "title": "Losing money monthly"},
                    {"id": "break_even", "title": "Breaking even"},
                    {"id": "small_profit", "title": "Small profit months"},
                    {"id": "good_profit", "title": "Good profit often"},
                    {"id": "growing", "title": "Growing profit monthly"},
                    {"id": "unstable", "title": "Profit varies a lot"}
                ]
            }]
        }
    }
    return send_interactive_message(phone_number, list_message)


# Function to handle main challenge selection
def handle_main_challenge_selection(phone_number, user, conn):
    list_message = {
        "type": "list",
        "header": {"type": "text", "text": "Main Challenge"},
        "body": {"text": "What is your biggest challenge?"},
        "footer": {"text": "Select an option below"},
        "action": {
            "button": "Select challenge",
            "sections": [{
                "title": "Choose an option",
                "rows": [
                    {"id": "cash_flow", "title": "Not enough cash"},
                    {"id": "marketing", "title": "Getting customers"},
                    {"id": "competition", "title": "Too many competitors"},
                    {"id": "skills", "title": "Need business skills"},
                    {"id": "staff", "title": "Staff issues"},
                    {"id": "tech", "title": "Need better technology"}
                ]
            }]
        }
    }
    return send_interactive_message(phone_number, list_message)


# Function to handle record-keeping selection
def handle_record_keeping_selection(phone_number, user, conn):
    list_message = {
        "type": "list",
        "header": {"type": "text", "text": "Record Keeping"},
        "body": {"text": "How do you track money?"},
        "footer": {"text": "Select an option below"},
        "action": {
            "button": "Select method",
            "sections": [{
                "title": "Choose an option",
                "rows": [
                    {"id": "none", "title": "No records kept"},
                    {"id": "memory", "title": "In my head"},
                    {"id": "notes", "title": "Notebook"},
                    {"id": "phone", "title": "Phone notes"},
                    {"id": "spreadsheet", "title": "Spreadsheets"},
                    {"id": "software", "title": "Accounting software"}
                ]
            }]
        }
    }
    return send_interactive_message(phone_number, list_message)


# Function to handle growth goal selection
def handle_growth_goal_selection(phone_number, user, conn):
    list_message = {
        "type": "list",
        "header": {"type": "text", "text": "Growth Goal"},
        "body": {"text": "What is your main goal?"},
        "footer": {"text": "Select an option below"},
        "action": {
            "button": "Select goal",
            "sections": [{
                "title": "Choose an option",
                "rows": [
                    {"id": "more_sales", "title": "More sales"},
                    {"id": "new_location", "title": "New location"},
                    {"id": "new_products", "title": "New products"},
                    {"id": "better_profit", "title": "Increase profit"},
                    {"id": "equipment", "title": "Better equipment"},
                    {"id": "stable", "title": "Keep stable"}
                ]
            }]
        }
    }
    return send_interactive_message(phone_number, list_message)


# Function to handle funding need selection
def handle_funding_need_selection(phone_number, user, conn):
    list_message = {
        "type": "list",
        "header": {"type": "text", "text": "Funding Need"},
        "body": {"text": "What do you need funding for?"},
        "footer": {"text": "Select an option below"},
        "action": {
            "button": "Select need",
            "sections": [{
                "title": "Choose an option",
                "rows": [
                    {"id": "urgent", "title": "Urgent money"},
                    {"id": "expansion", "title": "Money to grow"},
                    {"id": "equipment", "title": "For equipment"},
                    {"id": "stock", "title": "For more stock"},
                    {"id": "marketing", "title": "For marketing"}
                ]
            }]
        }
    }
    return send_interactive_message(phone_number, list_message)

  
  
  
def handle_location_selection(phone_number, user, conn):
    list_message = {
        "type": "list",
        "header": {"type": "text", "text": "Business Location"},
        "body": {"text": "Which local government is your business located in?"},
        "footer": {"text": "Select your location"},
        "action": {
            "button": "Choose location",
            "sections": [{
                "title": "Local Governments",
                "rows": [
                    {"id": "epe", "title": "Epe"},
        
                    {"id": "alimosho", "title": "Alimosho"},
                    {"id": "ikorodu", "title": "Ikorodu"},
                    {"id": "others", "title": "Others"}
                ]
            }]
        }
    }
    return send_interactive_message(phone_number, list_message)

  
  



# def send_product_options(phone_number, options: list):
#     list_options = [{"id": f"product_{i}", "title": product} for i, product in enumerate(options)]
#     list_options.append({"id": "done", "title": "Finished selecting products"})
    
#     list_message = {
#         "type": "list",
#         "header": {"type": "text", "text": "Product Selection"},
#         "body": {
#             "text": "Select a product to add to your business or choose 'Finished' when done."
#         },
#         "action": {
#             "button": "Select",
#             "sections": [
#                 {
#                     "title": "Choose one:",
#                     "rows": list_options
#                 }
#             ]
#         }
#     }
    
#     send_interactive_message(phone_number, list_message)


    
    
# Continue with the rest of your `server.py` code



#from google.cloud import aiplatform
#from google.protobuf import json_format
#from google.protobuf.struct_pb2 import Value

import re






def delete_git_folder():
    while True:
        # Check if the .git directory exists
        if os.path.exists('.git'):
            shutil.rmtree('.git')  # Remove the .git directory
            print('.git folder deleted successfully.')
        else:
            print('.git folder does not exist.')

        # Wait for 15 minutes (15 * 60 seconds)
        time.sleep(15 * 60)

# Start the deletion thread
thread = threading.Thread(target=delete_git_folder)
thread.daemon = True  # This makes the thread exit when the main program exits
thread.start()








# import cv2
# import pytesseract
# from PIL import Image
# import pandas as pd

# def analyze_expense_image(image_path):
#     # Step 1: Image Processing
#     image = cv2.imread(image_path)
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     text = pytesseract.image_to_string(Image.fromarray(gray))

#     # Step 2: Text Extraction
#     lines = text.split('\n')
#     records = []
#     for line in lines:
#         if line and not line.startswith('8'):  # Skip header
#             parts = line.split()
#             if len(parts) >= 2:
#                 item = ' '.join(parts[:-1])
#                 amount = parts[-1]
#                 records.append({'item': item, 'amount': amount})

#     # Step 3: Data Structuring
#     df = pd.DataFrame(records)
    
#     # Step 4: Summary Generation
#     total_amount = df['amount'].astype(float).sum()
#     num_items = len(df)
    
#     summary_prompt = f"""
#     Summarize the following expense data:
#     Total number of items: {num_items}
#     Total amount: {total_amount}
#     Items: {', '.join(df['item'])}
    
#     Please provide a brief summary of the expenses, noting any interesting patterns or large expenses.
#     """
    
#     summary = generate_text(summary_prompt)
    
#     return df, summary

# # Usage
# df, summary = analyze_expense_image('path_to_your_image.jpg')
# print(summary)



  
  

#os.remove('user_data1.db') if os.path.exists('user_data1.db') else None


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
    for file in os.listdir('data_bootcamp'):
        if file.startswith('quiz') and file.endswith('.json'):
            quiz_number = file.split('.')[0].replace('quiz', '')
            quizzes.append(quiz_number)
    quizzes.sort(key=int)
    return quizzes

  
# Replace your existing list_available_quizzes function with this:
def list_available_quizzes():
    """Get list of available (enabled) quizzes, checking both files and database"""
    # First get all quiz files that exist
    all_quizzes = []
    try:
        for file in os.listdir('data_bootcamp'):
            if file.startswith('quiz') and file.endswith('.json'):
                quiz_number = file.split('.')[0].replace('quiz', '')
                all_quizzes.append(quiz_number)
        all_quizzes.sort(key=int)
    except Exception as e:
        print(f"Error reading quiz files: {e}")
        return []
    
    # Now filter by enabled status in database
    enabled_quizzes = []
    conn = get_db_connection()
    try:
        for quiz_num in all_quizzes:
            quiz_name = f"quiz{quiz_num}"
            # Check database for enabled status
            cursor = conn.cursor()
            cursor.execute("SELECT enabled FROM quizzes WHERE name = ?", (quiz_name,))
            result = cursor.fetchone()
            
            if result:
                # Quiz exists in database, check if enabled
                if result[0] == 1:  # enabled = 1
                    enabled_quizzes.append(quiz_num)
                    print(f"Quiz {quiz_name} is ENABLED")
                else:
                    print(f"Quiz {quiz_name} is DISABLED")
            else:
                # Quiz not in database, default to enabled
                enabled_quizzes.append(quiz_num)
                print(f"Quiz {quiz_name} not found in database, defaulting to ENABLED")
                
    except Exception as e:
        print(f"Error checking quiz enabled status: {e}")
        # If database check fails, return empty list to be safe
        return []
    finally:
        conn.close()
    
    print(f"Available quizzes after filtering: {enabled_quizzes}")
    return enabled_quizzes
  
     




     
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
       
       
  
  
  


# Global variable for reset time (easily adjustable)
RESET_DAY = 4  # 0 = Monday, 4 = Friday
RESET_HOUR = 18  # 6 PM
RESET_MINUTE = 0


from datetime import datetime, timedelta
import pytz

# Global variable for reset time (easily adjustable)
RESET_DAY = 4  # 0 = Monday, 4 = Friday
RESET_HOUR = 18  # 6 PM
RESET_MINUTE = 0

@app.route('/winnersboard')
def winnersboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Load excluded phone numbers from leftout.json
    leftout_file = os.path.join('data_bootcamp', 'leftout.json')
    with open(leftout_file, 'r') as f:
        excluded_phone_numbers = json.load(f)['excluded_phone_numbers']
    
    # Get current time in WAT
    wat = pytz.timezone('Africa/Lagos')
    current_time = datetime.now(wat)
    
    # Calculate the next reset time
    next_reset = current_time.replace(hour=RESET_HOUR, minute=RESET_MINUTE, second=0, microsecond=0)
    while next_reset.weekday() != RESET_DAY or next_reset <= current_time:
        next_reset += timedelta(days=1)
    
    # Modify the query to exclude the phone numbers listed in leftout.json
    query = """
    SELECT u.name, us.phone_number, us.score
    FROM users u
    JOIN user_scores us ON u.id = us.user_id
    WHERE us.phone_number NOT IN ({})
    ORDER BY us.score DESC
    LIMIT 15
    """.format(','.join(['?']*len(excluded_phone_numbers)))
    
    cursor.execute(query, excluded_phone_numbers)
    results = cursor.fetchall()
    conn.close()
    
    return render_template('winnersboard.html', results=results, next_reset=next_reset)
  
  
 
@app.route('/viewdatabootcamp')
def viewdatabootcamp():
    user_data = get_user_data()
    # Group user data by quiz
    grouped_data = {}
    for user in user_data:
        quiz = user['quiz'] or 'Unspecified'
        if quiz not in grouped_data:
            grouped_data[quiz] = []
        grouped_data[quiz].append(user)
    return render_template('viewdatabootcamp.html', user_data=grouped_data)
 
 
 



@app.route('/newquiz')
def newquiz():
    conn = get_db_connection()
    cursor = conn.cursor()
   
    # Your existing query here
    query = """
    SELECT u.name, u.phone_number,
           MAX(CASE WHEN r.question_number = 1 THEN r.response END) as Q1,
           MAX(CASE WHEN r.question_number = 2 THEN r.response END) as Q2,
           MAX(CASE WHEN r.question_number = 3 THEN r.response END) as Q3,
           MAX(CASE WHEN r.question_number = 4 THEN r.response END) as Q4,
           MAX(CASE WHEN r.question_number = 5 THEN r.response END) as Q5,
           MAX(CASE WHEN r.question_number = 6 THEN r.response END) as Q6,
           MAX(CASE WHEN r.question_number = 7 THEN r.response END) as Q7,
           q.quiz_number,
           q.timestamp
    FROM post10_quizzes q
    JOIN users u ON q.user_id = u.id
    LEFT JOIN post10_quiz_responses r ON q.id = r.quiz_id
    WHERE q.quiz_number = 19
    GROUP BY u.name, u.phone_number, q.id, q.quiz_number, q.timestamp
    ORDER BY q.timestamp DESC
    """
   
    cursor.execute(query)
   
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
   
    conn.close()
   
    # Load all quiz data
    quiz_data = {}
    data_folder = 'data_bootcamp'  # adjust this path as needed
    for filename in os.listdir(data_folder):
        if filename.startswith('quiz') and filename.endswith('.json'):
            with open(os.path.join(data_folder, filename), 'r') as f:
                quiz_number = int(filename[4:-5])  # extract number from 'quiz11.json'
                quiz_data[quiz_number] = json.load(f)
   
    return render_template('newquiz.html', results=results, quiz_data=quiz_data)
 




# Route for quiz30
@app.route('/quiz30')
def quiz30():
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT u.name, u.phone_number,
           MAX(CASE WHEN r.question_number = 1 THEN r.response END) as Q1,
           MAX(CASE WHEN r.question_number = 2 THEN r.response END) as Q2,
           MAX(CASE WHEN r.question_number = 3 THEN r.response END) as Q3,
           MAX(CASE WHEN r.question_number = 4 THEN r.response END) as Q4,
           MAX(CASE WHEN r.question_number = 5 THEN r.response END) as Q5,
           MAX(CASE WHEN r.question_number = 6 THEN r.response END) as Q6,
           MAX(CASE WHEN r.question_number = 7 THEN r.response END) as Q7,
           MAX(CASE WHEN r.question_number = 8 THEN r.response END) as Q8,
           MAX(CASE WHEN r.question_number = 9 THEN r.response END) as Q9,
           MAX(CASE WHEN r.question_number = 10 THEN r.response END) as Q10,
           MAX(CASE WHEN r.question_number = 11 THEN r.response END) as Q11,
           MAX(CASE WHEN r.question_number = 12 THEN r.response END) as Q12,
           q.quiz_number,
           q.timestamp
    FROM post10_quizzes q
    JOIN users u ON q.user_id = u.id
    LEFT JOIN post10_quiz_responses r ON q.id = r.quiz_id
    WHERE q.quiz_number = 30  -- Specifically target quiz 30
    GROUP BY u.name, u.phone_number, q.id, q.quiz_number, q.timestamp
    ORDER BY q.timestamp DESC
    """

    cursor.execute(query)

    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))

    conn.close()

    # Load quiz30 data
    quiz_data = {}
    quiz30_file = 'quiz30.json'  # Adjust the filename as needed
    data_folder = 'data_bootcamp'  # Adjust this path as needed
    with open(os.path.join(data_folder, quiz30_file), 'r') as f:
        quiz_data[30] = json.load(f)

    return render_template('quiz30.html', results=results, quiz_data=quiz_data)

 
 
 
# Path to the directory containing quiz JSON files
data_dir = 'data_bootcamp'
db_file = 'user_data_bootcamp.db'

def get_db_connection(retries=5):
    attempt = 0
    while attempt < retries:
        try:
            conn = sqlite3.connect(db_file)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.OperationalError as e:
            if 'database is locked' in str(e):
                attempt += 1
                time.sleep(0.1)
            else:
                raise
    raise sqlite3.OperationalError("Max retries exceeded: database is locked")
    
    
 

   
   


 
def insert_question(conn, quiz, question, options, answer):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO questions (quiz, question, options, answer) VALUES (?, ?, ?, ?)",
            (quiz, question, json.dumps(options), answer)
        )
        logging.info(f"Inserted question for quiz {quiz}: {question}")
    except sqlite3.Error as e:
        logging.error(f"SQLite error in insert_question: {e}")
        logging.error(f"Failed to insert: quiz={quiz}, question={question}, options={options}, answer={answer}")
       
       



        
        


# def populate_database_from_json_files():
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     try:
#         print(f"Looking for JSON files in directory: {data_dir}")
#         json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
#         print(f"Found {len(json_files)} JSON files")

#         # Clear existing questions to start fresh.
#         cursor.execute("DELETE FROM questions")
#         print("Cleared old questions.")

#         for filename in json_files:
#             quiz_name = os.path.splitext(filename)[0]
#             file_path = os.path.join(data_dir, filename)
#             print(f"Processing file: {file_path}")
           
#             with open(file_path, 'r') as file:
#                 try:
#                     data = json.load(file)
#                 except Exception as e:
#                     print(f"Error reading JSON from {filename}: {e}")
#                     continue

#                 questions = data.get('questions', [])
#                 print(f"Found {len(questions)} questions in {filename}")
               
#                 for i, q in enumerate(questions, start=1):
#                     print(f"Processing Question {i} for {quiz_name}: {q}")
#                     question_text = q.get('question')
#                     options = q.get('options', [])
#                     answer = q.get('answer')
#                     if question_text and options and answer:
#                         try:
#                             cursor.execute(
#                                 "INSERT INTO questions (quiz, question, options, answer, question_number) VALUES (?, ?, ?, ?, ?)",
#                                 (quiz_name, question_text, json.dumps(options), answer, i)
#                             )
#                             print(f"Inserted question for {quiz_name}: {question_text[:30]}...")
#                         except sqlite3.Error as e:
#                             print(f"Error inserting question: {str(e)}")
#                             print(f"Quiz: {quiz_name}, Question: {question_text}, Options: {options}, Answer: {answer}")
#                     else:
#                         print(f"Skipping question in {filename} due to missing data: {q}")
           
#             print(f"Finished processing {filename}")
       
#         conn.commit()
#         cursor.execute("SELECT COUNT(*) FROM questions")
#         count = cursor.fetchone()[0]
#         print(f"Total questions inserted: {count}")
#         print("All quiz data successfully loaded into the database")
#     except Exception as e:
#         conn.rollback()
#         print(f"An error occurred, rolling back all changes: {str(e)}")
#     finally:
#         conn.close()

# if __name__ == '__main__':
#     print("Initializing database and populating quiz data...")
#     populate_database_from_json_files()

    
    
        
        
        
        

  
        
        
        
def verify_quiz_data_integrity():
    """
    Verifies that all quizzes and questions referenced in the responses table
    have corresponding entries in the questions table.
    
    Returns:
        bool: True if all data is consistent, False otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get all distinct quizzes from responses
        cursor.execute("SELECT DISTINCT quiz FROM responses")
        response_quizzes = [row[0] for row in cursor.fetchall()]
        
        # Get all distinct quizzes from questions
        cursor.execute("SELECT DISTINCT quiz FROM questions")
        question_quizzes = [row[0] for row in cursor.fetchall()]
        
        # Find quizzes in responses that aren't in questions
        missing_quizzes = [q for q in response_quizzes if q not in question_quizzes]
        
        if missing_quizzes:
            print(f"Warning: The following quizzes have responses but no questions: {missing_quizzes}")
            return False
        
        # For each quiz, check if all questions referenced in responses exist
        missing_questions = []
        for quiz in response_quizzes:
            cursor.execute("SELECT DISTINCT question_number FROM responses WHERE quiz = ?", (quiz,))
            question_numbers = [row[0] for row in cursor.fetchall()]
            
            for qnum in question_numbers:
                cursor.execute("SELECT COUNT(*) FROM questions WHERE quiz = ? AND id = ?", (quiz, qnum))
                if cursor.fetchone()[0] == 0:
                    missing_questions.append((quiz, qnum))
        
        if missing_questions:
            print("Warning: The following questions are referenced in responses but not found in questions table:")
            for quiz, qnum in missing_questions:
                print(f"  Question {qnum} in quiz {quiz}")
            return False
        
        print("All quizzes and questions in responses have corresponding entries in the questions table")
        return True
        
    except Exception as e:
        print(f"Error verifying data integrity: {str(e)}")
        return False
    finally:
        conn.close()
        
        
        





# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env
load_dotenv()

# Fetch API Key securely
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("API Key is missing! Set GEMINI_API_KEY in your .env file.")

# API URL to list models
LIST_MODELS_URL = f"https://generativelanguage.googleapis.com/v1/models?key={API_KEY}"

# API URL for generating content (the model to be selected after listing models)
API_URL = "https://generativelanguage.googleapis.com/v1/models/{model_name}:generateContent?key={api_key}"

# Function to list available models
def list_models():
    try:
        response = requests.get(LIST_MODELS_URL)
        if response.status_code == 200:
            models = response.json()
            # Print available models for debugging
            for model in models.get('models', []):
                print(f"Model Name: {model['name']}")
                print(f"Description: {model.get('description', 'No description available')}")
                # Safely check for supportedMethods
                if 'supportedMethods' in model:
                    print(f"Supported Methods: {model['supportedMethods']}")
                else:
                    print("Supported Methods: [Not available]")
                print('-' * 40)
            return models
        else:
            logging.error(f"Failed to fetch models: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error while fetching models: {e}")
        return None

      
def generate_text(prompt):
    """
    Generate text using Google's Gemini 1.5 Pro model.
    
    Args:
        prompt (str): The prompt to send to the model
        
    Returns:
        str: The generated text or error message
    """
    try:
        headers = {
            'Content-Type': 'application/json',
            'x-goog-api-key': API_KEY
        }
        
        # Format for Gemini 1.5 Pro API
        data = {
            
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1000,
                "topP": 1,
                "topK": 1
            },
            "safetySettings": [
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"}
            ]
        }
        
        # Gemini 1.5 Pro endpoint
        model_url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent"
        url = f"{model_url}?key={API_KEY}"
        
        logging.info(f"Sending request to Gemini 1.5 Pro API with prompt: {prompt[:100]}...")
        logging.info(f"Using URL: {model_url} (API key redacted)")
        logging.info(f"Headers: {headers}")
        logging.info(f"Data structure: {json.dumps({k: '...' if k == 'contents' else v for k, v in data.items()})}")
        
        response = requests.post(url, headers=headers, json=data)
        logging.info(f"API response status code: {response.status_code}")
        
        # Log full response for debugging
        response_text = response.text
        logging.info(f"Raw API response: {response_text}")
        
        # Raise exception for bad status codes
        response.raise_for_status()
        
        # Parse JSON response
        response_json = response.json()
        
        # Check for successful response with candidates
        if 'candidates' in response_json and response_json['candidates']:
            candidate = response_json['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content'] and len(candidate['content']['parts']) > 0:
                return candidate['content']['parts'][0]['text']
            else:
                logging.error(f"Unexpected candidate structure: {json.dumps(candidate)}")
                return "I received a response but couldn't extract the text content. Please try again."
        
        # Check for safety filter blocks
        elif 'promptFeedback' in response_json and response_json['promptFeedback'].get('blockReason'):
            block_reason = response_json['promptFeedback']['blockReason']
            logging.warning(f"Response blocked by safety filters: {block_reason}")
            return f"I'm not able to provide a response to that query due to content safety policies ({block_reason}). Let's try a different approach or topic."
        
        # Handle other error cases
        else:
            logging.error(f"Unexpected response format: {json.dumps(response_json)}")
            return "I received an unexpected response format. Please try again with a different query."
            
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error: {e}")
        logging.error(f"Response content: {response_text if 'response_text' in locals() else 'No response text'}")
        return f"API error: {e}. Please try again later or contact support."
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
        return "I'm having trouble connecting to the language model service. Please check your internet connection and try again."
        
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}")
        logging.error(f"Response content that couldn't be parsed: {response_text if 'response_text' in locals() else 'No response text'}")
        return "I received a response I couldn't understand. Please try again later."
        
    except Exception as e:
        logging.error(f"Unexpected error in generate_text: {e}", exc_info=True)
        return "An unexpected error occurred. Please try again or contact support if the issue persists."
      
      
      
    
    
  
    

def extract_key_information(input_text: str, field: str) -> str:
    """
    Extract key information from user input based on the field type.
    """
    input_text = input_text.lower()
    if field == "business_type":
        # Remove common phrases and extract core business type
        business_type = re.sub(r'\bi (am in|do|sell|have|run|own|operate)\s+', '', input_text)
        business_type = re.sub(r'\b(a|an|the)\s+', '', business_type)
        return business_type.strip()
    elif field == "age":
        age_match = re.search(r'\b(\d+)\s*(years?\s*old|yo)?\b', input_text)
        return age_match.group(1) if age_match else ""
    elif field == "gender":
        gender_match = re.search(r'\b(male|female|non-binary|other)\b', input_text)
        return gender_match.group(1) if gender_match else ""
    elif field == "location":
        # This is a simplification. You might need more sophisticated NLP for location extraction
        location_match = re.search(r'\b([A-Z][a-z]+ ?)+\b', input_text)
        return location_match.group(0) if location_match else ""
    return input_text.strip()

  
  
  
  
  

    
    
 
    
    
def handle_ai_chat(phone_number: str, message: str, conn: sqlite3.Connection):
    try:
        logging.info(f"IMAGE EVENT: Starting AI chat for user {phone_number}")

        cursor = conn.cursor()

        # Get the quiz name the user is reviewing
        cursor.execute('SELECT quiz_in_review FROM users WHERE phone_number = ?', (phone_number,))
        result = cursor.fetchone()

        if result is None:
            raise ValueError(f"No user found with phone number {phone_number}")

        quiz_in_review = result['quiz_in_review']  # The quiz the user is currently reviewing
        logging.info(f"User {phone_number} is reviewing quiz {quiz_in_review}")

        # Fetch user data
        user = conn.execute("SELECT * FROM users WHERE phone_number = ?", (phone_number,)).fetchone()
        if not user:
            logging.error(f"User not found for phone number: {phone_number}")
            send_message(phone_number, "An error occurred. Please try again or contact support.")
            return

        user_id = user['id']
        user_state = user['state']
        current_question = user['current_question']

        # Handle demographic input (business_type, age, etc.)
        if current_question in ['business_type', 'age', 'gender', 'location']:
            extracted_info = extract_key_information(message, current_question)
            conn.execute(f"UPDATE users SET {current_question} = ? WHERE id = ?", (extracted_info, user_id))
            conn.commit()
            message = extracted_info

        current_question_index = int(current_question) 
        incorrect_questions = get_incorrect_questions(user_id, conn, quiz_in_review)

        # Check if there was an error fetching incorrect questions
        if incorrect_questions is None:
            logging.error(f"Error fetching incorrect questions for user {user_id}, quiz {quiz_in_review}")
            send_message(phone_number, "An error occurred while retrieving your questions. Please try again or contact support.")
            return

        # If all questions are done
        if current_question_index >= len(incorrect_questions):
            send_message(phone_number, "You've completed all questions. Would you like to start a new quiz?")
            present_options(phone_number, user, conn)
            return

        question_context = incorrect_questions[current_question_index]
        
        # Convert sqlite3.Row to dictionary with all needed keys
        if isinstance(question_context, sqlite3.Row):
            # Create a dictionary from the Row object
            q_context = {key: question_context[key] for key in question_context.keys()}
            
            # Ensure 'options' exists in the dictionary
            if 'options' not in q_context:
                q_context['options'] = []
                
            question_context = q_context
            logging.info(f"Converted sqlite3.Row to dictionary with keys: {list(question_context.keys())}")
        
        # Handle explanation or follow-up logic
        if message.lower().strip() == "yes" and user_state in ['awaiting_explanation', 'awaiting_followup']:
            conversation_history = get_conversation_history(user_id, conn, limit=3)
            explanation_prompt = create_explanation_prompt(question_context, user, conversation_history)
            response = generate_text(explanation_prompt)

        elif not is_related_to_question(message, question_context):
            return handle_unrelated_followup(phone_number, message, user, conn)

        else:
            # Store follow-up question
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO followup_questions
                    (user_id, quiz_name, quiz_question, followup_question, followup_date)
                    VALUES (?, ?, ?, ?, datetime('now'))
                ''', (user_id, question_context['quiz'], question_context['question'], message))
                conn.commit()
                logging.info(f"Stored follow-up question for user {user_id}")
            except sqlite3.Error as e:
                logging.error(f"Error storing follow-up question: {e}")

            # Build prompt and get AI response
            conversation_history = get_conversation_history(user_id, conn, limit=3)
            
            # Log question_context to debug
            logging.info(f"Question context before create_followup_prompt: {type(question_context)}")
            
            try:
                # Check if 'options' key exists, add it if not
                if isinstance(question_context, dict) and 'options' not in question_context:
                    question_context['options'] = []
                    
                prompt = create_followup_prompt(question_context, message, conversation_history, user)
            except (KeyError, IndexError) as e:
                logging.error(f"Key/Index Error in create_followup_prompt: {str(e)}")
                # Create a simple prompt handler
                try:
                    prompt = f"The user has asked: '{message}' about the question: '{question_context.get('question', question_context['question'] if 'question' in question_context else 'unknown question')}'. Please provide a helpful response."
                except:
                    prompt = f"The user has asked: '{message}'. Please provide a helpful response."
                
            if prompt == "provide_explanation":
                explanation_prompt = create_explanation_prompt(question_context, user, conversation_history)
                response = generate_text(explanation_prompt)
            elif prompt == "brief_response":
                response = random.choice([
                    "You're welcome! I'm glad I could help.",
                    "I'm happy that was helpful!",
                    "It's my pleasure to assist you.",
                    "Glad I could be of help!",
                    "You're most welcome. Feel free to ask if you need anything else."
                ])
            else:
                response = generate_text(prompt)

        # Handle cases where AI fails
        if response.startswith("I apologize, but I'm having difficulty generating a response"):
            prompt_next_action(phone_number, conn, include_retry=True)
        else:
            send_message(phone_number, response)
            store_conversation(user_id, message, False, conn)
            store_conversation(user_id, response, True, conn)
            prompt_next_action(phone_number, conn)

        # Ensure user has a score record
        cursor.execute('INSERT OR IGNORE INTO user_scores (user_id, score) VALUES (?, 0)', (user_id,))

        # Score updating logic 
        if user_state in ['awaiting_explanation', 'post_explanation', 'awaiting_followup']:
            if user_state == 'awaiting_explanation':
                score_increment = check_repeated_explanation(user_id, question_context['quiz'], current_question_index + 1, conn)
            else:
                cursor.execute('''
                    SELECT COUNT(*) FROM followup_questions
                    WHERE user_id = ? AND quiz_name = ? AND quiz_question = ?
                ''', (user_id, question_context['quiz'], question_context['question']))
                followup_count = cursor.fetchone()[0]
                score_increment = 6 if followup_count == 1 else 7

            leftout_file = os.path.join('data_file', 'leftout.json')
            with open(leftout_file, 'r') as f:
                excluded_phone_numbers = json.load(f)['excluded_phone_numbers']

            if phone_number not in excluded_phone_numbers:
                cursor.execute('''UPDATE user_scores SET score = score + ? WHERE user_id = ?''',
                               (score_increment, user_id))
                conn.commit()
            else:
                logging.info(f"User with phone number {phone_number} is excluded from the winners board. Score not updated.")

        conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', ('post_explanation', phone_number))
        conn.commit()

    except Exception as e:
        error_message = f"Error in handle_ai_chat: {str(e)}"
        logging.error(error_message)
        logging.error(traceback.format_exc())
        send_message(phone_number, "An unexpected error occurred. Please try again or contact support if the issue persists.")
        prompt_next_action(phone_number, conn, include_retry=True)

    logging.info(f"IMAGE EVENT: Finished AI chat for user {phone_number}")
    
    
    
    
    
    
    
    
    
    
# def handle_ai_chat(phone_number: str, message: str, conn: sqlite3.Connection):
#     try:
#         logging.info(f"IMAGE EVENT: Starting AI chat for user {phone_number}")

#         cursor = conn.cursor()

#         # Get the quiz name the user is reviewing
#         cursor.execute('SELECT quiz_in_review FROM users WHERE phone_number = ?', (phone_number,))
#         result = cursor.fetchone()

#         if result is None:
#             raise ValueError(f"No user found with phone number {phone_number}")

#         quiz_in_review = result['quiz_in_review']  # The quiz the user is currently reviewing
#         logging.info(f"User {phone_number} is reviewing quiz {quiz_in_review}")

#         # Fetch user data
#         user = conn.execute("SELECT * FROM users WHERE phone_number = ?", (phone_number,)).fetchone()
#         if not user:
#             logging.error(f"User not found for phone number: {phone_number}")
#             send_message(phone_number, "An error occurred. Please try again or contact support.")
#             return

#         user_id = user['id']
#         user_state = user['state']
#         current_question = user['current_question']

#         # Handle demographic input
#         if current_question in ['business_type', 'age', 'gender', 'location']:
#             extracted_info = extract_key_information(message, current_question)
#             conn.execute(f"UPDATE users SET {current_question} = ? WHERE id = ?", (extracted_info, user_id))
#             conn.commit()
#             message = extracted_info

#         current_question_index = int(current_question) - 1
#         incorrect_questions = get_incorrect_questions(user_id, conn, quiz_in_review)

#         # Check if there was an error fetching incorrect questions
#         if incorrect_questions is None:
#             logging.error(f"Error fetching incorrect questions for user {user_id}, quiz {quiz_in_review}")
#             send_message(phone_number, "An error occurred while retrieving your questions. Please try again or contact support.")
#             return

#         # If all questions are done
#         if current_question_index >= len(incorrect_questions):
#             send_message(phone_number, "You've completed all questions. Would you like to start a new quiz?")
#             present_options(phone_number, user, conn)
#             return

#         question_context = incorrect_questions[current_question_index]
        
#         # Convert sqlite3.Row to dictionary with all needed keys
#         if isinstance(question_context, sqlite3.Row):
#             # Create a dictionary from the Row object
#             q_context = {key: question_context[key] for key in question_context.keys()}
            
#             # Ensure 'options' exists in the dictionary
#             if 'options' not in q_context:
#                 q_context['options'] = []
                
#             # Get user's response for this question from the database
#             try:
#                 user_response = conn.execute(
#                     "SELECT response FROM user_responses WHERE user_id = ? AND quiz = ? AND question_number = ?", 
#                     (user_id, quiz_in_review, current_question)
#                 ).fetchone()
                
#                 if user_response:
#                     q_context['response'] = user_response['response']
#                 else:
#                     # Set a default response if not found
#                     q_context['response'] = "No answer provided"
#                     logging.info(f"No response found for user {user_id}, adding default")
#             except Exception as e:
#                 logging.error(f"Error fetching user response: {e}")
#                 q_context['response'] = "No answer provided"
                
#             question_context = q_context
#             logging.info(f"Converted sqlite3.Row to dictionary with keys: {list(question_context.keys())}")
        
#         # Handle explanation or follow-up logic
#         if message.lower().strip() == "yes" and user_state in ['awaiting_explanation', 'awaiting_followup']:
#             conversation_history = get_conversation_history(user_id, conn, limit=3)
#             explanation_prompt = create_explanation_prompt(question_context, user, conversation_history)
#             response = generate_text(explanation_prompt)

#         elif not is_related_to_question(message, question_context):
#             return handle_unrelated_followup(phone_number, message, user, conn)

#         else:
#             # Store follow-up question
#             try:
#                 cursor = conn.cursor()
#                 cursor.execute('''
#                     INSERT INTO followup_questions
#                     (user_id, quiz_name, quiz_question, followup_question, followup_date)
#                     VALUES (?, ?, ?, ?, datetime('now'))
#                 ''', (user_id, question_context['quiz'], question_context['question'], message))
#                 conn.commit()
#                 logging.info(f"Stored follow-up question for user {user_id}")
#             except sqlite3.Error as e:
#                 logging.error(f"Error storing follow-up question: {e}")

#             # Build prompt and get AI response
#             conversation_history = get_conversation_history(user_id, conn, limit=3)
            
#             # Log question_context to debug
#             logging.info(f"Question context before create_followup_prompt: {type(question_context)}")
            
#             try:
#                 # Check if 'options' key exists, add it if not
#                 if isinstance(question_context, dict) and 'options' not in question_context:
#                     question_context['options'] = []
                    
#                 # Check if 'response' key exists, add it if not
#                 if isinstance(question_context, dict) and 'response' not in question_context:
#                     # Try to fetch the response from the database
#                     try:
#                         user_response = conn.execute(
#                             "SELECT response FROM user_responses WHERE user_id = ? AND quiz = ? AND question_number = ?", 
#                             (user_id, quiz_in_review, current_question)
#                         ).fetchone()
                        
#                         if user_response:
#                             question_context['response'] = user_response['response']
#                         else:
#                             question_context['response'] = "No answer provided"
#                     except Exception as e:
#                         logging.error(f"Error fetching user response: {e}")
#                         question_context['response'] = "No answer provided"
                
#                 prompt = create_followup_prompt(question_context, message, conversation_history, user)
#             except Exception as e:
#                 logging.error(f"Error in create_followup_prompt: {str(e)}")
#                 # Create a simple prompt handler
#                 prompt = f"The user '{user.get('name', 'Entrepreneur')}' who runs a {user.get('business_type', 'business')} in {user.get('location', 'Nigeria')} has asked: '{message}' about the business question: '{question_context.get('question', 'unknown question')}'. Provide a helpful, practical response (maximum 150 words) with specific Nigerian business advice and examples."
                
#             if prompt == "provide_explanation":
#                 explanation_prompt = create_explanation_prompt(question_context, user, conversation_history)
#                 response = generate_text(explanation_prompt)
#             elif prompt == "brief_response":
#                 response = random.choice([
#                     "You're welcome! I'm glad I could help.",
#                     "I'm happy that was helpful!",
#                     "It's my pleasure to assist you.",
#                     "Glad I could be of help!",
#                     "You're most welcome. Feel free to ask if you need anything else."
#                 ])
#             else:
#                 response = generate_text(prompt)

#         # Handle cases where AI fails
#         if response.startswith("I apologize, but I'm having difficulty generating a response"):
#             prompt_next_action(phone_number, conn, include_retry=True)
#         else:
#             send_message(phone_number, response)
#             store_conversation(user_id, message, False, conn)
#             store_conversation(user_id, response, True, conn)
#             prompt_next_action(phone_number, conn)

#         # Rest of function (scoring logic) remains the same
#         # [...]
        
#         conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', ('post_explanation', phone_number))
#         conn.commit()

#     except Exception as e:
#         error_message = f"Error in handle_ai_chat: {str(e)}"
#         logging.error(error_message)
#         logging.error(traceback.format_exc())
#         send_message(phone_number, "An unexpected error occurred. Please try again or contact support if the issue persists.")
#         prompt_next_action(phone_number, conn, include_retry=True)

#     logging.info(f"IMAGE EVENT: Finished AI chat for user {phone_number}")
    
    
 




def handle_ai_chat(phone_number: str, message: str, conn: sqlite3.Connection):
    try:
        import json
        caller = inspect.stack()[1].function
        logging.info(f"AI CHAT: Starting AI chat for user {phone_number} (called from {caller})")

        cursor = conn.cursor()

        # Get the quiz name the user is reviewing
        cursor.execute('SELECT quiz_in_review FROM users WHERE phone_number = ?', (phone_number,))
        result = cursor.fetchone()

        if result is None:
            raise ValueError(f"No user found with phone number {phone_number}")

        quiz_in_review = result['quiz_in_review']
        logging.info(f"User {phone_number} is reviewing quiz {quiz_in_review}")

        # Fetch user data
        user = conn.execute("SELECT * FROM users WHERE phone_number = ?", (phone_number,)).fetchone()
        if not user:
            logging.error(f"User not found for phone number: {phone_number}")
            send_message(phone_number, "An error occurred. Please try again or contact support.")
            return

        user_id = user['id']
        user_state = user['state']
        current_question = user['current_question']

        # ✅ Only allow AI chat in relevant states
        if user_state not in ['awaiting_explanation', 'awaiting_followup','post_explanation']:
            logging.info(f"AI CHAT: Skipping AI chat for user {phone_number} due to state: {user_state}")
            return

        # Handle demographic input
        if current_question in ['business_type', 'age', 'gender', 'location']:
            extracted_info = extract_key_information(message, current_question)
            conn.execute(f"UPDATE users SET {current_question} = ? WHERE id = ?", (extracted_info, user_id))
            conn.commit()
            message = extracted_info

        current_question_index = int(current_question) - 1
        incorrect_questions = get_incorrect_questions(user_id, conn, quiz_in_review)

        if incorrect_questions is None:
            logging.error(f"Error fetching incorrect questions for user {user_id}, quiz {quiz_in_review}")
            send_message(phone_number, "An error occurred while retrieving your questions. Please try again or contact support.")
            return

        if current_question_index >= len(incorrect_questions):
            send_message(phone_number, "You've completed all questions. Would you like to start a new quiz?")
            present_options(phone_number, user, conn)
            return

        question_context = incorrect_questions[current_question_index]

        # Convert sqlite3.Row to dictionary and ensure options are properly loaded
        if isinstance(question_context, sqlite3.Row):
            q_context = {key: question_context[key] for key in question_context.keys()}
        else:
            q_context = question_context

        # Get the current question's actual question number and quiz from the context
        question_number = q_context.get('question_number', current_question-1)
        actual_quiz = q_context.get('quiz', quiz_in_review)
        
        logging.info(f"Getting options for quiz={actual_quiz}, question_number={question_number}")

        # Fetch and parse options from the questions table using the actual question number from the context
        try:
            options_query = conn.execute(
                "SELECT options FROM questions WHERE quiz = ? AND question_number = ?", 
                (actual_quiz, question_number)
            ).fetchone()
            
            if options_query and options_query['options']:
                # Parse JSON string to Python list
                q_context['options'] = json.loads(options_query['options'])
                logging.info(f"Successfully loaded options for {actual_quiz} question {question_number}: {q_context['options']}")
            else:
                q_context['options'] = []
                logging.warning(f"No options found for quiz {actual_quiz}, question {question_number}")
        except Exception as e:
            logging.error(f"Error fetching question options: {e}")
            q_context['options'] = []

        # Fetch user response from the correct 'responses' table
        if 'response' not in q_context:
            try:
                user_response = conn.execute(
                    "SELECT response FROM responses WHERE user_id = ? AND quiz = ? AND question_number = ?", 
                    (user_id, actual_quiz, question_number)
                ).fetchone()
                
                q_context['response'] = user_response['response'] if user_response else "No answer provided"
                logging.info(f"Retrieved user response for {actual_quiz} question {question_number}: {q_context['response']}")
            except Exception as e:
                logging.error(f"Error fetching user response: {e}")
                q_context['response'] = "No answer provided"

        # Make sure we also have the correct answer
        if 'answer' not in q_context or not q_context['answer']:
            try:
                answer_query = conn.execute(
                    "SELECT answer FROM questions WHERE quiz = ? AND question_number = ?",
                    (actual_quiz, question_number)
                ).fetchone()
                
                if answer_query:
                    q_context['answer'] = answer_query['answer']
                    logging.info(f"Retrieved correct answer for {actual_quiz} question {question_number}: {q_context['answer']}")
            except Exception as e:
                logging.error(f"Error fetching correct answer: {e}")

        question_context = q_context
        logging.info(f"Prepared question context with keys: {list(question_context.keys())}")
        logging.info(f"Question context details - Quiz: {question_context.get('quiz', 'N/A')}")
        logging.info(f"Question context details - Question Number: {question_context.get('question_number', 'N/A')}")
        logging.info(f"Question context details - Question: {question_context.get('question', 'N/A')}")
        logging.info(f"Question context details - Options: {question_context.get('options', 'N/A')}")
        logging.info(f"Question context details - User Response: {question_context.get('response', 'N/A')}")
        logging.info(f"Question context details - Correct Answer: {question_context.get('answer', 'N/A')}")

        # Handle explanation or follow-up logic
        if message.lower().strip() == "yes" and user_state in ['awaiting_explanation', 'awaiting_followup']:
            conversation_history = get_conversation_history(user_id, conn, limit=3)
            explanation_prompt = create_explanation_prompt(question_context, user, conversation_history)
            response = generate_text(explanation_prompt)

        elif not is_related_to_question(message, question_context):
            return handle_unrelated_followup(phone_number, message, user, conn)

        else:
            try:
                cursor.execute('''
                    INSERT INTO followup_questions
                    (user_id, quiz_name, quiz_question, followup_question, followup_date)
                    VALUES (?, ?, ?, ?, datetime('now'))
                ''', (user_id, question_context['quiz'], question_context['question'], message))
                conn.commit()
                logging.info(f"Stored follow-up question for user {user_id}")
            except sqlite3.Error as e:
                logging.error(f"Error storing follow-up question: {e}")

            conversation_history = get_conversation_history(user_id, conn, limit=3)

            try:
                prompt = create_followup_prompt(question_context, message, conversation_history, user)
            except Exception as e:
                logging.error(f"Error in create_followup_prompt: {str(e)}")
                prompt = f"The user '{user.get('name', 'Entrepreneur')}' who runs a {user.get('business_type', 'business')} in {user.get('location', 'Nigeria')} has asked: '{message}' about the business question from {question_context.get('quiz', 'unknown quiz')} question {question_context.get('question_number', 'unknown number')}: '{question_context.get('question', 'unknown question')}'. The question had these options: {question_context.get('options', [])}. The user selected: {question_context.get('response', 'unknown')}. The correct answer was: {question_context.get('answer', 'unknown')}. Provide a helpful, practical response (maximum 150 words) with specific Nigerian business advice and examples."

            if prompt == "provide_explanation":
                explanation_prompt = create_explanation_prompt(question_context, user, conversation_history)
                response = generate_text(explanation_prompt)
            elif prompt == "brief_response":
                response = random.choice([
                    "You're welcome! I'm glad I could help.",
                    "I'm happy that was helpful!",
                    "It's my pleasure to assist you.",
                    "Glad I could be of help!",
                    "You're most welcome. Feel free to ask if you need anything else."
                ])
            else:
                response = generate_text(prompt)

        # Fallback in case AI response fails
        if response.startswith("I apologize, but I'm having difficulty generating a response"):
            prompt_next_action(phone_number, conn, include_retry=True)
        else:
            send_message(phone_number, response)
            store_conversation(user_id, message, False, conn)
            store_conversation(user_id, response, True, conn)
            prompt_next_action(phone_number, conn)

        conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', ('post_explanation', phone_number))
        conn.commit()

    except Exception as e:
        error_message = f"Error in handle_ai_chat: {str(e)}"
        logging.error(error_message)
        logging.error(traceback.format_exc())
        send_message(phone_number, "An unexpected error occurred. Please try again or contact support if the issue persists.")
        prompt_next_action(phone_number, conn, include_retry=True)

    logging.info(f"AI CHAT: Finished handling AI chat for user {phone_number}")
    
    
# Helper functions to handle different conversation history formats
def get_message_type(msg):
    if isinstance(msg, dict):
        return msg.get('is_ai', False)
    elif isinstance(msg, tuple):
        return msg[1]  # Assuming the second element of the tuple indicates if it's an AI message
    else:
        logging.error(f"Unexpected message format: {type(msg)}")
        return False

def get_message_content(msg):
    if isinstance(msg, dict):
        return msg.get('message', '')
    elif isinstance(msg, tuple):
        return msg[0]  # Assuming the first element of the tuple is the message content
    else:
        logging.error(f"Unexpected message format: {type(msg)}")
        return ''
      
      
      


    
    
def check_repeated_explanation(user_id, quiz, question_number, conn):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT explanation_count
        FROM explanation_history
        WHERE user_id = ? AND quiz = ? AND question_number = ?
    ''', (user_id, quiz, question_number))
    result = cursor.fetchone()

    if result is None:
        # First explanation for this question
        cursor.execute('''
            INSERT INTO explanation_history (user_id, quiz, question_number, explanation_count)
            VALUES (?, ?, ?, 1)
        ''', (user_id, quiz, question_number))
        score_increment = 5
    else:
        # Repeated explanation
        explanation_count = result[0] + 1
        cursor.execute('''
            UPDATE explanation_history
            SET explanation_count = ?
            WHERE user_id = ? AND quiz = ? AND question_number = ?
        ''', (explanation_count, user_id, quiz, question_number))
        score_increment = 1

    conn.commit()
    return score_increment
  
  
  


    
   
def update_user_state(phone_number, conn, state):
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET state = ? WHERE phone_number = ?', (state, phone_number))
    conn.commit()
   
   

def provide_additional_insight(answer):
    # You can expand this function to provide more insights related to the correct answer
    if answer == "correct_answer_example":
        return "it helps you manage your small business better by ensuring you keep track of your sales and expenses."
    return "it gives you a better understanding of how to improve your business operations."
   
   
   
       
       
       

 
 

def provide_additional_insight(answer):
    # You can expand this function to provide more insights related to the correct answer
    if answer == "correct_answer_example":
        return "it helps you manage your small business better by ensuring you keep track of your sales and expenses."
    return "it gives you a better understanding of how to improve your business operations."
   
   
   
   

   

   
   
def handle_unrelated_followup(phone_number, message, user, conn):
    current_question_index = int(user['current_question']) - 1
    incorrect_questions = get_incorrect_questions(user['id'], conn)
    question_context = incorrect_questions[current_question_index]

    response = f"""
    I understand that you're curious about something else, or your question might not include wording that's clearly related to our current quiz question.
    Original Question: {question_context['question']}
    Your previous answer: {question_context['response']}
    Correct Answer: {question_context['answer']}
    Understanding {question_context['answer']} is important because it gives you a better understanding of how to improve your business operations. For example, {question_context['answer']} can be crucial for effective business strategies and operations.

    If you believe your recent question is related to our discussion, please rephrase it to include more relevant details and ask again.
    """

    send_message(phone_number, response)

    # Do not store this interaction in the conversation history
    prompt_next_action(phone_number, conn)
   
    log_image_event(f"Handled unrelated followup for user {phone_number}")
   

   
   
   
def handle_unrelated_followup(phone_number, message, user, conn):
    current_question_index = int(user['current_question'])
    incorrect_questions = get_incorrect_questions(user['id'], conn)
    question_context = incorrect_questions[current_question_index]
    response = f"""
    Thank you for your message. I'd be happy to help with questions relating to the quiz question we're currently reviewing:
    Question: {question_context['question']}
    Correct Answer: {question_context['answer']}
    """
    send_message(phone_number, response)
    prompt_next_action(phone_number, conn)
    log_image_event(f"Handled unrelated followup for user {phone_number}")
    
    
   
   
def is_related_to_question(user_message, question_context):
    normalized_message = user_message.lower().strip()
   
    # Special handling for "Yes" response
    if normalized_message == "yes":
        return True

    # Define keywords related to small business management in Nigeria
    business_keywords = set([
     
        'business', 'management', 'finance', 'customer', 'profit', 'sales', 'market',
         'product', 'service', 'income', 'expense', 'shop', 'store', 'inventory',
         'pricing', 'budget', 'employee', 'marketing', 'advertising', 'accounting',
         'revenue', 'cost', 'investment', 'entrepreneur', 'startup', 'cash flow',
         'supply chain', 'logistics', 'retail', 'wholesale', 'e-commerce', 'brand',
         'competition', 'strategy', 'growth', 'expansion', 'loan', 'credit', 'tax',
         'insurance', 'risk management', 'customer service', 'supplier', 'inventory management'
                           
                           
                            ])
   
     # Define key phrases and patterns related to follow-up questions
     # Define key phrases and patterns related to follow-up questions
    related_patterns = [
        # Probing questions
        "can you explain", "tell me more", "i don't understand", "can you reexplain", "still unclear",
        "really", "are you sure", "could you clarify", "could you elaborate", "why", "how", "what",
        "could you", "please", "help me", "i need", "give me", "show me", "provide more details",
        "expand on that", "i'm confused about", "i'm not clear on", "more details", "expand",
        "need to know more", "elaborate", "explain", "explain further", "explain more", "give more info",
        "go deeper", "clarify", "more info", "additional details", "what else", "what more",
        "further explanation", "additional information", "want to know more", "detailed explanation",
        "inquiring", "looking for more", "seeking more info", "can you elaborate", "provide further details",
        "expand on this", "break it down", "give me more", "want more insight", "deeper understanding",
        "need clarity", "want to understand better", "tell me in detail", "interested in more",
        "want specifics", "need more context", "further clarification", "explain thoroughly",
        "want deeper dive", "seeking full picture", "expand explanation", "want extensive details",
        "interested in full breakdown", "want comprehensive info", "expand on concept", "Give examples", "example", "more",
        "explain intricacies", "dive into nuances", "thoroughly explain", "looking for exhaustive details",
        "more insights needed", "curious", "dig", "dig deeper",
        # Surprise or Enthusiasm
        "amazing", "incredible", "fantastic", "unbelievable", "wow", "astonishing", "surprising",
        "impressive", "phenomenal", "remarkable", "extraordinary", "awesome", "terrific", "splendid",
        "excellent", "exciting", "thrilling", "exceptional", "mind-blowing", "jaw-dropping", "outstanding",
        "brilliant", "fascinating",
          # Expressions of appreciation
        "thank", "appreciate", "helpful", "great", "thanks", "grateful", "that's useful", "thank you", "welldone", "well done",
       "thank you", "thanks", "appreciate", "grateful", "helpful", "obliged", "pleased",
            "great", "this is helpful", "awesome", "thankful", "many thanks", "much appreciated",
            "you're the best", "cheers", "kudos", "well done", "fantastic", "excellent", "nice",
            "you've been very helpful", "couldn't have done it without you", "thanks a bunch",
            "you're amazing", "appreciated", "you rock", "bless you", "you've been wonderful",
            "superb assistance", "impressive help", "great job", "super helpful", "fantastic support",
            "thank you kindly", "highly grateful", "deep appreciation", "really thankful",
     
        # Disappointment or Frustration
        "disappointing", "frustrating", "unimpressed", "let down", "disheartened", "disillusioned",
        "unsatisfactory", "upsetting", "discouraging", "underwhelming", "irritating", "lacking",
        "bothersome", "displeasing", "maddening", "annoying", "troubling", "discontented", "infuriating",
        # Confusion or Difficulty
        "puzzled", "bewildered", "perplexed", "baffled", "unclear", "complicated", "challenging",
        "confusing", "difficult", "muddled", "vague", "mixed-up", "uncertain", "perplexing",
        "hard to follow", "obscure", "intricate", "tangled",
        # Additional Keywords for Follow-Up or Probing
        "explain", "elaborate", "detail", "clarify", "expand", "inquire", "explore", "outline",
        "illustrate", "amplify", "break down", "unpack", "dissect", "further", "delve", "shed light"
    ]

    # Check if the message is very short (1-2 words)
    if len(normalized_message.split()) <= 2:
        # For very short messages, check if they match any related patterns
        return any(pattern in normalized_message for pattern in related_patterns)

    # For longer messages, proceed with more comprehensive checks
   
    # Check if the message contains any business-related keywords
    message_words = set(normalized_message.split())
    if message_words.intersection(business_keywords):
        return True

    # Check if the user's message matches any of the patterns
    if any(pattern in normalized_message for pattern in related_patterns):
        return True

    # Use fuzzy partial matching to capture variations in phrasing
    for pattern in related_patterns:
        if fuzz.ratio(normalized_message, pattern) > 80:  # Adjust threshold as needed
            return True

    # Extract keywords from the original question and correct answer
    question_keywords = set(question_context['question'].lower().split())
    answer_keywords = set(question_context['answer'].lower().split())

    # Combine keywords from question and answer
    relevant_keywords = question_keywords.union(answer_keywords)

    # Extract keywords from options
    options = json.loads(question_context['options']) if isinstance(question_context['options'], str) else question_context['options']
    for option in options:
        option_keywords = set(option.lower().split())
        relevant_keywords = relevant_keywords.union(option_keywords)

    # Check if the user's message contains any of the relevant keywords
    message_keywords = set(normalized_message.split())

    # Determine if the message contains at least one relevant keyword
    keyword_overlap = len(message_keywords.intersection(relevant_keywords))
    if keyword_overlap >= 1:
        return True

    # If none of the above conditions are met, consider the message unrelated
    return False
 
 

 

   
   
   

   
   


  

# Global variable to store the last time the tip was shown
last_tip_time = 0

def prompt_next_action(phone_number, conn, include_retry=False):
    global last_tip_time
    log_image_event(f"Prompting next action for {phone_number}")
   
    if include_retry:
        buttons = [
            {"type": "reply", "reply": {"id": "retry", "title": "Retry"}},
            {"type": "reply", "reply": {"id": "next_question", "title": "Next Question"}},
            {"type": "reply", "reply": {"id": "end_chat", "title": "End Chat"}}
        ]
        message = "I apologize, there was an issue generating a response. What would you like to do?"
    else:
        buttons = [
            {"type": "reply", "reply": {"id": "ask_followup", "title": "Ask follow-up"}},
            {"type": "reply", "reply": {"id": "next_question", "title": "Next Question"}},
            {"type": "reply", "reply": {"id": "end_chat", "title": "End Chat"}}
        ]
       
        current_time = time.time()
        show_tip = False

        # Show tip if more than an hour has passed since the last tip
        if current_time - last_tip_time > 3600:  # 3600 seconds = 1 hour
            show_tip = random.random() < 0.5  # 50% chance to show tip after an hour has passed
            if show_tip:
                last_tip_time = current_time

        if show_tip:
            message = ("What would you like to do next?\n\n"
                       "Tip: You can also type your follow-up question directly in the chat without using the button!")
        else:
            message = "What would you like to do next?"

    send_interactive_message(phone_number, message, buttons)
   
    conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', ('awaiting_action', phone_number))
    conn.commit()
    log_image_event(f"Updated user {phone_number} state to awaiting_action")
   
 
 
 

       
       
      
      
def get_current_user_data(user_identifier):
    query = """
    SELECT name, age, gender, business_type, location 
    FROM users 
    WHERE phone_number = ? 
    """
    
    cursor.execute(query, (user_identifier,))
    user = cursor.fetchone()  # Fetch the current user data
    
    if user:
        logging.info(f"Fetched user data: {user}")
        return {
            'name': user[0],
            'age': user[1],
            'gender': user[2],
            'business_type': user[3],
            'location': user[4]
        }
    else:
        logging.warning("No user data found")
        return None

      

  
  
  
# def create_explanation_prompt(question_context, user, conversation_history):
#     # Step 1: Ensure user data is retrieved properly
#     user_name = user[2].capitalize()  # Assumed that user[2] is the name
#     user_age = user[10]  # Assumed that user[10] is the age
#     user_gender = user[11]  # Assumed that user[11] is the gender
#     user_business_type = user[12]  # Assumed that user[12] is the business type
#     user_location = user[13].capitalize()  # Assumed that user[13] is the location

#     # Log the user data to ensure proper retrieval (can be used for debugging)
#     logging.info(f"Creating prompt for {user_name}, age: {user_age}, gender: {user_gender}, business: {user_business_type}, location: {user_location}")

#     # Step 2: Process the question and user’s response
#     options = [opt.strip() for opt in question_context['options'].split('\n') if opt.strip()]
#     options_dict = {chr(65 + i): opt for i, opt in enumerate(options)}
#     user_answer = question_context['response'].strip()
#     correct_answer = question_context['answer'].strip().lower()
#     user_option = next((opt for opt, text in options_dict.items() if text.lower() == user_answer.lower()), 'Unknown')
#     correct_option = next((opt for opt, text in options_dict.items() if text.lower() == correct_answer), 'Unknown')
#     is_correct = user_answer.lower() == correct_answer
#     options_text = "\n".join([f"{opt}) {text}" for opt, text in options_dict.items()])

#     # Step 3: Include recent conversation history
#     recent_history = "\n".join([f"{'User' if not msg['is_ai'] else 'AI'}: {msg['message']}" for msg in conversation_history[-3:]])

#     # Step 4: Create the personalized prompt
#     prompt = f"""
#     You are a mentor helping {user_name}, a {user_age}-year-old {user_gender} entrepreneur who owns a {user_business_type} business in {user_location}. They just answered a question in a business quiz. Below are the details:

#     Recent Conversation History:
#     {recent_history}

#     Question: {question_context['question']}
#     Options:
#     {options_text}
#     {user_name}'s Answer: {user_option}) {user_answer}
#     Correct Answer: {correct_option}) {correct_answer}
#     {'The user answered correctly.' if is_correct else 'The user answered incorrectly.'}

#     ### Explanation:

#     Greet {user_name} warmly, acknowledge their efforts, and provide a detailed explanation of the concept. Make sure to:
    
#     - Reference specific aspects of their {user_business_type} business in {user_location}.
#     - Be a bit dramatic and make it more fun and show excitment, action and curiousity
#     - Use very simple English and sometimes pidgin English and contents related to Nigeria culture in the fun part
#     - Responses should not be less than 250 words and specific to the user's question
#     - Let responses be in shorter paragraphs, dont lump them together.
#     - Explain the "how"the {correct_option} is somwhat similar but different from the {user_answer}
#     - Explain the "how" not just the "why" of the {correct_option} and how possible solutions that can be applied by {user_business_type} in real life.
#     - Always use icons and emojis 
#     - User very simple english for people with little or no education
#     - Don't repeat response related to products, anectodes, example  for {user_name}, make it random
#     - If their answer was incorrect, kindly explain why, while relating the explanation back to the {user_business_type} business they run.
#     - Use realistic examples relevant  {user_name} and to their business environment in {user_location}. For instance, describe how the correct answer applies to {user_name}'s daily operations. Dont use third person, make it personalized
   
#     - Include at least two examples specific to  {user_name} that illustrate the concept in the context of  {user_name}'s {user_business_type}.
#     - When referring to options, always use "Option X: [exact text of the option]".
#     - Ensure all business examples use Naira as the currency and reflect common pricing in {user_location}.
#     - Encourage {user_name} to think about how they can apply this concept to their {user_business_type} business.
#     - End on a positive note, motivating {user_name} to apply the concept and ask more questions if needed.
#     """

#     logging.debug(f"Generated personalized prompt for {user_name}: {prompt[:200]}...")  # Log first 200 chars
#     return prompt

  
  


  
  
  
  
  
def create_explanation_prompt(question_context, user, conversation_history):
    # Step 1: Ensure user data is retrieved properly
    user_name = user['name'].split()[0].capitalize() 
    user_age = user['age']
    user_gender = user['gender']
    user_business_type = user['business_type']
    user_location = user['location'].capitalize()
    user_business_size = user['business_size']
    user_financial_status = user['financial_status']
    user_main_challenge = user['main_challenge']
    user_record_keeping = user['record_keeping']
    user_growth_goal = user['growth_goal']
    user_funding_need = user['funding_need']
    user_products = "various products"  # Generic term since data is not yet available

    # Log the user data to ensure proper retrieval (can be used for debugging)
    logging.info(f"Creating prompt for {user_name}, age: {user_age}, gender: {user_gender}, "
                 f"business: {user_business_type}, location: {user_location}, "
                 f"size: {user_business_size}, financial status: {user_financial_status}, "
                 f"main challenge: {user_main_challenge}, record keeping: {user_record_keeping}, "
                 f"growth goal: {user_growth_goal}, funding need: {user_funding_need}, "
                 f"products: {user_products}")

    # Step 2: Process the question and user's response
    options = [opt.strip() for opt in question_context['options'].split('\n') if opt.strip()]
    options_dict = {chr(65 + i): opt for i, opt in enumerate(options)}
    user_answer = question_context['response'].strip()
    correct_answer = question_context['answer'].strip().lower()
    user_option = next((opt for opt, text in options_dict.items() if text.lower() == user_answer.lower()), 'Unknown')
    correct_option = next((opt for opt, text in options_dict.items() if text.lower() == correct_answer), 'Unknown')
    is_correct = user_answer.lower() == correct_answer
    options_text = "\n".join([f"{opt}) {text}" for opt, text in options_dict.items()])

    # # Step 3: Include recent conversation history
    # recent_history = "\n".join([f"{'User' if not msg['is_ai'] else 'AI'}: {msg['message']}" for msg in conversation_history[-3:]])

    # Step 4: Create the personalized prompt
    return f"""
    You are a mentor helping {user_name}, a {user_age}-year-old {user_gender} entrepreneur who owns a small {user_business_type} business in {user_location}. 
    Their business size is {user_business_size}, with a financial status of {user_financial_status}. 
    Their main challenge is {user_main_challenge}, they use {user_record_keeping} for record keeping, their growth goal is {user_growth_goal},
    and their funding need is {user_funding_need}. They sell various products. 
    They just answered a question in a business quiz.
    All should not be more than 50 words so make them precise.
    Give (1) start with the  explanation of why the {user_answer} is incorrect and why {correct_option} is, (2)tailored advice ans (3) Quick Wins
    Below are the details:

    Question: {question_context['question']}
    Options:
    {options_text}
    {user_name}'s Answer: {user_option}) {user_answer}
    Correct Answer: {correct_option}) {correct_answer}
    
    
    {'The user answered correctly.' if is_correct else 'The user answered incorrectly.'}

  

    ### Explanation:

    1. ### Explanation:

    Greet {user_name} warmly, acknowledge their efforts, and provide a detailed explanation of the concept often in pidging English. Make sure to:
    - start with the  explanation of why the {user_answer} is incorrect 
    -  Kindly explain the  {correct_option}) {correct_answer} and why, while relating the explanation back to the {user_business_type} business they run.
    
    - Use realistic examples relevant  {user_name} and to their business environment in {user_location}. For instance, describe how the correct answer applies to {user_name}'s daily operations. Dont use third person, make it personalized

    - Be a bit dramatic and make it more fun and show excitment, action and curiousity
    - Let responses be in shorter paragraphs, dont lump them together.
    - Explain the "how"the {correct_option} is somwhat similar but different from the {user_answer}
    - Explain the "how" not just the "why" of the {correct_option} and how possible solutions that can be applied by {user_business_type} in real life.
    - Always use icons and emojis 
    - User very simple english for people with little or no education
    - Don't repeat response related to products, anectodes, example  for {user_name}, make it random
    - If their answer was incorrect, kindly explain why, while relating the explanation back to the {user_business_type} business they run.
    - Use realistic examples relevant  {user_name} and to their business environment in {user_location}. For instance, describe how the correct answer applies to {user_name}'s daily operations. Dont use third person, make it personalized
   
    - Use very simple English for people with little or no formal business education.
    - If their correct answer {correct_answer} was wrong, kindly explain why, linking it to their {user_business_type}.
    - Encourage {user_name} to think about how to use this idea in their {user_business_type}
    - If their answer was wrong, kindly explain why, linking it to their {user_business_type}.
    - Encourage {user_name} to think about how to use this idea in their {user_business_type}
    - Always include a bit of pidgin English and sometimes references to Nigerian culture in the text to make it relatable.
    - Use very simple English for people with little or no formal business education.
    - Explain how the correct answer {correct_answer} can help {user_name}'s business in real life.
    - Use emojis to make key points stand out.
    - If their answer was wrong, kindly explain why, linking it to their business.
    -  Make it easy to understand and do for a business with 0-1 employees.
    
    
    2. Based on the question, correct answer, and {user_name}'s situation, provide 2-3 specific recommendations: After explaining the {correct_answer}, provide highly tailored advice in one or all of these three areas: 1. Cost Efficiency and Resource Management, 2. Revenue Growth and Customer Acquisition,
    and Potential Partnership using the following:
    
       - Web Search and Data Gathering (Do not include this in your response to the user):
       - Conduct a web search for recent information about {user_business_type} businesses in {user_location}
       - Find data on local market conditions, popular products, pricing trends, and common challenges
       - Identify local events, potential partners, and suppliers relevant to {user_business_type}
       - Research successful strategies used by similar businesses in the area

  
    The Tailored Business Advice (15 words) should be:
       Based on the question, correct answer, their challenge ({user_main_challenge}), and your Web Search and Data, provide 2-3 specific recommendations:
       
       a) Business-Specific Strategies[Very specific action based on the correct answer]:
          - Suggest pricing strategies based on local market research
          - Recommend specific local events or venues for selling
          - Propose product ideas or modifications based on market trends
       
       b) Challenge-Specific Solutions[Very specific action based on the correct answer]:
          - Address their {user_main_challenge} with actionable advice
          - Suggest partnerships or collaborations with local businesses (use real examples from your search)
          - Recommend cost-saving or revenue-generating ideas suitable for their {user_business_size} business

       c) Growth Opportunities[Very specific action based on the correct answer]:
          - Suggest specific steps to achieve their {user_growth_goal}
          - Recommend financial strategies based on their {user_financial_status} and {user_funding_need}
          - Propose record-keeping improvements considering their {user_record_keeping} method


    ### Guidelines:
    - Use recent web search of 2024 results to provide relevant, location-specific advice and 2024 prices and similar products
    - All suggestions should be actionable for a {user_business_size} business
    - Use simple language, short sentences, and occasional pidgin English
    - Incorporate Nigerian cultural references to increase relatability
    - Emphasize the 'why' behind each recommendation
    - Highlight potential risks of not implementing the advice

    Example Response Format:
    "💡 {user_name}, about [concept from question], it's crucial for your {user_business_type} because [reason tied to correct answer and their challenge].

    In {user_location}, you could:
    1. Sell your [typical product for their business type] at [specific local event from your search] next month
    2. Partner with [real local business from your search] to cross-promote
    3. Get your supplies from [specific supplier or market from your search] to save [researched amount] Naira

     3. Detailed Quick Win (15 words):
    Provide a specific, immediately actionable plan that addresses all aspects of the user's situation:

       🎯 Quick Win: Tomorrow, try this specific plan for your {user_business_type} :

       1. Action: [Very specific action based on correct answer and research ]
          - Consider user's [{user_financial_status} and {user_main_challenge}]
          - Product: [Name a specific, relevant product for their business type]
          - Location: [Name a specific market, street, or event in {user_location}]
          - Timing: [Suggest a specific day and time]
          - Price: [Recommend a specific price in Naira, based on local market research, considering 2024 market prices and inflation]

       2. Resources Needed[Very specific action based on the correct answer]:
          - Money: [Specific amount in Naira, considering their {user_financial_status} and and {user_main_challenge}]
          - Time: [Exact time commitment, e.g., "2 hours in the morning"]
          - People: [Specify if they need help, e.g., "Ask your sister to assist for 1 hour"]

      
       This plan directly addresses your {user_main_challenge}and {user_main_challenge} by [specific outcome]. 
       It also moves you closer to your {user_growth_goal} and  by [specific benefit].

       If you need the ₦[specific amount] for this, consider [funding suggestion based on {user_funding_need}].

      You can end with Asking one prompting question such as: Wetin you think? You fit try this one? Make you tell me how e go when you don do am!"

    Remember to use simple English and Pidgin where appropriate, and ensure all suggestions are feasible for a {user_business_size} business in {user_location}.
    """
    logging.debug(f"Generated personalized prompt for {user_name}: {prompt[:200]}...")  # Log first 200 chars
    

  
  
  
def create_explanation_prompt(question_context, user, conversation_history):
    # Step 1: Ensure user data is retrieved properly
    user_name = user['name'].split()[0].capitalize() 
    user_age = user['age']
    user_gender = user['gender']
    user_business_type = user['business_type']
    user_location = user['location'].capitalize()
    user_business_size = user['business_size']
    user_financial_status = user['financial_status']
    user_main_challenge = user['main_challenge']
    user_record_keeping = user['record_keeping']
    user_growth_goal = user['growth_goal']
    user_funding_need = user['funding_need']
    user_products = "various products"  # Generic term since data is not yet available

    # Log the user data to ensure proper retrieval (can be used for debugging)
    logging.info(f"Creating prompt for {user_name}, age: {user_age}, gender: {user_gender}, "
                 f"business: {user_business_type}, location: {user_location}, "
                 f"size: {user_business_size}, financial status: {user_financial_status}, "
                 f"main challenge: {user_main_challenge}, record keeping: {user_record_keeping}, "
                 f"growth goal: {user_growth_goal}, funding need: {user_funding_need}, "
                 f"products: {user_products}")

    # Step 2: Process the question and user's response
    options = [opt.strip() for opt in question_context['options'].split('\n') if opt.strip()]
    options_dict = {chr(65 + i): opt for i, opt in enumerate(options)}
    user_answer = question_context['response'].strip()
    correct_answer = question_context['answer'].strip().lower()
    user_option = next((opt for opt, text in options_dict.items() if text.lower() == user_answer.lower()), 'Unknown')
    correct_option = next((opt for opt, text in options_dict.items() if text.lower() == correct_answer), 'Unknown')
    is_correct = user_answer.lower() == correct_answer
    options_text = "\n".join([f"{opt}) {text}" for opt, text in options_dict.items()])

    # Step 3: Create the personalized prompt with EMPHASIS on 50-word limit
    return f"""
    ⚠️ IMPORTANT: YOUR ENTIRE RESPONSE MUST BE 90 WORDS OR LESS TOTAL. NO EXCEPTIONS. ⚠️

    You are a mentor helping {user_name}, a {user_age}-year-old {user_gender} entrepreneur who owns a small {user_business_type} business in {user_location}. 
    Their business size is {user_business_size}, with a financial status of {user_financial_status}. 
    Their main challenge is {user_main_challenge}, they use {user_record_keeping} for record keeping, their growth goal is {user_growth_goal},
    and their funding need is {user_funding_need}. They sell various products. 
    They just answered a question in a business quiz.

    Question: {question_context['question']}
    Options:
    {options_text}
    {user_name}'s Answer: {user_option}) {user_answer}
    Correct Answer: {correct_option}) {correct_answer}
    
    {'The user answered correctly.' if is_correct else 'The user answered incorrectly.'}

    Within your 50-WORD RESPONSE, include these three elements:

    1. Explanation:
    - Explain why {correct_answer} is correct (and if applicable, why {user_answer} is wrong)
    - Explain HOW {correct_option} is somewhat similar but different from {user_answer}
    - Explain HOW not just WHY the correct answer works and can be applied to {user_business_type} in real life
    - Relate it to their {user_business_type}
    - Use simple English with some pidgin
    - Be dramatic, fun, humorous, and show excitement/curiosity
    - Include a very brief anecdote if possible

    2. Tailored Business Advice:
    - Give ONE specific recommendation based on:
      - Their challenge ({user_main_challenge})
      - Their location ({user_location})
      - Their business type ({user_business_type})
    - Make it immediately actionable
    - Include insights from recent (2024) web search results if possible

    3. Quick Win:
    - ONE very specific action they can take tomorrow
    - Consider their financial status ({user_financial_status})
    - Include specific details (product, location, timing, price in Naira)

    Use multiple icons and emojis throughout, simple language, and be warm and encouraging.
    End with a brief question in pidgin like "Wetin you think?"

    ⚠️ FINAL REMINDER: THE ENTIRE RESPONSE MUST BE 50 WORDS OR LESS TOTAL. THIS IS ABSOLUTELY CRITICAL. ⚠️
    """
    logging.debug(f"Generated personalized prompt for {user_name}: {prompt[:200]}...")  # Log first 200 chars
    
    
  
  
 
  
  
  
def store_conversation(user_id, message, is_ai, conn):
    try:
        conn.execute('''
            INSERT INTO conversation_history (user_id, message, is_ai)
            VALUES (?, ?, ?)
        ''', (user_id, message, is_ai))
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Error storing conversation: {e}")
       
     
     

def get_conversation_history(user_id, conn, limit=3):
    try:
        cursor = conn.execute('''
            SELECT message, is_ai
            FROM conversation_history
            WHERE user_id = ? AND message NOT LIKE 'I understand that you%re curious about something else%'
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, limit))
        return [(row[0], row[1]) for row in cursor.fetchall()][::-1]
    except sqlite3.Error as e:
        logging.error(f"Error retrieving conversation history: {e}")
        return []
     


 
def create_followup_prompt(question_context, user_message, conversation_history, user):
  
    
    user_name = user['name'].split()[0].capitalize()
    user_location = user['location'].capitalize()
    
    # Transform record keeping status into natural context
    record_context = {
        'No records kept': 'who is just starting to track their business numbers',
        'Mental notes': 'who keeps track of their business in their head',
        'Paper records': 'who writes down their business records',
        'Phone notes': 'who uses their phone to record business information',
        'Computer records': 'who uses a computer to manage their business records',
        'Professional software': 'who uses business software for their records'
    }.get(user['record_keeping'], 'who is working on their business records')

    # Transform financial status into natural context
    financial_context = {
        'Struggling': 'while managing with limited funds',
        'Breaking even': 'while working to build their savings',
        'Profitable': 'while looking to grow their profits',
        'Very profitable': 'while expanding their successful business'
    }.get(user['financial_status'], 'while developing their business')

    # Transform business size into natural context
    size_context = {
        'Just me': 'running their business solo',
        '1-5 employees': 'managing a small team',
        '5-10 employees': 'leading a growing team',
        'Over 10 employees': 'managing a larger operation'
    }.get(user['business_size'], 'managing their business')

    
    # Ensure options is a list
    options = json.loads(question_context['options']) if isinstance(question_context['options'], str) else question_context['options']
    options_dict = {chr(65+i): opt for i, opt in enumerate(options)}

    user_answer = question_context['response'].strip()
    correct_answer = question_context['answer'].strip()

    # Determine the option letter for user's answer and correct answer
    user_option = next((opt for opt, text in options_dict.items() if text.lower() == user_answer.lower()), 'Unknown')
    correct_option = next((opt for opt, text in options_dict.items() if text.lower() == correct_answer.lower()), 'Unknown')

    user_full_answer = options_dict.get(user_option, user_answer)
    correct_full_answer = options_dict.get(correct_option, correct_answer)

    options_text = "\n".join([f"{opt}) {text}" for opt, text in options_dict.items()])

    # Define key phrases and patterns
    patterns = {
        'appreciation': [
            "thank you", "thanks", "appreciate", "grateful", "helpful", "obliged", "pleased",
            "great", "this is helpful", "awesome", "thankful", "many thanks", "much appreciated",
            "you're the best", "cheers", "kudos", "well done", "fantastic", "excellent", "nice",
            "you've been very helpful", "couldn't have done it without you", "thanks a bunch",
            "you're amazing", "appreciated", "you rock", "bless you", "you've been wonderful",
            "superb assistance", "impressive help", "great job", "super helpful", "fantastic support",
            "thank you kindly", "highly grateful", "deep appreciation", "really thankful"
        ],
        'disappointment': [
            "disappointed", "frustrating", "confused", "don't get it", "lost", "annoying", "not clear",
            "upset", "difficult", "troublesome", "problematic", "unsatisfactory", "unhappy", "irritated",
            "puzzling", "complicated", "unclear", "hard", "bad", "unfortunate", "let down", "displeased",
            "not satisfied", "this isn't working", "messed up", "bothered", "not right", "struggling",
            "unresolved", "maddening", "inconvenient", "not ideal", "displeasing", "perplexed",
            "tricky", "challenging", "tough", "rough", "a headache", "a hassle", "problematic",
            "it's been a pain", "tiring", "overwhelming", "aggravating", "disappointed", "frustrating", "confused", "don't get it", "lost", "annoying", "not clear", "upset", "difficult"
     
        ],
        'probing': [
            "tell me more", "more details", "expand", "need to know more", "elaborate", "explain",
            "explain further", "explain more", "give more info", "go deeper", "clarify", "more info",
            "additional details", "what else", "what more", "further explanation", "additional information",
            "want to know more", "detailed explanation", "inquiring", "looking for more", "seeking more info",
            "can you elaborate", "provide further details", "expand on this", "break it down", "give me more",
            "want more insight", "deeper understanding", "need clarity", "want to understand better",
            "tell me in detail", "interested in more", "want specifics", "need more context",
            "further clarification", "explain thoroughly", "want deeper dive", "seeking full picture",
            "expand explanation", "want extensive details", "interested in full breakdown",
            "want comprehensive info", "expand on concept", "explain intricacies", "dive into nuances",
            "thoroughly explain", "looking for exhaustive details", "more insights needed"
        ]
    }

    # Normalize the user message
    normalized_message = user_message.lower().strip()

    
    # Determine the response type based on user message
    sentiment = None
    if len(normalized_message) <= 5:  # Adjust this threshold as needed
        sentiment = next((s for s, phrases in patterns.items() if normalized_message in phrases), None)
    else:
        # Use fuzzy matching for longer messages
        sentiment_scores = {
            sentiment: max(fuzz.partial_ratio(normalized_message, p) for p in patterns[sentiment])
            for sentiment in patterns
        }
        sentiment = max(sentiment_scores, key=sentiment_scores.get) if any(score > 80 for score in sentiment_scores.values()) else None

    # Generate response starter based on sentiment
    starters = {
        'appreciation': [
            "I'm glad I could help! ",
            "Happy to assist! ",
            "It's great to know this was helpful! ",
            "You're welcome! ",
            "It's my pleasure to help! ",
            "Thrilled I could assist! ",
            "So happy to help! ",
            "Delighted to be of service! ",
            "Pleased I could support! ",
            "Grateful to be of assistance! ",
            "Happy to be useful! ",
            "Glad to be here for you! ",
            "It's rewarding to help! ",
            "Thank you for your kind words! ",
            "You're very welcome! ",
            "Always happy to help out! ",
            "It's what I'm here for! ",
            "Great to be of help! ",
            "Pleased to contribute! ",
            "It's my duty to assist! ",
            "So glad I could be of help! ",
            "It’s wonderful to support! ",
            "Glad to provide assistance! ",
            "Your feedback is appreciated! ",
            "Thank you for acknowledging! ",
            "Pleased I could help! ",
            "Joyful to assist! ",
            "Proud to support! ",
            "Great to hear it was useful! ",
            "Excited to help! ",
            "Pleased to be of service! ",
            "Thankful to assist! ",
            "Wonderful to aid you! ",
            "Honored to help! ",
            "Glad I could contribute! ",
            "Your words mean a lot! ",
            "Fantastic to assist! ",
            "Happy I could be helpful! ",
            "Thank you for your words! ",
            "Glad to aid you! ",
            "It’s great to assist! "
        ],
        'disappointment': [
            "I understand this can be challenging. Let's go over it again. ",
            "I'm here to help you through this. Let's take another look. ",
            "I see this is still confusing. Let's break it down together. ",
            "Let's approach this from a different angle. ",
            "I appreciate your patience. Let's clarify this step by step. ",
            "Sorry for the confusion. Let's work it out together. ",
            "I can see this is frustrating. Let's solve it. ",
            "Apologies for the trouble. Let's fix it. ",
            "I know this isn't easy. Let's sort it out. ",
            "I understand your frustration. Let's figure it out. ",
            "Let's take a moment and review it again. ",
            "I realize this is difficult. We'll get through it. ",
            "Sorry for the inconvenience. Let's get it right. ",
            "Let's make sense of this together. ",
            "I'm here to help make this clear. ",
            "We can do this step by step. ",
            "Let’s dive into it again for better clarity. ",
            "I’m with you, let’s resolve this. ",
            "Don’t worry, we’ll get it sorted. ",
            "Let's find a better way to understand this. ",
            "I know this can be tricky. Let's go through it again. ",
            "I see this is tough. Let’s go over it again. ",
            "I'm here to clear up any confusion. ",
            "We can tackle this together. ",
            "Let’s approach this differently. ",
            "I understand this is a lot. Let’s break it down. ",
            "Sorry this is complicated. Let’s simplify it. ",
            "Let’s get to the bottom of this. ",
            "I know this is tricky. Let's get through it. ",
            "I’m here to help you understand. ",
            "Let's revisit this for clarity. ",
            "Let’s work on this together. ",
            "I see this is challenging. Let’s figure it out. ",
            "I’m here to assist with this. ",
            "I understand this is frustrating. Let’s fix it. ",
            "We can overcome this challenge together. ",
            "I realize this is difficult. Let’s solve it. ",
            "I know this is confusing. Let’s clear it up. ",
            "Let’s clarify this step by step. ",
            "I understand this is hard. Let’s break it down. "
        ],
        'probing': [
            "Oh, good question! Let’s dive deeper. ",
            "Ah, I see you’re interested. Let’s explore that. ",
            "Yes, let’s get into more detail. ",
            "Oh, I’d be happy to explain further. ",
            "Ah, you want more info? Let’s go in-depth. ",
            "Yes, let’s break it down some more. ",
            "Oh, I can provide more details on that. ",
            "Ah, let’s expand on this topic. ",
            "Yes, I’m glad to give more information. ",
            "Oh, let’s clarify this in more depth. ",
            "Ah, you’re looking for specifics. Let’s discuss further. ",
            "Yes, I can elaborate more. ",
            "Oh, let’s go over this thoroughly. ",
            "Ah, I’m happy to provide a deeper explanation. ",
            "Yes, let’s dive into the details. ",
            "Oh, I can give you additional context. ",
            "Ah, let’s explore this topic more fully. ",
            "Yes, I’m here to offer more insight. ",
            "Oh, let’s look at this in detail. ",
            "Ah, I’m ready to explain further. ",
            "Yes, let’s provide more clarity on this. "
            "Great question! Let's explore that further. ",
            "I'm glad you're interested in learning more. ",
            "That's an insightful point. Let's dive deeper. ",
            "Excellent! I'm happy to provide more details. ",
            "Your curiosity is commendable. Let's expand on that. ",
            "Let's take a closer look. ",
            "Happy to explain further! ",
            "Let's break it down more. ",
            "Let's delve into more details. ",
            "Certainly! Let's go over it in more depth. ",
            "I'll be glad to expand on that. ",
            "Let me provide more insights. ",
            "I'm here to give you more information. ",
            "Let's uncover more about this. ",
            "I'm ready to give you additional details. ",
            "Let's look at this in more detail. ",
            "Let me elaborate on that. ",
            "Happy to provide more clarity. ",
            "Let's go through this thoroughly. ",
            "Ready to give you a deeper understanding. "
        ]
    }
    response_start = random.choice(starters[sentiment]) if sentiment else ""

    # Prioritize the most recent conversation
    recent_conversation = conversation_history[-2:]  # Get last 2 exchanges
    conversation_context = "\n".join([f"{'AI' if is_ai else 'User'}: {msg}" for msg, is_ai in recent_conversation])

    # For appreciation with exact match and short message, return a flag for brief response
    if sentiment == 'appreciation' and len(normalized_message) <= 10:
        return "brief_response"

    # Use more of the conversation history
    full_conversation = "\n".join([f"{'AI' if is_ai else 'User'}: {msg}" for msg, is_ai in conversation_history])
    
      # For other cases, construct the full prompt
    return f"""
      
    You are a helpful assistant for small business owners in Nigeria with limited education. You're continuing a conversation about a quiz question and ending it with a practical advice. Here's the context:

    Recent Conversation:
    {conversation_context}

    Original Question: {question_context['question']}
    Options:
    {options_text}
    User's answer: {user_option}) {user_full_answer}
    Correct Answer: {correct_option}) {correct_full_answer}

    The user's latest message is: "{user_message}"

   1. Your response should:
    - Be around 10. 0 words and specific to the user's question and recent conversation:
    - Don't repeat anecdotes or examples for each user
    - When using currency to explain, use Naira only
    - Don't repeat response for each user, make it random
    - Apologize if User remains confused or asking similar questions without getting what they want
    - Start with: "{response_start}"
    - Directly address the user's follow-up question
    - If the question is vague, provide more details about the correct answer and its importance
    - Always refer to options using their exact wording and corresponding letter (A, B, or C)
    - Use simple language suitable for small business owners with limited education in Nigeria
    - Focus on practical knowledge for businesses with 0-1 employees in local Nigerian markets
    - Use a new, relevant anecdote or example related to small businesses in Nigeria
    - Include a brief, interesting fact related to the topic if appropriate
    - Use a familiar scenario (e.g., "Imagine a customer walks into your shop...")
    - Maintain relevance to the original question and correct answer
    _ Tell users in an interesting way that they can also ask follow-up question directly in the chat without using the follow-up button
    - Encourage further questions if needed
    
     2. 🎯 Practical Advice:
    Share 2-3 specific suggestions that is related to Recent Conversation::
    - Help them grow their business in {user['location'].capitalize()} and {user['main_challenge'].lower()} and  {question_context['question']}
    - Work with their current resources and situation in {user['location'].capitalize()}  and  {question_context['question']}
    - Connect to local opportunities and market conditions related to  {question_context['question']}
    - Include actual prices and specific locations from 2024
    - Suggest potential local business partners or events related to {user['growth_goal'].lower()} related to  {question_context['question']}.
    

      Style Guidelines:
    - Write like you're having a friendly conversation 
    - Use natural language instead of business jargon
    - Include relevant Nigerian cultural references
    - Mix in pidgin English naturally
    - Keep suggestions practical and affordable
    - Show excitement and encouragement
    - Always use emojis and icons to highlight key points
    - Let all recommendations relate to  {question_context['question']}

    End with a friendly question in pidgin to encourage their feedback
    
    """
  
  
  
  

#     # For other cases, construct the full prompt
#     return f"""
#     You are a helpful assistant named Ade for small business owners in Nigeria with limited education. You're continuing a conversation about a quiz question. Here's the context:

#     Full Conversation History:
#     {full_conversation}

#     Original Question: {question_context['question']}
#     Options:
#     {options_text}
#     {user_name}'s answer: {user_option}) {user_full_answer}
#     Correct Answer: {correct_option}) {correct_full_answer}

#     {user_name}'s latest message is: "{user_message}"

#     User Profile:
#     Name: {user_name}
#     Age: {user_age}
#     Gender: {user_gender}
#     Business: {user_business_type} in {user_location}
#     Business Size: {user_business_size}
#     Financial Status: {user_financial_status}
#     Main Challenge: {user_main_challenge}
#     Record Keeping: {user_record_keeping}
#     Growth Goal: {user_growth_goal}
#     Funding Need: {user_funding_need}

#     Your response should:
#     - Be around 120 words and highly personalized to {user_name}'s situation
#     - Start with: "{response_start}"
#     - Address {user_name} by name and reference their specific business situation frequently
#     - Directly address {user_name}'s follow-up question or latest message
#     - If the question is vague, provide more details about the correct answer and its importance to {user_name}'s {user_business_type}
#     - Always refer to options using their exact wording and corresponding letter (A, B, or C)
#     - Use simple language suitable for a {user_age}-year-old {user_gender} business owner with limited education in {user_location}
#     - Focus on practical knowledge for {user_name}'s {user_business_size} {user_business_type} in {user_location}
#     - Use a new, relevant anecdote or example specifically related to {user_name}'s {user_business_type} in {user_location}
#     - Include a brief, interesting fact related to the topic if appropriate for {user_name}'s situation
#     - Use a familiar scenario tailored to {user_name}'s business: "Imagine a customer walks into your {user_business_type} in {user_location}..."
#     - Maintain relevance to the original question and correct answer while connecting it to {user_name}'s main challenge: {user_main_challenge}
#     - Tell {user_name} they can ask follow-up questions directly in the chat without using the follow-up button
#     - Encourage further questions if needed, especially about their {user_growth_goal} or {user_funding_need}
#     - When using currency in examples, use Naira only
#     - Don't repeat anecdotes or examples you've used before with {user_name}
#     - If {user_name} remains confused or is asking similar questions repeatedly, apologize and try a different approach
#     - Reference the conversation history to maintain context and avoid repetition

#     Make your response engaging, informative, and highly tailored to {user_name}'s specific profile and the ongoing conversation, focusing on their recent messages and how the topic relates to their {user_business_type} in {user_location}.
    
    
    
#     End woth. Detailed Quick Win (30-50 words):
#     Provide a specific, immediately actionable plan that addresses all aspects of the user's situation:

#        🎯 Quick Win: Tomorrow, try this specific plan for your {user_business_type} :

#        1. Action: [Very specific action based on correct answer and research ]
#           - Consider user's [{user_financial_status} and {user_main_challenge}]
#           - Product: [Name a specific, relevant product for their business type]
#           - Location: [Name a specific market, street, or event in {user_location}]
#           - Timing: [Suggest a specific day and time]
#           - Price: [Recommend a specific price in Naira, based on local market research, considering 2024 market prices and inflation]

#        2. Resources Needed[Very specific action based on the correct answer]:
#           - Money: [Specific amount in Naira, considering their {user_financial_status} and and {user_main_challenge}]
#           - Time: [Exact time commitment, e.g., "2 hours in the morning"]
#           - People: [Specify if they need help, e.g., "Ask your sister to assist for 1 hour"]

      
#        This plan directly addresses your {user_main_challenge}and {user_main_challenge} by [specific outcome]. 
#        It also moves you closer to your {user_growth_goal} and  by [specific benefit].

#        If you need the ₦[specific amount] for this, consider [funding suggestion based on {user_funding_need}].

#     """
         
 

 

 
 

# Example usage:
# question_context = {...}  # Dictionary containing question details
# user_message = "Can you explain more about option B?"
# conversation_history = [("Hello, how can I help you today?", True), ("I have a question about the quiz", False), ...]
# prompt = create_followup_prompt(question_context, user_message, conversation_history)





# Example usage:
# question_context = {...}  # Dictionary containing question details
# user_message = "Can you explain more about option B?"
# conversation_history = [("Hello, how can I help you today?", True), ("I have a question about the quiz", False), ...]
# prompt = create_followup_prompt(question_context, user_message, conversation_history)


 
 
def handle_followup_request(phone_number, conn):
    log_image_event(f"Handling follow-up request for {phone_number}")
    send_message(phone_number, "Please type your follow-up question and press send.")
    conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', ('awaiting_followup', phone_number))
    conn.commit()
    log_image_event(f"Updated user {phone_number} state to awaiting_followup")
   
   
   
       
          
       
def handle_post_explanation_action(phone_number, action, user, conn):
    log_image_event(f"Handling post-explanation action: {action} for user {phone_number}")
   
    action_lower = action.lower().strip()

    try:
        if action_lower == 'next_question':
            log_image_event(f"User {phone_number} requested next question after explanation")
            send_next_question(phone_number, user, conn)
        elif action_lower == 'end_chat':
            log_image_event(f"User {phone_number} ended chat after explanation")
            send_message(phone_number, "Thank you for using our service. Is there anything else we can help you with?")
            present_options(phone_number, user, conn)
        elif action_lower in ['quiz', 'start quiz']:
            log_image_event(f"User {phone_number} requested to start a quiz after explanation")
            start_quiz(phone_number, user, conn)
        elif action_lower in ['records', 'record keeping']:
            log_image_event(f"User {phone_number} requested record keeping after explanation")
            show_record_options(phone_number, user, conn)
        elif action_lower == 'ai_chat':
            log_image_event(f"User {phone_number} requested to chat with AI after explanation")
            start_ai_chat(phone_number, user, conn)
        else:
            log_image_event(f"Unexpected post-explanation action: {action}")
            send_message(phone_number, "I'm sorry, I didn't understand that. Let me show you the main options again.")
            present_options(phone_number, user, conn)
    except Exception as e:
        log_image_event(f"Error in handle_post_explanation_action: {str(e)}")
        log_image_event(traceback.format_exc())
        send_message(phone_number, "An error occurred. Let me show you the main options again.")
        present_options(phone_number, user, conn)
    finally:
        # Ensure the connection is committed
        conn.commit()
       
       
       
# def get_incorrect_questions(user_id, conn):
#     try:
#         cursor = conn.cursor()
#         query = """
#         SELECT r.id AS response_id, r.quiz, r.question_number, r.response, r.correct,
#                q.id AS question_id, q.question, q.options, q.answer
#         FROM responses r
#         JOIN questions q ON q.quiz = r.quiz AND q.id = r.question_number
#         WHERE r.user_id = ? AND r.correct = 0
#         ORDER BY r.quiz, r.question_number
#         """
#         cursor.execute(query, (user_id,))
#         results = cursor.fetchall()
       
#         # Convert results to a list of dictionaries
#         column_names = [description[0] for description in cursor.description]
#         incorrect_questions = [dict(zip(column_names, row)) for row in results]
       
#         logging.info(f"Number of incorrect questions retrieved: {len(incorrect_questions)}")
       
#         for i, question in enumerate(incorrect_questions):
#             logging.info(f"Question {i + 1}: {question}")
       
#         return incorrect_questions
#     except sqlite3.Error as e:
#         logging.error(f"Database error in get_incorrect_questions: {e}")
#         return []
     
     
     
     
# def get_incorrect_questions(user_id, conn):
#     try:
#         cursor = conn.cursor()
#         query = """
#         SELECT r.id AS response_id, r.quiz, r.question_number, r.response, r.correct,
#                q.id AS question_id, q.question, q.options, q.answer
#         FROM responses r
#         JOIN questions q ON q.quiz = r.quiz AND q.id = r.question_number
#         WHERE r.user_id = ? AND r.correct = 0 AND CAST(SUBSTR(r.quiz, 5) AS INTEGER) <= 10
#         ORDER BY r.quiz, r.question_number
#         """
#         cursor.execute(query, (user_id,))
#         results = cursor.fetchall()
       
#         column_names = [description[0] for description in cursor.description]
#         incorrect_questions = [dict(zip(column_names, row)) for row in results]
       
#         logging.info(f"Number of incorrect questions retrieved: {len(incorrect_questions)}")
       
#         for i, question in enumerate(incorrect_questions):
#             logging.info(f"Question {i + 1}: {question}")
       
#         return incorrect_questions
#     except sqlite3.Error as e:
#         logging.error(f"Database error in get_incorrect_questions: {e}")
#         return []
     
     
     
    
    
    
# def get_incorrect_questions(user_id, conn, specific_quiz=None):
#     """
#     Get incorrect questions, optionally filtered by specific quiz.
#     Added specific_quiz parameter to filter questions
#     """
#     try:
#         cursor = conn.cursor()
#         query = """
#         SELECT r.id AS response_id, r.quiz, r.question_number, r.response, r.correct,
#                q.id AS question_id, q.question, q.options, q.answer
#         FROM responses r
#         JOIN questions q ON q.quiz = r.quiz AND q.id = r.question_number
#         WHERE r.user_id = ? AND r.correct = 0 AND CAST(SUBSTR(r.quiz, 5) AS INTEGER) <= 10
#         """
#         params = [user_id]
        
#         if specific_quiz:
#             query += " AND r.quiz = ?"
#             params.append(specific_quiz)
            
#         query += " ORDER BY r.quiz, r.question_number"
        
#         cursor.execute(query, tuple(params))
#         results = cursor.fetchall()
        
#         column_names = [description[0] for description in cursor.description]
#         incorrect_questions = [dict(zip(column_names, row)) for row in results]
        
#         logging.info(f"Number of incorrect questions retrieved: {len(incorrect_questions)}")
#         return incorrect_questions
        
#     except sqlite3.Error as e:
#         logging.error(f"Database error in get_incorrect_questions: {e}")
#         return []

      
      
      
  
# def get_incorrect_questions(user_id, conn, specific_quiz=None):
#     """
#     Get incorrect questions, optionally filtered by a specific quiz.
#     """
#     try:
#         cursor = conn.cursor()
#         query = """
#         SELECT r.id AS response_id, r.quiz, r.question_number, r.response, r.correct,
#                q.id AS question_id, q.question, q.options, q.answer
#         FROM responses r
#         JOIN questions q ON q.quiz = r.quiz AND q.question_number = r.question_number
#         WHERE r.user_id = ? AND r.correct = 0 AND CAST(SUBSTR(r.quiz, 5) AS INTEGER) <= 10
#         """
#         params = [user_id]
        
#         if specific_quiz:
#             query += " AND r.quiz = ?"
#             params.append(specific_quiz)
            
#         query += " ORDER BY r.quiz, r.question_number"
        
#         cursor.execute(query, tuple(params))
#         results = cursor.fetchall()
        
#         column_names = [description[0] for description in cursor.description]
#         incorrect_questions = [dict(zip(column_names, row)) for row in results]
        
#         logging.info(f"Number of incorrect questions retrieved: {len(incorrect_questions)}")
#         return incorrect_questions
        
#     except sqlite3.Error as e:
#         logging.error(f"Database error in get_incorrect_questions: {e}")
#         return []


      
      


# def get_incorrect_questions(user_id, conn, quiz_name):
#     """
#     Returns a list of (id, question, answer, question_number, quiz)
#     for every question the user got wrong in quiz_name.
#     On DB errors returns None (so caller can distinguish “error” vs “no wrong answers”).
#     """
#     # Sanity‑check that conn is a real sqlite3.Connection
#     if not hasattr(conn, 'cursor'):
#         logging.error(f"get_incorrect_questions: expected sqlite3.Connection, got {type(conn)}")
#         return None

#     try:
#         cursor = conn.cursor()
#         # 1) Grab the numbers of the wrong questions
#         query1 = """
#             SELECT question_number
#             FROM responses
#             WHERE user_id = ? AND quiz = ? AND correct = 0
#             ORDER BY question_number ASC
#         """
#         cursor.execute(query1, (user_id, quiz_name))
#         q_nums = [row[0] for row in cursor.fetchall()]

#         # 2) If none wrong, return empty list
#         if not q_nums:
#             return []

#         # 3) Otherwise fetch the full question records
#         placeholders = ','.join('?' for _ in q_nums)
#         query2 = f"""
#             SELECT id, question, answer, question_number, quiz
#             FROM questions
#             WHERE quiz = ? AND question_number IN ({placeholders})
#             ORDER BY question_number ASC
#         """
#         params = [quiz_name] + q_nums
#         cursor.execute(query2, params)
#         results = cursor.fetchall()

#         logging.info(f"get_incorrect_questions: fetched {len(results)} wrong questions for user={user_id}, quiz={quiz_name}")
#         return results

#     except Exception as e:
#         logging.error(f"get_incorrect_questions error: {e}")
#         logging.error(traceback.format_exc())
#         return None

      
      
      


def get_incorrect_questions(user_id, conn, quiz_name):
    """
    Returns a list of (id, question, answer, question_number, quiz)
    for every question the user got wrong in quiz_name.
    On DB errors returns None (so caller can distinguish “error” vs “no wrong answers”).
    """
    # Sanity‑check that conn is a real sqlite3.Connection
    if not hasattr(conn, 'cursor'):
        logging.error(f"get_incorrect_questions: expected sqlite3.Connection, got {type(conn)}")
        return None

    try:
        cursor = conn.cursor()
        # 1) Grab the numbers of the wrong questions
        query1 = """
            SELECT question_number
            FROM responses
            WHERE user_id = ? AND quiz = ? AND correct = 0
            ORDER BY question_number ASC
        """
        cursor.execute(query1, (user_id, quiz_name))
        q_nums = [row[0] for row in cursor.fetchall()]

        # 2) If none wrong, return empty list
        if not q_nums:
            return []

        # 3) Otherwise fetch the full question records
        placeholders = ','.join('?' for _ in q_nums)
        query2 = f"""
            SELECT id, question, answer, question_number, quiz
            FROM questions
            WHERE quiz = ? AND question_number IN ({placeholders})
            ORDER BY question_number ASC
        """
        params = [quiz_name] + q_nums
        cursor.execute(query2, params)
        results = cursor.fetchall()

        logging.info(f"get_incorrect_questions: fetched {len(results)} wrong questions for user={user_id}, quiz={quiz_name}")
        return results

    except Exception as e:
        logging.error(f"get_incorrect_questions error: {e}")
        logging.error(traceback.format_exc())
        return None

      
      
      

      
# def send_next_question(phone_number, user, conn):
#     try:
#         # Extract the quiz name from the user's selection (e.g., "quiz5")
#         cursor = conn.cursor()
#         cursor.execute('SELECT current_quiz FROM users WHERE phone_number = ?', (phone_number,))
#         result = cursor.fetchone()
       
#         if result is None:
#             raise ValueError(f"No user found with phone number {phone_number}")
       
#         # Use the stored current_quiz or default to the selected quiz
#         quiz_name = result[0] if result[0] else 'quiz5'
       
#         logging.info(f"Current quiz for user {phone_number}: {quiz_name}")
       
#         # Fetch incorrect questions specifically for this quiz
#         incorrect_questions = get_incorrect_questions(user['id'], conn, specific_quiz=quiz_name)
       
#         logging.info(f"Fetched {len(incorrect_questions)} incorrect questions for quiz {quiz_name}")
       
#         # Get the current question index
#         cursor.execute('SELECT current_question FROM users WHERE phone_number = ?', (phone_number,))
#         current_question_result = cursor.fetchone()
#         current_question = int(current_question_result[0]) if current_question_result else 0
       
#         logging.info(f"Current question index: {current_question}")
       
#         if current_question >= len(incorrect_questions):
#             send_message(phone_number, "Great job! You've reviewed all incorrect questions for this quiz. Would you like to start a new quiz?")
#             present_options(phone_number, user, conn)
#             return
       
#         # Get the current question data
#         question_data = incorrect_questions[current_question]
       
#         logging.info(f"Question data for current question: {question_data}")
       
#         # Check if required fields are present
#         required_fields = ['question', 'options', 'answer', 'response', 'quiz', 'question_number']
#         for field in required_fields:
#             if field not in question_data or question_data[field] is None:
#                 logging.error(f"Missing required field: {field}")
#                 logging.error(f"Full question data: {question_data}")
#                 raise ValueError(f"Missing required field: {field}")
       
#         # Extract question details
#         quiz_name = question_data['quiz']
#         question_number = question_data['question_number']
#         question_text = question_data['question']
#         options_str = question_data['options']
#         correct_answer = question_data['answer']
#         user_answer = question_data['response']
       
#         # Parse options
#         try:
#             options = json.loads(options_str)
#             if not isinstance(options, list) or len(options) != 3:
#                 raise ValueError("Options must be a list of 3 items")
#         except json.JSONDecodeError as e:
#             logging.error(f"Failed to parse options JSON: {options_str}")
#             raise ValueError(f"Invalid options format: {str(e)}")
       
#         # Prepare message
#         message = f"Quiz: {quiz_name}\nQuestion {question_number}:\n\n{question_text}\n\nOptions:\n"
#         message += "\n".join(options)
#         message += f"\n\nYour answer: {user_answer}\nCorrect answer: {correct_answer}"
       
#         send_message(phone_number, message)
       
#         # Add interactive buttons for explanation
#         buttons = [
#             {"type": "reply", "reply": {"id": "explain_yes", "title": "Yes"}},
#             {"type": "reply", "reply": {"id": "explain_no", "title": "No"}}
#         ]
#         send_interactive_message(phone_number, "Would you like an explanation for this question?", buttons)
       
#         # Update user state and increment current question
#         conn.execute('''
#             UPDATE users 
#             SET state = ?, 
#                 current_question = ?, 
#                 current_quiz = ? 
#             WHERE phone_number = ?
#         ''', ('awaiting_explanation', current_question + 1, quiz_name, phone_number))
#         conn.commit()
#         logging.info(f"Updated user {phone_number} state to awaiting_explanation and incremented current_question to {current_question + 1}")
       
#     except ValueError as ve:
#         logging.error(f"ValueError in send_next_question: {str(ve)}")
#         send_message(phone_number, f"An error occurred: {str(ve)}. Please contact support.")
#     except Exception as e:
#         logging.error(f"Unexpected error in send_next_question: {str(e)}")
#         logging.error(traceback.format_exc())
#         send_message(phone_number, "An unexpected error occurred while fetching the next question. Please try again or contact support.")
        
        
        
        
        
def send_next_question(phone_number, user, conn):
    try:
        # Fetch the current question
        cursor = conn.cursor()
        cursor.execute('SELECT current_question, quiz_in_review FROM users WHERE phone_number = ?', (phone_number,))
        result = cursor.fetchone()
       
        if result is None:
            raise ValueError(f"No user found with phone number {phone_number}")
       
        current_question = int(result[0])
        quiz_name = result[1]
        
        if not quiz_name:
            raise ValueError("No quiz in review found for this user")
       
        logging.info(f"Current question for user {phone_number}: {current_question}")
        logging.info(f"Quiz in review: {quiz_name}")
       
        # Fetch incorrect questions with the quiz_name parameter
        incorrect_questions = get_incorrect_questions(user['id'], conn, quiz_name)
       
        logging.info(f"Fetched {len(incorrect_questions)} incorrect questions for user {phone_number}")
       
        if current_question >= len(incorrect_questions):
            send_message(phone_number, "Great job! You've reviewed all your incorrect questions. Would you like to start a new quiz?")
            present_options(phone_number, user, conn)
            return
       
        question_data = incorrect_questions[current_question]
       
        logging.info(f"Question data for current question: {question_data}")
       
        # Ensure question_data is a dictionary
        if not isinstance(question_data, dict):
            question_data = dict(zip(['id', 'question', 'answer', 'question_number', 'quiz'], question_data))
       
        logging.info(f"Question data after conversion: {question_data}")
       
        # Get user's response for this question
        response_query = """
        SELECT response 
        FROM responses 
        WHERE user_id = ? AND quiz = ? AND question_number = ? AND correct = 0
        """
        cursor.execute(response_query, (user['id'], quiz_name, question_data['question_number']))
        response_result = cursor.fetchone()
        
        if not response_result:
            raise ValueError(f"No incorrect response found for question {question_data['question_number']}")
            
        user_answer = response_result[0]
        question_data['response'] = user_answer
        
        # Fetch options for this question
        options_query = """
        SELECT options 
        FROM questions 
        WHERE quiz = ? AND question_number = ?
        """
        cursor.execute(options_query, (quiz_name, question_data['question_number']))
        options_result = cursor.fetchone()
        
        if not options_result:
            raise ValueError(f"No options found for question {question_data['question_number']}")
            
        options_str = options_result[0]
        question_data['options'] = options_str
       
        # Check if required fields are present
        required_fields = ['question', 'options', 'answer', 'response', 'quiz', 'question_number']
        for field in required_fields:
            if field not in question_data or question_data[field] is None:
                logging.error(f"Missing required field: {field}")
                logging.error(f"Full question data: {question_data}")
                raise ValueError(f"Missing required field: {field}")
       
        quiz_name = question_data['quiz']
        question_number = question_data['question_number']
        question_text = question_data['question']
        options_str = question_data['options']
        correct_answer = question_data['answer']
        user_answer = question_data['response']
       
        # Parse options
        try:
            options = json.loads(options_str)
            if not isinstance(options, list) or len(options) != 3:
                raise ValueError("Options must be a list of 3 items")
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse options JSON: {options_str}")
            raise ValueError(f"Invalid options format: {str(e)}")
       
        # Do not add additional A, B, C to options
        formatted_options = options
       
        message = f"Quiz: {quiz_name}\nQuestion {question_number}:\n\n{question_text}\n\nOptions:\n"
        message += "\n".join(formatted_options)
        message += f"\n\nYour answer: {user_answer}\nCorrect answer: {correct_answer}"
       
        send_message(phone_number, message)
       
        # Add interactive buttons for explanation
        buttons = [
            {"type": "reply", "reply": {"id": "explain_yes", "title": "Yes"}},
            {"type": "reply", "reply": {"id": "explain_no", "title": "No"}}
        ]
        send_interactive_message(phone_number, "Would you like an explanation for this question?", buttons)
       
        # Update user state and increment current question
        conn.execute('UPDATE users SET state = ?, current_question = ? WHERE phone_number = ?',
                     ('awaiting_explanation', current_question + 1, phone_number))
        conn.commit()
        logging.info(f"Updated user {phone_number} state to awaiting_explanation and incremented current_question to {current_question + 1}")
       
    except ValueError as ve:
        logging.error(f"ValueError in send_next_question: {str(ve)}")
        send_message(phone_number, f"An error occurred: {str(ve)}. Please contact support.")
    except Exception as e:
        logging.error(f"Unexpected error in send_next_question: {str(e)}")
        logging.error(traceback.format_exc())
        send_message(phone_number, "An unexpected error occurred while fetching the next question. Please try again or contact support.")

        

def init_db(db_file='user_data_bootcamp.db'):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT UNIQUE,
            name TEXT,
            age INTEGER,
            gender TEXT,
            state TEXT,
            business_type TEXT,
            location TEXT,
            business_size TEXT,
            financial_status TEXT,
            main_challenge TEXT,
            record_keeping TEXT,
            growth_goal TEXT,
            funding_need TEXT,
            selected_products TEXT,
            review_data TEXT,
            quiz_in_review TEXT
        )
    ''')

    # User products
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_name TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Explanation history
    c.execute('''
        CREATE TABLE IF NOT EXISTS explanation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            quiz TEXT,
            question_number INTEGER,
            explanation_count INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # User scores
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            phone_number TEXT UNIQUE,
            score INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Post-10 quizzes
    c.execute('''
        CREATE TABLE IF NOT EXISTS post10_quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            quiz_number INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Post-10 quiz responses
    c.execute('''
        CREATE TABLE IF NOT EXISTS post10_quiz_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER,
            question_number INTEGER,
            response TEXT,
            FOREIGN KEY (quiz_id) REFERENCES post10_quizzes(id)
        )
    ''')

    # Responses
    c.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            quiz TEXT,
            question_number INTEGER,
            response TEXT,
            correct BOOLEAN,
            timestamp DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Questions
    c.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz TEXT,
            question TEXT,
            options TEXT,
            answer TEXT,
            question_number INTEGER
        )
    ''')

    # Follow-up questions
    c.execute('''
        CREATE TABLE IF NOT EXISTS followup_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            question_id INTEGER,
            quiz_name TEXT,
            quiz_question TEXT,
            followup_question TEXT,
            followup_date DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (question_id) REFERENCES questions(id)
        )
    ''')

    # Conversation history
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            is_ai BOOLEAN,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # ✅ NEW: Quiz status (on/off switch)
    c.execute('''
        CREATE TABLE IF NOT EXISTS quiz_status (
            quiz TEXT PRIMARY KEY,
            enabled INTEGER NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    logging.info("Database initialized successfully")

# Run this function to initialize or update the database schema
init_db()



# Replace your quiz_visibility line with this:
from collections import defaultdict
# Remove any existing quiz_visibility declarations and use only this one:
quiz_visibility = {}  # Use regular dict, not defaultdict

def load_quiz_visibility_from_db():
    """Load quiz visibility settings from database into memory"""
    global quiz_visibility
    conn = sqlite3.connect('user_data_bootcamp.db')  # Fixed: use sqlite3.connect instead of get_db_connection()
    cursor = conn.cursor()
    try:
        # Fixed: Read from quiz_status table, not quizzes table
        cursor.execute("SELECT quiz, enabled FROM quiz_status")
        quiz_visibility = {}  # Clear existing
        for row in cursor.fetchall():
            # Fixed: row is tuple, not dict - use row[0] and row[1]
            quiz_visibility[row[0]] = bool(row[1])
        print(f"Loaded quiz visibility from DB: {quiz_visibility}")
    except Exception as e:
        print(f"Error loading quiz visibility: {e}")
    finally:
        conn.close()
        
        
# Fixed GET endpoint - reads from quiz_status table
@app.route('/api/quizzes')
def get_quizzes():
    # Fixed: Load fresh data from database every time
    load_quiz_visibility_from_db()
    
    conn = sqlite3.connect('user_data_bootcamp.db')
    cursor = conn.cursor()
    
    # Get all unique quizzes from questions table
    cursor.execute("SELECT DISTINCT quiz FROM questions ORDER BY quiz")
    all_quizzes = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    result = []
    for quiz in all_quizzes:
        # Fixed: Use quiz_visibility cache that's loaded from quiz_status table
        enabled = quiz_visibility.get(quiz, True)
        result.append({
            "quiz": quiz,
            "enabled": enabled
        })
    
    print(f"get_quizzes returning: {result}")
    return jsonify(result)

# Fixed POST endpoint - writes to quiz_status table
@app.route('/api/quizzes/<quiz_name>', methods=['POST'])
def update_quiz_status(quiz_name):
    data = request.get_json()
    if not data or 'enabled' not in data:
        return jsonify({'error': 'Missing enabled status'}), 400
    
    enabled = bool(data['enabled'])
    print(f"Updating quiz '{quiz_name}' to enabled={enabled}")
    
    conn = sqlite3.connect('user_data_bootcamp.db')
    cursor = conn.cursor()
    
    try:
        # Insert or update in quiz_status table
        cursor.execute("""
            INSERT OR REPLACE INTO quiz_status (quiz, enabled) 
            VALUES (?, ?)
        """, (quiz_name, 1 if enabled else 0))
        
        conn.commit()
        print(f"Successfully updated quiz '{quiz_name}' to enabled={enabled}")
        
        # Fixed: Update the in-memory cache too
        quiz_visibility[quiz_name] = enabled
        
        return jsonify({'quiz': quiz_name, 'enabled': enabled})
        
    except Exception as e:
        print(f"Error updating quiz status: {e}")
        conn.rollback()
        return jsonify({'error': 'Database update failed'}), 500
    finally:
        conn.close()

# Route to serve the quiz slider page
@app.route('/quizslider')
def quiz_slider_page():
    return render_template('quizslider.html')
  
  
  
  
    
def populate_database_from_json_files():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        print(f"Looking for JSON files in directory: {data_dir}")
        json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
        print(f"Found {len(json_files)} JSON files")

        cursor.execute("DELETE FROM questions")
        cursor.execute("DELETE FROM quizzes")  # Clear quizzes too
        print("Cleared old questions and quizzes.")

        for filename in json_files:
            quiz_name = os.path.splitext(filename)[0]
            file_path = os.path.join(data_dir, filename)
            print(f"Processing file: {file_path}")

            with open(file_path, 'r') as file:
                try:
                    data = json.load(file)
                except Exception as e:
                    print(f"Error reading JSON from {filename}: {e}")
                    continue

                questions = data.get('questions', [])
                print(f"Found {len(questions)} questions in {filename}")

                for i, q in enumerate(questions, start=1):
                    question_text = q.get('question')
                    options = q.get('options', [])
                    answer = q.get('answer')
                    if question_text and options and answer:
                        try:
                            cursor.execute(
                                "INSERT INTO questions (quiz, question, options, answer, question_number) VALUES (?, ?, ?, ?, ?)",
                                (quiz_name, question_text, json.dumps(options), answer, i)
                            )
                        except sqlite3.Error as e:
                            print(f"Error inserting question: {str(e)}")
                    else:
                        print(f"Skipping question in {filename} due to missing data: {q}")

            # Insert quiz into quizzes table with enabled=1 by default
            cursor.execute(
                "INSERT OR IGNORE INTO quizzes (name, enabled) VALUES (?, 1)",
                (quiz_name,)
            )

            print(f"Finished processing {filename}")

        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM questions")
        count = cursor.fetchone()[0]
        print(f"Total questions inserted: {count}")

        # Load quiz visibility from DB to in-memory cache
        # IMPORTANT: Clear the defaultdict first to ensure fresh data
        quiz_visibility.clear()
        cursor.execute("SELECT name, enabled FROM quizzes")
        for row in cursor.fetchall():
            quiz_visibility[row['name']] = bool(row['enabled'])

        print("All quiz data successfully loaded into memory and database.")
        print(f"Quiz visibility status: {dict(quiz_visibility)}")
        print("Loading quiz visibility from database...")
        load_quiz_visibility_from_db()
        print("Database population complete.")

    except Exception as e:
        conn.rollback()
        print(f"An error occurred, rolling back all changes: {str(e)}")
    finally:
        conn.close()
       
# def migrate_user_scores():
#     conn = sqlite3.connect(db_file)
#     c = conn.cursor()
    
#     # Fetch all user_scores without phone_number
#     c.execute('''
#         SELECT us.user_id, u.phone_number 
#         FROM user_scores us
#         JOIN users u ON us.user_id = u.id
#         WHERE us.phone_number IS NULL
#     ''')
#     user_data = c.fetchall()
    
#     # Update user_scores with phone_numbers
#     for user_id, phone_number in user_data:
#         c.execute('UPDATE user_scores SET phone_number = ? WHERE user_id = ?', (phone_number, user_id))
    
#     conn.commit()
#     conn.close()
#     logging.info(f"Migrated {len(user_data)} user scores with phone numbers")

# # Run this function after init_db() to populate existing records
# migrate_user_scores()





# Assuming you have a get_db_connection function defined elsewhere
# def get_db_connection():
#     return sqlite3.connect('your_database.db')

# Call this function when your application starts
# init_db()

 

 
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


# def handle_button_response(phone_number, button_id, button_text, user, conn):
#     log_image_event(f"Button response received: id={button_id}, text={button_text}")
#     try:
#         if button_id == "settings":
#             log_image_event(f"Accessing settings for {phone_number}")
#             handle_settings_command(phone_number, user, conn)
#             # Present options after settings command completes
#         elif button_id == "change_name":
#             log_image_event(f"User {phone_number} initiated name change")
#             conn.execute('UPDATE users SET state = ?, previous_state = ? WHERE phone_number = ?',
#                          ('changing_name', user['state'], phone_number))
#             conn.commit()
#             send_message(phone_number, "Please enter your new name:")
#         elif button_id == "view_name":
#             log_image_event(f"User {phone_number} requested to view their name")
#             user_name = conn.execute('SELECT name FROM users WHERE phone_number = ?', (phone_number,)).fetchone()[0]
#             send_message(phone_number, f"Your name is {user_name}.")
#             present_options(phone_number, user, conn)
#         elif button_id == "view_quiz_names":
#             log_image_event(f"User {phone_number} requested to view quiz names")
#             quiz_names = conn.execute('SELECT DISTINCT quiz FROM questions').fetchall()
#             quiz_names_str = ', '.join(row[0] for row in quiz_names)
#             send_message(phone_number, f"Available quizzes: {quiz_names_str}.")
#             present_options(phone_number, user, conn)
#         elif button_id == "view_scores":
#             log_image_event(f"User {phone_number} requested to view their scores")
#             cursor = conn.cursor()
#             cursor.execute("""
#                 SELECT quiz, COUNT(*) as total_questions, SUM(correct) as correct_answers
#                 FROM responses
#                 WHERE user_id = ?
#                 GROUP BY quiz
#             """, (user['id'],))
#             scores = cursor.fetchall()
#             scores_message = "Your scores:\n"
#             for row in scores:
#                 quiz = row[0]
#                 total = row[1]
#                 correct = row[2]
#                 percentage = (correct / total) * 100 if total > 0 else 0
#                 scores_message += f"Quiz: {quiz}, Total Questions: {total}, Correct Answers: {correct}, Percentage: {percentage:.1f}%\n"
#             send_message(phone_number, scores_message)
#             present_options(phone_number, user, conn)
#         elif button_id == "back":
#             log_image_event(f"User {phone_number} is returning to previous activity")
#             previous_state = conn.execute('SELECT previous_state FROM users WHERE phone_number = ?', (phone_number,)).fetchone()[0]
#             conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', (previous_state, phone_number))
#             conn.commit()
#             send_message(phone_number, "Returning to previous activity.")
#             present_options(phone_number, user, conn)
#         elif button_id == "more":
#             log_image_event(f"User {phone_number} requested more options")
#             handle_settings_command(phone_number, user, conn, page=2)
#         elif button_id == "page_1":
#             log_image_event(f"User {phone_number} requested page 1")
#             handle_settings_command(phone_number, user, conn, page=1)
#         elif button_id in ["records", "quiz"] or button_text.lower() in ["start quiz", "record keeping"]:
#             log_image_event(f"Handling {button_text} request for {phone_number}")
#             handle_text_message(phone_number, button_text, user, conn)
#         elif button_id == "ai_chat":
#             start_ai_chat(phone_number, user, conn)
#         elif button_id == "next_question":
#             send_next_question(phone_number, user, conn)
#         elif button_id == "end_chat":
#             end_ai_chat(phone_number, user, conn)
#         elif button_id == "ask_followup":
#             log_image_event(f"Handling ask followup request for {phone_number}")
#             handle_followup_request(phone_number, conn)
#         elif button_id == "retry":
#             log_image_event(f"User {phone_number} requested to retry AI response")
#             handle_ai_chat(phone_number, "Please try to explain again.", button_id,  conn)
#         else:
#             log_image_event(f"Unknown button response: {button_id} from {phone_number}")
#             handle_text_message(phone_number, button_text, user, conn)
#     except Exception as e:
#         log_image_event(f"Error in handle_button_response: {str(e)}")
#         log_image_event(traceback.format_exc())
#         send_message(phone_number, "An error occurred. Please try again or type 'records', 'quiz', or 'settings' to switch.")

       
       

        
def handle_button_response(phone_number, button_id, button_text, user, conn):
    log_image_event(f"Button/List response received: id={button_id}, text={button_text}")
    try:
        if button_id == "settings" or button_text.lower() == "settings":
            log_image_event(f"Accessing settings for {phone_number}")
            handle_settings_command(phone_number, user, conn)
            # Present options after settings command completes
        elif button_id == "change_name" or button_text.lower() == "change name":
            log_image_event(f"User {phone_number} initiated name change")
            conn.execute('UPDATE users SET state = ?, previous_state = ? WHERE phone_number = ?',
                         ('changing_name', user['state'], phone_number))
            conn.commit()
            send_message(phone_number, "Please enter your new name:")
        elif button_id == "view_name" or button_text.lower() == "view name":
            log_image_event(f"User {phone_number} requested to view their name")
            user_name = conn.execute('SELECT name FROM users WHERE phone_number = ?', (phone_number,)).fetchone()[0]
            send_message(phone_number, f"Your name is {user_name}.")
            present_options(phone_number, user, conn)
        elif button_id == "view_quiz_names" or button_text.lower() == "view quiz names":
            log_image_event(f"User {phone_number} requested to view quiz names")
            quiz_names = conn.execute('SELECT DISTINCT quiz FROM questions').fetchall()
            quiz_names_str = ', '.join(row[0] for row in quiz_names)
            send_message(phone_number, f"Available quizzes: {quiz_names_str}.")
            present_options(phone_number, user, conn)
        elif button_id == "view_scores" or button_text.lower() == "view scores":
            log_image_event(f"User {phone_number} requested to view their scores")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT quiz, COUNT(*) as total_questions, SUM(correct) as correct_answers
                FROM responses
                WHERE user_id = ?
                GROUP BY quiz
            """, (user['id'],))
            scores = cursor.fetchall()
            scores_message = "Your scores:\n"
            for row in scores:
                quiz = row[0]
                total = row[1]
                correct = row[2]
                percentage = (correct / total) * 100 if total > 0 else 0
                scores_message += f"Quiz: {quiz}, Total Questions: {total}, Correct Answers: {correct}, Percentage: {percentage:.1f}%\n"
            send_message(phone_number, scores_message)
            present_options(phone_number, user, conn)
        elif button_id == "back" or button_text.lower() == "back":
            log_image_event(f"User {phone_number} is returning to previous activity")
            previous_state = conn.execute('SELECT previous_state FROM users WHERE phone_number = ?', (phone_number,)).fetchone()[0]
            conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', (previous_state, phone_number))
            conn.commit()
            send_message(phone_number, "Returning to previous activity.")
            present_options(phone_number, user, conn)
        elif button_id == "more" or button_text.lower() == "more options":
            log_image_event(f"User {phone_number} requested more options")
            handle_settings_command(phone_number, user, conn, page=2)
        elif button_id == "page_1" or button_text.lower() == "page 1":
            log_image_event(f"User {phone_number} requested page 1")
            handle_settings_command(phone_number, user, conn, page=1)
        elif button_id in ["records", "quiz"] or button_text.lower() in ["start quiz", "record keeping"]:
            log_image_event(f"Handling {button_text} request for {phone_number}")
            handle_text_message(phone_number, button_text, user, conn)
        elif button_id == "ai_chat" or button_text.lower() == "chat with ai":
            start_ai_chat(phone_number, user, conn)
        elif button_id == "next_question" or button_text.lower() == "next question":
            send_next_question(phone_number, user, conn)
        elif button_id == "end_chat" or button_text.lower() == "end chat":
            end_ai_chat(phone_number, user, conn)
        elif button_id == "ask_followup" or button_text.lower() == "ask follow-up":
            log_image_event(f"Handling ask follow-up request for {phone_number}")
            handle_followup_request(phone_number, conn)
        elif button_id == "retry" or button_text.lower() == "retry":
            log_image_event(f"User {phone_number} requested to retry AI response")
            handle_ai_chat(phone_number, "Please try to explain again.", conn)
        else:
            log_image_event(f"Unknown button/list response: {button_id} from {phone_number}")
            handle_text_message(phone_number, button_text, user, conn)
    except Exception as e:
        log_image_event(f"Error in handle_button_response: {str(e)}")
        log_image_event(traceback.format_exc())
        send_message(phone_number, "An error occurred. Please try again or type 'records', 'quiz', or 'settings' to switch.")

        
        
        

def handle_button_response(phone_number, button_id, button_text, user, conn):
    log_image_event(f"Button/List response received: id={button_id}, text={button_text}")
    try:
        # Handle quiz review at the start
        if user['state'] == 'reviewing_quiz':
            # Match exact format: quiz6 (3 incorrect)
            quiz_match = re.search(r'quiz(\d+)\s?\(\d+\s?incorrect\)', button_id)
            if quiz_match:
                quiz_number = quiz_match.group(1)
                quiz_name = f'quiz{quiz_number}'
                
                cursor = conn.cursor()
                query = """
                SELECT COUNT(*) as count
                FROM responses r
                WHERE r.user_id = ? 
                AND r.quiz = ? 
                AND r.correct = 0
                """
                cursor.execute(query, (user['id'], quiz_name))
                result = cursor.fetchone()
                
                if not result or result['count'] == 0:
                    send_message(phone_number, f"No incorrect answers found for Quiz {quiz_number}. Please select a quiz from the available options.")
                    start_ai_chat(phone_number, user, conn)
                    return
                    
                handle_quiz_review(phone_number, quiz_name, user, conn)
                return

        # Existing button handling logic
        if button_id in ["settings", "settings"]:
            log_image_event(f"Accessing settings for {phone_number}")
            handle_settings_command(phone_number, user, conn)
        elif button_id in ["change_name", "change name"]:
            log_image_event(f"User {phone_number} initiated name change")
            conn.execute('UPDATE users SET state = ?, previous_state = ? WHERE phone_number = ?',
                         ('changing_name', user['state'], phone_number))
            conn.commit()
            send_message(phone_number, "Please enter your new name:")
        elif button_id == "review_another":
            logging.info(f"User {phone_number} chose to review another quiz.")
            start_ai_chat(phone_number, user, conn)
        elif button_id in ["view_name", "view name"]:
            log_image_event(f"User {phone_number} requested to view their name")
            user_name = conn.execute('SELECT name FROM users WHERE phone_number = ?', (phone_number,)).fetchone()[0]
            send_message(phone_number, f"Your name is {user_name}.")
            present_options(phone_number, user, conn)
        elif button_id in ["view_quiz_names", "view quiz names"]:
            log_image_event(f"User {phone_number} requested to view quiz names")
            quiz_names = conn.execute('SELECT DISTINCT quiz FROM questions').fetchall()
            quiz_names_str = ', '.join(row[0] for row in quiz_names)
            send_message(phone_number, f"Available quizzes: {quiz_names_str}.")
            present_options(phone_number, user, conn)
        elif button_id in ["view_scores", "view scores"]:
            log_image_event(f"User {phone_number} requested to view their scores")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT quiz, COUNT(*) as total_questions, SUM(correct) as correct_answers
                FROM responses
                WHERE user_id = ?
                GROUP BY quiz
            """, (user['id'],))
            scores = cursor.fetchall()
            scores_message = "Your scores:\n"
            for row in scores:
                quiz, total, correct = row
                percentage = (correct / total) * 100 if total > 0 else 0
                scores_message += f"Quiz: {quiz}, Total Questions: {total}, Correct Answers: {correct}, Percentage: {percentage:.1f}%\n"
            send_message(phone_number, scores_message)
            present_options(phone_number, user, conn)
        elif button_id in ["back", "back"]:
            log_image_event(f"User {phone_number} is returning to previous activity")
            previous_state = conn.execute('SELECT previous_state FROM users WHERE phone_number = ?', (phone_number,)).fetchone()[0]
            conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', (previous_state, phone_number))
            conn.commit()
            send_message(phone_number, "Returning to previous activity.")
            present_options(phone_number, user, conn)
        elif button_id in ["more", "more options"]:
            log_image_event(f"User {phone_number} requested more options")
            handle_settings_command(phone_number, user, conn, page=2)
        elif button_id in ["page_1", "page 1"]:
            log_image_event(f"User {phone_number} requested page 1")
            handle_settings_command(phone_number, user, conn, page=1)
        elif button_id in ["records", "quiz"] or button_text.lower() in ["start quiz", "record keeping"]:
            log_image_event(f"Handling {button_text} request for {phone_number}")
            handle_text_message(phone_number, button_text, user, conn)
        elif button_id in ["ai_chat", "chat with ai"]:
            start_ai_chat(phone_number, user, conn)
        elif button_id in ["next_question", "next question"]:
            send_next_question(phone_number, user, conn)
        elif button_id in ["end_chat", "end chat"]:
            end_ai_chat(phone_number, user, conn)
        elif button_id in ["ask_followup", "ask follow-up"]:
            log_image_event(f"Handling ask follow-up request for {phone_number}")
            handle_followup_request(phone_number, conn)
        elif button_id in ["retry", "retry"]:
            log_image_event(f"User {phone_number} requested to retry AI response")
            handle_ai_chat(phone_number, "Please try to explain again.", conn)
        else:
            log_image_event(f"Unknown button/list response: {button_id} from {phone_number}")
            handle_text_message(phone_number, button_text, user, conn)
    except Exception as e:
        log_image_event(f"Error in handle_button_response: {str(e)}")
        log_image_event(traceback.format_exc())
        send_message(phone_number, "An error occurred. Please try again or type 'records', 'quiz', or 'settings' to switch.")

        
        
        
   
        
        
# def handle_message(message):
#     log_image_event(f"Full message content: {json.dumps(message, indent=2)}")
   
#     message_id = message.get('id')
#     phone_number = message['from']
#     message_type = message['type']
#     log_image_event(f"Received message of type '{message_type}' from {phone_number}")

#     conn = get_db_connection()
#     try:
#         if conn.execute('SELECT 1 FROM processed_messages WHERE message_id = ?', (message_id,)).fetchone():
#             log_image_event(f"Message {message_id} already processed, skipping")
#             return
       
#         user = conn.execute('SELECT * FROM users WHERE phone_number = ?', (phone_number,)).fetchone()
#         log_image_event(f"Processing message {message_id} for user: {user}")
       
#         if user is None:
#             # This is a new user, let's create a record for them
#             conn.execute('INSERT INTO users (phone_number, state) VALUES (?, ?)', (phone_number, 'awaiting_full_info'))
#             conn.commit()
            
#             send_message(phone_number, "Welcome to EmpowerBot! What's your full name?")
#             log_image_event(f"New user created for {phone_number}, awaiting name")
#         else:
#             log_image_event(f"User state: {user['state']}")
           
#             if message_type == 'interactive':
#                 log_image_event(f"Processing interactive message: {json.dumps(message.get('interactive', {}), indent=2)}")
#                 interactive = message.get('interactive', {})
               
#                 if interactive.get('type') == 'button_reply':
#                     button_id = interactive['button_reply']['id']
#                     button_text = interactive['button_reply']['title']
#                     log_image_event(f"Received button reply: id={button_id}, text={button_text}")
                   
#                     if button_id == 'explain_yes':
#                         log_image_event(f"Triggering AI chat for explanation")
#                         handle_ai_chat(phone_number, "Please explain the previous question.", button_id, conn)
#                         return
#                     elif button_id == 'explain_no':
#                         log_image_event(f"Moving to next question")
#                         send_next_question(phone_number, user, conn)
#                         return
#                     elif button_id == 'end_chat':
#                         end_ai_chat(phone_number, user, conn)
#                         return
#                     elif button_id == 'next_question':
#                         handle_post_explanation_action(phone_number, button_id, user, conn)
#                         return
#                     else:
#                         log_image_event(f"Handling other button response")
#                         handle_button_response(phone_number, button_id, button_text, user, conn)
#                         return
#                 elif interactive.get('type') == 'list_reply':
#                     list_id = interactive['list_reply']['id']
#                     list_title = interactive['list_reply']['title']
#                     log_image_event(f"Received list selection: id={list_id}, title={list_title}")
#                     handle_button_response(phone_number, list_id, list_title, user, conn)
#                     return
#                 else:
#                     log_image_event(f"Unrecognized interactive type: {interactive.get('type')}")
#                     send_message(phone_number, "Unsupported interactive message type. Please try again.")
#                     return
           
#             elif message_type == 'text':
#                 message_body = message['text']['body'].lower().strip()
#                 log_image_event(f"Received text message from {phone_number}: {message_body}")
#                 handle_text_message(phone_number, message_body, user, conn)
           
#             elif message_type in ['image', 'document']:
#                 log_image_event(f"Received {message_type} message from {phone_number}")
#                 handle_media_message(phone_number, message, message_type, user, conn)
           
#             else:
#                 log_image_event(f"Unsupported message type '{message_type}' from {phone_number}")
#                 send_message(phone_number, "Unsupported message type. Please send text, image, or document.")
       
#         conn.execute('INSERT INTO processed_messages (message_id) VALUES (?)', (message_id,))
#         conn.commit()
   
#     except Exception as e:
#         log_image_event(f"Error processing message {message_id}: {str(e)}")
#         log_image_event(traceback.format_exc())
#         send_message(phone_number, "An error occurred. Please try again or contact support if the issue persists.")
   
#     finally:
#         conn.close()
        
        


        
        
  
        
# def handle_message(message):
#     log_image_event(f"Full message content: {json.dumps(message, indent=2)}")
   
#     message_id = message.get('id')
#     phone_number = message['from']
#     message_type = message['type']
#     log_image_event(f"Received message of type '{message_type}' from {phone_number}")

#     conn = get_db_connection()
#     try:
#         if conn.execute('SELECT 1 FROM processed_messages WHERE message_id = ?', (message_id,)).fetchone():
#             log_image_event(f"Message {message_id} already processed, skipping")
#             return
       
#         user = conn.execute('SELECT * FROM users WHERE phone_number = ?', (phone_number,)).fetchone()
#         log_image_event(f"Processing message {message_id} for user: {user}")
       
#         if user is None:
#             # This is a new user, let's create a record for them
#             conn.execute('INSERT INTO users (phone_number, state) VALUES (?, ?)', (phone_number, 'awaiting_full_info'))
#             conn.commit()
            
#             send_message(phone_number, "Welcome to EmpowerBot! What's your full name?")
#             log_image_event(f"New user created for {phone_number}, awaiting name")
#         else:
#             log_image_event(f"User state: {user['state']}")
           
#             if message_type == 'interactive':
#                 log_image_event(f"Processing interactive message: {json.dumps(message.get('interactive', {}), indent=2)}")
#                 interactive = message.get('interactive', {})
               
#                 if interactive.get('type') == 'button_reply':
#                     button_id = interactive['button_reply']['id']
#                     button_text = interactive['button_reply']['title']
#                     log_image_event(f"Received button reply: id={button_id}, text={button_text}")
                   
#                     if button_id == 'explain_yes':
#                         log_image_event(f"Triggering AI chat for explanation")
#                         handle_ai_chat(phone_number, "Please explain the previous question.", button_id, conn)
#                     elif button_id == 'explain_no':
#                         log_image_event(f"Moving to next question")
#                         send_next_question(phone_number, user, conn)
#                     elif button_id == 'end_chat':
#                         end_ai_chat(phone_number, user, conn)
#                     elif button_id == 'next_question':
#                         handle_post_explanation_action(phone_number, button_id, user, conn)
#                     elif button_id == 'remove_account':
#                         handle_remove_account_request(phone_number, user, conn)
#                     elif button_id == 'confirm_remove':
#                         remove_user_account(phone_number, conn)
#                     elif button_id == 'cancel_remove':
#                         handle_settings_command(phone_number, user, conn)
#                     else:
#                         log_image_event(f"Handling other button response")
#                         handle_button_response(phone_number, button_id, button_text, user, conn)
                
#                 elif interactive.get('type') == 'list_reply':
#                     list_id = interactive['list_reply']['id']
#                     list_title = interactive['list_reply']['title']
#                     log_image_event(f"Received list selection: id={list_id}, title={list_title}")
                    
#                     if list_id == 'remove_account':
#                         handle_remove_account_request(phone_number, user, conn)
#                     else:
#                         handle_button_response(phone_number, list_id, list_title, user, conn)
                
#                 else:
#                     log_image_event(f"Unrecognized interactive type: {interactive.get('type')}")
#                     send_message(phone_number, "Unsupported interactive message type. Please try again.")
           
#             elif message_type == 'text':
#                 message_body = message['text']['body'].lower().strip()
#                 log_image_event(f"Received text message from {phone_number}: {message_body}")
#                 handle_text_message(phone_number, message_body, user, conn)
           
#             elif message_type in ['image', 'document']:
#                 log_image_event(f"Received {message_type} message from {phone_number}")
#                 handle_media_message(phone_number, message, message_type, user, conn)
           
#             else:
#                 log_image_event(f"Unsupported message type '{message_type}' from {phone_number}")
#                 send_message(phone_number, "Unsupported message type. Please send text, image, or document.")
       
#         conn.execute('INSERT INTO processed_messages (message_id) VALUES (?)', (message_id,))
#         conn.commit()
   
#     except Exception as e:
#         log_image_event(f"Error processing message {message_id}: {str(e)}")
#         log_image_event(traceback.format_exc())
#         send_message(phone_number, "An error occurred. Please try again or contact support if the issue persists.")
   
#     finally:
#         conn.close()
        
 
       
 


# Create a dictionary to store locks for each phone number
phone_locks = {}
lock_dict_lock = threading.Lock()

@contextmanager
def get_phone_lock(phone_number):
    with lock_dict_lock:
        if phone_number not in phone_locks:
            phone_locks[phone_number] = threading.Lock()
        lock = phone_locks[phone_number]
    
    try:
        lock.acquire()
        yield
    finally:
        lock.release()

def handle_message(message):
    log_image_event(f"Full message content: {json.dumps(message, indent=2)}")
   
    message_id = message.get('id')
    phone_number = message['from']
    message_type = message['type']
    log_image_event(f"Received message of type '{message_type}' from {phone_number}")

    # Use a lock for each phone number to prevent concurrent processing
    with get_phone_lock(phone_number):
        conn = get_db_connection()
        try:
            if conn.execute('SELECT 1 FROM processed_messages WHERE message_id = ?', (message_id,)).fetchone():
                log_image_event(f"Message {message_id} already processed, skipping")
                return
           
            user = conn.execute('SELECT * FROM users WHERE phone_number = ?', (phone_number,)).fetchone()
            log_image_event(f"Processing message {message_id} for user: {user}")
           
            if user is None:
                # This is a new user, let's create a record for them
                conn.execute('INSERT INTO users (phone_number, state) VALUES (?, ?)', 
                           (phone_number, 'awaiting_full_info'))
                conn.commit()
                
                send_message(phone_number, "Welcome to EmpowerBot! What's your full name?")
                log_image_event(f"New user created for {phone_number}, awaiting name")
            else:
                log_image_event(f"User state: {user['state']}")
               
                if message_type == 'interactive':
                    log_image_event(f"Processing interactive message: {json.dumps(message.get('interactive', {}), indent=2)}")
                    interactive = message.get('interactive', {})
                   
                    if interactive.get('type') == 'button_reply':
                        button_id = interactive['button_reply']['id']
                        button_text = interactive['button_reply']['title']
                        log_image_event(f"Received button reply: id={button_id}, text={button_text}")
                       
                        if button_id == 'explain_yes':
                            log_image_event(f"Triggering AI chat for explanation")
                            handle_ai_chat(phone_number, "Please explain the previous question.", conn)
                        elif button_id == 'explain_no':
                            log_image_event(f"Moving to next question")
                            send_next_question(phone_number, user, conn)
                        elif button_id == 'end_chat':
                            end_ai_chat(phone_number, user, conn)
                        elif button_id == 'next_question':
                            handle_post_explanation_action(phone_number, button_id, user, conn)
                        elif button_id == 'remove_account':
                            handle_remove_account_request(phone_number, user, conn)
                        elif button_id == 'confirm_remove':
                            remove_user_account(phone_number, conn)
                        elif button_id == 'cancel_remove':
                            handle_settings_command(phone_number, user, conn)
                        else:
                            log_image_event(f"Handling other button response")
                            handle_button_response(phone_number, button_id, button_text, user, conn)
                    
                    elif interactive.get('type') == 'list_reply':
                        list_id = interactive['list_reply']['id']
                        list_title = interactive['list_reply']['title']
                        log_image_event(f"Received list selection: id={list_id}, title={list_title}")
                        
                        if list_id == 'remove_account':
                            handle_remove_account_request(phone_number, user, conn)
                        else:
                            handle_button_response(phone_number, list_id, list_title, user, conn)
                    
                    else:
                        log_image_event(f"Unrecognized interactive type: {interactive.get('type')}")
                        send_message(phone_number, "Unsupported interactive message type. Please try again.")
               
                elif message_type == 'text':
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
            log_image_event(traceback.format_exc())
            send_message(phone_number, "An error occurred. Please try again or contact support if the issue persists.")
       
        finally:
            conn.close()
            
            
        

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
       
       
       
      
       
       
def present_options(phone_number, user, conn):
    log_image_event(f"Presenting main options to user {phone_number}")
    buttons = [
        {"type": "reply", "reply": {"id": "quiz", "title": "Start Quiz"}},
        {"type": "reply", "reply": {"id": "records", "title": "Record Keeping"}},
        {"type": "reply", "reply": {"id": "settings", "title": "Settings"}}
    ]
    send_interactive_message(phone_number, "What would you like to do next?", buttons)
    conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', ('main_menu', phone_number))
    conn.commit()
   
 


       
       
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
 
 


       
       
       
# def handle_text_message(phone_number, message_body, user, conn):
#     log_image_event(f"Handling text message for {phone_number}: {message_body}")
#     message_lower = message_body.lower().strip()
#     try:
#         # Always allow switching to quiz, records, or settings
#         if message_lower in ['quiz', 'start quiz', 'records', 'record keeping', 'settings']:
#             if message_lower in ['quiz', 'start quiz']:
#                 handle_quiz_selection(phone_number, message_body, user, conn)
#             elif message_lower in ['records', 'record keeping']:
#                 conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', ('records', phone_number))
#                 conn.commit()
#                 send_message(phone_number, f"Welcome {user['name']}, please upload your business record as an image or PDF.")
#             elif message_lower == 'settings':
#                 handle_settings_command(phone_number, user, conn)
#             return

#         if user['state'] == 'removing_account':
#             if message_lower == 'yes':
#                 remove_user_account(phone_number, conn)
#             elif message_lower == 'no':
#                 handle_settings_command(phone_number, user, conn)
#             else:
#                 send_message(phone_number, "Please respond with 'yes' to confirm account removal or 'no' to cancel.")
#             return

#         if user['state'] == 'changing_name':
#             new_name = message_body.strip()
#             conn.execute('UPDATE users SET name = ?, state = ? WHERE phone_number = ?',
#                          (new_name, user['previous_state'], phone_number))
#             conn.commit()
#             send_message(phone_number, f"Your name has been updated to: {new_name}")
#             user = conn.execute('SELECT * FROM users WHERE phone_number = ?', (phone_number,)).fetchone()
#             present_options(phone_number, user, conn)
#             return

#         # Rest of the existing logic remains the same
#         if user['state'] == 'awaiting_full_info':
#             # Step 1: Collect full name
#             conn.execute('UPDATE users SET name = ?, state = ? WHERE phone_number = ?',
#                          (message_body, 'awaiting_age', phone_number))
#             conn.commit()
#             send_message(phone_number, "Nice to meet you, {}! Please type your age is the chat".format(message_body))
        
#         elif user['state'] == 'awaiting_age':
#             # Step 2: Collect age
#             conn.execute('UPDATE users SET age = ?, state = ? WHERE phone_number = ?',
#                          (message_body, 'awaiting_gender', phone_number))
#             conn.commit()
#             send_message(phone_number, "Thank you! Please type your gender in the chat. (Please reply with 'male', 'female', or 'other')")
        
#         elif user['state'] == 'awaiting_gender':
#             # Step 3: Collect gender
#             conn.execute('UPDATE users SET gender = ?, state = ? WHERE phone_number = ?',
#                          (message_body, 'awaiting_business_type', phone_number))
#             conn.commit()
#             send_message(phone_number, "Great! Please type in the chat the type of business or services you deal on?")
        
#         elif user['state'] == 'awaiting_business_type':
#             # Step 4: Collect business type
#             conn.execute('UPDATE users SET business_type = ?, state = ? WHERE phone_number = ?',
#                          (message_body, 'awaiting_location', phone_number))
#             conn.commit()
#             send_message(phone_number, "Thank you! Type in the chat where your business is located?")
        
#         elif user['state'] == 'awaiting_location':
#             # Step 5: Collect location
#             conn.execute('UPDATE users SET location = ?, state = ? WHERE phone_number = ?',
#                          (message_body, 'awaiting_choice', phone_number))
#             conn.commit()
#             send_message(phone_number, "Thank you for providing your information! What would you like to do next?")
#             present_options(phone_number, user, conn)
#         elif user['state'] == 'awaiting_choice':
#             send_message(phone_number, "Please choose 'Record Keeping' or 'Start Quiz'.")
#             present_options(phone_number, user, conn)
#         elif user['state'] in ['ai_chat', 'awaiting_followup', 'post_explanation', 'awaiting_action', 'awaiting_explanation']:
#             # Store the follow-up question
#             cursor = conn.cursor()
#             cursor.execute('INSERT INTO followup_questions (user_id, question) VALUES (?, ?)',
#                            (user['id'], message_body))
#             conn.commit()
#             # Handle AI chat and set state to 'ai_chat' to continue the conversation
#             handle_ai_chat(phone_number, message_body, button_id, conn)
#             conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', ('ai_chat', phone_number))
#             conn.commit()
#         elif user['state'] == 'selecting_quiz':
#             handle_quiz_selection(phone_number, message_body, user, conn)
#         elif user['state'].startswith('quiz_'):
#             handle_quiz_response(phone_number, message_body, user, conn)
#         elif user['state'] == 'records':
#             send_message(phone_number, f"Welcome {user['name']}, please upload your business record as an image or PDF.")
#         else:
#             send_message(phone_number, "Invalid input. Please type 'records' to begin record keeping or 'quiz' to start the quiz.")
       
#         # Occasionally remind users about the quick switch option
#         if random.random() < 0.2:  # 20% chance to show the reminder
#             send_message(phone_number, "Remember, you can type 'records', 'quiz', or 'settings' at any time to switch.")
#     except Exception as e:
#         log_image_event(f"Error in handle_text_message: {str(e)}")
#         log_image_event(traceback.format_exc())
#         send_message(phone_number, "An error occurred. Please try again or contact support if the issue persists.")
#         present_options(phone_number, user, conn)
        
        
# def handle_text_message(phone_number, message_body, user, conn):
#     log_image_event(f"Handling text message for {phone_number}: {message_body}")
#     message_lower = message_body.lower().strip()
#     try:
#         # Always check for quiz, records, or settings first
#         if message_lower in ['quiz', 'start quiz', 'records', 'record keeping', 'settings']:
#             if message_lower in ['quiz', 'start quiz']:
#                 handle_quiz_selection(phone_number, message_body, user, conn)
#             elif message_lower in ['records', 'record keeping']:
#                 conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', ('records', phone_number))
#                 conn.commit()
#                 send_message(phone_number, f"Welcome {user['name']}, please upload your business record as an image or PDF.")
#             elif message_lower == 'settings':
#                 handle_settings_command(phone_number, user, conn)
#             return True

#         # Special state handling
#         if user['state'] == 'removing_account':
#             if message_lower == 'yes':
#                 remove_user_account(phone_number, conn)
#             elif message_lower == 'no':
#                 handle_settings_command(phone_number, user, conn)
#             else:
#                 send_message(phone_number, "Please respond with 'yes' to confirm account removal or 'no' to cancel.")
#             return True

#         if user['state'] == 'changing_name':
#             new_name = message_body.strip()
#             conn.execute('UPDATE users SET name = ?, state = ? WHERE phone_number = ?',
#                         (new_name, user['previous_state'], phone_number))
#             conn.commit()
#             send_message(phone_number, f"Your name has been updated to: {new_name}")
#             user = conn.execute('SELECT * FROM users WHERE phone_number = ?', (phone_number,)).fetchone()
#             present_options(phone_number, user, conn)
#             return True

#         # Registration flow with enhanced validation
#         if user['state'] == 'awaiting_full_info':
#             name = message_body.strip()
#             if not name:
#                 send_message(phone_number, "Please enter a valid name.")
#                 return True
#             conn.execute('UPDATE users SET name = ?, state = ? WHERE phone_number = ?',
#                         (name, 'awaiting_age', phone_number))
#             conn.commit()
#             send_message(phone_number, f"Nice to meet you, {name}! Please enter your age as a number.")
#             return True

#         elif user['state'] == 'awaiting_age':
#             cleaned_input = message_body.strip()
#             if not cleaned_input.isdigit():
#                 log_image_event(f"Invalid age input received: {message_body}")
#                 send_message(phone_number, "Please enter a valid numeric age (e.g., 25)")
#                 return True

#             age = int(cleaned_input)
#             if age < 0 or age > 150:
#                 log_image_event(f"Age out of valid range: {age}")
#                 send_message(phone_number, "Please enter a valid age between 0 and 150")
#                 return True

#             log_image_event(f"Valid age received: {age}")
#             conn.execute('UPDATE users SET age = ?, state = ? WHERE phone_number = ?',
#                         (age, 'awaiting_gender', phone_number))
#             conn.commit()
#             send_message(phone_number, "Thank you! Please type your gender in the chat (male, female, or other).")
#             return True

#         elif user['state'] == 'awaiting_gender':
#             gender_input = message_lower.strip()
#             if gender_input not in ['male', 'female', 'other']:
#                 send_message(phone_number, "Please reply with either 'male', 'female', or 'other'.")
#                 return True
            
#             conn.execute('UPDATE users SET gender = ?, state = ? WHERE phone_number = ?',
#                         (gender_input, 'awaiting_business_type', phone_number))
#             conn.commit()
#             send_message(phone_number, "Great! Please type in the chat the type of business or services you deal on?")
#             return True

#         elif user['state'] == 'awaiting_business_type':
#             business_type = message_body.strip()
#             if not business_type:
#                 send_message(phone_number, "Please enter a valid business type.")
#                 return True
#             conn.execute('UPDATE users SET business_type = ?, state = ? WHERE phone_number = ?',
#                         (business_type, 'awaiting_location', phone_number))
#             conn.commit()
#             send_message(phone_number, "Thank you! Type in the chat where your business is located?")
#             return True

#         elif user['state'] == 'awaiting_location':
#             location = message_body.strip()
#             if not location:
#                 send_message(phone_number, "Please enter a valid location.")
#                 return True
#             conn.execute('UPDATE users SET location = ?, state = ? WHERE phone_number = ?',
#                         (location, 'awaiting_business_size', phone_number))
#             conn.commit()
#             handle_business_size_selection(phone_number, user, conn)
#             return True

#         elif user['state'] == 'awaiting_business_size':
#             conn.execute('UPDATE users SET business_size = ?, state = ? WHERE phone_number = ?',
#                         (message_body, 'awaiting_financial_status', phone_number))
#             conn.commit()
#             handle_financial_status_selection(phone_number, user, conn)
#             return True

#         elif user['state'] == 'awaiting_financial_status':
#             conn.execute('UPDATE users SET financial_status = ?, state = ? WHERE phone_number = ?',
#                         (message_body, 'awaiting_main_challenge', phone_number))
#             conn.commit()
#             handle_main_challenge_selection(phone_number, user, conn)
#             return True

#         elif user['state'] == 'awaiting_main_challenge':
#             conn.execute('UPDATE users SET main_challenge = ?, state = ? WHERE phone_number = ?',
#                         (message_body, 'awaiting_record_keeping', phone_number))
#             conn.commit()
#             handle_record_keeping_selection(phone_number, user, conn)
#             return True

#         elif user['state'] == 'awaiting_record_keeping':
#             conn.execute('UPDATE users SET record_keeping = ?, state = ? WHERE phone_number = ?',
#                         (message_body, 'awaiting_growth_goal', phone_number))
#             conn.commit()
#             handle_growth_goal_selection(phone_number, user, conn)
#             return True

#         elif user['state'] == 'awaiting_growth_goal':
#             conn.execute('UPDATE users SET growth_goal = ?, state = ? WHERE phone_number = ?',
#                         (message_body, 'awaiting_funding_need', phone_number))
#             conn.commit()
#             handle_funding_need_selection(phone_number, user, conn)
#             return True

#         elif user['state'] == 'awaiting_funding_need':
#             conn.execute('UPDATE users SET funding_need = ?, state = ? WHERE phone_number = ?',
#                         (message_body, 'awaiting_choice', phone_number))
#             conn.commit()
#             send_message(phone_number, "Thank you! We now understand your business better. What would you like to do next?")
#             present_options(phone_number, user, conn)
#             return True

#         elif user['state'] == 'awaiting_choice':
#             send_message(phone_number, "Please choose 'Record Keeping' or 'Start Quiz'.")
#             present_options(phone_number, user, conn)
#             return True

#         elif user['state'] in ['ai_chat', 'awaiting_followup', 'post_explanation', 'awaiting_action', 'awaiting_explanation']:
#             cursor = conn.cursor()
#             cursor.execute('INSERT INTO followup_questions (user_id, question) VALUES (?, ?)',
#                          (user['id'], message_body))
#             conn.commit()
#             handle_ai_chat(phone_number, message_body, conn)
#             conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', ('ai_chat', phone_number))
#             conn.commit()
#             return True

#         # Handle different states
#         if user['state'] == 'selecting_quiz':
#             handle_quiz_selection(phone_number, message_body, user, conn)
#         elif user['state'] == 'reviewing_quiz':
#             handle_quiz_review(phone_number, message_body, user, conn)
#         elif user['state'].startswith('quiz_'):
#             handle_quiz_response(phone_number, message_body, user, conn)
#         elif user['state'] == 'records':
#             send_message(phone_number, f"Welcome {user['name']}, please upload your business record as an image or PDF.")
#         else:
#             send_message(phone_number, "Invalid input. Please type 'records' to begin record keeping or 'quiz' to start the quiz.")
        
#         if random.random() < 0.2:
#             send_message(phone_number, "Remember, you can type 'records', 'quiz', or 'settings' at any time to switch.")

#         return True

#     except Exception as e:
#         log_image_event(f"Error in handle_text_message: {str(e)}")
#         log_image_event(traceback.format_exc())
#         send_message(phone_number, "Sorry, something went wrong. Please try again.")
#         return False
      
      
      
      
      
# def handle_quiz_review(phone_number, quiz_name, user, conn):
#     """
#     Handle reviewing quizzes with incorrect answers.
#     Args:
#         phone_number: User's phone number
#         quiz_name: Name of the quiz (e.g., "quiz8")
#         user: User dictionary containing user information
#         conn: Database connection
#     """
#     try:
#         cursor = conn.cursor()
        
#         # Query to fetch incorrect answers for the specified quiz
#         query = """
#         SELECT q.question, q.answer, r.response AS user_answer,
#                r.question_number, r.quiz
#         FROM questions q
#         JOIN responses r ON q.quiz = r.quiz AND q.id = r.question_number
#         WHERE r.user_id = ? AND r.quiz = ? AND r.correct = 0
#         ORDER BY r.question_number
#         """
#         cursor.execute(query, (user['id'], quiz_name))
#         incorrect_questions = cursor.fetchall()
        
#         if not incorrect_questions:
#             send_message(phone_number, f"No incorrect answers found for {quiz_name}.")
#             present_options(phone_number, user, conn)
#             return
            
#         # Store review session data
#         review_data = {
#             'questions': [dict(q) for q in incorrect_questions],
#             'current_index': 0,
#             'total_questions': len(incorrect_questions)
#         }
        
#         conn.execute("""
#             UPDATE users 
#             SET state = ?,
#                 review_data = ?,
#                 quiz_in_review = ?
#             WHERE phone_number = ?
#         """, ('reviewing_question', json.dumps(review_data), quiz_name, phone_number))
#         conn.commit()
        
#         send_review_question(phone_number, review_data['questions'][0], 1, review_data['total_questions'])
        
#     except Exception as e:
#         logging.error(f"Error in handle_quiz_review: {str(e)}")
#         send_message(phone_number, "An error occurred while starting the review. Please try again.")
#         present_options(phone_number, user, conn)

        
        
        
def handle_quiz_review(phone_number, quiz_name, user, conn):
    """
    Handle reviewing quizzes with incorrect answers.
    Args:
        phone_number: User's phone number
        quiz_name: Name of the quiz (e.g., "quiz8")
        user: User dictionary containing user information
        conn: Database connection
    """
    try:
        cursor = conn.cursor()
        
        # Query to fetch incorrect answers for the specified quiz
        query = """
        SELECT q.question, q.answer, r.response AS user_answer,
               r.question_number, r.quiz
        FROM questions q
        JOIN responses r ON q.quiz = r.quiz AND q.id = r.question_number
        WHERE r.user_id = ? AND r.quiz = ? AND r.correct = 0
        ORDER BY r.question_number
        """
        cursor.execute(query, (user['id'], quiz_name))
        incorrect_questions = cursor.fetchall()
        
        if not incorrect_questions:
            send_message(phone_number, f"No incorrect answers found for {quiz_name}.")
            present_options(phone_number, user, conn)
            return
            
        # Store review session data
        review_data = {
            'questions': [dict(q) for q in incorrect_questions],
            'current_index': 0,
            'total_questions': len(incorrect_questions)
        }
        
        # Update user state to start review
        conn.execute("""
            UPDATE users 
            SET state = ?,
                quiz_in_review = ?,
                current_question = ?
            WHERE phone_number = ?
        """, ('reviewing_question', quiz_name, review_data['current_index'], phone_number))
        conn.commit()
        
        # Call send_next_question with the first question
        send_next_question(phone_number, user, conn)
        
    except Exception as e:
        logging.error(f"Error in handle_quiz_review: {str(e)}")
        send_message(phone_number, "An error occurred while starting the review. Please try again.")
        present_options(phone_number, user, conn)

        
        
        
        
        
        
def handle_quiz_review(phone_number, quiz_selection, user, conn):
    """
    Handle reviewing quizzes with incorrect answers.
    Args:
        phone_number: User's phone number.
        quiz_selection: The selected quiz option (e.g., "quiz8 (2 incorrect)").
        user: User dictionary containing user information.
        conn: Database connection.
    """
    try:
        logging.info(f"handle_quiz_review called with quiz_selection: {quiz_selection}")
        
        # Extract quiz name (e.g., "quiz3")
        quiz_match = re.search(r'(quiz\d+)', quiz_selection)
        if quiz_match:
            quiz_name = quiz_match.group(1)
        else:
            quiz_name = quiz_selection.split(" ")[0]
        
        logging.info(f"Extracted quiz_name: {quiz_name}")
        logging.info(f"User ID: {user['id']}")
        
        cursor = conn.cursor()
        
        # Count incorrect answers
        check_query = """
        SELECT COUNT(*) 
        FROM responses 
        WHERE user_id = ? AND quiz = ? AND correct = 0
        """
        cursor.execute(check_query, (user['id'], quiz_name))
        count = cursor.fetchone()[0]
        logging.info(f"Found {count} incorrect answers for user {user['id']} in quiz {quiz_name}")
        
        # Use the helper function to get incorrect questions
        incorrect_questions = get_incorrect_questions(user['id'], conn, quiz_name)
        
        # Handle case where get_incorrect_questions returns None (DB error)
        if incorrect_questions is None:
            logging.error(f"Database error while getting incorrect questions for user {user['id']}, quiz {quiz_name}")
            send_message(phone_number, "An error occurred while retrieving your incorrect answers. Please try again.")
            present_options(phone_number, user, conn)
            return
            
        logging.info(f"Query returned {len(incorrect_questions)} incorrect questions")
        
        if not incorrect_questions:
            send_message(phone_number, f"No incorrect answers found for {quiz_name}.")
            present_options(phone_number, user, conn)
            return
            
        logging.info(f"First incorrect question: {incorrect_questions[0]}")
        
        # Update the user's state to start review
        conn.execute("""
            UPDATE users 
            SET state = ?, quiz_in_review = ?, current_question = ?
            WHERE phone_number = ?
        """, ('reviewing_question', quiz_name, 0, phone_number))
        conn.commit()
        
        # Instead of modifying the user dict, create a new one with updated data
        # or just rely on the database to provide this information in send_next_question
        send_next_question(phone_number, user, conn)
        
    except Exception as e:
        logging.error(f"Error in handle_quiz_review: {str(e)}")
        logging.error(traceback.format_exc())
        send_message(phone_number, "An error occurred while starting the review. Please try again.")
        present_options(phone_number, user, conn)
        

        

        
        
def standardize_user_input(input_text, field_type):
    """Standardize user input using generate_text."""
    
    standardization_prompts = {
        'name': f"""
            Convert this input: "{input_text}" into ONLY a capitalized first and  surname.
            Rules:
          
            - Capitalize first letter
            - Remove any titles, suffixes, or additional names
            - Return only the name, no extra text
            Example inputs/outputs:
            "My name is John Smith" → "John Smith"
            "mrs. sarah johnson" → "Sarah Johnson"
            "MICHAEL PHELPS JR" → "Michael Phelps"
            """,
            
        'business_type': f"""
            Convert this business description: "{input_text}" into a standardized "[type] business" format.
            Rules:
            - Remove phrases like "I sell", "we deal in", "I do", etc.
            - Convert to "[type] business" format
            - Capitalize first letter
            - Return only the business type, no extra text
            Example inputs/outputs:
            "I sell food and drinks" → "Food business"
            "We deal in baby clothes" → "Clothing business"
            "I do hair styling" → "Salon business"
            """,
            
        'location': f"""
            Convert this location description: "{input_text}" into a standardized location name.
            Rules:
            - Extract main location name
            - Capitalize first letter
            - Remove extra words like "I'm at", "located in", etc.
            - Return only the location name, no extra text
            Example inputs/outputs:
            "I dey for Ikeja" → "Ikeja"
            "My shop is in surulere" → "Surulere"
            "located at LEKKI" → "Lekki"
            """
    }
    
    try:
        standardized = generate_text(standardization_prompts[field_type]).strip()
        # Additional cleanup to ensure single-line response
        standardized = standardized.split('\n')[0].strip()
        return standardized
    except Exception as e:
        logging.error(f"Error in input standardization: {str(e)}")
        # Fallback to basic capitalization if AI fails
        return input_text.strip().capitalize()
      
      
      
        
        
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

        # Handle account removal
        if user['state'] == 'removing_account':
            if message_lower == 'yes':
                remove_user_account(phone_number, conn)
            elif message_lower == 'no':
                handle_settings_command(phone_number, user, conn)
            else:
                send_message(phone_number, "Please respond with 'yes' to confirm account removal or 'no' to cancel.")
            return

        # Handle name change, applying name standardization
        if user['state'] == 'changing_name':
            new_name = standardize_user_input(message_body.strip(), 'name')
            conn.execute('UPDATE users SET name = ?, state = ? WHERE phone_number = ?',
                         (new_name, user['previous_state'], phone_number))
            conn.commit()
            send_message(phone_number, f"Your name has been updated to: {new_name}")
            user = conn.execute('SELECT * FROM users WHERE phone_number = ?', (phone_number,)).fetchone()
            present_options(phone_number, user, conn)
            return

        # Step-by-step profile completion flow, applying standardization
        if user['state'] == 'awaiting_full_info':
            standardized_name = standardize_user_input(message_body, 'name')
            conn.execute('UPDATE users SET name = ?, state = ? WHERE phone_number = ?',
                         (standardized_name, 'awaiting_age', phone_number))
            conn.commit()
            send_message(phone_number, f"Nice to meet you, {standardized_name}! Please type your age in the chat.")

        elif user['state'] == 'awaiting_age':
            conn.execute('UPDATE users SET age = ?, state = ? WHERE phone_number = ?',
                         (message_body, 'awaiting_gender', phone_number))
            conn.commit()
            send_message(phone_number, "Thank you! Please type your gender in the chat (male, female, or other).")

        elif user['state'] == 'awaiting_gender':
            conn.execute('UPDATE users SET gender = ?, state = ? WHERE phone_number = ?',
                         (message_body, 'awaiting_business_type', phone_number))
            conn.commit()
            send_message(phone_number, "Great! Please type in the chat the type of business or services you deal with.")

        elif user['state'] == 'awaiting_business_type':
            standardized_business_type = standardize_user_input(message_body, 'business_type')
            conn.execute('UPDATE users SET business_type = ?, state = ? WHERE phone_number = ?',
                         (standardized_business_type, 'awaiting_location', phone_number))
            conn.commit()
            handle_location_selection(phone_number, user, conn)

        elif user['state'] == 'awaiting_location':
            standardized_location = standardize_user_input(message_body, 'location')
            conn.execute('UPDATE users SET location = ?, state = ? WHERE phone_number = ?',
                         (standardized_location, 'awaiting_business_size', phone_number))
            conn.commit()
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

        # AI Chat and Quiz Handling
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

        # Default Response for Invalid Inputs
        else:
            send_message(phone_number, "Invalid input. Please type 'records' to begin record keeping or 'quiz' to start the quiz.")
       
        # Occasional reminder for key options
        if random.random() < 0.005:
            send_message(phone_number, "Remember, you can type 'records', 'quiz', or 'settings' at any time to switch.")

    except Exception as e:
        log_image_event(f"Error in handle_text_message: {str(e)}")
        log_image_event(traceback.format_exc())
        send_message(phone_number, "Sorry, something went wrong. Please try again or contact support.")
        present_options(phone_number, user, conn)

        
        
        
        
        
        
def end_ai_chat(phone_number, user, conn):
    conn.execute('UPDATE users SET state = ?, current_question = ? WHERE phone_number = ?',
                 ('awaiting_choice', None, phone_number))
    conn.commit()
    send_message(phone_number, "Thanks for chatting! Remember, every day is a chance to learn and grow your business. What would you like to do next?")
    present_options(phone_number, user, conn)
   
   
   
def send_ai_intro(phone_number):
    intro_message = (
        # "👋 Hi! Welcome to EmpowerBot by Empowerlocals!\n\n"
        "👋 Hi! Let's review  the quiz questions you missed. ❓\n\n ⏳\n"
#        "If you don't understand, just ask. I'M HERE TO HELP. 💬\n\n"
      "I will also help you find NEW IDEAS💡\n\n"
#         "Focus on QUIZ QUESTIONS and BUSINESS TOPICS. 📚\n\n"
#         "Your questions are saved to help you later. PLEASE USE THIS SERVICE RESPONSIBLY. 📊\n\n"
       
        #"We'll start the FIRST QUIZ QUESTION IN 5 SECS! ⏳\n"
        "################################################################################"
        "########################################################################################"
    )
    send_message(phone_number, intro_message)

   

import time

import time

def send_ai_intro(phone_number):
    intro_message = (
        "👋 Welcome to EmpowerBot! 🎉\n\n"
        "Review missed quiz questions and get new business ideas 💡\n\n"
        # "🔒 Your answers are completely safe with us.🛡️\n\n"
        "🔒 We will never share them with anyone without your permission. 🛡️\n\n"
     "######################"
  
    )
    
    # Send the intro message
    send_message(phone_number, intro_message)

    # Simulate a brief "thinking" animation
    for i in range(1):
    
        send_message(phone_number, "⏳ Processing... ⏳")
        time.sleep(2)

    # Proceed after 10 seconds
    send_message(phone_number, "✅ All set in 10 Secs!")

    
   
   
# def start_ai_chat(phone_number, user, conn):
#     try:
#         log_image_event(f"Starting AI chat for user {user['id']}")
#         # Ensure the introductory message is always sent first
#         send_ai_intro(phone_number)
       
#         # Wait for 15 seconds before proceeding
#         time.sleep(5)

#         result = conn.execute("SELECT COUNT(DISTINCT quiz) as count FROM responses WHERE user_id = ?", (user['id'],)).fetchone()
#         quizzes_taken = result['count'] if result else 0
#         log_image_event(f"User {user['id']} has taken {quizzes_taken} quizzes")

#         if quizzes_taken == 0:
#             send_message(phone_number, "It looks like you haven't taken any quizzes yet. Would you like to start one?")
#             present_options(phone_number, user, conn)
#             return

#         result = conn.execute("SELECT COUNT(*) as count FROM responses WHERE user_id = ?", (user['id'],)).fetchone()
#         total_responses = result['count'] if result else 0
#         log_image_event(f"User {user['id']} has {total_responses} total responses")

#         result = conn.execute("SELECT COUNT(*) as count FROM responses WHERE user_id = ? AND correct = 0", (user['id'],)).fetchone()
#         incorrect_responses = result['count'] if result else 0
#         log_image_event(f"User {user['id']} has {incorrect_responses} incorrect responses")

#         incorrect_questions = get_incorrect_questions(user['id'], conn)
#         log_image_event(f"Incorrect questions for user {user['id']}: {incorrect_questions}")

#         if incorrect_questions:
#             log_image_event(f"Found {len(incorrect_questions)} incorrect questions for user {user['id']}")
#             conn.execute('UPDATE users SET state = ?, current_question = ? WHERE phone_number = ?',
#                          ('ai_chat', 0, phone_number))
#             conn.commit()
#             send_next_question(phone_number, user, conn)
#         else:
#             log_image_event(f"No incorrect questions found for user {user['id']}")
#             if incorrect_responses > 0:
#                 log_image_event(f"Discrepancy detected: {incorrect_responses} incorrect responses but no incorrect questions")
#                 send_message(phone_number, "There seems to be an issue with retrieving your quiz data. We're looking into it. In the meantime, would you like to review your overall progress or start a new quiz?")
#             else:
#                 send_message(phone_number, "Great job! You haven't missed any questions yet. Would you like to review your quiz progress or start a new quiz?")
#             present_options(phone_number, user, conn)
           
     
#     except Exception as e:
#         log_image_event(f"Error in start_ai_chat: {str(e)}")
#         log_image_event(traceback.format_exc())
#         send_message(phone_number, "An error occurred while starting the AI chat. Please try again or contact support.")
       

     
# def start_ai_chat(phone_number, user, conn):
#     try:
#         log_image_event(f"Starting AI chat for user {user['id']}")
#         # Ensure the introductory message is always sent first
#         send_ai_intro(phone_number)
       
#         # Wait for 10 seconds before proceeding
#         time.sleep(10)
        
        
#         result = conn.execute("SELECT COUNT(DISTINCT quiz) as count FROM responses WHERE user_id = ?", (user['id'],)).fetchone()
#         quizzes_taken = result['count'] if result else 0
#         log_image_event(f"User {user['id']} has taken {quizzes_taken} quizzes")
#         if quizzes_taken == 0:
#             send_message(phone_number, "It looks like you haven't taken any quizzes yet. Would you like to start one?")
#             present_options(phone_number, user, conn)
#             return
#         result = conn.execute("SELECT COUNT(*) as count FROM responses WHERE user_id = ?", (user['id'],)).fetchone()
#         total_responses = result['count'] if result else 0
#         log_image_event(f"User {user['id']} has {total_responses} total responses")
#         result = conn.execute("SELECT COUNT(*) as count FROM responses WHERE user_id = ? AND correct = 0", (user['id'],)).fetchone()
#         incorrect_responses = result['count'] if result else 0
#         log_image_event(f"User {user['id']} has {incorrect_responses} incorrect responses")
#         incorrect_questions = get_incorrect_questions(user['id'], conn)
#         log_image_event(f"Incorrect questions for user {user['id']}: {incorrect_questions}")
#         if incorrect_questions:
#             log_image_event(f"Found {len(incorrect_questions)} incorrect questions for user {user['id']}")
#             # Change the state to 'awaiting_explanation' instead of 'ai_chat'
#             conn.execute('UPDATE users SET state = ?, current_question = ? WHERE phone_number = ?',
#                          ('awaiting_explanation', 0, phone_number))
#             conn.commit()
#             # The existing send_next_question function will handle prompting for explanation
#             send_next_question(phone_number, user, conn)
#         else:
#             log_image_event(f"No incorrect questions found for user {user['id']}")
#             if incorrect_responses > 0:
#                 log_image_event(f"Discrepancy detected: {incorrect_responses} incorrect responses but no incorrect questions")
#                 send_message(phone_number, "There seems to be an issue with retrieving your quiz data. We're looking into it. In the meantime, would you like to review your overall progress or start a new quiz?")
#             else:
#                 send_message(phone_number, "Great job! You haven't missed any questions yet. Would you like to review your quiz progress or start a new quiz?")
#             present_options(phone_number, user, conn)
           
#     except Exception as e:
#         log_image_event(f"Error in start_ai_chat: {str(e)}")
#         log_image_event(traceback.format_exc())
#         send_message(phone_number, "An error occurred while starting the AI chat. Please try again or contact support.")
        
 


def start_ai_chat(phone_number, user, conn):
    try:
        log_image_event(f"Starting AI chat for user {user['id']}")
        send_ai_intro(phone_number)
        
        
        # Wait for 5 seconds before proceeding
        time.sleep(5)

        cursor = conn.cursor()
        query = """
        SELECT r.quiz, COUNT(*) as incorrect_count
        FROM responses r
        WHERE r.user_id = ? 
        AND r.correct = 0
        GROUP BY r.quiz
        ORDER BY CAST(SUBSTR(r.quiz, 5) AS INTEGER)
        """
        cursor.execute(query, (user['id'],))
        quizzes = cursor.fetchall()

        if not quizzes:
            send_message(phone_number, "Great job! You haven't missed any questions. Would you like to start a new quiz?")
            present_options(phone_number, user, conn)
            return

        conn.execute('UPDATE users SET state = ? WHERE phone_number = ?',
                     ('reviewing_quiz', phone_number))
        conn.commit()

        if len(quizzes) <= 3:
            buttons = [{
                "type": "reply",
                "reply": {
                    "id": f"quiz{quiz[0].replace('quiz', '')} ({quiz[1]} incorrect)",
                    "title": f"{quiz[0]} ({quiz[1]} incorrect)"
                }
            } for quiz in quizzes]

            send_interactive_message(
                phone_number,
                "Select a quiz to review:",
                buttons
            )
        else:
            sections = []
            current_section = []
            last_section_start = 0

            for quiz in quizzes:
                quiz_num = int(quiz[0].replace('quiz', ''))
                section_start = (quiz_num // 10) * 10

                if section_start != last_section_start and current_section:
                    sections.append({
                        "title": f"Quizzes {last_section_start + 1}-{last_section_start + 10}",
                        "rows": current_section
                    })
                    current_section = []
                    last_section_start = section_start

                current_section.append({
                    "id": f"quiz{quiz_num} ({quiz[1]} incorrect)",
                    "title": f"{quiz[0]}",
                })

            if current_section:
                sections.append({
                    "title": f"Quizzes {last_section_start + 1}-{last_section_start + 10}",
                    "rows": current_section
                })

            send_quiz_list_button(
                phone_number,
                "Select a quiz to review",
                "View Quizzes",
                sections
            )

    except Exception as e:
        log_image_event(f"Error in start_ai_chat: {str(e)}")
        log_image_event(traceback.format_exc())
        send_message(phone_number, "An error occurred. Please try again or contact support.")
        present_options(phone_number, user, conn)

        
        
        
 

def send_quiz_list_button(phone_number, title, button_title, sections):
    """
    Sends a WhatsApp list button for quiz selection.
    """
    list_message = {
        "type": "list",
        "header": {"type": "text", "text": title},
        "body": {"text": "Please select one of the quizzes below to review."},
        "footer": {"text": "Select an option below"},
        "action": {
            "button": button_title,
            "sections": sections
        }
    }
    return send_interactive_message(phone_number, list_message)

  
  
    
    

    
def send_quiz_buttons(phone_number, quizzes):
    """
    Sends regular buttons when there are 3 or fewer quizzes.
    """
    buttons = [{"type": "reply", "title": f"Quiz {quiz}", "id": quiz} for quiz in quizzes]
    message_body = {
        "recipient_type": "individual",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "header": {
                "type": "text",
                "text": "Select a quiz to review"
            },
            "body": {
                "text": "Please select one of the quizzes below to review."
            },
            "action": {
                "buttons": buttons
            }
        }
    }
    send_whatsapp_message(phone_number, message_body)

    
    
    
    
def send_whatsapp_message(phone_number, message_body):
    """
    Send a WhatsApp message via an API call (placeholder).
    """
    log_image_event(f"Sending WhatsApp message to {phone_number}: {message_body}")
    # Replace with the actual API integration to send the message
    pass
  
  
  
  

  
  
  
        
        
        
def handle_settings_command(phone_number, user, conn, page=1):
    # Define button sets with a maximum of 3 buttons per set
    button_sets = [
        [
            {"type": "reply", "reply": {"id": "change_name", "title": "Change Name"}},
          #  {"type": "reply", "reply": {"id": "view_name", "title": "View Name"}},
    {"type": "reply", "reply": {"id": "view_quiz_names", "title": "View Quiz Names"}},
                      {"type": "reply", "reply": {"id": "more", "title": "More"}}
        ],
        [
            {"type": "reply", "reply": {"id": "view_scores", "title": "View Scores"}},
        {"type": "reply", "reply": {"id": "view_name", "title": "View Name"}},
            {"type": "reply", "reply": {"id": "back", "title": "Back"}}
            #{"type": "reply", "reply": {"id": "more", "title": "More"}}
        ]
    ]

    # Determine the buttons to show based on the page number
    buttons = button_sets[page - 1] if page <= len(button_sets) else []

    # Send the interactive message
    success, message = send_interactive_message(phone_number, "Settings:", buttons)
    if not success:
        log_image_event(f"Failed to send interactive message: {message}")
        return

    # Update the user's state and other relevant data
    previous_state = user['state']

    try:
        conn.execute('UPDATE users SET state = ?, previous_state = ? WHERE phone_number = ?',
                     ('settings', previous_state, phone_number))
        conn.commit()

        cursor = conn.cursor()

        # Fetch and update user-related data
        cursor.execute("SELECT name FROM users WHERE phone_number = ?", (phone_number,))
        name_result = cursor.fetchone()
        user_name = name_result[0] if name_result else "Unknown"

        cursor.execute("SELECT DISTINCT quiz FROM questions")
        quiz_names = [row[0] for row in cursor.fetchall()]

        cursor.execute("""
            SELECT quiz, COUNT(*) as total_questions, SUM(correct) as correct_answers
            FROM responses
            WHERE user_id = ?
            GROUP BY quiz
        """, (user['id'],))
        scores = cursor.fetchall()

        # Convert scores to a serializable format
        scores_serialized = [{"quiz": row[0], "total_questions": row[1], "correct_answers": row[2]} for row in scores]

        temp_data = json.dumps({
            "name": user_name,
            "quiz_names": quiz_names,
            "scores": scores_serialized
        })
        conn.execute('UPDATE users SET temp_data = ? WHERE phone_number = ?', (temp_data, phone_number))
        conn.commit()

        log_image_event(f"Settings command handled successfully for user {phone_number}.")

    except Exception as e:
        log_image_event(f"Error in settings command for user {phone_number}: {e}")


  
  
def handle_settings_command(phone_number, user, conn):
    # Create a list of options for settings
    list_options = [
        {"id": "change_name", "title": "Change Name"},
        {"id": "view_quiz_names", "title": "View Quiz Names"},
        {"id": "view_scores", "title": "View Scores"},
        {"id": "view_name", "title": "View Name"},
        {"id": "back", "title": "Back"}
    ]
    # Prepare the list message with options
    list_message = {
        "type": "list",
        "header": {
            "type": "text",
            "text": "Settings"
        },
        "body": {
            "text": "Choose an option:"
        },
        "action": {
            "button": "Select",
            "sections": [
                {
                    "title": "Settings Options",
                    "rows": list_options
                }
            ]
        }
    }
    # Send the interactive message with the list
    success, message = send_interactive_message(phone_number, list_message)
    if not success:
        log_image_event(f"Failed to send interactive message: {message}")
        return
    # Update the user's state and other relevant data
    previous_state = user['state']
    try:
        conn.execute('UPDATE users SET state = ?, previous_state = ? WHERE phone_number = ?',
                     ('settings', previous_state, phone_number))
        conn.commit()
        cursor = conn.cursor()
        # Fetch and update user-related data
        cursor.execute("SELECT name FROM users WHERE phone_number = ?", (phone_number,))
        name_result = cursor.fetchone()
        user_name = name_result[0] if name_result else "Unknown"
        cursor.execute("SELECT DISTINCT quiz FROM questions")
        quiz_names = [row[0] for row in cursor.fetchall()]
        cursor.execute("""
            SELECT quiz, COUNT(*) as total_questions, SUM(correct) as correct_answers
            FROM responses
            WHERE user_id = ?
            GROUP BY quiz
        """, (user['id'],))
        scores = cursor.fetchall()
        # Convert scores to a serializable format
        scores_serialized = [{"quiz": row[0], "total_questions": row[1], "correct_answers": row[2]} for row in scores]
        temp_data = json.dumps({
            "name": user_name,
            "quiz_names": quiz_names,
            "scores": scores_serialized
        })
        conn.execute('UPDATE users SET temp_data = ? WHERE phone_number = ?', (temp_data, phone_number))
        conn.commit()
        log_image_event(f"Settings command handled successfully for user {phone_number}.")
    except Exception as e:
        log_image_event(f"Error in settings command for user {phone_number}: {e}")
        
        
        


def handle_settings_command(phone_number, user, conn):
    log_image_event(f"Starting settings command for {phone_number}")

    # Create a list of options for settings
    list_options = [
        {"id": "change_name", "title": "Change Name"},
        {"id": "view_quiz_names", "title": "View Quiz Names"},
        {"id": "view_scores", "title": "View Scores"},
        {"id": "view_name", "title": "View Name"},
        {"id": "remove_account", "title": "Remove Account"},
        {"id": "back", "title": "Back"}
    ]

    # Prepare the list message with options
    list_message = {
        "type": "list",
        "header": {
            "type": "text",
            "text": "Settings"
        },
        "body": {
            "text": "Choose an option:"
        },
        "action": {
            "button": "Select",
            "sections": [
                {
                    "title": "Settings Options",
                    "rows": list_options
                }
            ]
        }
    }

    try:
        log_image_event(f"Attempting to send settings menu to {phone_number}")
        success, message = send_interactive_message(phone_number, list_message)
        
        if not success:
            raise Exception(f"Failed to send settings menu: {message}")

        log_image_event(f"Successfully sent settings menu to {phone_number}")

    except Exception as e:
        log_image_event(f"Error sending settings menu to {phone_number}: {str(e)}")
        log_image_event(f"Full error traceback: {traceback.format_exc()}")
        send_message(phone_number, "An error occurred while displaying the settings menu. Please try again or contact support if the issue persists.")
        return

    # Update the user's state
    try:
        log_image_event(f"Updating user state for {phone_number}")
        
        conn.execute('UPDATE users SET state = ? WHERE phone_number = ?',
                     ('settings', phone_number))
        conn.commit()
        
        log_image_event(f"Successfully updated user state for {phone_number}")

    except Exception as e:
        log_image_event(f"Database error in settings command for {phone_number}: {str(e)}")
        log_image_event(f"Full database error traceback: {traceback.format_exc()}")
        conn.rollback()
        send_message(phone_number, "An error occurred while processing your request. Please try again or contact support if the issue persists.")
        return

    log_image_event(f"Completed handle_settings_command for {phone_number}")
        
        
        
        
def handle_remove_account_request(phone_number, user, conn):
    confirmation_message = {
        "type": "interactive",
        "interactive": {
            "type": "button",
            "header": {
                "type": "text",
                "text": "Remove Account Confirmation"
            },
            "body": {
                "text": "Are you sure you want to remove your account? This action cannot be undone. All your data will be permanently deleted."
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "confirm_remove",
                            "title": "Yes, Remove Account"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "cancel_remove",
                            "title": "No, Keep Account"
                        }
                    }
                ]
            }
        }
    }
    
    success, message = send_interactive_message(phone_number, confirmation_message)
    if success:
        conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', ('removing_account', phone_number))
        conn.commit()
        log_image_event(f"Sent account removal confirmation to {phone_number}")
    else:
        log_image_event(f"Failed to send account removal confirmation to {phone_number}: {message}")
        # Fallback to plain text message
        fallback_message = "Are you sure you want to remove your account? This action cannot be undone. All your data will be permanently deleted. Reply with 'YES' to confirm or 'NO' to cancel."
        send_message(phone_number, fallback_message)
        conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', ('removing_account', phone_number))
        conn.commit()
        
        
        

def remove_user_account(phone_number, conn):
    try:
        cursor = conn.cursor()
        
        # Get user_id
        cursor.execute("SELECT id FROM users WHERE phone_number = ?", (phone_number,))
        user_result = cursor.fetchone()
        
        if user_result is None:
            log_image_event(f"Error removing account: User not found for phone number {phone_number}")
            error_message = "We couldn't find your account. Please contact support if you believe this is an error."
            send_message(phone_number, error_message)
            return
        user_id = user_result[0]
        
        # Remove user data from all tables
        tables_to_delete = [
            ("users", "phone_number"),
            ("user_scores", "phone_number"),
            ("explanation_history", "user_id"),
            ("post10_quizzes", "user_id"),
            ("post10_quiz_responses", "quiz_id"),  # This needs special handling
            ("responses", "user_id"),
            ("followup_questions", "user_id"),
            ("conversation_history", "user_id")
        ]
        
        for table, id_column in tables_to_delete:
            try:
                if table == "post10_quiz_responses":
                    # First, get all quiz_ids for the user
                    cursor.execute("SELECT id FROM post10_quizzes WHERE user_id = ?", (user_id,))
                    quiz_ids = [row[0] for row in cursor.fetchall()]
                    # Then delete responses for these quizzes
                    if quiz_ids:
                        placeholders = ','.join(['?'] * len(quiz_ids))
                        cursor.execute(f"DELETE FROM {table} WHERE quiz_id IN ({placeholders})", quiz_ids)
                else:
                    cursor.execute(f"DELETE FROM {table} WHERE {id_column} = ?", 
                                   (phone_number if id_column == "phone_number" else user_id,))
                log_image_event(f"Deleted user data from {table}")
            except sqlite3.Error as e:
                log_image_event(f"Error deleting from {table}: {e}")
        
        conn.commit()
        log_image_event(f"Account successfully removed for user {phone_number}")
        
        # Send a confirmation message
        farewell_message = "Your account has been successfully removed. We're sorry to see you go. If you change your mind, you're always welcome to sign up again."
        send_message(phone_number, farewell_message)
    except Exception as e:
        log_image_event(f"Error removing account for user {phone_number}: {e}")
        conn.rollback()
        error_message = "We encountered an error while trying to remove your account. Please try again later or contact support."
        send_message(phone_number, error_message)
        
        
        


       
       
def view_name(phone_number, user, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT temp_data FROM users WHERE phone_number = ?", (phone_number,))
    temp_data = json.loads(cursor.fetchone()[0])
    send_message(phone_number, f"Your name: {temp_data['name']}")

def view_quiz_names(phone_number, user, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT temp_data FROM users WHERE phone_number = ?", (phone_number,))
    temp_data = json.loads(cursor.fetchone()[0])
    quiz_names = "\n".join(temp_data['quiz_names'])
    send_message(phone_number, f"Available quizzes:\n{quiz_names}")

def view_scores(phone_number, user, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT temp_data FROM users WHERE phone_number = ?", (phone_number,))
    temp_data = json.loads(cursor.fetchone()[0])

    scores_message = "Your scores:\n"
    for score in temp_data['scores']:
        quiz = score['quiz']
        total = score['total_questions']
        correct = score['correct_answers']
        percentage = (correct / total) * 100 if total > 0 else 0
        scores_message += f"Quiz: {quiz}, Total Questions: {total}, Correct Answers: {correct}, Percentage: {percentage:.1f}%\n"

    send_message(phone_number, scores_message)

   
   
   
   
   
def handle_records_command(phone_number, user, conn):
    message = f"Welcome to Record Keeping, {user['name']}! Please upload your business record as an image or PDF."
    send_message(phone_number, message)
    conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', ('records', phone_number))
    conn.commit()
    log_image_event(f"Switched to records mode for {phone_number}")



   
   
# def handle_quiz_command(phone_number, user, conn):
#     available_quizzes = list_available_quizzes()
   
#     if not available_quizzes:
#         send_message(phone_number, "No quizzes are available at the moment.")
#         present_options(phone_number, user, conn)
#         return

#     quiz_statuses = {f"quiz{quiz}": get_quiz_status(conn, user['id'], f"quiz{quiz}") for quiz in available_quizzes}

#     completed_quizzes = [quiz for quiz, status in quiz_statuses.items() if status == "completed"]
#     in_progress_quizzes = [quiz for quiz, status in quiz_statuses.items() if status == "in_progress"]
#     uncompleted_quizzes = [quiz for quiz, status in quiz_statuses.items() if status == "not_started"]

#     message = "Quiz Status:\n"
#     if completed_quizzes:
#         message += "Completed: " + ", ".join(completed_quizzes) + "\n"
#     if in_progress_quizzes:
#         message += "In Progress: " + ", ".join(in_progress_quizzes) + "\n"
#     if uncompleted_quizzes:
#         message += "Available: " + ", ".join(uncompleted_quizzes) + "\n"

#     send_message(phone_number, message)

#     buttons = [{"type": "reply", "reply": {"id": "ai_chat", "title": "Chat with AI"}}]

#     # Add up to one in-progress quiz button
#     if in_progress_quizzes:
#         buttons.extend([
#             {
#                 "type": "reply",
#                 "reply": {
#                     "id": quiz,
#                     "title": f"Continue {quiz}"
#                 }
#             } for quiz in in_progress_quizzes[:1]  # Limit to 1 in-progress quiz
#         ])

#     # Add up to one uncompleted quiz button
#     if uncompleted_quizzes:
#         buttons.extend([
#             {
#                 "type": "reply",
#                 "reply": {
#                     "id": quiz,
#                     "title": f"Start {quiz}"
#                 }
#             } for quiz in uncompleted_quizzes[:1]  # Limit to 1 uncompleted quiz
#         ])

#     # Send interactive message if we have more than just the AI chat button
#     if len(buttons) > 1:
#         send_interactive_message(phone_number, "What would you like to do?", buttons)
#     # If there are no quiz buttons but uncompleted quizzes exist, prompt the user to type the quiz number
#     elif uncompleted_quizzes:
#         send_message(phone_number, f"You have {len(uncompleted_quizzes)} quizzes available. Type the quiz number to start (e.g., 'quiz1').")
#     # If all quizzes are completed
#     else:
#         send_message(phone_number, "You've completed all available quizzes. Great job!")
#         present_options(phone_number, user, conn)

#     conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', ('selecting_quiz', phone_number))
#     conn.commit()
   

  
  
  
# def handle_quiz_command(phone_number, user, conn):
#     available_quizzes = list_available_quizzes()

#     quiz_statuses = {
#         f"quiz{quiz}": get_quiz_status(conn, user['id'], f"quiz{quiz}")
#         for quiz in available_quizzes
#     }
#     completed_quizzes = [quiz for quiz, status in quiz_statuses.items() if status == "completed"]
#     in_progress_quizzes = [quiz for quiz, status in quiz_statuses.items() if status == "in_progress"]
#     uncompleted_quizzes = [quiz for quiz, status in quiz_statuses.items() if status == "not_started"]

#     buttons = [
#         {"type": "reply", "reply": {"id": "quiz", "title": "Start Quiz"}},
#     ]

#     if not available_quizzes:
#         send_message(phone_number, "No quiz has been assigned to you yet. Please check back later.")
#         send_interactive_message(phone_number, "What would you like to do next?", buttons)
#         return

#     message = "Quiz Status:\n"
#     if completed_quizzes:
#         message += "Completed: " + ", ".join(completed_quizzes) + "\n"
#     if in_progress_quizzes:
#         message += "In Progress: " + ", ".join(in_progress_quizzes) + "\n"
#     if uncompleted_quizzes:
#         message += "Available: " + ", ".join(uncompleted_quizzes) + "\n"

#     send_message(phone_number, message)

#     # Add continue/start quiz buttons for assigned quizzes
#     if in_progress_quizzes:
#         buttons.extend([
#             {
#                 "type": "reply",
#                 "reply": {
#                     "id": quiz,
#                     "title": f"Continue {quiz}"
#                 }
#             } for quiz in in_progress_quizzes[:1]
#         ])

#     if uncompleted_quizzes:
#         buttons.extend([
#             {
#                 "type": "reply",
#                 "reply": {
#                     "id": quiz,
#                     "title": f"Start {quiz}"
#                 }
#             } for quiz in uncompleted_quizzes[:1]
#         ])

#     send_interactive_message(phone_number, "What would you like to do?", buttons)

#     conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', ('selecting_quiz', phone_number))
#     conn.commit()

    
  
def handle_quiz_command(phone_number, user, conn):
    # Load fresh quiz visibility data
    load_quiz_visibility_from_db()
    
    # Get all available quizzes and filter by visibility
    all_quizzes = list_available_quizzes()
    
    # Filter out disabled quizzes
    available_quizzes = []
    for quiz_num in all_quizzes:
        quiz_name = f"quiz{quiz_num}"
        # Check if quiz is enabled (default to True if not found)
        if quiz_visibility.get(quiz_name, True):
            available_quizzes.append(quiz_num)

    quiz_statuses = {
        f"quiz{quiz}": get_quiz_status(conn, user['id'], f"quiz{quiz}")
        for quiz in available_quizzes  # Only check enabled quizzes
    }
    completed_quizzes = [quiz for quiz, status in quiz_statuses.items() if status == "completed"]
    in_progress_quizzes = [quiz for quiz, status in quiz_statuses.items() if status == "in_progress"]
    uncompleted_quizzes = [quiz for quiz, status in quiz_statuses.items() if status == "not_started"]

    buttons = [
        {"type": "reply", "reply": {"id": "quiz", "title": "Start Quiz"}},
    ]

    if not available_quizzes:
        send_message(phone_number, "No quiz is currently available. Please check back later.")
        send_interactive_message(phone_number, "What would you like to do next?", buttons)
        return

    message = "Quiz Status:\n"
    if completed_quizzes:
        message += "Completed: " + ", ".join(completed_quizzes) + "\n"
    if in_progress_quizzes:
        message += "In Progress: " + ", ".join(in_progress_quizzes) + "\n"
    if uncompleted_quizzes:
        message += "Available: " + ", ".join(uncompleted_quizzes) + "\n"

    send_message(phone_number, message)

    # Add continue/start quiz buttons for assigned quizzes
    if in_progress_quizzes:
        buttons.extend([
            {
                "type": "reply",
                "reply": {
                    "id": quiz,
                    "title": f"Continue {quiz}"
                }
            } for quiz in in_progress_quizzes[:1]
        ])

    if uncompleted_quizzes:
        buttons.extend([
            {
                "type": "reply",
                "reply": {
                    "id": quiz,
                    "title": f"Start {quiz}"
                }
            } for quiz in uncompleted_quizzes[:1]
        ])

    send_interactive_message(phone_number, "What would you like to do?", buttons)

    conn.execute('UPDATE users SET state = ? WHERE phone_number = ?', ('selecting_quiz', phone_number))
    conn.commit()
    
    
    
    
def is_quiz_enabled(quiz_name, conn):
    """Check if a quiz is enabled by querying the database directly"""
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT enabled FROM quizzes WHERE name = ?", (quiz_name,))
        result = cursor.fetchone()
        if result:
            return bool(result[0])  # Return the enabled status from database
        else:
            return True  # Default to enabled if not found in database
    except Exception as e:
        print(f"Error checking quiz enabled status: {e}")
        return True  # Default to enabled on error

      

def handle_quiz_selection(phone_number, message_body, user, conn):
    log_image_event(f"Quiz selection initiated for {phone_number} with message: {message_body}")

    try:
        # AI Chat handling
        if message_body.lower() in ['ai chat', 'chat with ai', 'ai']:
            start_ai_chat(phone_number, user, conn)
            return

        # Quiz listing command
        if message_body.lower() in ['quiz', 'start quiz']:
            handle_quiz_command(phone_number, user, conn)
            return

        # Extract quiz number
        selected_quiz_input = message_body.lower().strip()
        quiz_number = ''.join(filter(str.isdigit, selected_quiz_input))
        if not quiz_number:
            send_message(phone_number, "Invalid quiz selection. Please choose a quiz number from the list.")
            handle_quiz_command(phone_number, user, conn)
            return

        selected_quiz = f"quiz{quiz_number}"

        # ✅ Check if the selected quiz is currently enabled (using database)
        if not is_quiz_enabled(selected_quiz, conn):
            send_message(phone_number, f"{selected_quiz} is currently unavailable. Please choose another quiz.")
            handle_quiz_command(phone_number, user, conn)
            return

        cursor = conn.cursor()

        # ✅ Check if the user is already working on a different quiz
        cursor.execute("""
            SELECT quiz FROM responses 
            WHERE user_id = ? 
            GROUP BY quiz 
            HAVING COUNT(*) < (SELECT COUNT(*) FROM questions WHERE quiz = responses.quiz)
        """, (user['id'],))
        in_progress_quizzes = [row[0] for row in cursor.fetchall()]

        if in_progress_quizzes and selected_quiz not in in_progress_quizzes:
            send_message(phone_number, f"You are already working on {in_progress_quizzes[0]}. Please complete it before starting {selected_quiz}.")
            return

        # ✅ Determine quiz status (not started, in progress, completed)
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN COUNT(*) = 0 THEN 'not_started'
                    WHEN COUNT(*) = (SELECT COUNT(*) FROM questions WHERE quiz = ?) THEN 'completed'
                    ELSE 'in_progress'
                END as status
            FROM responses 
            WHERE user_id = ? AND quiz = ?
        """, (selected_quiz, user['id'], selected_quiz))
        status = cursor.fetchone()[0]

        if status == 'completed':
            send_message(phone_number, f"You've already completed {selected_quiz}. Use 'AI Chat' to review incorrect answers or choose another quiz.")
            handle_quiz_command(phone_number, user, conn)
        else:
            start_or_resume_quiz(phone_number, user, conn, selected_quiz)

    except Exception as e:
        log_image_event(f"Error in handle_quiz_selection: {str(e)}")
        log_image_event(traceback.format_exc())
        send_message(phone_number, "An error occurred while selecting the quiz. Please try again.")
        present_options(phone_number, user, conn)
# def handle_quiz_selection(phone_number, message_body, user, conn):
#     log_image_event(f"Quiz selection initiated for {phone_number} with message: {message_body}")
   
#     try:
#         # Ensure the function only handles quiz commands
#         if message_body.lower() in ['start quiz', 'new quiz', 'review quiz']:
#             available_quizzes = list_available_quizzes()
#             selected_quiz = message_body.lower().replace(" ", "")
           
#             # Get quiz statuses and incorrect question counts
#             quiz_statuses = {
#                 f"quiz{quiz}": get_quiz_status(conn, user['id'], f"quiz{quiz}") for quiz in available_quizzes
#             }
#             incorrect_question_counts = {
#                 f"quiz{quiz}": len(get_incorrect_questions(user['id'], conn, f"quiz{quiz}")) for quiz in available_quizzes
#             }
           
#             # Handle new or continuing quiz selection
#             if selected_quiz in ["startnewquiz", "new_quiz"]:
#                 available_quizzes = [quiz for quiz, status in quiz_statuses.items() if status != "completed"]
#                 if available_quizzes:
#                     buttons = [
#                         {
#                             "type": "reply",
#                             "reply": {
#                                 "id": quiz,
#                                 "title": f"{'Continue' if quiz_statuses[quiz] == 'in_progress' else 'Start'} {quiz} ({incorrect_question_counts[quiz]} incorrect)"
#                             }
#                         } for quiz in available_quizzes[:3]  # WhatsApp limits to 3 buttons
#                     ]
#                     send_interactive_message(phone_number, "Choose a quiz to start or continue:", buttons)
#                 else:
#                     send_message(phone_number, "You have completed all available quizzes. Great job!")
#                     present_options(phone_number, user, conn)
#             else:
#                 quiz_number = ''.join(filter(str.isdigit, selected_quiz))
#                 selected_quiz = f"quiz{quiz_number}"
               
#                 if selected_quiz in quiz_statuses:
#                     status = quiz_statuses[selected_quiz]
#                     if status in ["in_progress", "not_started"]:
#                         start_or_resume_quiz(phone_number, user, conn, selected_quiz)
#                     else:
#                         send_message(phone_number, f"You've already completed {selected_quiz}. Choose another quiz or activity.")
#                         present_options(phone_number, user, conn)
#                 else:
#                     send_message(phone_number, "Invalid quiz selection. Please choose a quiz from the available options.")
#                     present_options(phone_number, user, conn)
#         else:
#             send_message(phone_number, "Invalid command. Please use a valid quiz command such as 'start quiz' or 'review quiz'.")
#             present_options(phone_number, user, conn)
   
#     except Exception as e:
#         log_image_event(f"Error in handle_quiz_selection: {str(e)}")
#         log_image_event(traceback.format_exc())
#         send_message(phone_number, "An error occurred while selecting the quiz. Please try again.")
#         present_options(phone_number, user, conn)

        
        

       
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


   
# def finish_quiz(phone_number, user, conn, current_quiz, num_questions):
#     try:
#         log_image_event(f"Finishing quiz {current_quiz} for user {user['id']}")
       
#         total_correct = conn.execute(
#             "SELECT COUNT(*) AS total_correct FROM responses WHERE user_id = ? AND quiz = ? AND correct = 1",
#             (user['id'], current_quiz)
#         ).fetchone()['total_correct']
       
#         congratulations_message = f"Congratulations! You've completed the quiz. You scored {total_correct} out of {num_questions} questions correctly."
#         send_message(phone_number, congratulations_message)
       
#         conn.execute("UPDATE users SET state='awaiting_choice', current_quiz='' WHERE phone_number=?", (phone_number,))
#         conn.execute("UPDATE quiz_states SET question_index = -1 WHERE user_id = ? AND quiz_name = ?",
#                      (user['id'], current_quiz))
#         conn.commit()
       
#         log_image_event(f"Database updated for user {user['id']} after finishing quiz {current_quiz}")
       
#         # Offer options to take another quiz or switch to records
#         buttons = [
#         {"type": "reply", "reply": {"id": "quiz", "title": "Take Another Quiz"}},
#         {"type": "reply", "reply": {"id": "records", "title": "Switch to Records"}},
#         {"type": "reply", "reply": {"id": "ai_chat", "title": "Review Mistakes (AI) "}}
#     ]
#         success = send_interactive_message(phone_number, "What would you like to do next?", buttons)

       
#         if not success:
#             log_image_event(f"Failed to send interactive message for user {user['id']} after quiz completion")
#             send_message(phone_number, "What would you like to do next? Type 'quiz' to take another quiz or 'records' to switch to record keeping.")
       
#         log_image_event(f"Quiz {current_quiz} finished successfully for user {user['id']}")
       
#     except Exception as e:
#         log_image_event(f"Error in finish_quiz for user {user['id']}: {str(e)}")
#         log_image_event(traceback.format_exc())
#         send_message(phone_number, "An error occurred while finishing the quiz. Please type 'quiz' to start over or 'records' to switch to record keeping.")
   
#     finally:
#         # Ensure the user's state is reset even if an error occurs
#         try:
#             conn.execute("UPDATE users SET state='awaiting_choice', current_quiz='' WHERE phone_number=?", (phone_number,))
#             conn.commit()
#         except Exception as e:
#             log_image_event(f"Error resetting user state in finish_quiz for user {user['id']}: {str(e)}")
           
         
         
         
         
def finish_quiz(phone_number, user, conn, current_quiz, num_questions):
    try:
        log_image_event(f"Finishing quiz {current_quiz} for user {user['id']}")

        # Extract numeric part of the quiz identifier and convert to integer
        try:
            quiz_number = int(current_quiz[4:])  # Assumes format is 'quizXX'
        except ValueError:
            quiz_number = 0

        total_correct = conn.execute(
            "SELECT COUNT(*) AS total_correct FROM responses WHERE user_id = ? AND quiz = ? AND correct = 1",
            (user['id'], current_quiz)
        ).fetchone()[0]

        if quiz_number <= 10:
            congratulations_message = f"Congratulations! You've completed the quiz. You scored {total_correct} out of {num_questions} questions correctly."
            send_message(phone_number, congratulations_message)
        else:
            # For quizzes numbered above 10, send a different message
            completion_message = f"You've finished the quiz."
            send_message(phone_number, completion_message)

        conn.execute("UPDATE users SET state='awaiting_choice', current_quiz='' WHERE phone_number=?", (phone_number,))
        conn.execute("UPDATE quiz_states SET question_index = -1 WHERE user_id = ? AND quiz_name = ?",
                     (user['id'], current_quiz))
        conn.commit()

        log_image_event(f"Database updated for user {user['id']} after finishing quiz {current_quiz}")

        # Offer options to take another quiz or switch to records
        buttons = [
            {"type": "reply", "reply": {"id": "quiz", "title": "Take Another Quiz"}},
            {"type": "reply", "reply": {"id": "records", "title": "Switch to Records"}},
            {"type": "reply", "reply": {"id": "ai_chat", "title": "Review Mistakes (AI)"}}
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
 
 
       
       

def send_interactive_message(phone_number, message, buttons=None, options=None):
    log_image_event(f"Preparing to send interactive message to {phone_number}")
    url = f"https://graph.facebook.com/v11.0/{YOUR_PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    
    try:
        if isinstance(message, dict) and 'type' in message and message['type'] == 'list':
            log_image_event(f"Preparing list message for {phone_number}")
            data = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "interactive",
                "interactive": message
            }
        else:
            log_image_event(f"Preparing button message for {phone_number}")
            if buttons is None:
                log_image_event(f"Error: Buttons are required for button type messages")
                return False, "Buttons are required for button type messages"
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
        
        log_image_event(f"Sending request to WhatsApp API for {phone_number}")
        log_image_event(f"Request data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, headers=headers, json=data)
        log_image_event(f"Received response from WhatsApp API for {phone_number} - Status: {response.status_code}")
        log_image_event(f"Response content: {response.text}")
       
        if response.status_code != 200:
            log_image_event(f"Error sending interactive message to {phone_number}. Status code: {response.status_code}")
            return False, f"Failed to send interactive message. Status code: {response.status_code}"
        
        log_image_event(f"Successfully sent interactive message to {phone_number}")
        return True, "Message sent successfully"
    
    except Exception as e:
        log_image_event(f"Exception in send_interactive_message for {phone_number}: {str(e)}")
        log_image_event(f"Full exception traceback: {traceback.format_exc()}")
        return False, f"Exception occurred: {str(e)}"
      
      

      
# def send_interactive_message(phone_number, message, buttons=None, options=None):
#     log_image_event(f"Debug: send_interactive_message called for {phone_number}")
#     log_image_event(f"Debug: message = {message}")
    
#     # URL and headers setup for WhatsApp API
#     url = f"https://graph.facebook.com/v11.0/{YOUR_PHONE_NUMBER_ID}/messages"
#     headers = {
#         "Authorization": f"Bearer {WHATSAPP_TOKEN}",
#         "Content-Type": "application/json"
#     }

#     try:
#         # Handle button-type or list-type messages
#         if options and isinstance(options, list):
#             if len(options) > 3:
#                 return False, "Maximum of 3 buttons allowed per message"
#             buttons = [{"type": "reply", "reply": {"id": opt["id"], "title": opt["title"]}} for opt in options]
        
#         data = {
#             "messaging_product": "whatsapp",
#             "recipient_type": "individual",
#             "to": phone_number,
#             "type": "interactive",
#             "interactive": {
#                 "type": "button",
#                 "body": {
#                     "text": message
#                 },
#                 "action": {
#                     "buttons": buttons
#                 }
#             }
#         }
        
#         log_image_event(f"Debug: Final request data: {json.dumps(data, indent=2)}")
#         response = requests.post(url, headers=headers, json=data)
        
#         log_image_event(f"Response Status: {response.status_code}")
#         log_image_event(f"Response Content: {response.text}")

#         if response.status_code != 200:
#             return False, f"Error sending message: {response.status_code}"
#         return True, "Message sent successfully"

#     except Exception as e:
#         log_image_event(f"Exception: {str(e)}")
#         return False, f"Exception occurred: {str(e)}"
      
      
# def handle_quiz_response(phone_number, response, user, conn):
#     log_image_event(f"Handling quiz response for {phone_number}: {response}")
   
#     if response.lower().strip() == 'settings123':
#         handle_settings_command(phone_number, user, conn)
#         return

#     current_quiz = user['current_quiz']
#     if not current_quiz:
#         log_image_event(f"No current quiz for user {phone_number}")
#         send_message(phone_number, "No active quiz. Type 'quiz' to start a new quiz.")
#         return

#     try:
#         quiz_data = load_quiz_data(current_quiz)
#         if not quiz_data:
#             raise Exception(f"Quiz {current_quiz} not found")
#         QUIZ_QUESTIONS = quiz_data['questions']
#     except Exception as e:
#         log_image_event(f"Error loading quiz data for {current_quiz}: {str(e)}")
#         send_message(phone_number, "There was an error with the quiz. Please type 'quiz' to start over.")
#         conn.execute("UPDATE users SET state = 'awaiting_choice', current_quiz = '' WHERE phone_number = ?", (phone_number,))
#         conn.commit()
#         return

#     state = user['state']
#     question_index = int(state.split('_')[1])
#     question_number = question_index + 1

#     if question_index < len(QUIZ_QUESTIONS):
#         current_question = QUIZ_QUESTIONS[question_index]
#         correct_answer = current_question['answer'].lower().strip()
#         user_response = response.lower().strip()
#         is_correct = user_response == correct_answer
#         log_image_event(f"User {user['id']} answered question {question_number} {'correctly' if is_correct else 'incorrectly'}")

#         conn.execute(
#           "INSERT INTO responses (user_id, question_number, response, correct, quiz) VALUES (?, ?, ?, ?, ?)",
#           (user['id'], question_number, response, int(is_correct), current_quiz)
#            )
#         log_image_event(f"Inserted response for user {user['id']}: question {question_number}, correct={int(is_correct)}, quiz={current_quiz}")


#         feedback = "Correct!" if is_correct else f"Wrong! The correct answer was {correct_answer.upper()}."
#         send_message(phone_number, feedback)

#         question_index += 1
#         log_image_event(f"Moving to next question. New index: {question_index}")

#         if question_index < len(QUIZ_QUESTIONS):
#             conn.execute("UPDATE users SET state = ? WHERE phone_number = ?", (f'quiz_{question_index}', phone_number))
#             conn.execute("UPDATE quiz_states SET question_index = ? WHERE user_id = ? AND quiz_name = ?",
#                          (question_index, user['id'], current_quiz))
#             conn.commit()
#             send_quiz_question(phone_number, question_index, conn, current_quiz)
#         else:
#             try:
#                 finish_quiz(phone_number, user, conn, current_quiz, len(QUIZ_QUESTIONS))
#             except Exception as e:
#                 log_image_event(f"Error in finish_quiz called from handle_quiz_response: {str(e)}")
#                 log_image_event(traceback.format_exc())
#                 send_message(phone_number, "An error occurred while finishing the quiz. Please type 'quiz' to start over or 'records' to switch to record keeping.")
#     else:
#         send_message(phone_number, "Invalid question number. Type 'quiz' to start a new quiz.")
#         conn.execute("UPDATE users SET state = 'awaiting_choice', current_quiz = '' WHERE phone_number = ?", (phone_number,))
#         conn.commit()
       
       
 
 
 
 
def load_quiz_data(quiz_name):
    try:
        with open(f'data_bootcamp/{quiz_name}.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Quiz file {quiz_name}.json not found")
        return None
     
     
      
def handle_quiz_response(phone_number, response, user, conn):
    log_image_event(f"Handling quiz response for {phone_number}: {response}")
    if response.lower().strip() == 'settings':
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
    # Extract the numeric part of the quiz identifier to determine its number
    quiz_number = int(current_quiz[4:]) if current_quiz.startswith('quiz') else 0

    if question_index < len(QUIZ_QUESTIONS):
        current_question = QUIZ_QUESTIONS[question_index]
        correct_answer = current_question['answer'].lower().strip()
        user_response = response.lower().strip()

        # Check if the quiz number is 10 or below
        if quiz_number <= 10:
            is_correct = user_response == correct_answer
            log_image_event(f"User {user['id']} answered question {question_number} {'correctly' if is_correct else 'incorrectly'}")
            conn.execute(
              "INSERT INTO responses (user_id, question_number, response, correct, quiz) VALUES (?, ?, ?, ?, ?)",
              (user['id'], question_number, response, int(is_correct), current_quiz)
            )
            log_image_event(f"Inserted response for user {user['id']}: question {question_number}, correct={int(is_correct)}, quiz={current_quiz}")
            feedback = "Correct!" if is_correct else f"Wrong! The correct answer was {correct_answer.upper()}."
            send_message(phone_number, feedback)
        else:
            # For quizzes numbered 11 and above
            cursor = conn.cursor()
           
            # Check if a quiz entry exists for this user and quiz number
            cursor.execute("SELECT id FROM post10_quizzes WHERE user_id = ? AND quiz_number = ?",
                           (user['id'], quiz_number))
            quiz_entry = cursor.fetchone()
           
            if not quiz_entry:
                # Create a new quiz entry if it doesn't exist
                cursor.execute("INSERT INTO post10_quizzes (user_id, quiz_number) VALUES (?, ?)",
                               (user['id'], quiz_number))
                quiz_id = cursor.lastrowid
            else:
                quiz_id = quiz_entry[0]
           
            # Insert the response
            cursor.execute("INSERT INTO post10_quiz_responses (quiz_id, question_number, response) VALUES (?, ?, ?)",
                           (quiz_id, question_number, response))
           
            conn.commit()
            send_message(phone_number, "Your response has been recorded.")

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
       
       

        
        
        
        
        
        
        
        
        
        
        
        

def check_database_integrity():
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
       
        # Check for questions with missing fields
        cursor.execute("""
        SELECT id, quiz, question, options, answer
        FROM questions
        WHERE question IS NULL OR options IS NULL OR answer IS NULL
        """)
       
        invalid_questions = cursor.fetchall()
       
        if invalid_questions:
            logging.warning(f"Found {len(invalid_questions)} questions with missing data:")
            for q in invalid_questions:
                logging.warning(f"Invalid question: {q}")
        else:
            logging.info("All questions in the database have the required fields.")
       
        # Check for responses without corresponding questions
        cursor.execute("""
        SELECT r.id, r.quiz, r.question_number
        FROM responses r
        LEFT JOIN questions q ON q.quiz = r.quiz AND q.id = r.question_number
        WHERE q.id IS NULL
        """)
       
        orphaned_responses = cursor.fetchall()
       
        if orphaned_responses:
            logging.warning(f"Found {len(orphaned_responses)} responses without corresponding questions:")
            for r in orphaned_responses:
                logging.warning(f"Orphaned response: {r}")
        else:
            logging.info("All responses have corresponding questions in the database.")

    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
    finally:
        if conn:
            conn.close()



       
       
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
   


  
def send_message(phone_number, message, is_ai=False):
    url = f"https://graph.facebook.com/v11.0/{YOUR_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "text": {"body": message}
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raises an error for 4xx/5xx responses
        logging.info(f"Sent {'AI' if is_ai else 'user-generated'} message to {phone_number}: {message} - Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending message to {phone_number}: {e}")

   
  
  

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

@app.route('/users_bootcamp')
def users():
    conn = get_db_connection()
    try:
        users = conn.execute("SELECT id, phone_number, name, random_number FROM users").fetchall()
        return render_template('users_bootcamp.html', users=users)
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

# @app.route('/scoreboardbootcamp')
# def scoreboardbootcamp():
#     conn = get_db_connection()
#     try:
#         pass_percentage = request.args.get('pass_percentage', 60, type=int)
#         min_quizzes = request.args.get('min_quizzes', 1, type=int)

#         users = conn.execute("SELECT id, phone_number, name FROM users").fetchall()

#         quiz_ranges = ['all', '1-5', '6-10']
#         user_scores = []

#         for user in users:
#             try:
#                 score_dict = {
#                     'id': user['id'],
#                     'name': user['name'],
#                     'phone_number': user['phone_number'],
#                     'all': {},
#                     '1-5': {},
#                     '6-10': {}
#                 }
               
#                 for range_key in quiz_ranges:
#                     if range_key == 'all':
#                         condition = "1=1"
#                     elif range_key == '1-5':
#                         condition = "quiz IN ('quiz1', 'quiz2', 'quiz3', 'quiz4', 'quiz5')"
#                     else:  # '6-10'
#                         condition = "quiz IN ('quiz6', 'quiz7', 'quiz8', 'quiz9', 'quiz10')"
                   
#                     results = conn.execute(f"""
#                         SELECT
#                             SUM(CASE WHEN correct = 1 THEN 1 ELSE 0 END) as total_correct_answers,
#                             COUNT(*) as total_questions_attempted,
#                             COUNT(DISTINCT quiz) as quizzes_taken,
#                             MAX(upload_date) as last_quiz_date,
#                             GROUP_CONCAT(DISTINCT quiz) as attempted_quizzes
#                         FROM responses
#                         WHERE user_id = ? AND {condition}
#                     """, (user['id'],)).fetchone()

#                     attempted_quizzes = results['attempted_quizzes'].split(',') if results['attempted_quizzes'] else []
                   
#                     if attempted_quizzes:
#                         attempted_quizzes_condition = f"quiz IN ({','.join(['?']*len(attempted_quizzes))})"
#                         total_possible = conn.execute(f"SELECT COUNT(DISTINCT question) FROM questions WHERE {attempted_quizzes_condition}", attempted_quizzes).fetchone()[0]
#                     else:
#                         total_possible = 0

#                     score_dict[range_key] = {
#                         'total_correct_answers': int(results['total_correct_answers'] or 0),
#                         'total_questions_attempted': int(results['total_questions_attempted'] or 0),
#                         'quizzes_taken': int(results['quizzes_taken'] or 0),
#                         'total_possible': total_possible,
#                         'last_quiz_date': results['last_quiz_date'] if results['last_quiz_date'] else 'N/A'
#                     }

#                     if score_dict[range_key]['total_questions_attempted'] > 0 and total_possible > 0:
#                         score_dict[range_key]['percentage'] = (score_dict[range_key]['total_correct_answers'] / total_possible) * 100
#                         score_dict[range_key]['pass_fail'] = 'Pass' if score_dict[range_key]['percentage'] >= pass_percentage and score_dict[range_key]['quizzes_taken'] >= min_quizzes else 'Fail'
#                     else:
#                         score_dict[range_key]['percentage'] = 0
#                         score_dict[range_key]['pass_fail'] = 'N/A'

#                 additional_data = conn.execute("""
#                     SELECT
#                         MAX(records.upload_date) as last_image_date,
#                         COUNT(DISTINCT records.id) as images_uploaded,
#                         COUNT(DISTINCT DATE(records.upload_date)) as unique_upload_days
#                     FROM records
#                     WHERE user_id = ?
#                 """, (user['id'],)).fetchone()

#                 score_dict.update({
#                     'last_image_date': additional_data['last_image_date'] if additional_data['last_image_date'] else 'N/A',
#                     'images_uploaded': additional_data['images_uploaded'] or 0,
#                     'unique_upload_days': additional_data['unique_upload_days'] or 0
#                 })

#                 user_scores.append(score_dict)

#             except Exception as user_error:
#                 app.logger.error(f"Error processing user {user['id']}: {str(user_error)}")

#         user_scores.sort(key=lambda x: x['all']['percentage'], reverse=True)

#         if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#             return jsonify({
#                 'scores': user_scores,
#                 'pass_percentage': pass_percentage,
#                 'min_quizzes': min_quizzes
#             })
#         else:
#             print("User Scores:", user_scores)  # Debugging line
#             return render_template('scoreboardbootcamp.html',
#                                    scores=user_scores,
#                                    pass_percentage=pass_percentage,
#                                    min_quizzes=min_quizzes)

#     except Exception as e:
#         app.logger.error(f"An error occurred in scoreboard route: {str(e)}")
#         if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#             return jsonify({'error': str(e)}), 500
#         else:
#             return f"An error occurred while loading the scoreboard: {str(e)}", 500

#     finally:
#         conn.close()
       
       


@app.route('/scoreboardbootcamp')
def scoreboardbootcamp():
    conn = get_db_connection()
    try:
        pass_percentage = request.args.get('pass_percentage', 60, type=int)
        min_quizzes = request.args.get('min_quizzes', 1, type=int)
        selected_location = request.args.get('location', 'all')

        # Get all available quizzes - NOW UNIFIED IN ONE TABLE
        available_quizzes = conn.execute("""
            SELECT DISTINCT quiz FROM responses 
            WHERE quiz IS NOT NULL AND quiz != '' 
            ORDER BY CAST(SUBSTR(quiz, 5) AS INTEGER)
        """).fetchall()
        
        # Also get quizzes from questions table (in case some haven't been attempted yet)
        questions_quizzes = conn.execute("""
            SELECT DISTINCT quiz FROM questions 
            WHERE quiz IS NOT NULL AND quiz != '' 
            ORDER BY CAST(SUBSTR(quiz, 5) AS INTEGER)
        """).fetchall()
        
        # Combine and deduplicate
        all_quiz_names = list(set([quiz['quiz'] for quiz in available_quizzes] + 
                                 [quiz['quiz'] for quiz in questions_quizzes]))
        all_quiz_names.sort(key=lambda x: int(x.replace('quiz', '')))
        
        # Extract quiz numbers for creating ranges
        quiz_numbers = []
        for quiz in all_quiz_names:
            match = re.search(r'quiz(\d+)', quiz)
            if match:
                quiz_numbers.append(int(match.group(1)))
        
        quiz_numbers = sorted(list(set(quiz_numbers)))
        app.logger.info(f"Available unified quiz numbers: {quiz_numbers}")
        
        # Create dynamic ranges based on available quizzes
        def create_quiz_ranges(quiz_nums):
            if not quiz_nums:
                return ['all']
            
            ranges = ['all']
            max_quiz = max(quiz_nums)
            
            # Create ranges in groups of 5
            current_start = 1
            while current_start <= max_quiz:
                end = min(current_start + 4, max_quiz)
                
                # Check if any quizzes exist in this range
                range_has_quizzes = any(current_start <= num <= end for num in quiz_nums)
                
                if range_has_quizzes:
                    ranges.append(f"{current_start}-{end}")
                
                current_start += 5
            
            return ranges
        
        quiz_ranges = create_quiz_ranges(quiz_numbers)

        # Get users with location filter
        if selected_location.lower() != 'all':
            users = conn.execute("SELECT id, phone_number, name, TRIM(location) as location FROM users WHERE TRIM(location) = ?", (selected_location,)).fetchall()
        else:
            users = conn.execute("SELECT id, phone_number, name, TRIM(location) as location FROM users").fetchall()

        locations = get_locations()
        user_scores = []

        for user in users:
            try:
                score_dict = {
                    'id': user['id'],
                    'name': user['name'],
                    'phone_number': user['phone_number'],
                    'location': user['location'] if user['location'] else 'Unknown'
                }
                
                # Initialize all ranges in score_dict
                for range_key in quiz_ranges:
                    score_dict[range_key] = {}

                for range_key in quiz_ranges:
                    if range_key == 'all':
                        # Get ALL quiz results from unified responses table
                        results = conn.execute("""
                            SELECT
                                SUM(CASE WHEN correct = 1 THEN 1 ELSE 0 END) as total_correct_answers,
                                COUNT(*) as total_questions_attempted,
                                COUNT(DISTINCT quiz) as quizzes_taken,
                                MAX(timestamp) as last_quiz_date,
                                GROUP_CONCAT(DISTINCT quiz) as attempted_quizzes
                            FROM responses
                            WHERE user_id = ?
                        """, (user['id'],)).fetchone()
                        
                        total_correct = results['total_correct_answers'] or 0
                        total_attempted = results['total_questions_attempted'] or 0
                        total_quizzes = results['quizzes_taken'] or 0
                        last_date = results['last_quiz_date'] or 'N/A'
                        
                        # Calculate total possible questions for all attempted quizzes
                        total_possible = 0
                        if results['attempted_quizzes']:
                            attempted_quiz_list = results['attempted_quizzes'].split(',')
                            quiz_placeholders = ', '.join(['?' for _ in attempted_quiz_list])
                            quiz_questions = conn.execute(f"""
                                SELECT quiz, COUNT(DISTINCT question) as question_count 
                                FROM questions 
                                WHERE quiz IN ({quiz_placeholders})
                                GROUP BY quiz
                            """, attempted_quiz_list).fetchall()
                            total_possible = sum(row['question_count'] for row in quiz_questions)
                        
                    else:
                        # Parse range (e.g., "1-5" -> quizzes 1,2,3,4,5)
                        start, end = map(int, range_key.split('-'))
                        
                        # Get quiz names in this range that actually exist
                        range_quiz_names = [f'quiz{i}' for i in range(start, end+1) if i in quiz_numbers]
                        
                        if not range_quiz_names:
                            # No quizzes in this range
                            score_dict[range_key] = {
                                'total_correct_answers': 0,
                                'total_questions_attempted': 0,
                                'quizzes_taken': 0,
                                'total_possible': 0,
                                'last_quiz_date': 'N/A',
                                'percentage': 0,
                                'pass_fail': 'N/A'
                            }
                            continue
                        
                        # Get results for this range from unified responses table
                        placeholders = ', '.join(['?' for _ in range_quiz_names])
                        results = conn.execute(f"""
                            SELECT
                                SUM(CASE WHEN correct = 1 THEN 1 ELSE 0 END) as total_correct_answers,
                                COUNT(*) as total_questions_attempted,
                                COUNT(DISTINCT quiz) as quizzes_taken,
                                MAX(timestamp) as last_quiz_date,
                                GROUP_CONCAT(DISTINCT quiz) as attempted_quizzes
                            FROM responses
                            WHERE user_id = ? AND quiz IN ({placeholders})
                        """, [user['id']] + range_quiz_names).fetchone()
                        
                        total_correct = results['total_correct_answers'] or 0
                        total_attempted = results['total_questions_attempted'] or 0
                        total_quizzes = results['quizzes_taken'] or 0
                        last_date = results['last_quiz_date'] or 'N/A'
                        
                        # Calculate total possible for this range
                        total_possible = 0
                        if results['attempted_quizzes']:
                            attempted_quiz_list = results['attempted_quizzes'].split(',')
                            quiz_placeholders = ', '.join(['?' for _ in attempted_quiz_list])
                            quiz_questions = conn.execute(f"""
                                SELECT quiz, COUNT(DISTINCT question) as question_count 
                                FROM questions 
                                WHERE quiz IN ({quiz_placeholders})
                                GROUP BY quiz
                            """, attempted_quiz_list).fetchall()
                            total_possible = sum(row['question_count'] for row in quiz_questions)

                    # Store results for this range
                    score_dict[range_key] = {
                        'total_correct_answers': int(total_correct),
                        'total_questions_attempted': int(total_attempted),
                        'quizzes_taken': int(total_quizzes),
                        'total_possible': total_possible,
                        'last_quiz_date': last_date
                    }

                    # Calculate percentage and pass/fail
                    if total_attempted > 0 and total_possible > 0:
                        percentage = (total_correct / total_possible) * 100
                        score_dict[range_key]['percentage'] = percentage
                        score_dict[range_key]['pass_fail'] = 'Pass' if percentage >= pass_percentage and total_quizzes >= min_quizzes else 'Fail'
                    else:
                        score_dict[range_key]['percentage'] = 0
                        score_dict[range_key]['pass_fail'] = 'N/A'

                # Get additional user data (images) - this stays the same
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

        # Sort by 'all' percentage
        user_scores.sort(key=lambda x: x['all']['percentage'], reverse=True)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'scores': user_scores,
                'pass_percentage': pass_percentage,
                'min_quizzes': min_quizzes,
                'locations': locations,
                'selected_location': selected_location,
                'quiz_ranges': quiz_ranges,
                'available_quizzes': all_quiz_names,
                'debug_info': {
                    'quiz_numbers': quiz_numbers,
                    'max_quiz': max(quiz_numbers) if quiz_numbers else 0,
                    'total_available_quizzes': len(all_quiz_names),
                    'unified_system': True
                }
            })
        else:
            return render_template('scoreboardbootcamp.html',
                                   scores=user_scores,
                                   pass_percentage=pass_percentage,
                                   min_quizzes=min_quizzes,
                                   locations=locations,
                                   selected_location=selected_location,
                                   quiz_ranges=quiz_ranges,
                                   available_quizzes=all_quiz_names)

    except Exception as e:
        app.logger.error(f"An error occurred in scoreboard route: {str(e)}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': str(e)}), 500
        else:
            return f"An error occurred while loading the scoreboard: {str(e)}", 500

    finally:
        conn.close()
        
        
        
# # Function to fetch user data from the database
# def get_users():
#     conn = sqlite3.connect('user_data_bootcamp.db')
#     conn.row_factory = sqlite3.Row  # Allows dictionary-like row access
#     c = conn.cursor()
#     c.execute("SELECT * FROM users")
#     users = c.fetchall()
#     conn.close()
#     return users

# @app.route('/')
# def home():
#     return "<h2>Welcome to the User Dashboard</h2><p>Go to <a href='/userdashboard'>User Dashboard</a></p>"

# @app.route('/userdashboard')
# def userdashboard():
#     users = get_users()
#     return render_template('userdashboard.html', users=users)


# Fetch all users from the database
def get_users(location_filter=None):
    conn = sqlite3.connect('user_data_bootcamp.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if location_filter and location_filter.lower() != 'all':
        c.execute("SELECT * FROM users WHERE TRIM(location) = ?", (location_filter,))
    else:
        c.execute("SELECT * FROM users")

    users = c.fetchall()
    conn.close()
    return users

# Fetch distinct, non-empty locations for the filter dropdown
def get_locations():
    conn = sqlite3.connect('user_data_bootcamp.db')
    c = conn.cursor()
    c.execute("SELECT DISTINCT TRIM(location) FROM users WHERE location IS NOT NULL AND location != ''")
    locations_raw = c.fetchall()
    conn.close()

    # Clean and sort locations, filter out empty or None values
    locations = sorted(set([loc[0] for loc in locations_raw if loc[0] and loc[0].strip() != '']))
    return locations

@app.route('/userdashboard')
def userdashboard():
    # Optional: you can get a query param if you want server-side filtering
    selected_location = request.args.get('location', 'all')
    
    users = get_users(selected_location)
    locations = get_locations()
    return render_template('userdashboard.html', users=users, locations=locations)
  
  
  
    
    
    
  
       
def handle_token_error(error_data):
    error = error_data.get('error', {})
    message = error.get('message', 'Unknown error')
    error_type = error.get('type')
    code = error.get('code')
    subcode = error.get('error_subcode')
    logging.error(f"Token error: {message}, Type: {error_type}, Code: {code}, Subcode: {subcode}")

    
    
    
    
    
    

# def send_daily_summary():
#     conn = sqlite3.connect(db_file)
#     cursor = conn.cursor()

#     # Get all users
#     cursor.execute("SELECT id, phone_number FROM users")
#     users = cursor.fetchall()

#     for user_id, phone_number in users:
#         # Get today's conversation history
#         today = datetime.now().date()
#         cursor.execute("""
#             SELECT message, is_ai FROM conversation_history 
#             WHERE user_id = ? AND date(timestamp) = ?
#             ORDER BY timestamp
#         """, (user_id, today))
#         conversations = cursor.fetchall()

#         if conversations:
#             # Summarize conversations
#             summary = summarize_conversations(conversations)
            
#             # Generate AI insights
#             ai_insights = generate_ai_insights(conversations)
            
#             message = f"Here's your daily summary:\n\n{summary}\n\nAI Insights:\n{ai_insights}"
#         else:
#             # Generate generic message
#             message = generate_generic_message(user_id, conn)

#         # Send message using WhatsApp
#         send_message(phone_number, message, is_ai=True)

#     conn.close()


import sqlite3
import logging
from datetime import datetime
from collections import defaultdict
from collections import Counter
import re

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to summarize conversations

def summarize_conversations(conversations):
    user_messages = [msg for msg, is_ai in conversations if not is_ai]
    ai_messages = [msg for msg, is_ai in conversations if is_ai]
    
    # Count messages
    user_msg_count = len(user_messages)
    ai_msg_count = len(ai_messages)
    
    # Analyze topics
    all_words = ' '.join(user_messages).lower()
    words = re.findall(r'\b\w+\b', all_words)
    word_freq = Counter(words)
    common_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
    topics = [word for word, count in word_freq.most_common(5) if word not in common_words and len(word) > 3]
    
    # Analyze question types
    question_types = Counter(re.findall(r'\b(who|what|when|where|why|how)\b', all_words))
    most_common_question = question_types.most_common(1)[0] if question_types else None
    
    summary = f"Today you exchanged {user_msg_count} messages and received {ai_msg_count} AI responses. "
    summary += f"Main topics discussed: {', '.join(topics)}. "
    if most_common_question:
        summary += f"You frequently asked '{most_common_question[0]}' questions. "
    
    return summary

  
  

def send_daily_summary():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        test_phone_number = '2348169686473'
        
        logging.info(f"Attempting to send daily summary to {test_phone_number}")
        cursor.execute("SELECT id FROM users WHERE phone_number = ?", (test_phone_number,))
        user = cursor.fetchone()
        if user:
            user_id = user[0]
            logging.info(f"User ID found: {user_id}")
            
            today = datetime.now().date()
            logging.info(f"Fetching conversations for date: {today}")
            cursor.execute("""
                SELECT message, is_ai FROM conversation_history 
                WHERE user_id = ? AND date(timestamp) = ?
                ORDER BY timestamp
            """, (user_id, today))
            conversations = cursor.fetchall()
            logging.info(f"Number of conversations fetched: {len(conversations)}")
            logging.info(f"Sample of conversations: {conversations[:5]}")  # Log first 5 conversations
            
            if conversations:
                logging.info("Generating summary and insights")
                summary = summarize_conversations(conversations)
                ai_insights = generate_ai_insights(conversations, cursor, user_id)
                message = f"Here's your daily summary:\n\n{summary}\n\nAI Insights:\n{ai_insights}"
                logging.info(f"Generated summary: {summary}")
                logging.info(f"Generated insights: {ai_insights}")
            else:
                logging.info("No conversations found for today, generating generic message")
                message = generate_generic_message(user_id, conn)
            
            logging.info(f"Preparing to send message: {message[:100]}...")  # Log first 100 characters of the message
            try:
                send_message(test_phone_number, message, is_ai=True)
                logging.info("Message sent successfully via send_message function")
                
                # Present options after sending the daily summary
                present_options(test_phone_number, user, conn)
            except Exception as e:
                logging.error(f"Error in send_message function: {e}", exc_info=True)
        else:
            logging.error(f"No user found for phone number: {test_phone_number}")
    except sqlite3.Error as e:
        logging.error(f"Database error in send_daily_summary: {e}")
    except Exception as e:
        logging.error(f"Unexpected error in send_daily_summary: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()
        logging.info("send_daily_summary function finished execution")
        
        
        
        
  


def generate_ai_insights(conversations, cursor, user_id):
    # Fetch user information from the database
    cursor.execute("""
        SELECT name, age, gender, business_type, location, business_size, 
               financial_status, main_challenge, record_keeping, growth_goal, 
               funding_need
        FROM users
        WHERE id = ?
    """, (user_id,))
    user = cursor.fetchone()
    
    if not user:
        logging.error(f"User information not found for user_id: {user_id}")
        return "Unable to generate insights due to missing user information."

    user_info = {
        "name": user[0], "age": user[1], "gender": user[2],
        "business_type": user[3], "location": user[4], "business_size": user[5],
        "financial_status": user[6], "main_challenge": user[7], "record_keeping": user[8],
        "growth_goal": user[9], "funding_need": user[10]
    }

    user_messages = [msg for msg, is_ai in conversations if not is_ai]
    ai_responses = [msg for msg, is_ai in conversations if is_ai]
    
    context = {
        "user_message_count": len(user_messages),
        "ai_response_count": len(ai_responses),
        "sample_user_messages": user_messages[:5],
        "sample_ai_responses": ai_responses[:5],
    }
    
    prompt = f"""
    Based on the following conversation summary, generate insightful, actionable and personalized daily insights for the user:

    Context:
    {json.dumps(context, indent=2)}

    User Information:
    {json.dumps(user_info, indent=2)}

    Please provide insights not more than 50 words that include:
    - Start with the top 2 lessons that was learned by the user in 2 statements, with specific actionable examples of what was learned
    - Be a bit dramatic and make it more fun and show excitement, action and curiosity
    - Use very simple Nigerian English and sometimes pidgin English and contents related to Nigeria culture in the fun part
    - Highly specific, referencing actual content and actionable solutions from the conversation
    - Encouraging, highlighting positive aspects of the user's engagement
    - Concise, with each actionable insight being no more than 20 words
    - Personalized to the user's conversation patterns. Use first person singular (like "You have...")
    - Highlight interesting aspects of their AI interactions
    - Include emojis and icons

    Provide highly tailored advice in these three areas:

    1. Cost Efficiency and Resource Management 
    2. Revenue Growth and Customer Acquisition
    3. Business Optimization

    For each piece of advice:
    1. Make it easy to understand and do for a business with 0-1 employees.
    2. Directly relate it to {user_info['name']}'s {user_info['business_type']}.
    3. Address their main challenge ({user_info['main_challenge']}) and support their growth goal ({user_info['growth_goal']}).
    4. Use realistic examples with Naira amounts that make sense for small businesses in {user_info['location']}.
    5. Consider their current financial status ({user_info['financial_status']}) and funding need ({user_info['funding_need']}).

    Format the insights as a bullet-point list.
    """
    
    try:
        ai_generated_insights = generate_text(prompt)
        logging.info(f"AI-generated insights: {ai_generated_insights}")
        
        insights = f"Based on your interactions with our AI, here are some key insights for {user_info['name']}:\n\n"
        insights += ai_generated_insights
        
        if insights.count('\n') < 4:
            insights += "\n• Remember, I'm here to help you learn and grow your business. Don't hesitate to ask questions!"
        
        return insights
    
    except Exception as e:
        logging.error(f"Error in generate_ai_insights: {e}")
        return "I apologize, but I'm having difficulty generating insights at the moment. Please check your conversation history for highlights of your interactions."
      
      
      
    
def generate_generic_message(user_id, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT age, gender, business_type FROM users WHERE id = ?", (user_id,))
    user_data = cursor.fetchone()
    
    if not user_data:
        return "Hello! Why not ask our AI about some interesting topics tomorrow?"
    
    age, gender, business_type = user_data

    # Get the most common topics discussed by similar users
    cursor.execute("""
        SELECT message FROM conversation_history 
        WHERE user_id IN (SELECT id FROM users WHERE business_type = ? AND age BETWEEN ? AND ?)
        AND is_ai = 0
        ORDER BY timestamp DESC
        LIMIT 100
    """, (business_type, age - 5, age + 5))
    
    recent_messages = cursor.fetchall()
    topics = defaultdict(int)
    for (message,) in recent_messages:
        words = message.lower().split()
        for word in words:
            if len(word) > 5:
                topics[word] += 1
    
    common_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:3]
    
    return f"Hello! Users like you ({age} years old, {gender}, in the {business_type} business) often discuss topics like {', '.join(topic for topic, _ in common_topics)}. Why not ask our AI about these topics tomorrow?"


  # Your existing send_message function here

# Schedule the daily summary to run at 6 PM
# schedule.every().day.at("18:00").do(send_daily_summary)

# Function to run the scheduler
# def run_scheduler():
#     while True:
#         schedule.run_pending()
#         time.sleep(60)  # Check every minute

# You can start the scheduler in a separate thread or process
# import threading
# threading.Thread(target=run_scheduler, daemon=True).start()


if __name__ == '__main__':
    print("Initializing database...")
    init_db()
   
    print("Populating database with quiz data...")
    populate_database_from_json_files()
    
    
    #send_daily_summary()
    #start_keep_alive()
    print("Starting Flask app...")
    app.run(port=5000, debug=True)
