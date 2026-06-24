import os
import logging
import base64



from dotenv import load_dotenv
load_dotenv()

from db_adapter import db, USE_MONGODB





# Configure logging FIRST (beforee any other imports that might use it)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Decode base64 and save as a temp file
b64_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_B64")
if b64_creds:
    creds_path = "/tmp/google_creds.json"
    with open(creds_path, "wb") as f:
        f.write(base64.b64decode(b64_creds))
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
else:
    logger.warning("GOOGLE_APPLICATION_CREDENTIALS_B64 not found in environment")

# Load environment variables EARLY
from dotenv import load_dotenv
load_dotenv()

# CRITICAL: Load Gemini API key AFTER load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not found in environment variables!")

# Now import everything else
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
from collections import defaultdict, Counter
from contextlib import contextmanager
from flask import Flask, request, render_template, jsonify, send_from_directory, Response
from functools import lru_cache
from logging.handlers import RotatingFileHandler
from rapidfuzz import fuzz, process
import pytz
import schedule
from werkzeug.utils import secure_filename
import traceback

# Initialize Flask app
app = Flask(__name__)

# Load environment variables for Flask config
WHATSAPP_TOKEN = os.getenv('GRAPH_API_TOKEN')
WEBHOOK_VERIFY_TOKEN = os.getenv('WEBHOOK_VERIFY_TOKEN')
YOUR_PHONE_NUMBER_ID = os.getenv('YOUR_PHONE_NUMBER_ID')
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')

# Configure Flask app
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure rotating file handler for app logger
log_file = 'app.log'
log_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024 * 5, backupCount=5)
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)
app.logger.addHandler(log_handler)
app.logger.setLevel(logging.INFO)






# Simple ping endpoint
@app.route('/ping')
def ping():
    return 'OK'


def keep_alive():
    while True:
        try:
            requests.get('https://empowerbot2025-1.onrender.com/ping')
            print("Ping successful")
        except Exception as e:
            print(f"Ping failed: {str(e)}")
        
        # Wait 4 minutes before next ping
        time.sleep(240)  # 240 seconds = 4 minutes

# Start the keeep-alive thread when your app starts
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
                    
                    {"id": "agege", "title": "Agege"},
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






# def delete_git_folder():
#     while True:
#         # Check if the .git directory exists
#         if os.path.exists('.git'):
#             shutil.rmtree('.git')  # Remove the .git directory
#             print('.git folder deleted successfully.')
#         else:
#             print('.git folder does not exist.')
# 
#         # Wait for 15 minutes (15 * 60 seconds)
#         time.sleep(15 * 60)
# 
# # Start the deletion thread
# thread = threading.Thread(target=delete_git_folder)
# thread.daemon = True  # This makes the thread exit when the main program exits
# thread.start()








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
 
       
       

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
WHATSAPP_TOKEN = os.getenv('GRAPH_API_TOKEN')
WEBHOOK_VERIFY_TOKEN = os.getenv('WEBHOOK_VERIFY_TOKEN')
YOUR_PHONE_NUMBER_ID = os.getenv('YOUR_PHONE_NUMBER_ID')
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# with open('data/quiz1.json') as f:
#     QUIZ_QUESTIONS = json.load(f)['questions']
   
 

 




  
# Replace your existing list_available_quizzes function with this:
def list_available_quizzes():
    """Get list of all quiz files from MongoDB or filesystem (returns quiz numbers as strings)"""
    all_quizzes = []
    
    if USE_MONGODB:
        # Get from MongoDB questions collection
        try:
            from db_mongo import get_mongo_db
            mongo_db = get_mongo_db()
            
            # Get distinct quiz names from questions
            quiz_names = mongo_db.questions.distinct("quiz")
            
            for quiz_name in quiz_names:
                # Extract number from quiz name (e.g., "quiz1" -> "1")
                if quiz_name.startswith('quiz'):
                    quiz_number = quiz_name.replace('quiz', '')
                    if quiz_number.isdigit():
                        all_quizzes.append(quiz_number)
            
            all_quizzes.sort(key=int)
            logging.info(f"Found {len(all_quizzes)} quizzes in MongoDB")
            return all_quizzes
        except Exception as e:
            logging.error(f"Error reading quizzes from MongoDB: {e}")
            # Fall back to filesystem
    
    # Fallback: Get from filesystem
    try:
        for file in os.listdir('data_bootcamp'):
            if file.startswith('quiz') and file.endswith('.json'):
                quiz_number = file.split('.')[0].replace('quiz', '')
                all_quizzes.append(quiz_number)
        all_quizzes.sort(key=int)
        logging.info(f"Found {len(all_quizzes)} quiz files in data_bootcamp/")
        return all_quizzes
    except Exception as e:
        logging.error(f"Error reading quiz files from data_bootcamp: {e}")
        return []




     
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
    leftout_file = os.path.join('data_bootcamp', 'leftout.json')
    with open(leftout_file, 'r') as f:
        excluded_phone_numbers = json.load(f)['excluded_phone_numbers']

    wat = pytz.timezone('Africa/Lagos')
    current_time = datetime.now(wat)
    next_reset = current_time.replace(hour=RESET_HOUR, minute=RESET_MINUTE, second=0, microsecond=0)
    while next_reset.weekday() != RESET_DAY or next_reset <= current_time:
        next_reset += timedelta(days=1)

    if USE_MONGODB:
        from db_mongo import get_mongo_db
        mongo_db = get_mongo_db()

        pipeline = [
            {"$lookup": {
                "from": "users",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "user_info"
            }},
            {"$unwind": "$user_info"},
            {"$match": {
                "user_info.phone_number": {"$nin": excluded_phone_numbers}
            }},
            {"$project": {
                "name": "$user_info.name",
                "phone_number": "$user_info.phone_number",
                "score": 1
            }},
            {"$sort": {"score": -1}},
            {"$limit": 15}
        ]
        results = list(mongo_db.user_scores.aggregate(pipeline))
        results = [(r['name'], r['phone_number'], r['score']) for r in results]
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
        SELECT u.name, us.phone_number, us.score
        FROM users u
        JOIN user_scores us ON u.id = us.user_id
        WHERE us.phone_number NOT IN ({})
        ORDER BY us.score DESC
        LIMIT 15
        """.format(','.join(['?'] * len(excluded_phone_numbers)))
        cursor.execute(query, excluded_phone_numbers)
        results = cursor.fetchall()
        conn.close()

    return render_template('winnersboard.html', results=results, next_reset=next_reset)


  
 


@app.route('/viewdatabootcamp')
def viewdatabootcamp():
    if USE_MONGODB:
        from db_mongo import get_mongo_db
        mongo_db = get_mongo_db()

        users = list(mongo_db.users.find({}))
        grouped_data = {}

        for user in users:
            user_id = str(user['_id'])
            responses = list(mongo_db.responses.find({"user_id": user_id}))

            quizzes = {}
            for r in responses:
                quiz = r.get('quiz', 'Unspecified')
                if quiz not in quizzes:
                    quizzes[quiz] = {'correct': 0, 'wrong': []}
                if r.get('correct'):
                    quizzes[quiz]['correct'] += 1
                else:
                    quizzes[quiz]['wrong'].append(str(r.get('question_number', '')))

            for quiz, data in quizzes.items():
                entry = {
                    'phone_number': user.get('phone_number', ''),
                    'name': user.get('name', ''),
                    'correct_answers': data['correct'],
                    'wrong_answers': ','.join(data['wrong']),
                    'quiz': quiz
                }
                if quiz not in grouped_data:
                    grouped_data[quiz] = []
                grouped_data[quiz].append(entry)
    else:
        user_data = get_user_data()
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
    Generate AI response using Google's Gemini models.
    Tries models in order — falls back if quota exceeded (429).
    """
    global GEMINI_API_KEY

    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY is not set")
        return "I apologize, but I'm having difficulty generating a response right now. Please try again later."

    MODELS = [
        "gemini-2.5-flash",      # primary — working
        "gemini-2.0-flash",      # fallback
        "gemini-2.0-flash-lite", # last resort
    ]

    headers = {'Content-Type': 'application/json'}

    data = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2000,
            "topP": 1,
            "topK": 1
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HATE_SPEECH",       "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HARASSMENT",        "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"}
        ]
    }

    for model in MODELS:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
            logger.info(f"Sending request to {model} with prompt: {prompt[:100]}...")

            response = requests.post(url, headers=headers, json=data, timeout=30)
            logger.info(f"API response status code: {response.status_code}")

            response_text = response.text
            logger.info(f"Raw API response: {response_text[:500]}...")

            # If quota exceeded, try next model
            if response.status_code == 429:
                logger.warning(f"429 quota exceeded on {model}, trying next model...")
                continue

            response.raise_for_status()

            response_json = response.json()

            if 'candidates' in response_json and response_json['candidates']:
                candidate = response_json['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content'] and len(candidate['content']['parts']) > 0:
                    generated_text = candidate['content']['parts'][0]['text']
                    logger.info(f"Successfully generated text via {model} ({len(generated_text)} chars): {generated_text[:100]}...")
                    return generated_text
                else:
                    logger.error(f"Unexpected candidate structure: {json.dumps(candidate)}")
                    return "I received a response but couldn't extract the text content. Please try again."

            elif 'promptFeedback' in response_json and response_json['promptFeedback'].get('blockReason'):
                block_reason = response_json['promptFeedback']['blockReason']
                logger.warning(f"Response blocked by safety filters: {block_reason}")
                return f"I'm not able to provide a response to that query due to content safety policies ({block_reason}). Let's try a different approach or topic."

            else:
                logger.error(f"Unexpected response format: {json.dumps(response_json)}")
                return "I received an unexpected response format. Please try again with a different query."

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error on {model}: {e}")
            if 'response_text' in locals():
                logger.error(f"Response content: {response_text}")
            if '429' in str(e):
                logger.warning(f"429 on {model}, trying next model...")
                continue
            return "API error occurred. Please try again later."

        except requests.exceptions.Timeout:
            logger.error(f"Request to {model} timed out")
            return "The request took too long to process. Please try again."

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error on {model}: {e}")
            return "I'm having trouble connecting to the AI service. Please check your connection and try again."

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error on {model}: {e}")
            if 'response_text' in locals():
                logger.error(f"Response content that couldn't be parsed: {response_text}")
            return "I received a response I couldn't understand. Please try again."

        except Exception as e:
            logger.error(f"Unexpected error in generate_text on {model}: {e}", exc_info=True)
            return "An unexpected error occurred. Please try again or contact support if the issue persists."

    # All models exhausted
    logger.error("All Gemini models returned 429. Daily quota fully exhausted.")
    return "I'm temporarily unavailable due to high demand. Please try again in a few minutes."



      
    
    
  
    

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
#         user = db.get_user_by_phone(phone_number,)
#         if not user:
#             logging.error(f"User not found for phone number: {phone_number}")
#             send_message(phone_number, "An error occurred. Please try again or contact support.")
#             return

#         user_id = user['id']
#         user_state = user['state']
#         current_question = user['current_question']

#         # Handle demographic input (business_type, age, etc.)
#         if current_question in ['business_type', 'age', 'gender', 'location']:
#             extracted_info = extract_key_information(message, current_question)
#             conn.execute(f"UPDATE users SET {current_question} = ? WHERE id = ?", (extracted_info, user_id))
#             conn.commit()
#             message = extracted_info

#         current_question_index = int(current_question) 
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
                    
#                 prompt = create_followup_prompt(question_context, message, conversation_history, user)
#             except (KeyError, IndexError) as e:
#                 logging.error(f"Key/Index Error in create_followup_prompt: {str(e)}")
#                 # Create a simple prompt handler
#                 try:
#                     prompt = f"The user has asked: '{message}' about the question: '{question_context.get('question', question_context['question'] if 'question' in question_context else 'unknown question')}'. Please provide a helpful response."
#                 except:
#                     prompt = f"The user has asked: '{message}'. Please provide a helpful response."
                
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

#         # Ensure user has a score record
#         cursor.execute('INSERT OR IGNORE INTO user_scores (user_id, score) VALUES (?, 0)', (user_id,))

#         # Score updating logic 
#         if user_state in ['awaiting_explanation', 'post_explanation', 'awaiting_followup']:
#             if user_state == 'awaiting_explanation':
#                 score_increment = check_repeated_explanation(user_id, question_context['quiz'], current_question_index + 1, conn)
#             else:
#                 cursor.execute('''
#                     SELECT COUNT(*) FROM followup_questions
#                     WHERE user_id = ? AND quiz_name = ? AND quiz_question = ?
#                 ''', (user_id, question_context['quiz'], question_context['question']))
#                 followup_count = cursor.fetchone()[0]
#                 score_increment = 6 if followup_count == 1 else 7

#             leftout_file = os.path.join('data_file', 'leftout.json')
#             with open(leftout_file, 'r') as f:
#                 excluded_phone_numbers = json.load(f)['excluded_phone_numbers']

#             if phone_number not in excluded_phone_numbers:
#                 cursor.execute('''UPDATE user_scores SET score = score + ? WHERE user_id = ?''',
#                                (score_increment, user_id))
#                 conn.commit()
#             else:
#                 logging.info(f"User with phone number {phone_number} is excluded from the winners board. Score not updated.")

#         db.update_user_field(phone_number, {"state": "post_explanation"})
#         conn.commit()

#     except Exception as e:
#         error_message = f"Error in handle_ai_chat: {str(e)}"
#         logging.error(error_message)
#         logging.error(traceback.format_exc())
#         send_message(phone_number, "An unexpected error occurred. Please try again or contact support if the issue persists.")
#         prompt_next_action(phone_number, conn, include_retry=True)

#     logging.info(f"IMAGE EVENT: Finished AI chat for user {phone_number}")
    
    
    
    
    
    
    
    
    
    
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
#         user = db.get_user_by_phone(phone_number,)
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
        
#         db.update_user_field(phone_number, {"state": "post_explanation"})
#         conn.commit()

#     except Exception as e:
#         error_message = f"Error in handle_ai_chat: {str(e)}"
#         logging.error(error_message)
#         logging.error(traceback.format_exc())
#         send_message(phone_number, "An unexpected error occurred. Please try again or contact support if the issue persists.")
#         prompt_next_action(phone_number, conn, include_retry=True)

#     logging.info(f"IMAGE EVENT: Finished AI chat for user {phone_number}")
    
    
 



# def handle_ai_chat(phone_number: str, message: str, conn: sqlite3.Connection):
#     try:
#         import json
#         caller = inspect.stack()[1].function
#         logger.info(f"AI CHAT: Starting AI chat for user {phone_number} (called from {caller})")

#         cursor = conn.cursor()

#         # Get the quiz name the user is reviewing
#         cursor.execute('SELECT quiz_in_review FROM users WHERE phone_number = ?', (phone_number,))
#         result = cursor.fetchone()

#         if result is None:
#             raise ValueError(f"No user found with phone number {phone_number}")

#         quiz_in_review = result['quiz_in_review']
#         logger.info(f"User {phone_number} is reviewing quiz {quiz_in_review}")

#         # Fetch user data
#         user = db.get_user_by_phone(phone_number,)
#         if not user:
#             logger.error(f"User not found for phone number: {phone_number}")
#             send_message(phone_number, "An error occurred. Please try again or contact support.")
#             return

#         user_id = user['id']
#         user_state = user['state']
#         current_question = user['current_question']

#         # ✅ Only allow AI chat in relevant states
#         if user_state not in ['awaiting_explanation', 'awaiting_followup', 'post_explanation']:
#             logger.info(f"AI CHAT: Skipping AI chat for user {phone_number} due to state: {user_state}")
#             return

#         # Handle demographic input
#         if current_question in ['business_type', 'age', 'gender', 'location']:
#             extracted_info = extract_key_information(message, current_question)
#             conn.execute(f"UPDATE users SET {current_question} = ? WHERE id = ?", (extracted_info, user_id))
#             conn.commit()
#             message = extracted_info

#         current_question_index = int(current_question) - 1
#         incorrect_questions = get_incorrect_questions(user_id, conn, quiz_in_review)

#         if incorrect_questions is None:
#             logger.error(f"Error fetching incorrect questions for user {user_id}, quiz {quiz_in_review}")
#             send_message(phone_number, "An error occurred while retrieving your questions. Please try again or contact support.")
#             return

#         if current_question_index >= len(incorrect_questions):
#             send_message(phone_number, "You've completed all questions. Would you like to start a new quiz?")
#             present_options(phone_number, user, conn)
#             return

#         question_context = incorrect_questions[current_question_index]

#         # Convert sqlite3.Row to dictionary and ensure options are properly loaded
#         if isinstance(question_context, sqlite3.Row):
#             q_context = {key: question_context[key] for key in question_context.keys()}
#         else:
#             q_context = question_context

#         # Get the current question's actual question number and quiz from the context
#         question_number = q_context.get('question_number', current_question-1)
#         actual_quiz = q_context.get('quiz', quiz_in_review)
        
#         logger.info(f"Getting options for quiz={actual_quiz}, question_number={question_number}")

#         # Fetch and parse options from the questions table using the actual question number from the context
#         try:
#             options_query = conn.execute(
#                 "SELECT options FROM questions WHERE quiz = ? AND question_number = ?", 
#                 (actual_quiz, question_number)
#             ).fetchone()
            
#             if options_query and options_query['options']:
#                 # Parse JSON string to Python list
#                 q_context['options'] = json.loads(options_query['options'])
#                 logger.info(f"Successfully loaded options for {actual_quiz} question {question_number}: {q_context['options']}")
#             else:
#                 q_context['options'] = []
#                 logger.warning(f"No options found for quiz {actual_quiz}, question {question_number}")
#         except Exception as e:
#             logger.error(f"Error fetching question options: {e}")
#             q_context['options'] = []

#         # Fetch user response from the correct 'responses' table
#         if 'response' not in q_context:
#             try:
#                 user_response = conn.execute(
#                     "SELECT response FROM responses WHERE user_id = ? AND quiz = ? AND question_number = ?", 
#                     (user_id, actual_quiz, question_number)
#                 ).fetchone()
                
#                 q_context['response'] = user_response['response'] if user_response else "No answer provided"
#                 logger.info(f"Retrieved user response for {actual_quiz} question {question_number}: {q_context['response']}")
#             except Exception as e:
#                 logger.error(f"Error fetching user response: {e}")
#                 q_context['response'] = "No answer provided"

#         # Make sure we also have the correct answer
#         if 'answer' not in q_context or not q_context['answer']:
#             try:
#                 answer_query = conn.execute(
#                     "SELECT answer FROM questions WHERE quiz = ? AND question_number = ?",
#                     (actual_quiz, question_number)
#                 ).fetchone()
                
#                 if answer_query:
#                     q_context['answer'] = answer_query['answer']
#                     logger.info(f"Retrieved correct answer for {actual_quiz} question {question_number}: {q_context['answer']}")
#             except Exception as e:
#                 logger.error(f"Error fetching correct answer: {e}")

#         question_context = q_context
#         logger.info(f"Prepared question context with keys: {list(question_context.keys())}")

#         # Handle explanation or follow-up logic
#         response = None  # Initialize response to None
        
#         if message.lower().strip() == "yes" and user_state in ['awaiting_explanation', 'awaiting_followup']:
#             conversation_history = get_conversation_history(user_id, conn, limit=3)
#             explanation_prompt = create_explanation_prompt(question_context, user, conversation_history)
#             response = generate_text(explanation_prompt)

#         elif not is_related_to_question(message, question_context):
#             return handle_unrelated_followup(phone_number, message, user, conn)

#         else:
#             try:
#                 cursor.execute('''
#                     INSERT INTO followup_questions
#                     (user_id, quiz_name, quiz_question, followup_question, followup_date)
#                     VALUES (?, ?, ?, ?, datetime('now'))
#                 ''', (user_id, question_context['quiz'], question_context['question'], message))
#                 conn.commit()
#                 logger.info(f"Stored follow-up question for user {user_id}")
#             except sqlite3.Error as e:
#                 logger.error(f"Error storing follow-up question: {e}")

#             conversation_history = get_conversation_history(user_id, conn, limit=3)

#             try:
#                 prompt = create_followup_prompt(question_context, message, conversation_history, user)
#             except Exception as e:
#                 logger.error(f"Error in create_followup_prompt: {str(e)}")
#                 prompt = f"The user '{user.get('name', 'Entrepreneur')}' who runs a {user.get('business_type', 'business')} in {user.get('location', 'Nigeria')} has asked: '{message}' about the business question from {question_context.get('quiz', 'unknown quiz')} question {question_context.get('question_number', 'unknown number')}: '{question_context.get('question', 'unknown question')}'. The question had these options: {question_context.get('options', [])}. The user selected: {question_context.get('response', 'unknown')}. The correct answer was: {question_context.get('answer', 'unknown')}. Provide a helpful, practical response (maximum 200 words) with specific Nigerian business advice and examples."

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

#         # ✅ FIXED: Handle None response properly
#         if response is None:
#             logger.warning(f"AI response is None for user {phone_number}")
#             send_message(phone_number, "I'm having difficulty connecting to the AI service right now. Please try again in a moment.")
#             prompt_next_action(phone_number, conn, include_retry=True)
#         elif response.startswith("I apologize, but I'm having difficulty generating a response"):
#             logger.warning(f"AI returned error message for user {phone_number}")
#             prompt_next_action(phone_number, conn, include_retry=True)
#         else:
#             send_message(phone_number, response)
#             store_conversation(user_id, message, False, conn)
#             store_conversation(user_id, response, True, conn)
#             prompt_next_action(phone_number, conn)

#         db.update_user_field(phone_number, {"state": "post_explanation"})
#         conn.commit()

#     except Exception as e:
#         error_message = f"Error in handle_ai_chat: {str(e)}"
#         logger.error(error_message)
#         logger.error(traceback.format_exc())
#         send_message(phone_number, "An unexpected error occurred. Please try again or contact support if the issue persists.")
#         prompt_next_action(phone_number, conn, include_retry=True)

#     logger.info(f"AI CHAT: Finished handling AI chat for user {phone_number}")


def handle_ai_chat(phone_number: str, message: str, conn):
    try:
        logger.info(f"AI CHAT: Starting for user {phone_number}, message: {message}")

        user = db.get_user_by_phone(phone_number)
        if not user:
            send_message(phone_number, "An error occurred. Please try again.")
            return

        user_id = str(user['_id']) if USE_MONGODB else user['id']
        user_state = user['state']
        current_question = user.get('current_question', 0)
        quiz_in_review = user.get('quiz_in_review')

        if user_state not in ['awaiting_explanation', 'awaiting_followup', 'post_explanation', 'awaiting_action']:
            logger.info(f"AI CHAT: Skipping - user in wrong state: {user_state}")
            return

        if not quiz_in_review:
            logger.error(f"No quiz_in_review for user {phone_number}")
            send_message(phone_number, "No quiz in review. Please start a quiz review first.")
            present_options(phone_number, user, conn)
            return

        current_question_index = int(current_question) - 1
        incorrect_questions = get_incorrect_questions(user_id, conn, quiz_in_review)

        if incorrect_questions is None or current_question_index >= len(incorrect_questions):
            send_message(phone_number, "You've completed all questions. Would you like to start a new quiz?")
            present_options(phone_number, user, conn)
            return

        question_context = incorrect_questions[current_question_index]
        if not isinstance(question_context, dict):
            question_context = dict(zip(['id', 'question', 'answer', 'question_number', 'quiz'], question_context))

        actual_quiz = question_context.get('quiz', quiz_in_review)
        question_number = question_context.get('question_number')

        # Get options
        if USE_MONGODB:
            from db_mongo import get_mongo_db
            mongo_db = get_mongo_db()
            q_doc = mongo_db.questions.find_one({
                "quiz": actual_quiz,
                "question_number": question_number
            })
            question_context['options'] = q_doc.get('options', []) if q_doc else []

            resp_doc = mongo_db.responses.find_one({
                "user_id": user_id,
                "quiz": actual_quiz,
                "question_number": question_number,
                "correct": False
            })
            question_context['response'] = resp_doc['response'] if resp_doc else "No answer provided"
        else:
            if conn and hasattr(conn, 'execute'):
                options_result = conn.execute(
                    "SELECT options FROM questions WHERE quiz = ? AND question_number = ?",
                    (actual_quiz, question_number)
                ).fetchone()
                question_context['options'] = json.loads(options_result[0]) if options_result else []

                resp_result = conn.execute(
                    "SELECT response FROM responses WHERE user_id = ? AND quiz = ? AND question_number = ?",
                    (user_id, actual_quiz, question_number)
                ).fetchone()
                question_context['response'] = resp_result[0] if resp_result else "No answer provided"

        if USE_MONGODB:
            conversation_history = []
            history_docs = list(mongo_db.conversation_history.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(3))
            for doc in reversed(history_docs):
                conversation_history.append((doc['message'], doc['is_ai']))
        else:
            conversation_history = get_conversation_history(user_id, conn, limit=3)

        # Decide which prompt to use
        if user_state == 'awaiting_explanation':
            if message.lower().strip() == "yes":
                prompt = create_explanation_prompt(question_context, user, conversation_history)
                response = generate_text(prompt)
            else:
                prompt = create_followup_prompt(question_context, message, conversation_history, user)
                response = generate_text(prompt)
        elif user_state in ['awaiting_followup', 'post_explanation', 'awaiting_action']:
            thank_you_phrases = ['thank', 'thanks', 'appreciate', 'grateful', 'helpful']
            if any(phrase in message.lower() for phrase in thank_you_phrases) and len(message.split()) <= 5:
                response = random.choice([
                    "You're welcome! I'm glad I could help.",
                    "Happy to help!",
                    "It's my pleasure to assist you.",
                    "Glad I could be of help!",
                ])
            elif not is_related_to_question(message, question_context):
                return handle_unrelated_followup(phone_number, message, user, conn)
            else:
                prompt = create_followup_prompt(question_context, message, conversation_history, user)
                response = generate_text(prompt)
        else:
            prompt = create_followup_prompt(question_context, message, conversation_history, user)
            response = generate_text(prompt)

        if response is None:
            send_message(phone_number, "I'm having difficulty connecting right now. Please try again.")
            prompt_next_action(phone_number, conn, include_retry=True)
        elif response.startswith("I apologize, but I'm having difficulty"):
            prompt_next_action(phone_number, conn, include_retry=True)
        else:
            send_message(phone_number, response)

            if USE_MONGODB:
                mongo_db.conversation_history.insert_one({
                    "user_id": user_id,
                    "message": message,
                    "is_ai": False,
                    "timestamp": datetime.utcnow()
                })
                mongo_db.conversation_history.insert_one({
                    "user_id": user_id,
                    "message": response,
                    "is_ai": True,
                    "timestamp": datetime.utcnow()
                })
            else:
                store_conversation(user_id, message, False, conn)
                store_conversation(user_id, response, True, conn)

            prompt_next_action(phone_number, conn)

        db.update_user_field(phone_number, {"state": "post_explanation"})

    except Exception as e:
        logger.error(f"Error in handle_ai_chat: {str(e)}")
        logger.error(traceback.format_exc())
        send_message(phone_number, "An unexpected error occurred. Please try again or contact support.")
        prompt_next_action(phone_number, conn, include_retry=True)



    
    
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
   
    db.update_user_field(phone_number, {"state": "awaiting_action"})
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

  
  


  
  
  
  
  
# def create_explanation_prompt(question_context, user, conversation_history):
#     # Step 1: Ensure user data is retrieved properly
#     user_name = user['name'].split()[0].capitalize() 
#     user_age = user['age']
#     user_gender = user['gender']
#     user_business_type = user['business_type']
#     user_location = user['location'].capitalize()
#     user_business_size = user['business_size']
#     user_financial_status = user['financial_status']
#     user_main_challenge = user['main_challenge']
#     user_record_keeping = user['record_keeping']
#     user_growth_goal = user['growth_goal']
#     user_funding_need = user['funding_need']
#     user_products = "various products"  # Generic term since data is not yet available

#     # Log the user data to ensure proper retrieval (can be used for debugging)
#     logging.info(f"Creating prompt for {user_name}, age: {user_age}, gender: {user_gender}, "
#                  f"business: {user_business_type}, location: {user_location}, "
#                  f"size: {user_business_size}, financial status: {user_financial_status}, "
#                  f"main challenge: {user_main_challenge}, record keeping: {user_record_keeping}, "
#                  f"growth goal: {user_growth_goal}, funding need: {user_funding_need}, "
#                  f"products: {user_products}")

#     # Step 2: Process the question and user's response
#     options = [opt.strip() for opt in question_context['options'].split('\n') if opt.strip()]
#     options_dict = {chr(65 + i): opt for i, opt in enumerate(options)}
#     user_answer = question_context['response'].strip()
#     correct_answer = question_context['answer'].strip().lower()
#     user_option = next((opt for opt, text in options_dict.items() if text.lower() == user_answer.lower()), 'Unknown')
#     correct_option = next((opt for opt, text in options_dict.items() if text.lower() == correct_answer), 'Unknown')
#     is_correct = user_answer.lower() == correct_answer
#     options_text = "\n".join([f"{opt}) {text}" for opt, text in options_dict.items()])

#     # # Step 3: Include recent conversation history
#     # recent_history = "\n".join([f"{'User' if not msg['is_ai'] else 'AI'}: {msg['message']}" for msg in conversation_history[-3:]])

#     # Step 4: Create the personalized prompt
#     return f"""
#     You are a mentor helping {user_name}, a {user_age}-year-old {user_gender} entrepreneur who owns a small {user_business_type} business in {user_location}. 
#     Their business size is {user_business_size}, with a financial status of {user_financial_status}. 
#     Their main challenge is {user_main_challenge}, they use {user_record_keeping} for record keeping, their growth goal is {user_growth_goal},
#     and their funding need is {user_funding_need}. They sell various products. 
#     They just answered a question in a business quiz.
#     All should not be more than 50 words so make them precise.
#     Give (1) start with the  explanation of why the {user_answer} is incorrect and why {correct_option} is, (2)tailored advice ans (3) Quick Wins
#     Below are the details:

#     Question: {question_context['question']}
#     Options:
#     {options_text}
#     {user_name}'s Answer: {user_option}) {user_answer}
#     Correct Answer: {correct_option}) {correct_answer}
    
    
#     {'The user answered correctly.' if is_correct else 'The user answered incorrectly.'}

  

#     ### Explanation:

#     1. ### Explanation:

#     Greet {user_name} warmly, acknowledge their efforts, and provide a detailed explanation of the concept often in pidging English. Make sure to:
#     - start with the  explanation of why the {user_answer} is incorrect 
#     -  Kindly explain the  {correct_option}) {correct_answer} and why, while relating the explanation back to the {user_business_type} business they run.
    
#     - Use realistic examples relevant  {user_name} and to their business environment in {user_location}. For instance, describe how the correct answer applies to {user_name}'s daily operations. Dont use third person, make it personalized

#     - Be a bit dramatic and make it more fun and show excitment, action and curiousity
#     - Let responses be in shorter paragraphs, dont lump them together.
#     - Explain the "how"the {correct_option} is somwhat similar but different from the {user_answer}
#     - Explain the "how" not just the "why" of the {correct_option} and how possible solutions that can be applied by {user_business_type} in real life.
#     - Always use icons and emojis 
#     - User very simple english for people with little or no education
#     - Don't repeat response related to products, anectodes, example  for {user_name}, make it random
#     - If their answer was incorrect, kindly explain why, while relating the explanation back to the {user_business_type} business they run.
#     - Use realistic examples relevant  {user_name} and to their business environment in {user_location}. For instance, describe how the correct answer applies to {user_name}'s daily operations. Dont use third person, make it personalized
   
#     - Use very simple English for people with little or no formal business education.
#     - If their correct answer {correct_answer} was wrong, kindly explain why, linking it to their {user_business_type}.
#     - Encourage {user_name} to think about how to use this idea in their {user_business_type}
#     - If their answer was wrong, kindly explain why, linking it to their {user_business_type}.
#     - Encourage {user_name} to think about how to use this idea in their {user_business_type}
#     - Always include a bit of pidgin English and sometimes references to Nigerian culture in the text to make it relatable.
#     - Use very simple English for people with little or no formal business education.
#     - Explain how the correct answer {correct_answer} can help {user_name}'s business in real life.
#     - Use emojis to make key points stand out.
#     - If their answer was wrong, kindly explain why, linking it to their business.
#     -  Make it easy to understand and do for a business with 0-1 employees.
    
    
#     2. Based on the question, correct answer, and {user_name}'s situation, provide 2-3 specific recommendations: After explaining the {correct_answer}, provide highly tailored advice in one or all of these three areas: 1. Cost Efficiency and Resource Management, 2. Revenue Growth and Customer Acquisition,
#     and Potential Partnership using the following:
    
#        - Web Search and Data Gathering (Do not include this in your response to the user):
#        - Conduct a web search for recent information about {user_business_type} businesses in {user_location}
#        - Find data on local market conditions, popular products, pricing trends, and common challenges
#        - Identify local events, potential partners, and suppliers relevant to {user_business_type}
#        - Research successful strategies used by similar businesses in the area

  
#     The Tailored Business Advice (15 words) should be:
#        Based on the question, correct answer, their challenge ({user_main_challenge}), and your Web Search and Data, provide 2-3 specific recommendations:
       
#        a) Business-Specific Strategies[Very specific action based on the correct answer]:
#           - Suggest pricing strategies based on local market research
#           - Recommend specific local events or venues for selling
#           - Propose product ideas or modifications based on market trends
       
#        b) Challenge-Specific Solutions[Very specific action based on the correct answer]:
#           - Address their {user_main_challenge} with actionable advice
#           - Suggest partnerships or collaborations with local businesses (use real examples from your search)
#           - Recommend cost-saving or revenue-generating ideas suitable for their {user_business_size} business

#        c) Growth Opportunities[Very specific action based on the correct answer]:
#           - Suggest specific steps to achieve their {user_growth_goal}
#           - Recommend financial strategies based on their {user_financial_status} and {user_funding_need}
#           - Propose record-keeping improvements considering their {user_record_keeping} method


#     ### Guidelines:
#     - Use recent web search of 2024 results to provide relevant, location-specific advice and 2024 prices and similar products
#     - All suggestions should be actionable for a {user_business_size} business
#     - Use simple language, short sentences, and occasional pidgin English
#     - Incorporate Nigerian cultural references to increase relatability
#     - Emphasize the 'why' behind each recommendation
#     - Highlight potential risks of not implementing the advice

#     Example Response Format:
#     "💡 {user_name}, about [concept from question], it's crucial for your {user_business_type} because [reason tied to correct answer and their challenge].

#     In {user_location}, you could:
#     1. Sell your [typical product for their business type] at [specific local event from your search] next month
#     2. Partner with [real local business from your search] to cross-promote
#     3. Get your supplies from [specific supplier or market from your search] to save [researched amount] Naira

#      3. Detailed Quick Win (15 words):
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

#       You can end with Asking one prompting question such as: Wetin you think? You fit try this one? Make you tell me how e go when you don do am!"

#     Remember to use simple English and Pidgin where appropriate, and ensure all suggestions are feasible for a {user_business_size} business in {user_location}.
#     """
#     logging.debug(f"Generated personalized prompt for {user_name}: {prompt[:200]}...")  # Log first 200 chars
    

  
  
  
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

    # Step 2: Process the question and user's response
    options = [opt.strip() for opt in question_context['options'].split('\n') if opt.strip()] if isinstance(question_context['options'], str) else question_context['options']
    options_dict = {chr(65 + i): opt for i, opt in enumerate(options)}
    user_answer = question_context['response'].strip()
    correct_answer = question_context['answer'].strip().lower()
    user_option = next((opt for opt, text in options_dict.items() if text.lower() == user_answer.lower()), 'Unknown')
    correct_option = next((opt for opt, text in options_dict.items() if text.lower() == correct_answer), 'Unknown')
    is_correct = user_answer.lower() == correct_answer
    options_text = "\n".join([f"{opt}) {text}" for opt, text in options_dict.items()])

    # Step 3: Create the personalized prompt
    return f"""
    ⚠️ CRITICAL INSTRUCTIONS - READ FIRST ⚠️
    - The user's name is {user_name} - USE THIS NAME throughout by personalizing the response, NOT fictional names like "Uncle Kunle"
    - They run a {user_business_type} business in {user_location} - USE THIS as your example
    - DO NOT create fictional characters or scenarios with made-up names
    - Speak directly to {user_name} about THEIR {user_business_type} business
    - Say "Imagine YOU, {user_name}, with your {user_business_type} in {user_location}..."
    - NOT "Imagine Uncle Kunle with his mama put joint"
    
    ⚠️ WORD COUNT: YOUR ENTIRE RESPONSE MUST BE 200-250 WORDS TOTAL ⚠️

    You are a mentor helping {user_name}, a {user_age}-year-old {user_gender} entrepreneur who owns a {user_business_type} business in {user_location}. 
    Business size: {user_business_size}
    Financial status: {user_financial_status}
    Main challenge: {user_main_challenge}
    Record keeping: {user_record_keeping}
    Growth goal: {user_growth_goal}
    Funding need: {user_funding_need}

    Question: {question_context['question']}
    Options:
    {options_text}
    {user_name}'s Answer: {user_option}) {user_answer}
    Correct Answer: {correct_option}) {correct_answer}
    
    {'The user answered correctly.' if is_correct else 'The user answered incorrectly.'}

    Structure your 200-250 word response in THREE parts:

    1. Explanation (100-120 words):
    - Greet {user_name} warmly using pidgin English
    - Address {user_name} directly throughout
    - Explain why {correct_answer} is correct (and if applicable, why {user_answer} is wrong)
    - Use {user_name}'s actual {user_business_type} business in {user_location} as the example
    - Say: "Imagine YOU, {user_name}, with YOUR {user_business_type} in {user_location}..."
    - Use simple English mixed with pidgin
    - Be dramatic, fun, and show excitement with emojis
    - Include realistic Naira amounts relevant to {user_business_type}

    2. Practical Advice (50-70 words):
    - Give ONE specific recommendation for {user_name}'s {user_business_type}
    - Address their challenge: {user_main_challenge}
    - Make it actionable in {user_location}
    - Include realistic 2024 Naira prices for {user_business_type}

    3. Quick Win (50-60 words):
    - ONE specific action {user_name} can take tomorrow
    - For their {user_business_type} in {user_location}
    - Consider their financial status: {user_financial_status}
    - Include specific details (product, location, timing, price)
    - End with a pidgin question: "Wetin you think?"

    Remember: Use emojis, simple language, be warm and encouraging.
    TOTAL: 200-250 WORDS. Use {user_name}'s name and business throughout!
    """



    
  
  
 
  
  
  
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
    user_age = user['age']
    user_business_type = user['business_type']
    user_location = user['location'].capitalize()
    user_business_size = user['business_size']
    user_financial_status = user['financial_status']
    user_main_challenge = user['main_challenge']
    user_growth_goal = user['growth_goal']
    
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
    ⚠️ CRITICAL INSTRUCTIONS - READ FIRST ⚠️
    - The user's name is {user_name} - USE THIS NAME, NOT fictional names
    - They run a {user_business_type} business in {user_location} - USE THIS as examples
    - DO NOT create fictional characters like "Uncle Kunle" or "Mama Ngozi"
    - Speak directly to {user_name} about THEIR business
    
    ⚠️ WORD COUNT: 150-200 WORDS TOTAL ⚠️

    You are continuing a conversation with {user_name}, a {user_age}-year-old entrepreneur with a {user_business_type} business in {user_location}.
    Recent Conversation:
    {conversation_context}

    Original Question: {question_context['question']}
    Options:
    {options_text}
    User's answer: {user_option}) {user_full_answer}
    Correct Answer: {correct_option}) {correct_full_answer}

    The user's latest message is: "{user_message}"

   1. Your response should:
    - Be around 100 words and specific to the user's question and recent conversation:
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
    db.update_user_field(phone_number, {"state": "awaiting_followup"})
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
    try:
        if USE_MONGODB:
            from db_mongo import get_mongo_db
            mongo_db = get_mongo_db()
            user_id_str = str(user_id)

            # Get question numbers the user got wrong
            wrong_responses = list(mongo_db.responses.find({
                "user_id": user_id_str,
                "quiz": quiz_name,
                "correct": False
            }, {"question_number": 1, "response": 1}))

            if not wrong_responses:
                return []

            wrong_q_nums = [r['question_number'] for r in wrong_responses]
            response_map = {r['question_number']: r['response'] for r in wrong_responses}

            # Get the actual questions
            questions = list(mongo_db.questions.find({
                "quiz": quiz_name,
                "question_number": {"$in": wrong_q_nums}
            }).sort("question_number", 1))

            # Build result as list of dicts
            results = []
            for q in questions:
                results.append({
                    "id": str(q.get('_id')),
                    "question": q.get('question'),
                    "answer": q.get('answer'),
                    "question_number": q.get('question_number'),
                    "quiz": q.get('quiz'),
                    "options": q.get('options', []),
                    "response": response_map.get(q.get('question_number'), "No answer provided")
                })

            logging.info(f"get_incorrect_questions: fetched {len(results)} wrong questions for user={user_id_str}, quiz={quiz_name}")
            return results

        else:
            if not hasattr(conn, 'cursor'):
                logging.error(f"get_incorrect_questions: expected sqlite3.Connection, got {type(conn)}")
                return None

            cursor = conn.cursor()
            cursor.execute("""
                SELECT question_number FROM responses
                WHERE user_id = ? AND quiz = ? AND correct = 0
                ORDER BY question_number ASC
            """, (user_id, quiz_name))
            q_nums = [row[0] for row in cursor.fetchall()]

            if not q_nums:
                return []

            placeholders = ','.join('?' for _ in q_nums)
            cursor.execute(f"""
                SELECT id, question, answer, question_number, quiz
                FROM questions
                WHERE quiz = ? AND question_number IN ({placeholders})
                ORDER BY question_number ASC
            """, [quiz_name] + q_nums)
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
        user_id = str(user['_id']) if USE_MONGODB else user['id']

        if USE_MONGODB:
            from db_mongo import get_mongo_db
            mongo_db = get_mongo_db()
            current_question = int(user.get('current_question', 0))
            quiz_name = user.get('quiz_in_review')
        else:
            cursor = conn.cursor()
            cursor.execute('SELECT current_question, quiz_in_review FROM users WHERE phone_number = ?', (phone_number,))
            result = cursor.fetchone()
            if result is None:
                raise ValueError(f"No user found with phone number {phone_number}")
            current_question = int(result[0])
            quiz_name = result[1]

        if not quiz_name:
            raise ValueError("No quiz in review found for this user")

        logging.info(f"Current question for user {phone_number}: {current_question}, quiz: {quiz_name}")

        incorrect_questions = get_incorrect_questions(user_id, conn, quiz_name)

        if incorrect_questions is None:
            send_message(phone_number, "An error occurred while retrieving questions. Please try again.")
            return

        if current_question >= len(incorrect_questions):
            send_message(phone_number, "Great job! You've reviewed all your incorrect questions. Would you like to start a new quiz?")
            present_options(phone_number, user, conn)
            return

        question_data = incorrect_questions[current_question]

        if not isinstance(question_data, dict):
            question_data = dict(zip(['id', 'question', 'answer', 'question_number', 'quiz'], question_data))

        q_number = question_data['question_number']

        # Get user response and options
        if USE_MONGODB:
            from db_mongo import get_mongo_db
            mongo_db = get_mongo_db()

            response_doc = mongo_db.responses.find_one({
                "user_id": user_id,
                "quiz": quiz_name,
                "question_number": q_number,
                "correct": False
            })
            user_answer = response_doc['response'] if response_doc else "No answer provided"

            q_doc = mongo_db.questions.find_one({
                "quiz": quiz_name,
                "question_number": q_number
            })

            if q_doc:
                raw_options = q_doc.get('options', [])
            else:
                raw_options = []

            # Options are stored as a JSON string in MongoDB — parse it
            if isinstance(raw_options, str):
                try:
                    raw_options = json.loads(raw_options)
                except Exception:
                    raw_options = []

        else:
            cursor = conn.cursor()
            response_result = cursor.execute(
                "SELECT response FROM responses WHERE user_id = ? AND quiz = ? AND question_number = ? AND correct = 0",
                (user_id, quiz_name, q_number)
            ).fetchone()
            user_answer = response_result[0] if response_result else "No answer provided"

            options_result = cursor.execute(
                "SELECT options FROM questions WHERE quiz = ? AND question_number = ?",
                (quiz_name, q_number)
            ).fetchone()
            raw_options = json.loads(options_result[0]) if options_result else []

        # Normalize options
        if isinstance(raw_options, str):
            try:
                options = json.loads(raw_options)
            except Exception:
                options = []
        elif isinstance(raw_options, list):
            options = raw_options
        else:
            options = []

        # Final fallback — load from JSON file if options still empty
        if len(options) == 0:
            logging.warning(f"Options empty for {quiz_name} q{q_number}, loading from JSON file")
            quiz_data = load_quiz_data(quiz_name)
            if quiz_data:
                questions_list = quiz_data.get('questions', [])
                for i, q in enumerate(questions_list):
                    if i + 1 == q_number:
                        options = q.get('options', [])
                        break

        if len(options) == 0:
            raise ValueError(f"Could not find options for {quiz_name} question {q_number}")

        logging.info(f"Options for {quiz_name} q{q_number}: {options}")

        question_data['response'] = user_answer
        question_data['options'] = options

        # Validate required fields
        for field in ['question', 'answer', 'response', 'quiz', 'question_number']:
            if field not in question_data or question_data[field] is None:
                raise ValueError(f"Missing required field: {field}")

        question_text = question_data['question']
        correct_answer = question_data['answer']

        message = f"Quiz: {quiz_name}\nQuestion {q_number}:\n\n{question_text}\n\nOptions:\n"
        message += "\n".join(options)
        message += f"\n\nYour answer: {user_answer}\nCorrect answer: {correct_answer.upper()}"

        send_message(phone_number, message)

        buttons = [
            {"type": "reply", "reply": {"id": "explain_yes", "title": "Yes"}},
            {"type": "reply", "reply": {"id": "explain_no", "title": "No"}}
        ]
        send_interactive_message(phone_number, "Would you like an explanation for this question?", buttons)

        db.update_user_field(phone_number, {
            "state": "awaiting_explanation",
            "current_question": current_question + 1
        })
        logging.info(f"Updated user {phone_number} to awaiting_explanation, next question index: {current_question + 1}")

    except ValueError as ve:
        logging.error(f"ValueError in send_next_question: {str(ve)}")
        send_message(phone_number, f"An error occurred: {str(ve)}. Please contact support.")
    except Exception as e:
        logging.error(f"Unexpected error in send_next_question: {str(e)}")
        logging.error(traceback.format_exc())
        send_message(phone_number, "An unexpected error occurred. Please try again or contact support.")




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
app.config['QUIZ_VISIBILITY'] = {}

def load_quiz_visibility_from_db():
    """Load quiz visibility settings from database into memory"""
    
    if USE_MONGODB:
        from db_mongo import get_mongo_db
        try:
            mongo_db = get_mongo_db()
            temp_visibility = {}  # Use temp dict
            
            # Get all quiz statuses from MongoDB
            statuses = mongo_db.quiz_status.find({})
            for status in statuses:
                temp_visibility[status['quiz']] = bool(status.get('enabled', True))
            
            # Store in Flask config
            app.config['QUIZ_VISIBILITY'] = temp_visibility
            print(f"Loaded quiz visibility from MongoDB: {temp_visibility}")
        except Exception as e:
            print(f"Error loading quiz visibility from MongoDB: {e}")
    else:
        # SQLite version
        conn = db.get_connection()
        try:
            temp_visibility = {}
            cursor = conn.cursor()
            
            # Get all quizzes from files
            all_quizzes = []
            for file in os.listdir('data_bootcamp'):
                if file.startswith('quiz') and file.endswith('.json'):
                    quiz_number = file.split('.')[0].replace('quiz', '')
                    all_quizzes.append(quiz_number)
            
            for quiz_num in all_quizzes:
                quiz_name = f"quiz{quiz_num}"
                cursor.execute("SELECT enabled FROM quiz_status WHERE quiz = ?", (quiz_name,))
                result = cursor.fetchone()
                
                if result:
                    temp_visibility[quiz_name] = bool(result[0])
                else:
                    temp_visibility[quiz_name] = True
            
            # Store in Flask config
            app.config['QUIZ_VISIBILITY'] = temp_visibility
            print(f"Loaded quiz visibility from SQLite: {temp_visibility}")
        except Exception as e:
            print(f"Error loading quiz visibility from SQLite: {e}")
        finally:
            conn.close()


                
        
# Fixed GET endpoint - reads from quiz_status table
@app.route('/api/quizzes', methods=['GET'])
def api_get_quizzes():
    try:
        if USE_MONGODB:
            from db_mongo import get_mongo_db
            mongo_db = get_mongo_db()

            # Get all unique quiz names from questions collection
            quiz_names = sorted(
                mongo_db.questions.distinct("quiz"),
                key=lambda x: int(x.replace('quiz', '')) if x.replace('quiz', '').isdigit() else 999
            )

            # Load latest visibility from DB into config
            load_quiz_visibility_from_db()
            visibility = app.config.get('QUIZ_VISIBILITY', {})

            quizzes = [
                {
                    "quiz": name,
                    "enabled": visibility.get(name, True)
                }
                for name in quiz_names
            ]
        else:
            conn = get_db_connection()
            rows = conn.execute("SELECT quiz, enabled FROM quiz_status ORDER BY quiz").fetchall()
            conn.close()
            quizzes = [{"quiz": row[0], "enabled": bool(row[1])} for row in rows]

        return jsonify(quizzes)

    except Exception as e:
        logging.error(f"api_get_quizzes error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/quizzes/<quiz_name>', methods=['POST'])
def api_update_quiz(quiz_name):
    try:
        data = request.get_json()
        if data is None or 'enabled' not in data:
            return jsonify({"error": "Missing 'enabled' field"}), 400

        enabled = bool(data['enabled'])

        if USE_MONGODB:
            from db_mongo import get_mongo_db
            mongo_db = get_mongo_db()

            mongo_db.quiz_status.update_one(
                {"quiz": quiz_name},
                {"$set": {"quiz": quiz_name, "enabled": enabled}},
                upsert=True
            )

            # Update in-memory config immediately so quiz visibility is live
            visibility = app.config.get('QUIZ_VISIBILITY', {})
            visibility[quiz_name] = enabled
            app.config['QUIZ_VISIBILITY'] = visibility

        else:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO quiz_status (quiz, enabled) VALUES (?, ?) "
                "ON CONFLICT(quiz) DO UPDATE SET enabled = ?",
                (quiz_name, int(enabled), int(enabled))
            )
            conn.commit()
            conn.close()

        logging.info(f"Quiz '{quiz_name}' set to enabled={enabled}")
        return jsonify({"quiz": quiz_name, "enabled": enabled, "status": "updated"})

    except Exception as e:
        logging.error(f"api_update_quiz error: {e}")
        return jsonify({"error": str(e)}), 500
    
    

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





@app.route('/debug/scoreboard')
def debug_scoreboard():
    try:
        from db_mongo import get_mongo_db
        mongo_db = get_mongo_db()
        
        users = list(mongo_db.users.find({}, {"_id": 1, "name": 1, "location": 1}))
        locations = mongo_db.users.distinct("location")
        response_count = mongo_db.responses.count_documents({})
        
        return jsonify({
            "user_count": len(users),
            "sample_users": [{"id": str(u["_id"]), "name": u.get("name"), "location": u.get("location")} for u in users[:3]],
            "locations": locations,
            "response_count": response_count,
            "USE_MONGODB": USE_MONGODB
        })
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

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
#             db.update_user_field(phone_number, {"state": previous_state})
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
            db.update_user_field(phone_number, {"state": "changing_name", "previous_state": user['state']})
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
            db.update_user_field(phone_number, {"state": previous_state})
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
            quiz_match = re.search(r'quiz(\d+)\s?\(\d+\s?incorrect\)', button_id)
            if quiz_match:
                quiz_number = quiz_match.group(1)
                quiz_name = f'quiz{quiz_number}'

                if USE_MONGODB:
                    from db_mongo import get_mongo_db
                    mongo_db = get_mongo_db()
                    user_id = str(user['_id'])
                    count = mongo_db.responses.count_documents({
                        "user_id": user_id,
                        "quiz": quiz_name,
                        "correct": False
                    })
                else:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT COUNT(*) as count FROM responses r
                        WHERE r.user_id = ? AND r.quiz = ? AND r.correct = 0
                    """, (user['id'], quiz_name))
                    result = cursor.fetchone()
                    count = result['count'] if result else 0

                if count == 0:
                    send_message(phone_number, f"No incorrect answers found for Quiz {quiz_number}. Please select another.")
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
            db.update_user_field(phone_number, {"state": "changing_name", "previous_state": user['state']})
            send_message(phone_number, "Please enter your new name:")
        elif button_id == "review_another":
            logging.info(f"User {phone_number} chose to review another quiz.")
            start_ai_chat(phone_number, user, conn)
        elif button_id in ["view_name", "view name"]:
            log_image_event(f"User {phone_number} requested to view their name")
            send_message(phone_number, f"Your name is {user['name']}.")
            present_options(phone_number, user, conn)
        elif button_id in ["view_quiz_names", "view quiz names"]:
            log_image_event(f"User {phone_number} requested to view quiz names")
            if USE_MONGODB:
                from db_mongo import get_mongo_db
                mongo_db = get_mongo_db()
                quiz_names = mongo_db.questions.distinct("quiz")
                quiz_names_str = ', '.join(sorted(quiz_names))
            else:
                quiz_names = conn.execute('SELECT DISTINCT quiz FROM questions').fetchall()
                quiz_names_str = ', '.join(row[0] for row in quiz_names)
            send_message(phone_number, f"Available quizzes: {quiz_names_str}.")
            present_options(phone_number, user, conn)
        elif button_id in ["view_scores", "view scores"]:
            log_image_event(f"User {phone_number} requested to view their scores")
            if USE_MONGODB:
                from db_mongo import get_mongo_db
                mongo_db = get_mongo_db()
                user_id = str(user['_id'])
                pipeline = [
                    {"$match": {"user_id": user_id}},
                    {"$group": {
                        "_id": "$quiz",
                        "total": {"$sum": 1},
                        "correct": {"$sum": {"$cond": ["$correct", 1, 0]}}
                    }}
                ]
                scores = list(mongo_db.responses.aggregate(pipeline))
                scores_message = "Your scores:\n"
                for row in scores:
                    total = row['total']
                    correct = row['correct']
                    percentage = (correct / total) * 100 if total > 0 else 0
                    scores_message += f"Quiz: {row['_id']}, Total: {total}, Correct: {correct}, Percentage: {percentage:.1f}%\n"
            else:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT quiz, COUNT(*) as total_questions, SUM(correct) as correct_answers
                    FROM responses WHERE user_id = ? GROUP BY quiz
                """, (user['id'],))
                scores = cursor.fetchall()
                scores_message = "Your scores:\n"
                for row in scores:
                    quiz, total, correct = row
                    percentage = (correct / total) * 100 if total > 0 else 0
                    scores_message += f"Quiz: {quiz}, Total: {total}, Correct: {correct}, Percentage: {percentage:.1f}%\n"
            send_message(phone_number, scores_message)
            present_options(phone_number, user, conn)
        elif button_id in ["back", "back"]:
            log_image_event(f"User {phone_number} is returning to previous activity")
            previous_state = user.get('previous_state', 'main_menu')
            db.update_user_field(phone_number, {"state": previous_state})
            send_message(phone_number, "Returning to previous activity.")
            present_options(phone_number, user, conn)
        elif button_id in ["more", "more options"]:
            log_image_event(f"User {phone_number} requested more options")
            handle_settings_command(phone_number, user, conn)
        elif button_id in ["page_1", "page 1"]:
            log_image_event(f"User {phone_number} requested page 1")
            handle_settings_command(phone_number, user, conn)
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
       
#         user = db.get_user_by_phone(phone_number,)
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
       
#         user = db.get_user_by_phone(phone_number,)
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
    """Handle incoming WhatsApp messages with MongoDB/SQLite support"""
    log_image_event(f"Full message content: {json.dumps(message, indent=2)}")

    message_id = message.get('id')
    phone_number = message['from']
    message_type = message['type']
    log_image_event(f"Received message of type '{message_type}' from {phone_number}")

    try:
        # Check if message already processed
        if USE_MONGODB:
            from db_mongo import get_mongo_db
            mongo_db = get_mongo_db()
            processed = mongo_db.processed_messages.find_one({"message_id": message_id})
            if processed:
                log_image_event(f"Message {message_id} already processed, skipping")
                return
        else:
            conn = get_db_connection()
            try:
                if conn.execute('SELECT 1 FROM processed_messages WHERE message_id = ?', (message_id,)).fetchone():
                    log_image_event(f"Message {message_id} already processed, skipping")
                    return
            finally:
                conn.close()

        # Get user using database adapter
        user = db.get_user_by_phone(phone_number)
        log_image_event(f"Processing message {message_id} for user: {user}")

        if user is None:
            try:
                user = db.create_new_user(phone_number, state="awaiting_location_code")
            except Exception:
                user = db.get_user_by_phone(phone_number)
                if user is None:
                    return
            send_message(phone_number, "👋 Welcome to EmpowerBot!\n\nPlease enter your *location code* to get started.\n\nDon't have a code? Type *OPEN* to continue.")
            log_image_event(f"New user created for {phone_number}, awaiting name")

        else:
            log_image_event(f"User state: {user['state']}")

            if message_type == 'interactive':
                log_image_event(f"Processing interactive message")
                interactive = message.get('interactive', {})

                if interactive.get('type') == 'button_reply':
                    button_id = interactive['button_reply']['id']
                    button_text = interactive['button_reply']['title']
                    log_image_event(f"Received button reply: id={button_id}, text={button_text}")

                    if button_id == 'explain_yes':
                        handle_ai_chat(phone_number, "Please explain the previous question.", None)
                    elif button_id == 'explain_no':
                        send_next_question(phone_number, user, None)
                    elif button_id == 'end_chat':
                        end_ai_chat(phone_number, user, None)
                    elif button_id == 'next_question':
                        handle_post_explanation_action(phone_number, button_id, user, None)
                    elif button_id == 'remove_account':
                        handle_remove_account_request(phone_number, user, None)
                    elif button_id == 'confirm_remove':
                        remove_user_account(phone_number, None)
                    elif button_id == 'cancel_remove':
                        handle_settings_command(phone_number, user, None)
                    else:
                        handle_button_response(phone_number, button_id, button_text, user, None)

                elif interactive.get('type') == 'list_reply':
                    list_id = interactive['list_reply']['id']
                    list_title = interactive['list_reply']['title']
                    log_image_event(f"Received list selection: id={list_id}, title={list_title}")

                    if list_id == 'remove_account':
                        handle_remove_account_request(phone_number, user, None)
                    else:
                        handle_button_response(phone_number, list_id, list_title, user, None)

                else:
                    log_image_event(f"Unrecognized interactive type: {interactive.get('type')}")
                    send_message(phone_number, "Unsupported interactive message type. Please try again.")

            elif message_type == 'text':
                message_body = message['text']['body'].lower().strip()
                log_image_event(f"Received text message from {phone_number}: {message_body}")
                handle_text_message(phone_number, message_body, user, None)

            elif message_type in ['image', 'document']:
                log_image_event(f"Received {message_type} message from {phone_number}")
                handle_media_message(phone_number, message, message_type, user, None)

            else:
                log_image_event(f"Unsupported message type '{message_type}' from {phone_number}")
                send_message(phone_number, "Unsupported message type. Please send text, image, or document.")

        # Mark message as processed
        if USE_MONGODB:
            try:
                mongo_db.processed_messages.insert_one({
                    "message_id": message_id,
                    "processed_at": datetime.utcnow()
                })
                log_image_event(f"Message {message_id} marked as processed in MongoDB")
            except Exception:
                pass  # Already processed, ignore duplicate key error
        else:
            conn = get_db_connection()
            try:
                conn.execute('INSERT INTO processed_messages (message_id) VALUES (?)', (message_id,))
                conn.commit()
            finally:
                conn.close()

    except Exception as e:
        log_image_event(f"Error processing message {message_id}: {str(e)}")
        log_image_event(traceback.format_exc())
        try:
            send_message(phone_number, "An error occurred. Please try again or contact support if the issue persists.")
        except Exception:
            pass



# def handle_text_message(phone_number, message_body, user, conn):
#     """Handle text messages with MongoDB/SQLite support"""
#     log_image_event(f"Handling text message for {phone_number}: {message_body}")
#     message_lower = message_body.lower().strip()

#     try:
#         # Always allow switching to quiz, records, or settings
#         if message_lower in ['quiz', 'start quiz', 'records', 'record keeping', 'settings']:
#             if message_lower in ['quiz', 'start quiz']:
#                 handle_quiz_selection(phone_number, message_body, user, conn)
#             elif message_lower in ['records', 'record keeping']:
#                 if USE_MONGODB:
#                     db.update_user_field(phone_number, {"state": "records"})
#                 else:
#                     db.update_user_field(phone_number, {"state": "records"})
#                 send_message(phone_number, f"Welcome {user['name']}, please upload your business record as an image or PDF.")
#             elif message_lower == 'settings':
#                 handle_settings_command(phone_number, user, conn)
#             return

#         # Handle account removal
#         if user['state'] == 'removing_account':
#             if message_lower == 'yes':
#                 remove_user_account(phone_number, conn)
#             elif message_lower == 'no':
#                 handle_settings_command(phone_number, user, conn)
#             else:
#                 send_message(phone_number, "Please respond with 'yes' to confirm account removal or 'no' to cancel.")
#             return

#         # Handle name change
#         if user['state'] == 'changing_name':
#             new_name = standardize_user_input(message_body.strip(), 'name')
            
#             if USE_MONGODB:
#                 db.update_user_field(phone_number, {
#                     "name": new_name,
#                     "state": user.get('previous_state', 'main_menu')
#                 })
#             else:
#                 db.update_user_field(phone_number, {"name": new_name, "state": user['previous_state']})
            
#             send_message(phone_number, f"Your name has been updated to: {new_name}")
#             user = db.get_user_by_phone(phone_number) if USE_MONGODB else db.get_user_by_phone(phone_number,)
#             present_options(phone_number, user, conn)
#             return

#         # Step-by-step profile completion flow
#         if user['state'] == 'awaiting_full_info':
#             standardized_name = standardize_user_input(message_body, 'name')
            
#             if USE_MONGODB:
#                 db.update_user_field(phone_number, {
#                     "name": standardized_name,
#                     "state": "awaiting_age"
#                 })
#             else:
#                 db.update_user_field(phone_number, {"name": standardized_name, "state": "awaiting_age"})
            
#             send_message(phone_number, f"Nice to meet you, {standardized_name}! Please type your age in the chat.")

#         elif user['state'] == 'awaiting_age':
#             if USE_MONGODB:
#                 db.update_user_field(phone_number, {
#                     "age": message_body,
#                     "state": "awaiting_gender"
#                 })
#             else:
#                 db.update_user_field(phone_number, {"age": message_body, "state": "awaiting_gender"})
            
#             send_message(phone_number, "Thank you! Please type your gender in the chat (male, female, or other).")

#         elif user['state'] == 'awaiting_gender':
#             if USE_MONGODB:
#                 db.update_user_field(phone_number, {
#                     "gender": message_body,
#                     "state": "awaiting_business_type"
#                 })
#             else:
#                 db.update_user_field(phone_number, {"gender": message_body, "state": "awaiting_business_type"})
            
#             send_message(phone_number, "Great! Please type in the chat the type of business or services you deal with.")

#         elif user['state'] == 'awaiting_business_type':
#             standardized_business_type = standardize_user_input(message_body, 'business_type')
            
#             if USE_MONGODB:
#                 db.update_user_field(phone_number, {
#                     "business_type": standardized_business_type,
#                     "state": "awaiting_location"
#                 })
#             else:
#                 db.update_user_field(phone_number, {"business_type": standardized_business_type, "state": "awaiting_location"})
            
#             handle_location_selection(phone_number, user, conn)

#         elif user['state'] == 'awaiting_location':
#             standardized_location = standardize_user_input(message_body, 'location')
            
#             if USE_MONGODB:
#                 db.update_user_field(phone_number, {
#                     "location": standardized_location,
#                     "state": "awaiting_business_size"
#                 })
#             else:
#                 db.update_user_field(phone_number, {"location": standardized_location, "state": "awaiting_business_size"})
            
#             handle_business_size_selection(phone_number, user, conn)

#         elif user['state'] == 'awaiting_business_size':
#             if USE_MONGODB:
#                 db.update_user_field(phone_number, {
#                     "business_size": message_body,
#                     "state": "awaiting_financial_status"
#                 })
#             else:
#                 db.update_user_field(phone_number, {"business_size": message_body, "state": "awaiting_financial_status"})
            
#             handle_financial_status_selection(phone_number, user, conn)

#         elif user['state'] == 'awaiting_financial_status':
#             if USE_MONGODB:
#                 db.update_user_field(phone_number, {
#                     "financial_status": message_body,
#                     "state": "awaiting_main_challenge"
#                 })
#             else:
#                 db.update_user_field(phone_number, {"financial_status": message_body, "state": "awaiting_main_challenge"})
            
#             handle_main_challenge_selection(phone_number, user, conn)

#         elif user['state'] == 'awaiting_main_challenge':
#             if USE_MONGODB:
#                 db.update_user_field(phone_number, {
#                     "main_challenge": message_body,
#                     "state": "awaiting_record_keeping"
#                 })
#             else:
#                 db.update_user_field(phone_number, {"main_challenge": message_body, "state": "awaiting_record_keeping"})
            
#             handle_record_keeping_selection(phone_number, user, conn)

#         elif user['state'] == 'awaiting_record_keeping':
#             if USE_MONGODB:
#                 db.update_user_field(phone_number, {
#                     "record_keeping": message_body,
#                     "state": "awaiting_growth_goal"
#                 })
#             else:
#                 db.update_user_field(phone_number, {"record_keeping": message_body, "state": "awaiting_growth_goal"})
            
#             handle_growth_goal_selection(phone_number, user, conn)

#         elif user['state'] == 'awaiting_growth_goal':
#             if USE_MONGODB:
#                 db.update_user_field(phone_number, {
#                     "growth_goal": message_body,
#                     "state": "awaiting_funding_need"
#                 })
#             else:
#                 db.update_user_field(phone_number, {"growth_goal": message_body, "state": "awaiting_funding_need"})
            
#             handle_funding_need_selection(phone_number, user, conn)

#         elif user['state'] == 'awaiting_funding_need':
#             if USE_MONGODB:
#                 db.update_user_field(phone_number, {
#                     "funding_need": message_body,
#                     "state": "awaiting_choice"
#                 })
#             else:
#                 db.update_user_field(phone_number, {"funding_need": message_body, "state": "awaiting_choice"})
            
#             send_message(phone_number, "Thank you! We now understand your business better. What would you like to do next?")
#             present_options(phone_number, user, conn)

#         elif user['state'] in ['awaiting_choice', 'main_menu']:
#             send_message(phone_number, "Please choose 'Record Keeping' or 'Start Quiz'.")
#             present_options(phone_number, user, conn)

#         elif user['state'] in ['ai_chat', 'awaiting_followup', 'post_explanation', 'awaiting_action', 'awaiting_explanation']:
#             # Store follow-up question
#             if USE_MONGODB:
#                 from db_mongo import get_mongo_db
#                 mongo_db = get_mongo_db()
#                 user_id = str(user['_id'])
#                 mongo_db.followup_questions.insert_one({
#                     "user_id": user_id,
#                     "question": message_body,
#                     "timestamp": datetime.utcnow()
#                 })
#             else:
#                 cursor = conn.cursor()
#                 cursor.execute('INSERT INTO followup_questions (user_id, question) VALUES (?, ?)',
#                              (user['id'], message_body))
#                 conn.commit()
            
#             handle_ai_chat(phone_number, message_body, conn)
            
#             if USE_MONGODB:
#                 db.update_user_field(phone_number, {"state": "ai_chat"})
#             else:
#                 db.update_user_field(phone_number, {"state": "ai_chat"})

#         elif user['state'] == 'selecting_quiz':
#             handle_quiz_selection(phone_number, message_body, user, conn)

#         elif user['state'].startswith('quiz_'):
#             handle_quiz_response(phone_number, message_body, user, conn)

#         elif user['state'] == 'records':
#             send_message(phone_number, f"Welcome {user['name']}, please upload your business record as an image or PDF.")

#         else:
#             send_message(phone_number, "Invalid input. Please type 'records' to begin record keeping or 'quiz' to start the quiz.")
        
#         # Occasional reminder
#         if random.random() < 0.005:
#             send_message(phone_number, "Remember, you can type 'records', 'quiz', or 'settings' at any time to switch.")

#     except Exception as e:
#         log_image_event(f"Error in handle_text_message: {str(e)}")
#         log_image_event(traceback.format_exc())
#         send_message(phone_number, "Sorry, something went wrong. Please try again or contact support.")
#         present_options(phone_number, user, conn)



        

def generate_random_number(user_id):
    seed = f"user_{user_id}_seed"
    hash_object = hashlib.md5(seed.encode())
    random.seed(hash_object.hexdigest())
    return ''.join(random.choices(string.digits, k=6))

 


def handle_media_message(phone_number, message, message_type, user, conn):
    log_image_event(f"Handling media message for user {phone_number}")

    if user['state'] != 'records':
        send_message(phone_number, "To upload a record, please select the 'Record Keeping' option first.")
        present_options(phone_number, user, conn)
        return

    media_id = message[message_type]['id']
    media_url = f"https://graph.facebook.com/v11.0/{media_id}"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}

    try:
        response = requests.get(media_url, headers=headers)
        if response.status_code == 200:
            file_url = response.json()['url']
            file_content = requests.get(file_url, headers=headers).content

            user_id = str(user['_id']) if USE_MONGODB else user['id']
            filename = secure_filename(f"{user_id}_{media_id}.{'jpg' if message_type == 'image' else 'pdf'}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            with open(file_path, 'wb') as f:
                f.write(file_content)

            random_number = generate_random_number(user_id)

            if USE_MONGODB:
                from db_mongo import get_mongo_db
                mongo_db = get_mongo_db()
                mongo_db.records.insert_one({
                    "user_id": user_id,
                    "media_url": filename,
                    "upload_date": datetime.utcnow()
                })
                db.update_user_field(phone_number, {
                    "random_number": random_number,
                    "state": "awaiting_choice"
                })
            else:
                conn.execute(
                    'UPDATE users SET random_number = ?, state = ? WHERE id = ?',
                    (random_number, 'awaiting_choice', user['id'])
                )
                conn.execute(
                    'INSERT INTO records (user_id, media_url) VALUES (?, ?)',
                    (user['id'], filename)
                )
                conn.commit()

            base_url = "https://empowerbot2025-1.onrender.com"
            user_url = f"{base_url}/user/{user_id}/{random_number}"
            thank_you_message = (
                f"Thank you {user['name']}! Your record has been uploaded successfully. "
                f"You can view your records here: {user_url}"
            )
            send_message(phone_number, thank_you_message)
            user = db.get_user_by_phone(phone_number)
            present_options(phone_number, user, conn)
        else:
            send_message(phone_number, "Sorry, there was an error processing your file. Please try again.")
            present_options(phone_number, user, conn)

    except Exception as e:
        log_image_event(f"Unexpected error in handle_media_message: {str(e)}")
        log_image_event(traceback.format_exc())
        send_message(phone_number, "An unexpected error occurred. Please try again or contact support.")
        present_options(phone_number, user, conn)


       
       
      
       
       
def present_options(phone_number, user, conn):
    """Present main options - MongoDB compatible"""
    log_image_event(f"Presenting main options to user {phone_number}")
    
    buttons = [
        {"type": "reply", "reply": {"id": "quiz", "title": "Start Quiz"}},
        {"type": "reply", "reply": {"id": "records", "title": "Record Keeping"}},
        {"type": "reply", "reply": {"id": "settings", "title": "Settings"}}
    ]
    
    send_interactive_message(phone_number, "What would you like to do next?", buttons)
    
    # Use database adapter instead of conn.execute()
    db.update_user_field(phone_number, {"state": "main_menu"})
    
    log_image_event(f"Updated user {phone_number} state to main_menu")

    
 


       
       
def handle_records_command(phone_number, user, conn):
    message = f"Welcome to Record Keeping, {user['name']}! Please upload your business record as an image or PDF."
    send_message(phone_number, message)
    db.update_user_field(phone_number, {"state": "records"})
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
#                 db.update_user_field(phone_number, {"state": "records"})
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
#             user = db.get_user_by_phone(phone_number,)
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
#             db.update_user_field(phone_number, {"state": "ai_chat"})
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
#                 db.update_user_field(phone_number, {"state": "records"})
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
#             user = db.get_user_by_phone(phone_number,)
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
#             db.update_user_field(phone_number, {"state": "ai_chat"})
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
    try:
        logging.info(f"handle_quiz_review called with quiz_selection: {quiz_selection}")

        quiz_match = re.search(r'(quiz\d+)', quiz_selection)
        if quiz_match:
            quiz_name = quiz_match.group(1)
        else:
            quiz_name = quiz_selection.split(" ")[0]

        logging.info(f"Extracted quiz_name: {quiz_name}")

        user_id = str(user['_id']) if USE_MONGODB else user['id']

        if USE_MONGODB:
            from db_mongo import get_mongo_db
            mongo_db = get_mongo_db()
            count = mongo_db.responses.count_documents({
                "user_id": user_id,
                "quiz": quiz_name,
                "correct": False
            })
        else:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM responses
                WHERE user_id = ? AND quiz = ? AND correct = 0
            """, (user_id, quiz_name))
            count = cursor.fetchone()[0]

        logging.info(f"Found {count} incorrect answers for user {user_id} in quiz {quiz_name}")

        if count == 0:
            send_message(phone_number, f"No incorrect answers found for {quiz_name}.")
            present_options(phone_number, user, conn)
            return

        incorrect_questions = get_incorrect_questions(user_id, conn, quiz_name)

        if incorrect_questions is None:
            logging.error(f"Database error while getting incorrect questions")
            send_message(phone_number, "An error occurred while retrieving your incorrect answers. Please try again.")
            present_options(phone_number, user, conn)
            return

        if not incorrect_questions:
            send_message(phone_number, f"No incorrect answers found for {quiz_name}.")
            present_options(phone_number, user, conn)
            return

        logging.info(f"First incorrect question: {incorrect_questions[0]}")

        db.update_user_field(phone_number, {
            "state": "reviewing_question",
            "quiz_in_review": quiz_name,
            "current_question": 0
        })

        # Refresh user object after update
        user = db.get_user_by_phone(phone_number)
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
            Convert this input: "{input_text}" into a properly formatted full name (first and last name).
            Rules:
            - Keep BOTH first name AND last name (surname)
            - Capitalize the first letter of each name
            - Remove any titles (Mr., Mrs., Dr., etc.), suffixes (Jr., Sr., III), or nicknames
            - Return ONLY the first and last name, no extra text, NO quotes, NO special characters
            - If only one name is provided, keep it as is
            - Output should be plain text only
            
            Example inputs/outputs:
            My name is John Smith → John Smith
            mrs. sarah johnson → Sarah Johnson
            MICHAEL PHELPS JR → Michael Phelps
            "Jane Doe" → Jane Doe
            abiola oyebanjo → Abiola Oyebanjo
            Mr. David Brown III → David Brown
            chioma → Chioma
            BLESSING ADEBAYO → Blessing Adebayo
            """,
            
        'business_type': f"""
            Convert this business description: "{input_text}" into a standardized "[type] business" format.
            Rules:
            - Remove phrases like "I sell", "we deal in", "I do", etc.
            - Convert to "[type] business" format
            - Capitalize first letter
            - Return only the business type, no extra text, NO quotes
            Example inputs/outputs:
            I sell food and drinks → Food business
            We deal in baby clothes → Clothing business
            I do hair styling → Salon business
            """,
            
        'location': f"""
            Convert this location description: "{input_text}" into a standardized location name.
            Rules:
            - Extract main location name
            - Capitalize first letter
            - Remove extra words like "I'm at", "located in", etc.
            - Return only the location name, no extra text, NO quotes
            Example inputs/outputs:
            I dey for Ikeja → Ikeja
            My shop is in surulere → Surulere
            located at LEKKI → Lekki
            """
    }
    
    try:
        standardized = generate_text(standardization_prompts[field_type]).strip()
        
        # Additional cleanup to ensure single-line response
        standardized = standardized.split('\n')[0].strip()
        
        # ✅ CRITICAL FIX: Remove quotes and extra whitespace
        # Remove both double and single quotes from start and end
        standardized = standardized.strip('"').strip("'").strip()
        
        # Remove any remaining quotes if AI wrapped the response
        if standardized.startswith('"') and standardized.endswith('"'):
            standardized = standardized[1:-1]
        if standardized.startswith("'") and standardized.endswith("'"):
            standardized = standardized[1:-1]
            
        # Remove any markdown code block formatting
        standardized = standardized.replace('```', '').replace('`', '').strip()
        
        # Remove any "Output:" or "Result:" prefixes that AI might add
        for prefix in ['Output:', 'Result:', 'Answer:', 'Response:']:
            if standardized.startswith(prefix):
                standardized = standardized[len(prefix):].strip()
        
        # Final cleanup - remove any remaining quotes
        standardized = standardized.strip('"').strip("'").strip()
        
        # For names specifically, ensure proper capitalization
        if field_type == 'name':
            # Split by space and capitalize each word (handles "abiola oyebanjo" → "Abiola Oyebanjo")
            name_parts = standardized.split()
            standardized = ' '.join(word.capitalize() for word in name_parts if word)
        
        logging.info(f"Standardized {field_type}: '{input_text}' → '{standardized}'")
        
        return standardized
        
    except Exception as e:
        logging.error(f"Error in input standardization for {field_type}: {e}")
        # Fallback to basic capitalization if AI fails
        fallback = input_text.strip().strip('"').strip("'").strip()
        
        if field_type == 'name':
            # For names, capitalize each word
            name_parts = fallback.split()
            return ' '.join(word.capitalize() for word in name_parts if word)
        else:
            return fallback.capitalize()
        




def clean_quoted_names_in_database():
    """
    Clean up all user names that have quotes around them.
    This fixes the bug where AI standardization adds quotes.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Find all users with quoted names
        cursor.execute("""
            SELECT id, name, phone_number 
            FROM users 
            WHERE name LIKE '"%' OR name LIKE '''%'
        """)
        
        users_to_fix = cursor.fetchall()
        
        if not users_to_fix:
            logging.info("No users with quoted names found. Database is clean.")
            return 0
        
        logging.info(f"Found {len(users_to_fix)} users with quoted names. Cleaning...")
        
        # Fix each user
        fixed_count = 0
        for user in users_to_fix:
            user_id = user['id']
            old_name = user['name']
            phone = user['phone_number']
            
            # Remove quotes and clean up
            new_name = old_name.strip('"').strip("'").strip()
            
            # Update the database
            cursor.execute("UPDATE users SET name = ? WHERE id = ?", (new_name, user_id))
            
            logging.info(f"Fixed user {user_id} ({phone}): '{old_name}' → '{new_name}'")
            fixed_count += 1
        
        conn.commit()
        logging.info(f"Successfully cleaned {fixed_count} user names")
        return fixed_count
        
    except Exception as e:
        logging.error(f"Error cleaning quoted names: {e}")
        conn.rollback()
        return 0
    finally:
        conn.close()

      
      
        
        
def handle_text_message(phone_number, message_body, user, conn):
    log_image_event(f"Handling text message for {phone_number}: {message_body}")
    message_lower = message_body.lower().strip()

    try:
        # Always allow switching to quiz, records, or settings
        if message_lower in ['quiz', 'start quiz', 'records', 'record keeping', 'settings']:
            if message_lower in ['quiz', 'start quiz']:
                handle_quiz_selection(phone_number, message_body, user, conn)
            elif message_lower in ['records', 'record keeping']:
                db.update_user_field(phone_number, {"state": "records"})
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

        # Handle name change - direct capitalize, no Gemini
        if user['state'] == 'changing_name':
            new_name = ' '.join(word.capitalize() for word in message_body.strip().split() if word)
            db.update_user_field(phone_number, {"name": new_name, "state": user.get('previous_state', 'main_menu')})
            send_message(phone_number, f"Your name has been updated to: {new_name}")
            user = db.get_user_by_phone(phone_number)
            present_options(phone_number, user, conn)
            return

        # Step-by-step profile completion flow
        if user['state'] == 'awaiting_location_code':
            _code = message_body.strip().upper()
            if _code == 'OPEN':
                db.update_user_field(phone_number, {'state': 'awaiting_full_info'})
                send_message(phone_number, "No problem! Continuing without a location code.\n\nWhat's your full name?")
            else:
                _valid, _loc, _cfg = False, None, None
                if USE_MONGODB:
                    try:
                        from db_mongo import get_mongo_db as _gmdb
                        _mdb = _gmdb()
                        _ldoc = _mdb.location_codes.find_one({'code': _code, 'active': {'$ne': False}})
                        if _ldoc:
                            _valid = True
                            _loc = _ldoc.get('location', 'Unknown')
                            if _ldoc.get('detail'): _loc += ', ' + _ldoc['detail']
                            _cfg = _ldoc.get('config_id')
                    except Exception as _le:
                        logging.warning(f'Location code lookup: {_le}')
                if _valid:
                    _upd = {'state': 'awaiting_full_info', 'location_code': _code, 'location': _loc}
                    if _cfg: _upd['configuration'] = _cfg
                    db.update_user_field(phone_number, _upd)
                    send_message(phone_number, f"✅ Location confirmed: *{_loc}*\n\nWhat's your full name?")
                else:
                    send_message(phone_number, "❌ That code wasn't recognised.\n\nTry again or type *OPEN* to continue.")

        elif user['state'] == 'awaiting_full_info':
            # Direct capitalize - no Gemini
            new_name = ' '.join(word.capitalize() for word in message_body.strip().split() if word)
            db.update_user_field(phone_number, {"name": new_name, "state": "awaiting_age"})
            send_message(phone_number, f"Nice to meet you, {new_name}! Please type your age in the chat.")

        elif user['state'] == 'awaiting_age':
            db.update_user_field(phone_number, {"age": message_body, "state": "awaiting_gender"})
            send_interactive_message(phone_number, "What is your gender?", [
                {"type": "reply", "reply": {"id": "gender_male",   "title": "Male"}},
                {"type": "reply", "reply": {"id": "gender_female", "title": "Female"}},
                {"type": "reply", "reply": {"id": "gender_other",  "title": "Prefer not to say"}},
            ])

        elif user['state'] == 'awaiting_gender':
            _gmap = {"gender_male":"Male","gender_female":"Female","gender_other":"Prefer not to say"}
            _g = _gmap.get(message_body, message_body.capitalize())
            db.update_user_field(phone_number, {"gender": _g, "state": "awaiting_business_type"})
            _bl = {"type":"list","header":{"type":"text","text":"Business type"},"body":{"text":"What type of business or service do you run?"},"footer":{"text":"Scroll to see all options"},"action":{"button":"See options","sections": [{"title": "Select business type", "rows": [{"id": "biz_food", "title": "Food & Beverages"}, {"id": "biz_fashion", "title": "Fashion & Clothing"}, {"id": "biz_beauty", "title": "Hair Salon & Beauty"}, {"id": "biz_trading", "title": "Trading & Merchandise"}, {"id": "biz_transport", "title": "Transport & Logistics"}, {"id": "biz_agric", "title": "Agriculture & Farming"}, {"id": "biz_health", "title": "Healthcare & Pharmacy"}, {"id": "biz_education", "title": "Education & Training"}, {"id": "biz_ict", "title": "ICT & Digital Services"}, {"id": "biz_others", "title": "Others (type your own)"}]}]}}
            send_interactive_message(phone_number, _bl)
        elif user['state'] == 'awaiting_business_type':
            _bmap = {"biz_food":"Food & Beverages","biz_fashion":"Fashion & Clothing","biz_beauty":"Hair Salon & Beauty","biz_electronics":"Electronics & Gadgets","biz_phone":"Phone & Computer Repair","biz_trading":"Trading & Merchandise","biz_agric":"Agriculture & Farming","biz_wholesale":"Wholesale & Distribution","biz_transport":"Transport & Logistics","biz_construction":"Construction & Property","biz_education":"Education & Training","biz_health":"Healthcare & Pharmacy","biz_finance":"Financial Services","biz_auto":"Auto Repair & Parts","biz_events":"Entertainment & Events","biz_media":"Media & Printing","biz_mfg":"Manufacturing","biz_hospitality":"Hospitality & Catering","biz_artisan":"Artisan & Crafts","biz_ict":"ICT & Digital Services","biz_cleaning":"Cleaning & Laundry","biz_photo":"Photography & Video","biz_consulting":"Consulting & Legal"}
            if message_body == "biz_others":
                db.update_user_field(phone_number, {"state": "awaiting_custom_biz_type"})
                send_message(phone_number, "Please type your business type:")
            else:
                _biz = _bmap.get(message_body, " ".join(w.capitalize() for w in message_body.strip().split() if w))
                db.update_user_field(phone_number, {"business_type": _biz, "state": "awaiting_location"})
                handle_location_selection(phone_number, user, conn)

        elif user['state'] == 'awaiting_custom_biz_type':
            _biz = " ".join(w.capitalize() for w in message_body.strip().split() if w)
            db.update_user_field(phone_number, {"business_type": _biz, "state": "awaiting_location"})
            handle_location_selection(phone_number, user, conn)
            handle_location_selection(phone_number, user, conn)

        elif user['state'] == 'awaiting_location':
            # Direct capitalize - no Gemini
            location = ' '.join(word.capitalize() for word in message_body.strip().split() if word)
            db.update_user_field(phone_number, {"location": location, "state": "awaiting_business_size"})
            handle_business_size_selection(phone_number, user, conn)

        elif user['state'] == 'awaiting_business_size':
            db.update_user_field(phone_number, {"business_size": message_body, "state": "awaiting_financial_status"})
            handle_financial_status_selection(phone_number, user, conn)

        elif user['state'] == 'awaiting_financial_status':
            db.update_user_field(phone_number, {"financial_status": message_body, "state": "awaiting_main_challenge"})
            handle_main_challenge_selection(phone_number, user, conn)

        elif user['state'] == 'awaiting_main_challenge':
            db.update_user_field(phone_number, {"main_challenge": message_body, "state": "awaiting_record_keeping"})
            handle_record_keeping_selection(phone_number, user, conn)

        elif user['state'] == 'awaiting_record_keeping':
            db.update_user_field(phone_number, {"record_keeping": message_body, "state": "awaiting_growth_goal"})
            handle_growth_goal_selection(phone_number, user, conn)

        elif user['state'] == 'awaiting_growth_goal':
            db.update_user_field(phone_number, {"growth_goal": message_body, "state": "awaiting_funding_need"})
            handle_funding_need_selection(phone_number, user, conn)

        elif user['state'] == 'awaiting_funding_need':
            db.update_user_field(phone_number, {"funding_need": message_body, "state": "awaiting_choice"})
            send_message(phone_number, "Thank you! We now understand your business better. What would you like to do next?")
            present_options(phone_number, user, conn)

        elif user['state'] in ['awaiting_choice', 'main_menu']:
            send_message(phone_number, "Please choose 'Record Keeping' or 'Start Quiz'.")
            present_options(phone_number, user, conn)

        elif user['state'] in ['ai_chat', 'awaiting_followup', 'post_explanation', 'awaiting_action', 'awaiting_explanation']:
            if USE_MONGODB:
                from db_mongo import get_mongo_db
                mongo_db = get_mongo_db()
                user_id = str(user['_id'])
                mongo_db.followup_questions.insert_one({
                    "user_id": user_id,
                    "question": message_body,
                    "timestamp": datetime.utcnow()
                })
            else:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO followup_questions (user_id, question) VALUES (?, ?)',
                               (user['id'], message_body))
                conn.commit()
            handle_ai_chat(phone_number, message_body, conn)
            db.update_user_field(phone_number, {"state": "ai_chat"})

        elif user['state'] == 'selecting_quiz':
            handle_quiz_selection(phone_number, message_body, user, conn)

        elif user['state'].startswith('quiz_'):
            handle_quiz_response(phone_number, message_body, user, conn)

        elif user['state'] == 'records':
            send_message(phone_number, f"Welcome {user['name']}, please upload your business record as an image or PDF.")

        else:
            send_message(phone_number, "Invalid input. Please type 'records' to begin record keeping or 'quiz' to start the quiz.")

        if random.random() < 0.005:
            send_message(phone_number, "Remember, you can type 'records', 'quiz', or 'settings' at any time to switch.")

    except Exception as e:
        log_image_event(f"Error in handle_text_message: {str(e)}")
        log_image_event(traceback.format_exc())
        send_message(phone_number, "Sorry, something went wrong. Please try again or contact support.")
        present_options(phone_number, user, conn)


        
        
        
        
        
        
def end_ai_chat(phone_number, user, conn):
    db.update_user_field(phone_number, {"state": "awaiting_choice", "current_question": None})
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
        time.sleep(5)

        user_id = str(user['_id']) if USE_MONGODB else user['id']

        if USE_MONGODB:
            from db_mongo import get_mongo_db
            mongo_db = get_mongo_db()

            # Get quizzes with incorrect answers
            pipeline = [
                {"$match": {"user_id": user_id, "correct": False}},
                {"$group": {"_id": "$quiz", "incorrect_count": {"$sum": 1}}},
                {"$sort": {"_id": 1}}
            ]
            quizzes = list(mongo_db.responses.aggregate(pipeline))

        else:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.quiz, COUNT(*) as incorrect_count
                FROM responses r
                WHERE r.user_id = ? AND r.correct = 0
                GROUP BY r.quiz
                ORDER BY CAST(SUBSTR(r.quiz, 5) AS INTEGER)
            """, (user_id,))
            quizzes_raw = cursor.fetchall()
            quizzes = [{"_id": row[0], "incorrect_count": row[1]} for row in quizzes_raw]

        if not quizzes:
            send_message(phone_number, "Great job! You haven't missed any questions. Would you like to start a new quiz?")
            present_options(phone_number, user, conn)
            return

        db.update_user_field(phone_number, {"state": "reviewing_quiz"})

        if len(quizzes) <= 3:
            buttons = [{
                "type": "reply",
                "reply": {
                    "id": f"{q['_id']} ({q['incorrect_count']} incorrect)",
                    "title": f"{q['_id']} ({q['incorrect_count']} incorrect)"
                }
            } for q in quizzes]
            send_interactive_message(phone_number, "Select a quiz to review:", buttons)

        else:
            sections = []
            current_section = []
            last_section_start = 0

            for q in quizzes:
                quiz_name = q['_id']
                incorrect_count = q['incorrect_count']
                try:
                    quiz_num = int(quiz_name.replace('quiz', ''))
                except:
                    continue
                section_start = (quiz_num // 10) * 10

                if section_start != last_section_start and current_section:
                    sections.append({
                        "title": f"Quizzes {last_section_start + 1}-{last_section_start + 10}",
                        "rows": current_section
                    })
                    current_section = []
                    last_section_start = section_start

                current_section.append({
                    "id": f"{quiz_name} ({incorrect_count} incorrect)",
                    "title": f"{quiz_name} ({incorrect_count} incorrect)"
                })

            if current_section:
                sections.append({
                    "title": f"Quizzes {last_section_start + 1}-{last_section_start + 10}",
                    "rows": current_section
                })

            send_quiz_list_button(phone_number, "Select a quiz to review", "View Quizzes", sections)

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
        db.update_user_field(phone_number, {"state": "settings", "previous_state": previous_state})

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
        db.update_user_field(phone_number, {"temp_data": temp_data})

        log_image_event(f"Settings command handled successfully for user {phone_number}.")

    except Exception as e:
        log_image_event(f"Error in settings command for user {phone_number}: {e}")


  
  
# def handle_settings_command(phone_number, user, conn):
#     # Create a list of options for settings
#     list_options = [
#         {"id": "change_name", "title": "Change Name"},
#         {"id": "view_quiz_names", "title": "View Quiz Names"},
#         {"id": "view_scores", "title": "View Scores"},
#         {"id": "view_name", "title": "View Name"},
#         {"id": "back", "title": "Back"}
#     ]
#     # Prepare the list message with options
#     list_message = {
#         "type": "list",
#         "header": {
#             "type": "text",
#             "text": "Settings"
#         },
#         "body": {
#             "text": "Choose an option:"
#         },
#         "action": {
#             "button": "Select",
#             "sections": [
#                 {
#                     "title": "Settings Options",
#                     "rows": list_options
#                 }
#             ]
#         }
#     }
#     # Send the interactive message with the list
#     success, message = send_interactive_message(phone_number, list_message)
#     if not success:
#         log_image_event(f"Failed to send interactive message: {message}")
#         return
#     # Update the user's state and other relevant data
#     previous_state = user['state']
#     try:
#         conn.execute('UPDATE users SET state = ?, previous_state = ? WHERE phone_number = ?',
#                      ('settings', previous_state, phone_number))
#         conn.commit()
#         cursor = conn.cursor()
#         # Fetch and update user-related data
#         cursor.execute("SELECT name FROM users WHERE phone_number = ?", (phone_number,))
#         name_result = cursor.fetchone()
#         user_name = name_result[0] if name_result else "Unknown"
#         cursor.execute("SELECT DISTINCT quiz FROM questions")
#         quiz_names = [row[0] for row in cursor.fetchall()]
#         cursor.execute("""
#             SELECT quiz, COUNT(*) as total_questions, SUM(correct) as correct_answers
#             FROM responses
#             WHERE user_id = ?
#             GROUP BY quiz
#         """, (user['id'],))
#         scores = cursor.fetchall()
#         # Convert scores to a serializable format
#         scores_serialized = [{"quiz": row[0], "total_questions": row[1], "correct_answers": row[2]} for row in scores]
#         temp_data = json.dumps({
#             "name": user_name,
#             "quiz_names": quiz_names,
#             "scores": scores_serialized
#         })
#         db.update_user_field(phone_number, {"temp_data": temp_data})
#         conn.commit()
#         log_image_event(f"Settings command handled successfully for user {phone_number}.")
#     except Exception as e:
#         log_image_event(f"Error in settings command for user {phone_number}: {e}")
        
        
        


def handle_settings_command(phone_number, user, conn):
    log_image_event(f"Starting settings command for {phone_number}")

    list_options = [
        {"id": "change_name", "title": "Change Name"},
        {"id": "view_quiz_names", "title": "View Quiz Names"},
        {"id": "view_scores", "title": "View Scores"},
        {"id": "view_name", "title": "View Name"},
        {"id": "remove_account", "title": "Remove Account"},
        {"id": "back", "title": "Back"}
    ]

    list_message = {
        "type": "list",
        "header": {"type": "text", "text": "Settings"},
        "body": {"text": "Choose an option:"},
        "action": {
            "button": "Select",
            "sections": [{"title": "Settings Options", "rows": list_options}]
        }
    }

    try:
        success, message = send_interactive_message(phone_number, list_message)
        if not success:
            raise Exception(f"Failed to send settings menu: {message}")
        log_image_event(f"Successfully sent settings menu to {phone_number}")
    except Exception as e:
        log_image_event(f"Error sending settings menu: {str(e)}")
        send_message(phone_number, "An error occurred displaying settings. Please try again.")
        return

    db.update_user_field(phone_number, {"state": "settings"})
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
        db.update_user_field(phone_number, {"state": "removing_account"})
        log_image_event(f"Sent account removal confirmation to {phone_number}")
    else:
        log_image_event(f"Failed to send account removal confirmation to {phone_number}: {message}")
        # Fallback to plain text message
        fallback_message = "Are you sure you want to remove your account? This action cannot be undone. All your data will be permanently deleted. Reply with 'YES' to confirm or 'NO' to cancel."
        send_message(phone_number, fallback_message)
        db.update_user_field(phone_number, {"state": "removing_account"})
        
        
        

def remove_user_account(phone_number, conn):
    try:
        if USE_MONGODB:
            from db_mongo import get_mongo_db
            mongo_db = get_mongo_db()

            user = mongo_db.users.find_one({"phone_number": phone_number})
            if not user:
                send_message(phone_number, "Account not found.")
                return

            user_id = str(user['_id'])
            logging.info(f"Starting MongoDB account deletion for user_id={user_id}, phone={phone_number}")

            collections_to_clean = [
                'responses', 'quiz_states', 'conversation_history',
                'followup_questions', 'explanation_history', 'user_scores',
                'user_products', 'records', 'post10_quiz_responses',
                'post10_quizzes', 'processed_messages'
            ]

            deletion_summary = {}
            for collection_name in collections_to_clean:
                try:
                    result = mongo_db[collection_name].delete_many({"user_id": user_id})
                    deletion_summary[collection_name] = result.deleted_count
                except Exception as e:
                    logging.error(f"Error deleting from {collection_name}: {e}")

            mongo_db.users.delete_one({"_id": user['_id']})
            deletion_summary['users'] = 1

            summary_text = "\n".join([f"• {k}: {v} items" for k, v in deletion_summary.items() if v > 0])
            send_message(phone_number,
                f"✅ Your account has been completely removed.\n\n"
                f"Deleted data:\n{summary_text}\n\n"
                f"You can create a new account anytime by messaging us again.")
            logging.info(f"✅ Successfully deleted all MongoDB data for user {user_id}")

        else:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE phone_number = ?", (phone_number,))
            user_result = cursor.fetchone()

            if user_result is None:
                send_message(phone_number, "Account not found.")
                return

            user_id = user_result[0]
            logging.info(f"Starting SQLite account deletion for user_id={user_id}")

            deletion_steps = [
                {"table": "post10_quiz_responses",
                 "query": "DELETE FROM post10_quiz_responses WHERE quiz_id IN (SELECT id FROM post10_quizzes WHERE user_id = ?)",
                 "params": (user_id,)},
                {"table": "post10_quizzes", "query": "DELETE FROM post10_quizzes WHERE user_id = ?", "params": (user_id,)},
                {"table": "responses", "query": "DELETE FROM responses WHERE user_id = ?", "params": (user_id,)},
                {"table": "quiz_states", "query": "DELETE FROM quiz_states WHERE user_id = ?", "params": (user_id,)},
                {"table": "conversation_history", "query": "DELETE FROM conversation_history WHERE user_id = ?", "params": (user_id,)},
                {"table": "followup_questions", "query": "DELETE FROM followup_questions WHERE user_id = ?", "params": (user_id,)},
                {"table": "explanation_history", "query": "DELETE FROM explanation_history WHERE user_id = ?", "params": (user_id,)},
                {"table": "user_scores", "query": "DELETE FROM user_scores WHERE user_id = ?", "params": (user_id,)},
                {"table": "user_products", "query": "DELETE FROM user_products WHERE user_id = ?", "params": (user_id,)},
                {"table": "records", "query": "DELETE FROM records WHERE user_id = ?", "params": (user_id,)},
                {"table": "users", "query": "DELETE FROM users WHERE id = ?", "params": (user_id,)},
            ]

            for step in deletion_steps:
                cursor.execute(step['query'], step['params'])

            conn.commit()
            send_message(phone_number,
                "✅ Your account has been completely removed.\n\n"
                "You can create a new account anytime by messaging us again.")

    except Exception as e:
        logging.error(f"Error in remove_user_account for {phone_number}: {e}")
        logging.error(traceback.format_exc())
        send_message(phone_number, "An error occurred while removing your account. Please try again or contact support.")




        


       
       
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
    db.update_user_field(phone_number, {"state": "records"})
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

#     db.update_user_field(phone_number, {"state": "selecting_quiz"})
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

#     db.update_user_field(phone_number, {"state": "selecting_quiz"})
#     conn.commit()

    
  
def handle_quiz_command(phone_number, user, conn):
    print(f"🔥 DEBUG: handle_quiz_command called for {phone_number}")
    logging.info(f"📱 handle_quiz_command called for {phone_number}")

    load_quiz_visibility_from_db()
    quiz_visibility = app.config.get('QUIZ_VISIBILITY', {})

    all_quizzes = list_available_quizzes()
    available_quizzes = []
    for quiz_num in all_quizzes:
        quiz_name = f"quiz{quiz_num}"
        is_enabled = quiz_visibility.get(quiz_name, True)
        if is_enabled:
            available_quizzes.append(quiz_num)

    logging.info(f"🔍 available_quizzes after filtering: {len(available_quizzes)}")

    quiz_statuses = {
        f"quiz{quiz}": get_quiz_status(conn, user['id'], f"quiz{quiz}")
        for quiz in available_quizzes
    }
    completed_quizzes = [quiz for quiz, status in quiz_statuses.items() if status == "completed"]
    in_progress_quizzes = [quiz for quiz, status in quiz_statuses.items() if status == "in_progress"]
    uncompleted_quizzes = [quiz for quiz, status in quiz_statuses.items() if status == "not_started"]

    if not available_quizzes:
        send_message(phone_number, "No quiz is currently available. Please check back later.")
        buttons = [
            {"type": "reply", "reply": {"id": "ai_chat", "title": "Chat with AI"}},
            {"type": "reply", "reply": {"id": "records", "title": "Record Keeping"}},
        ]
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

    # Always include Chat with AI button
    buttons = [
        {"type": "reply", "reply": {"id": "ai_chat", "title": "Chat with AI"}},
    ]

    if in_progress_quizzes:
        buttons.append({
            "type": "reply",
            "reply": {
                "id": in_progress_quizzes[0],
                "title": f"Continue {in_progress_quizzes[0]}"
            }
        })
    elif uncompleted_quizzes:
        buttons.append({
            "type": "reply",
            "reply": {
                "id": uncompleted_quizzes[0],
                "title": f"Start {uncompleted_quizzes[0]}"
            }
        })

    send_interactive_message(phone_number, "What would you like to do?", buttons)
    db.update_user_field(phone_number, {"state": "selecting_quiz"})


    
    
    
def is_quiz_enabled(quiz_name):
    """Check if a quiz is enabled - MongoDB/SQLite compatible"""
    if USE_MONGODB:
        from db_mongo import get_mongo_db
        try:
            mongo_db = get_mongo_db()
            quiz_status = mongo_db.quiz_status.find_one({"quiz": quiz_name})
            
            if quiz_status:
                return bool(quiz_status.get('enabled', True))
            else:
                return True  # Default to enabled if not found
        except Exception as e:
            print(f"Error checking quiz enabled status in MongoDB: {e}")
            return True  # Default to enabled on error
    else:
        # SQLite version
        conn = db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT enabled FROM quiz_status WHERE quiz = ?", (quiz_name,))
            result = cursor.fetchone()
            
            if result:
                return bool(result[0])
            else:
                return True  # Default to enabled if not found
        except Exception as e:
            print(f"Error checking quiz enabled status in SQLite: {e}")
            return True  # Default to enabled on error
        finally:
            conn.close()





      

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

        # Check if the selected quiz is currently enabled
        if not is_quiz_enabled(selected_quiz):
            send_message(phone_number, f"{selected_quiz} is currently unavailable. Please choose another quiz.")
            handle_quiz_command(phone_number, user, conn)
            return

        # Check quiz status using MongoDB
        status = get_quiz_status(conn, user['id'], selected_quiz)

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
    user_id = str(user['_id']) if USE_MONGODB else user['id']
    quiz_state = check_quiz_state(conn, user_id, selected_quiz)
    question_index = quiz_state['question_index'] if quiz_state else 0

    if not quiz_state:
        if USE_MONGODB:
            from db_mongo import get_mongo_db
            mongo_db = get_mongo_db()
            mongo_db.quiz_states.insert_one({
                "user_id": user_id,
                "quiz_name": selected_quiz,
                "question_index": question_index
            })
        else:
            conn.execute('INSERT INTO quiz_states (user_id, quiz_name, question_index) VALUES (?, ?, ?)',
                         (user_id, selected_quiz, question_index))

    db.update_user_field(phone_number, {"current_quiz": selected_quiz, "state": f'quiz_{question_index}'})

    action = "Resuming" if quiz_state else "Starting"
    log_image_event(f"{action} {selected_quiz} for user {user_id} at question {question_index}")
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
       
#         db.update_user_field(phone_number, {"state": "awaiting_choice", "current_quiz": ""})
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
#             db.update_user_field(phone_number, {"state": "awaiting_choice", "current_quiz": ""})
#             conn.commit()
#         except Exception as e:
#             log_image_event(f"Error resetting user state in finish_quiz for user {user['id']}: {str(e)}")
           
         
         
         
         
def finish_quiz(phone_number, user, conn, current_quiz, num_questions):
    try:
        log_image_event(f"Finishing quiz {current_quiz} for user {user['id']}")

        user_id = str(user['_id']) if USE_MONGODB else user['id']

        try:
            quiz_number = int(current_quiz[4:])
        except ValueError:
            quiz_number = 0

        # Get total correct
        if USE_MONGODB:
            from db_mongo import get_mongo_db
            mongo_db = get_mongo_db()
            total_correct = mongo_db.responses.count_documents({
                "user_id": user_id,
                "quiz": current_quiz,
                "correct": True
            })
        else:
            total_correct = conn.execute(
                "SELECT COUNT(*) AS total_correct FROM responses WHERE user_id = ? AND quiz = ? AND correct = 1",
                (user['id'], current_quiz)
            ).fetchone()[0]

        if quiz_number <= 10:
            congratulations_message = f"Congratulations! You've completed the quiz. You scored {total_correct} out of {num_questions} questions correctly."
            send_message(phone_number, congratulations_message)
        else:
            send_message(phone_number, f"Congratulations! You've completed the quiz. You scored {total_correct} out of {num_questions} questions correctly.")

        # Update user state
        db.update_user_field(phone_number, {"state": "awaiting_choice", "current_quiz": ""})

        # Mark quiz as completed in quiz_states
        if USE_MONGODB:
            from db_mongo import get_mongo_db
            mongo_db = get_mongo_db()
            mongo_db.quiz_states.update_one(
                {"user_id": user_id, "quiz_name": current_quiz},
                {"$set": {"question_index": -1, "state": "completed"}},
                upsert=True
            )
        else:
            conn.execute(
                "UPDATE quiz_states SET question_index = -1 WHERE user_id = ? AND quiz_name = ?",
                (user['id'], current_quiz)
            )
            conn.commit()

        log_image_event(f"Database updated for user {user['id']} after finishing quiz {current_quiz}")

        buttons = [
            {"type": "reply", "reply": {"id": "quiz",     "title": "Take Another Quiz"}},
            {"type": "reply", "reply": {"id": "records",  "title": "Switch to Records"}},
            {"type": "reply", "reply": {"id": "ai_chat",  "title": "Review Mistakes (AI)"}}
        ]
        success = send_interactive_message(phone_number, "What would you like to do next?", buttons)

        if not success:
            send_message(phone_number, "What would you like to do next? Type 'quiz' to take another quiz or 'records' to switch to record keeping.")

        log_image_event(f"Quiz {current_quiz} finished successfully for user {user['id']}")

    except Exception as e:
        log_image_event(f"Error in finish_quiz for user {user['id']}: {str(e)}")
        log_image_event(traceback.format_exc())
        send_message(phone_number, "An error occurred while finishing the quiz. Please type 'quiz' to start over or 'records' to switch to record keeping.")

    finally:
        try:
            db.update_user_field(phone_number, {"state": "awaiting_choice", "current_quiz": ""})
        except Exception as e:
            log_image_event(f"Error resetting user state in finish_quiz: {str(e)}")



           
           
           
       
def get_quiz_status(conn, user_id, quiz_name):
    """Get quiz status: completed, in_progress, or not_started"""
    try:
        if USE_MONGODB:
            from db_mongo import get_mongo_db
            mongo_db = get_mongo_db()

            # Check quiz_states first - most reliable source
            quiz_state = mongo_db.quiz_states.find_one({
                "user_id": str(user_id),
                "quiz_name": quiz_name
            })
            if quiz_state and quiz_state.get("state") == "completed":
                return "completed"
            if quiz_state and quiz_state.get("question_index", 0) == -1:
                return "completed"

            # Fall back to counting responses
            total_questions = mongo_db.questions.count_documents({"quiz": quiz_name})
            if total_questions == 0:
                return "not_started"

            # Count distinct question numbers answered
            answered = mongo_db.responses.distinct("question_number", {
                "user_id": str(user_id),
                "quiz": quiz_name
            })

            if not answered:
                return "not_started"
            if len(answered) >= total_questions:
                return "completed"
            return "in_progress"

        else:
            # SQLite version
            state = conn.execute(
                "SELECT state FROM quiz_states WHERE user_id = ? AND quiz_name = ?",
                (user_id, quiz_name)
            ).fetchone()

            if state and state[0] == 'completed':
                return "completed"

            cursor = conn.execute(
                "SELECT COUNT(*) FROM responses WHERE user_id = ? AND quiz = ?",
                (user_id, quiz_name)
            )
            response_count = cursor.fetchone()[0]

            if response_count > 0:
                return "in_progress"
            else:
                return "not_started"

    except Exception as e:
        logging.error(f"Error getting quiz status: {e}")
        return "not_started"
    

    
def check_quiz_state(conn, user_id, quiz_name):
    if USE_MONGODB:
        try:
            from db_mongo import get_mongo_db
            mongo_db = get_mongo_db()
            state = mongo_db.quiz_states.find_one({"user_id": str(user_id), "quiz_name": quiz_name})
            logging.info(f"Current state for {quiz_name} for user {user_id}: {state}")
            return state
        except Exception as e:
            logging.error(f"Error checking quiz state in MongoDB: {e}")
            return None
    else:
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
#         db.update_user_field(phone_number, {"state": "awaiting_choice", "current_quiz": ""})
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
#             db.update_user_field(phone_number, {"state": f'quiz_{question_index}'})
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
#         db.update_user_field(phone_number, {"state": "awaiting_choice", "current_quiz": ""})
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
        db.update_user_field(phone_number, {"state": "awaiting_choice", "current_quiz": ""})
        return

    state = user['state']
    question_index = int(state.split('_')[1])
    question_number = question_index + 1

    user_id = str(user['_id']) if USE_MONGODB else user['id']

    if question_index < len(QUIZ_QUESTIONS):
        current_question = QUIZ_QUESTIONS[question_index]
        correct_answer = current_question['answer'].lower().strip()
        user_response = response.lower().strip()
        is_correct = user_response == correct_answer

        log_image_event(f"User {user_id} answered question {question_number} {'correctly' if is_correct else 'incorrectly'}")

        # Save ALL quizzes to responses collection (unified)
        if USE_MONGODB:
            db.save_user_response(
                user_id=user_id,
                quiz=current_quiz,
                question_number=question_number,
                response=response,
                correct=is_correct
            )
        else:
            conn.execute(
                "INSERT INTO responses (user_id, question_number, response, correct, quiz) VALUES (?, ?, ?, ?, ?)",
                (user['id'], question_number, response, int(is_correct), current_quiz)
            )
            conn.commit()

        log_image_event(f"Inserted response: question {question_number}, correct={is_correct}, quiz={current_quiz}")
        feedback = "Correct!" if is_correct else f"Wrong! The correct answer was {correct_answer.upper()}."
        send_message(phone_number, feedback)

        question_index += 1

        if question_index < len(QUIZ_QUESTIONS):
            db.update_user_field(phone_number, {"state": f'quiz_{question_index}'})
            if USE_MONGODB:
                from db_mongo import get_mongo_db
                mongo_db = get_mongo_db()
                mongo_db.quiz_states.update_one(
                    {"user_id": user_id, "quiz_name": current_quiz},
                    {"$set": {"question_index": question_index}},
                    upsert=True
                )
            else:
                conn.execute(
                    "UPDATE quiz_states SET question_index = ? WHERE user_id = ? AND quiz_name = ?",
                    (question_index, user['id'], current_quiz)
                )
                conn.commit()
            send_quiz_question(phone_number, question_index, conn, current_quiz)
        else:
            finish_quiz(phone_number, user, conn, current_quiz, len(QUIZ_QUESTIONS))
    else:
        send_message(phone_number, "Invalid question number. Type 'quiz' to start a new quiz.")
        db.update_user_field(phone_number, {"state": "awaiting_choice", "current_quiz": ""})



            
                 
       

        
        
        
        
        
        
        
        
        
        
        
        

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
        db.update_user_field(phone_number, {"state": "awaiting_choice", "current_quiz": ""})
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
        # send media if stored in MongoDB — image+question together as caption
        _media_sent = False
        if USE_MONGODB:
            try:
                from db_mongo import get_mongo_db
                _mdb = get_mongo_db()
                _qdoc = _mdb.questions.find_one({"quiz": quiz_name, "question_number": question_index + 1})
                if _qdoc and _qdoc.get("media_url"):
                    send_image_message(phone_number, _qdoc["media_url"],
                        caption=question_message.strip())
                    _media_sent = True
                    time.sleep(1.5)
            except Exception as _me:
                logging.warning(f"Could not send media: {_me}")
       
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
                msg_body = "Choose your answer:" if _media_sent else question_message
                success = send_interactive_message(phone_number, msg_body, buttons)
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
                    db.update_user_field(phone_number, {"state": "awaiting_choice", "current_quiz": ""})
                    conn.commit()
                else:
                    time.sleep(2 ** attempt)  # Exponential backoff
    else:
        logging.warning(f"Question index {question_index} out of range for {quiz_name}")
        finish_quiz(phone_number, db.get_user_by_phone(phone_number,), conn, quiz_name, len(QUIZ_QUESTIONS))

       
       
       
       

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

   
  
  

def send_image_message(phone_number, image_url, caption=""):
    """Send an image or video to a WhatsApp user via URL link."""
    url = f"https://graph.facebook.com/v11.0/{YOUR_PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    is_video = any(x in image_url.lower() for x in ['.mp4', '.mov', '.avi', 'export=download'])
    media_type = "video" if is_video else "image"
    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": media_type,
        media_type: {"link": image_url, "caption": caption}
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        logging.info(f"Image sent to {phone_number}: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        logging.error(f"Error sending image to {phone_number}: {e}")
        return False


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
        user = db.get_user_by_phone(phone_number,)
        present_options(phone_number, user, conn)




@app.route('/admin/cleanup-names')
def admin_cleanup_names():
    """Admin endpoint to clean up quoted names in database"""
    try:
        fixed_count = clean_quoted_names_in_database()
        return jsonify({
            'success': True,
            'message': f'Cleaned {fixed_count} user names',
            'fixed_count': fixed_count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


       
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
       
       

@app.route('/user/<user_id>', defaults={'random_number': None})
@app.route('/user/<user_id>/<random_number>')
def user_details(user_id, random_number=None):
    try:
        if USE_MONGODB:
            from db_mongo import get_mongo_db
            from bson import ObjectId
            mongo_db = get_mongo_db()

            # Try finding by ObjectId string
            try:
                user = mongo_db.users.find_one({"_id": ObjectId(user_id)})
            except Exception:
                user = mongo_db.users.find_one({"sqlite_id": int(user_id)})

            if not user:
                return jsonify({'status': 'error', 'message': 'User not found'}), 404

            stored_random = user.get('random_number', '')
            if random_number and str(stored_random) != str(random_number):
                return jsonify({'status': 'error', 'message': 'Invalid random number'}), 403

            user_id_str = str(user['_id'])
            records = list(mongo_db.records.find({"user_id": user_id_str}))

            user_data = {
                'phone_number': user.get('phone_number'),
                'name': user.get('name'),
                'random_number': stored_random
            }
            return render_template('user_details.html', user=user_data, records=records)

        else:
            conn = get_db_connection()
            try:
                user = conn.execute(
                    "SELECT phone_number, name, random_number FROM users WHERE id=?",
                    (user_id,)
                ).fetchone()
                if not user:
                    return jsonify({'status': 'error', 'message': 'User not found'}), 404
                if random_number and user['random_number'] != random_number:
                    return jsonify({'status': 'error', 'message': 'Invalid random number'}), 403
                records = conn.execute(
                    "SELECT media_url, upload_date FROM records WHERE user_id=?",
                    (user_id,)
                ).fetchall()
                return render_template('user_details.html', user=user, records=records)
            finally:
                conn.close()

    except Exception as e:
        logging.error(f"Error fetching user details: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


       

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
    try:
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        pass_percentage = request.args.get('pass_percentage', 60, type=int)
        min_quizzes = request.args.get('min_quizzes', 1, type=int)

        if USE_MONGODB:
            from db_mongo import get_mongo_db
            mongo_db = get_mongo_db()

            # Single pipeline — all users, all responses in one query
            pipeline = [
                {"$group": {
                    "_id": "$user_id",
                    "quizzes": {"$addToSet": "$quiz"},
                    "total_correct": {"$sum": {"$cond": ["$correct", 1, 0]}},
                    "total_attempted": {"$sum": 1}
                }}
            ]
            response_data = {r['_id']: r for r in mongo_db.responses.aggregate(pipeline)}

            # Questions count per quiz — one query
            quiz_totals = {}
            for q in mongo_db.questions.aggregate([
                {"$group": {"_id": "$quiz", "count": {"$sum": 1}}}
            ]):
                quiz_totals[q['_id']] = q['count']

            # Records count per user — one query
            records_data = {}
            for r in mongo_db.records.aggregate([
                {"$group": {"_id": "$user_id", "count": {"$sum": 1}}}
            ]):
                records_data[r['_id']] = r['count']

            # All users — one query
            users = list(mongo_db.users.find(
                {}, {"_id": 1, "name": 1, "phone_number": 1, "location": 1}
            ))

            # Clean locations
            raw_locations = mongo_db.users.distinct("location")
            locations = sorted([
                l.strip().strip('"') for l in raw_locations
                if l and l.strip().strip('"') not in ('', 'null')
            ])
            if 'Agege' not in locations:
                locations.insert(0, 'Agege')

            user_scores = []
            for user in users:
                user_id = str(user['_id'])
                rd = response_data.get(user_id, {})

                quizzes_taken = len(rd.get('quizzes', []))
                total_correct = rd.get('total_correct', 0)
                total_possible = sum(
                    quiz_totals.get(q, 0) for q in rd.get('quizzes', [])
                )
                percentage = round(
                    (total_correct / total_possible * 100), 1
                ) if total_possible > 0 else 0
                pass_fail = 'Pass' if (
                    percentage >= pass_percentage and
                    quizzes_taken >= min_quizzes
                ) else 'Fail'

                user_scores.append({
                    'id': user_id,
                    'name': user.get('name', 'Unknown'),
                    'phone_number': user.get('phone_number', ''),
                    'location': (user.get('location') or 'Unknown').strip().strip('"'),
                    'images_uploaded': records_data.get(user_id, 0),
                    'last_image_date': 'N/A',
                    'unique_upload_days': 0,
                    'all': {
                        'total_correct_answers': total_correct,
                        'total_possible': total_possible,
                        'quizzes_taken': quizzes_taken,
                        'percentage': percentage,
                        'pass_fail': pass_fail,
                        'last_quiz_date': 'N/A'
                    }
                })

            user_scores.sort(key=lambda x: x['all']['percentage'], reverse=True)

            if is_ajax:
                return jsonify({
                    'scores': user_scores,
                    'locations': locations,
                    'quiz_ranges': ['all']
                })

            return render_template('scoreboardbootcamp.html',
                                   scores=user_scores,
                                   pass_percentage=pass_percentage,
                                   min_quizzes=min_quizzes,
                                   locations=locations,
                                   selected_location='all',
                                   quiz_ranges=['all'])

    except Exception as e:
        import traceback
        logging.error(f"scoreboardbootcamp error: {e}")
        logging.error(traceback.format_exc())
        return f"<pre>ERROR: {e}\n\n{traceback.format_exc()}</pre>", 500
        

@app.route('/quizslider')
def quizslider():
    return render_template('quizslider.html')


        
        
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
    selected_location = request.args.get('location', 'all')

    if USE_MONGODB:
        from db_mongo import get_mongo_db
        mongo_db = get_mongo_db()

        if selected_location.lower() != 'all':
            users = list(mongo_db.users.find({"location": selected_location}))
        else:
            users = list(mongo_db.users.find({}))

        locations = sorted([l for l in mongo_db.users.distinct("location") if l])

        # Normalize for template compatibility
        for u in users:
            u['id'] = str(u['_id'])
    else:
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
# ─── ADMIN PIN VERIFICATION ─────────────────────────────────────────────────

@app.route('/api/admin/verify-pin', methods=['POST'])
def verify_admin_pin():
    data = request.get_json()
    if not data or 'pin' not in data:
        return jsonify({'error': 'Missing pin'}), 400
    admin_pin = os.getenv('ADMIN_PIN', '2025')
    if str(data['pin']) == str(admin_pin):
        return jsonify({'valid': True})
    return jsonify({'valid': False}), 401


# ─── QUIZ EDITOR PAGES ───────────────────────────────────────────────────────

@app.route('/quizeditor')
def quiz_editor_page():
    return render_template('quizeditor.html')


@app.route('/engagementdashboard')
def engagement_dashboard_page():
    return render_template('engagementdashboard.html')


# ─── QUESTIONS API ───────────────────────────────────────────────────────────

@app.route('/api/questions/<quiz_name>', methods=['GET'])
def get_quiz_questions_route(quiz_name):
    try:
        if USE_MONGODB:
            from db_mongo import get_mongo_db
            mongo_db = get_mongo_db()
            qs = list(mongo_db.questions.find(
                {'quiz': quiz_name},
                {'_id': 0}
            ).sort('question_number', 1))
        else:
            conn = get_db_connection()
            rows = conn.execute(
                'SELECT * FROM questions WHERE quiz = ? ORDER BY question_number',
                (quiz_name,)
            ).fetchall()
            qs = []
            for row in rows:
                q = dict(row)
                q['options'] = json.loads(q['options']) if isinstance(q['options'], str) else q['options']
                qs.append(q)
            conn.close()
        return jsonify(qs)
    except Exception as e:
        logging.error(f'get_quiz_questions_route error: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/questions/update', methods=['PUT'])
def update_question_route():
    try:
        data = request.get_json()
        quiz = data['quiz']
        question_number = int(data['question_number'])
        updates = {
            'question': data['question'],
            'options': data['options'],
            'answer': data['answer'],
        }
        if data.get('media_url'):
            updates['media_url'] = data['media_url']

        if USE_MONGODB:
            from db_mongo import get_mongo_db
            mongo_db = get_mongo_db()
            result = mongo_db.questions.update_one(
                {'quiz': quiz, 'question_number': question_number},
                {'$set': updates}
            )
            if result.matched_count == 0:
                return jsonify({'error': 'Question not found'}), 404
        else:
            conn = get_db_connection()
            conn.execute(
                'UPDATE questions SET question=?, options=?, answer=? WHERE quiz=? AND question_number=?',
                (updates['question'], json.dumps(updates['options']), updates['answer'], quiz, question_number)
            )
            conn.commit()
            conn.close()

        return jsonify({'success': True})
    except Exception as e:
        logging.error(f'update_question_route error: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/questions/add', methods=['POST'])
def add_question_route():
    try:
        data = request.get_json()
        new_q = {
            'quiz': data['quiz'],
            'question_number': int(data['question_number']),
            'question': data.get('question', ''),
            'options': data.get('options', ['', '', '']),
            'answer': data.get('answer', 'A'),
            'media_url': data.get('media_url', None),
        }

        if USE_MONGODB:
            from db_mongo import get_mongo_db
            mongo_db = get_mongo_db()
            mongo_db.questions.insert_one({**new_q})
            new_q.pop('_id', None)
        else:
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO questions (quiz, question, options, answer, question_number) VALUES (?,?,?,?,?)',
                (new_q['quiz'], new_q['question'], json.dumps(new_q['options']), new_q['answer'], new_q['question_number'])
            )
            conn.commit()
            conn.close()

        return jsonify(new_q)
    except Exception as e:
        logging.error(f'add_question_route error: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/questions/delete', methods=['DELETE'])
def delete_question_route():
    try:
        data = request.get_json()
        quiz = data['quiz']
        question_number = int(data['question_number'])

        if USE_MONGODB:
            from db_mongo import get_mongo_db
            mongo_db = get_mongo_db()
            mongo_db.questions.delete_one({'quiz': quiz, 'question_number': question_number})
        else:
            conn = get_db_connection()
            conn.execute('DELETE FROM questions WHERE quiz=? AND question_number=?', (quiz, question_number))
            conn.commit()
            conn.close()

        return jsonify({'success': True})
    except Exception as e:
        logging.error(f'delete_question_route error: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/quiz-stats/<quiz_name>', methods=['GET'])
def quiz_stats_route(quiz_name):
    try:
        if USE_MONGODB:
            from db_mongo import get_mongo_db
            mongo_db = get_mongo_db()
            total = mongo_db.responses.count_documents({'quiz': quiz_name})
            correct = mongo_db.responses.count_documents({'quiz': quiz_name, 'correct': True})
            avg_correct = round((correct / total * 100), 1) if total > 0 else 0
        else:
            conn = get_db_connection()
            total = conn.execute('SELECT COUNT(*) FROM responses WHERE quiz=?', (quiz_name,)).fetchone()[0]
            correct = conn.execute('SELECT COUNT(*) FROM responses WHERE quiz=? AND correct=1', (quiz_name,)).fetchone()[0]
            avg_correct = round((correct / total * 100), 1) if total > 0 else 0
            conn.close()

        return jsonify({'total_responses': total, 'correct_responses': correct, 'avg_correct': avg_correct})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─── ENGAGEMENT METRICS API ──────────────────────────────────────────────────

@app.route('/api/engagement/metrics', methods=['GET'])
def engagement_metrics_route():
    try:
        if USE_MONGODB:
            from db_mongo import get_mongo_db
            mongo_db = get_mongo_db()

            total_users   = mongo_db.users.count_documents({})
            total_responses = mongo_db.responses.count_documents({})
            ai_chats      = mongo_db.conversation_history.count_documents({'is_ai': True})

            week_ago      = datetime.utcnow() - timedelta(days=7)
            active_ids    = mongo_db.responses.distinct('user_id', {'timestamp': {'$gte': week_ago}})
            active_this_week = len(active_ids)

            today_start   = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            messages_today = mongo_db.processed_messages.count_documents({'processed_at': {'$gte': today_start}})

            # Location breakdown
            loc_pipeline = [
                {'$group': {'_id': '$location', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}}, {'$limit': 10}
            ]
            locations = list(mongo_db.users.aggregate(loc_pipeline))

            # Quiz stats
            quiz_pipeline = [
                {'$group': {
                    '_id': '$quiz',
                    'total':   {'$sum': 1},
                    'correct': {'$sum': {'$cond': ['$correct', 1, 0]}}
                }},
                {'$sort': {'_id': 1}}
            ]
            quiz_stats = list(mongo_db.responses.aggregate(quiz_pipeline))

            # Per-user aggregate stats
            user_agg = [
                {'$group': {
                    '_id': '$user_id',
                    'quizzes_list':      {'$addToSet': '$quiz'},
                    'total_responses':   {'$sum': 1},
                    'correct_responses': {'$sum': {'$cond': ['$correct', 1, 0]}},
                    'last_active':       {'$max': '$timestamp'}
                }}
            ]
            u_stats = {r['_id']: r for r in mongo_db.responses.aggregate(user_agg)}

            # AI chats per user
            ai_agg = [
                {'$match': {'is_ai': False}},
                {'$group': {'_id': '$user_id', 'ai_chats': {'$sum': 1}}}
            ]
            ai_per_user = {r['_id']: r['ai_chats'] for r in mongo_db.conversation_history.aggregate(ai_agg)}

            # All users
            users_raw = list(mongo_db.users.find({}, {
                '_id': 1, 'name': 1, 'phone_number': 1, 'location': 1,
                'business_type': 1, 'business_size': 1, 'financial_status': 1,
                'main_challenge': 1, 'state': 1
            }))

            users_table = []
            for u in users_raw:
                uid = str(u['_id'])
                stats = u_stats.get(uid, {})
                total_r   = stats.get('total_responses', 0)
                correct_r = stats.get('correct_responses', 0)
                qlist     = sorted(stats.get('quizzes_list', []))
                chats     = ai_per_user.get(uid, 0)
                last_act  = stats.get('last_active')
                correct_pct = round(correct_r / total_r * 100, 1) if total_r > 0 else 0

                # Engagement score (0–100): responses 30%, quiz diversity 25%, accuracy 25%, AI use 20%
                q_score   = min(len(qlist) / 10 * 100, 100) * 0.25
                r_score   = min(total_r / 30 * 100, 100) * 0.30
                a_score   = correct_pct * 0.25
                c_score   = min(chats / 5 * 100, 100) * 0.20
                eng_score = round(q_score + r_score + a_score + c_score, 1)

                users_table.append({
                    'name':             u.get('name', '—'),
                    'phone_number':     u.get('phone_number', ''),
                    'location':         (u.get('location') or '—').strip().strip('"'),
                    'business_type':    u.get('business_type', '—'),
                    'business_size':    u.get('business_size', '—'),
                    'financial_status': u.get('financial_status', '—'),
                    'main_challenge':   u.get('main_challenge', '—'),
                    'quizzes_taken':    len(qlist),
                    'quizzes_list':     qlist,
                    'total_responses':  total_r,
                    'correct_responses': correct_r,
                    'correct_pct':      correct_pct,
                    'ai_chats':         chats,
                    'last_active':      last_act.isoformat() if last_act else None,
                    'engagement_score': eng_score,
                })

            users_table.sort(key=lambda u: u['engagement_score'], reverse=True)

            return jsonify({
                'total_users':       total_users,
                'active_this_week':  active_this_week,
                'total_responses':   total_responses,
                'ai_chats':          ai_chats,
                'messages_today':    messages_today,
                'locations':         locations,
                'quiz_stats':        quiz_stats,
                'users':             users_table,
            })

        else:
            conn = get_db_connection()
            total_users     = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
            total_responses = conn.execute('SELECT COUNT(*) FROM responses').fetchone()[0]
            conn.close()
            return jsonify({
                'total_users': total_users, 'active_this_week': 0,
                'total_responses': total_responses, 'ai_chats': 0,
                'messages_today': 0, 'locations': [], 'quiz_stats': [], 'users': []
            })

    except Exception as e:
        import traceback as _tb
        logging.error(f'engagement_metrics_route error: {e}')
        logging.error(_tb.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/api/engagement/csv', methods=['GET'])
def engagement_csv_route():
    """Return all user engagement data as a downloadable CSV."""
    try:
        if USE_MONGODB:
            from db_mongo import get_mongo_db
            import csv, io
            mongo_db = get_mongo_db()

            user_agg = [
                {'$group': {
                    '_id': '$user_id',
                    'quizzes_list':      {'$addToSet': '$quiz'},
                    'total_responses':   {'$sum': 1},
                    'correct_responses': {'$sum': {'$cond': ['$correct', 1, 0]}},
                    'last_active':       {'$max': '$timestamp'}
                }}
            ]
            u_stats = {r['_id']: r for r in mongo_db.responses.aggregate(user_agg)}

            ai_agg = [
                {'$match': {'is_ai': False}},
                {'$group': {'_id': '$user_id', 'ai_chats': {'$sum': 1}}}
            ]
            ai_per_user = {r['_id']: r['ai_chats'] for r in mongo_db.conversation_history.aggregate(ai_agg)}

            users_raw = list(mongo_db.users.find({}, {
                '_id': 1, 'name': 1, 'phone_number': 1, 'location': 1,
                'business_type': 1, 'business_size': 1, 'financial_status': 1,
                'main_challenge': 1, 'growth_goal': 1, 'funding_need': 1, 'record_keeping': 1
            }))

            output = io.StringIO()
            cols = ['name', 'phone_number', 'location', 'business_type', 'business_size',
                    'financial_status', 'main_challenge', 'growth_goal', 'funding_need',
                    'record_keeping', 'quizzes_taken', 'quizzes_completed',
                    'total_responses', 'correct_responses', 'correct_pct',
                    'ai_chats', 'last_active', 'engagement_score']
            writer = csv.DictWriter(output, fieldnames=cols, extrasaction='ignore')
            writer.writeheader()

            for u in users_raw:
                uid   = str(u['_id'])
                stats = u_stats.get(uid, {})
                total_r   = stats.get('total_responses', 0)
                correct_r = stats.get('correct_responses', 0)
                qlist     = sorted(stats.get('quizzes_list', []))
                chats     = ai_per_user.get(uid, 0)
                last_act  = stats.get('last_active')
                correct_pct = round(correct_r / total_r * 100, 1) if total_r > 0 else 0
                q_score   = min(len(qlist) / 10 * 100, 100) * 0.25
                r_score   = min(total_r / 30 * 100, 100) * 0.30
                a_score   = correct_pct * 0.25
                c_score   = min(chats / 5 * 100, 100) * 0.20
                eng_score = round(q_score + r_score + a_score + c_score, 1)
                writer.writerow({
                    'name':             u.get('name', ''),
                    'phone_number':     u.get('phone_number', ''),
                    'location':         (u.get('location') or '').strip().strip('"'),
                    'business_type':    u.get('business_type', ''),
                    'business_size':    u.get('business_size', ''),
                    'financial_status': u.get('financial_status', ''),
                    'main_challenge':   u.get('main_challenge', ''),
                    'growth_goal':      u.get('growth_goal', ''),
                    'funding_need':     u.get('funding_need', ''),
                    'record_keeping':   u.get('record_keeping', ''),
                    'quizzes_taken':    len(qlist),
                    'quizzes_completed': ';'.join(qlist),
                    'total_responses':  total_r,
                    'correct_responses': correct_r,
                    'correct_pct':      correct_pct,
                    'ai_chats':         chats,
                    'last_active':      last_act.isoformat() if last_act else '',
                    'engagement_score': eng_score,
                })

            from flask import Response as FlaskResponse
            filename = 'empowerbot_engagement_' + datetime.utcnow().strftime('%Y%m%d') + '.csv'
            return FlaskResponse(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename={filename}'}
            )

        else:
            return jsonify({'error': 'CSV export only supported with MongoDB'}), 400

    except Exception as e:
        logging.error(f'engagement_csv_route error: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/configurations')
# And add templates/configurations.html (provided separately)

# ── 1. CONFIGURATIONS PAGE ────────────────────────────────────────────────────

@app.route('/configurations')
def configurations_page():
    return render_template('configurations.html')


# ── 2. LIST ALL CONFIGURATIONS ───────────────────────────────────────────────

@app.route('/api/configs', methods=['GET'])
def list_configs():
    try:
        if USE_MONGODB:
            from db_mongo import get_mongo_db
            from bson import ObjectId
            mongo_db = get_mongo_db()
            configs = list(mongo_db.configurations.find({}).sort('created_at', 1))
            for c in configs:
                c['_id'] = str(c['_id'])
                c['user_count'] = mongo_db.users.count_documents({
                    '$or': [
                        {'configuration': c['_id']},
                        {'configuration': c['name']}
                    ]
                })
                if 'created_at' in c:
                    c['created_at'] = c['created_at'].isoformat()
            return jsonify(configs)
        return jsonify([])
    except Exception as e:
        logging.error(f'list_configs error: {e}')
        return jsonify({'error': str(e)}), 500


# ── 3. CREATE CONFIGURATION ───────────────────────────────────────────────────

@app.route('/api/configs', methods=['POST'])
def create_config():
    try:
        if USE_MONGODB:
            from db_mongo import get_mongo_db
            from bson import ObjectId
            data = request.json
            mongo_db = get_mongo_db()
            doc = {
                'name':        data.get('name', 'New Configuration'),
                'description': data.get('description', ''),
                'color':       data.get('color', '#22D3EE'),
                'features':    data.get('features', []),
                'quizzes':     data.get('quizzes', []),
                'created_at':  datetime.utcnow(),
                'updated_at':  datetime.utcnow(),
            }
            result = mongo_db.configurations.insert_one(doc)
            doc['_id'] = str(result.inserted_id)
            doc['created_at'] = doc['created_at'].isoformat()
            doc['updated_at'] = doc['updated_at'].isoformat()
            return jsonify(doc), 201
        return jsonify({'error': 'MongoDB not enabled'}), 400
    except Exception as e:
        logging.error(f'create_config error: {e}')
        return jsonify({'error': str(e)}), 500


# ── 4. UPDATE CONFIGURATION ───────────────────────────────────────────────────

@app.route('/api/configs/<config_id>', methods=['PUT'])
def update_config(config_id):
    try:
        if USE_MONGODB:
            from db_mongo import get_mongo_db
            from bson import ObjectId
            mongo_db = get_mongo_db()
            data = request.json
            update = {
                '$set': {
                    'name':        data.get('name', ''),
                    'description': data.get('description', ''),
                    'color':       data.get('color', '#22D3EE'),
                    'features':    data.get('features', []),
                    'quizzes':     data.get('quizzes', []),
                    'updated_at':  datetime.utcnow(),
                }
            }
            mongo_db.configurations.update_one({'_id': ObjectId(config_id)}, update)
            return jsonify({'success': True})
        return jsonify({'error': 'MongoDB not enabled'}), 400
    except Exception as e:
        logging.error(f'update_config error: {e}')
        return jsonify({'error': str(e)}), 500


# ── 5. DELETE CONFIGURATION ───────────────────────────────────────────────────

@app.route('/api/configs/<config_id>', methods=['DELETE'])
def delete_config(config_id):
    try:
        if USE_MONGODB:
            from db_mongo import get_mongo_db
            from bson import ObjectId
            mongo_db = get_mongo_db()
            # Unassign users from this config
            mongo_db.users.update_many(
                {'configuration': config_id},
                {'$unset': {'configuration': ''}}
            )
            mongo_db.configurations.delete_one({'_id': ObjectId(config_id)})
            return jsonify({'success': True})
        return jsonify({'error': 'MongoDB not enabled'}), 400
    except Exception as e:
        logging.error(f'delete_config error: {e}')
        return jsonify({'error': str(e)}), 500


# ── 6. ASSIGN USER TO CONFIGURATION ──────────────────────────────────────────

@app.route('/api/users/assign-config', methods=['POST'])
def assign_user_config():
    try:
        if USE_MONGODB:
            from db_mongo import get_mongo_db
            from bson import ObjectId
            data = request.json
            user_id  = data.get('user_id')
            config_id = data.get('config_id')  # can be empty string to unassign
            mongo_db = get_mongo_db()
            if config_id:
                mongo_db.users.update_one(
                    {'_id': ObjectId(user_id)},
                    {'$set': {'configuration': config_id}}
                )
            else:
                mongo_db.users.update_one(
                    {'_id': ObjectId(user_id)},
                    {'$unset': {'configuration': ''}}
                )
            return jsonify({'success': True})
        return jsonify({'error': 'MongoDB not enabled'}), 400
    except Exception as e:
        logging.error(f'assign_user_config error: {e}')
        return jsonify({'error': str(e)}), 500


# ── 7. LIST USERS WITH THEIR CONFIGURATIONS ───────────────────────────────────

@app.route('/api/users/config-list', methods=['GET'])
def users_config_list():
    try:
        if USE_MONGODB:
            from db_mongo import get_mongo_db
            mongo_db = get_mongo_db()
            users = list(mongo_db.users.find({}, {
                '_id': 1, 'name': 1, 'phone_number': 1,
                'location': 1, 'configuration': 1
            }).sort('name', 1))
            for u in users:
                u['_id'] = str(u['_id'])
            return jsonify(users)
        return jsonify([])
    except Exception as e:
        logging.error(f'users_config_list error: {e}')
        return jsonify({'error': str(e)}), 500


# ── 8. CHECK USER'S CONFIGURATION (use in WhatsApp handlers) ─────────────────
#
# Call this in your WhatsApp message handlers to check if a feature is enabled:
#
# def user_has_feature(phone_number, feature_key):
#     """Check if a user's configuration includes a specific feature."""
#     if not USE_MONGODB:
#         return True  # default: allow all features if no MongoDB
#     try:
#         from db_mongo import get_mongo_db
#         mongo_db = get_mongo_db()
#         user = mongo_db.users.find_one({'phone_number': phone_number})
#         if not user or not user.get('configuration'):
#             return True  # no config assigned = full access
#         cfg_id = user['configuration']
#         config = mongo_db.configurations.find_one({
#             '$or': [{'_id': ObjectId(cfg_id)}, {'name': cfg_id}]
#         })
#         if not config:
#             return True
#         return feature_key in (config.get('features') or [])
#     except Exception as e:
#         logging.warning(f'user_has_feature check failed: {e}')
#         return True  # fail open
#
# Usage example:
#   if user_has_feature(phone_number, 'ai_chatbot'):
#       # show AI chat option
#   if user_has_feature(phone_number, 'quiz_modules'):
#       # allow quiz access


@app.route('/location-admin')
def location_admin_page():
    return render_template('location_admin.html')


@app.route('/api/location-codes', methods=['GET'])
def list_location_codes():
    try:
        if USE_MONGODB:
            from db_mongo import get_mongo_db
            mongo_db = get_mongo_db()
            codes = list(mongo_db.location_codes.find({}).sort('created_at', -1))
            for c in codes:
                c['_id'] = str(c['_id'])
                c['user_count'] = mongo_db.users.count_documents({'location_code': c['code']})
                if 'created_at' in c:
                    c['created_at'] = c['created_at'].isoformat()
            return jsonify(codes)
        return jsonify([])
    except Exception as e:
        logging.error(f'list_location_codes error: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/location-codes', methods=['POST'])
def create_location_codes():
    """Generate one or more location codes for a given location."""
    try:
        if USE_MONGODB:
            from db_mongo import get_mongo_db
            mongo_db = get_mongo_db()
            data = request.json
            location  = data.get('location', '').strip()
            detail    = data.get('detail', '').strip()
            config_id = data.get('config_id') or None
            count     = min(50, max(1, int(data.get('count', 1))))

            if not location:
                return jsonify({'error': 'Location name is required'}), 400

            # Generate prefix: first 3 letters of location, uppercase
            prefix = ''.join(filter(str.isalpha, location))[:3].upper()
            if len(prefix) < 3:
                prefix = (prefix + 'LOC')[:3]

            # Find highest existing number for this prefix
            existing = list(mongo_db.location_codes.find(
                {'code': {'$regex': f'^{prefix}'}},
                {'code': 1}
            ))
            existing_nums = []
            for e in existing:
                try:
                    existing_nums.append(int(e['code'][3:]))
                except:
                    pass
            start_num = (max(existing_nums) + 1) if existing_nums else 1

            created = []
            for i in range(count):
                code = f"{prefix}{str(start_num + i).zfill(2)}"
                doc = {
                    'code':       code,
                    'location':   location,
                    'detail':     detail,
                    'config_id':  config_id,
                    'active':     True,
                    'created_at': datetime.utcnow(),
                }
                mongo_db.location_codes.insert_one(doc)
                doc['_id'] = str(doc['_id'])
                doc['created_at'] = doc['created_at'].isoformat()
                created.append(doc)

            return jsonify({'codes': created}), 201
        return jsonify({'error': 'MongoDB not enabled'}), 400
    except Exception as e:
        logging.error(f'create_location_codes error: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/location-codes/<code_id>', methods=['PUT'])
def update_location_code(code_id):
    try:
        if USE_MONGODB:
            from db_mongo import get_mongo_db
            from bson import ObjectId
            mongo_db = get_mongo_db()
            data = request.json
            update = {'$set': {k: v for k, v in data.items() if k != '_id'}}
            mongo_db.location_codes.update_one({'_id': ObjectId(code_id)}, update)
            return jsonify({'success': True})
        return jsonify({'error': 'MongoDB not enabled'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/location-codes/<code_id>', methods=['DELETE'])
def delete_location_code(code_id):
    try:
        if USE_MONGODB:
            from db_mongo import get_mongo_db
            from bson import ObjectId
            mongo_db = get_mongo_db()
            mongo_db.location_codes.delete_one({'_id': ObjectId(code_id)})
            return jsonify({'success': True})
        return jsonify({'error': 'MongoDB not enabled'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── SECTION B: BOT ONBOARDING PATCH ──────────────────────────────────────────
#
# Add this function to server.py:

def validate_location_code(code_input):
    """
    Check a location code entered by a user.
    Returns: (valid: bool, location: str, config_id: str|None)
    Special keyword: 'OPEN' → skip code, location = 'Unspecified'
    """
    if not USE_MONGODB:
        return True, 'Unspecified', None

    code_upper = code_input.strip().upper()

    if code_upper == 'OPEN':
        return True, 'Unspecified', None

    try:
        from db_mongo import get_mongo_db
        mongo_db = get_mongo_db()
        doc = mongo_db.location_codes.find_one({
            'code': code_upper,
            'active': True
        })
        if doc:
            location = doc.get('location', 'Unknown')
            if doc.get('detail'):
                location += f", {doc['detail']}"
            return True, location, doc.get('config_id')
        return False, None, None
    except Exception as e:
        logging.error(f'validate_location_code error: {e}')
        return False, None, None


#
# ── SECTION C: BOT FLOW PATCH ─────────────────────────────────────────────────
#
# Find the part of your bot that handles NEW USER registration.
# It likely looks something like:
#
#   if not user:
#       # new user - ask for name
#       send_message(phone_number, "Welcome! What is your name?")
#       ...
#
# REPLACE with:
#
#   if not user:
#       # Check if location codes are enabled (set to True to activate)
#       LOCATION_CODES_ENABLED = True
#
#       if LOCATION_CODES_ENABLED:
#           # Check if user is in 'awaiting_location_code' state
#           temp_state = get_temp_state(phone_number)  # or however you track state
#
#           if temp_state != 'awaiting_location_code':
#               # First message from new user - ask for location code
#               send_message(phone_number,
#                   "👋 Welcome to EmpowerBot!\n\n"
#                   "To get started, please enter your *location code*.\n\n"
#                   "Don't have a code? Type *OPEN* to continue."
#               )
#               set_temp_state(phone_number, 'awaiting_location_code')
#               return
#
#           else:
#               # User has sent their location code
#               code_input = incoming_message.strip()
#               valid, location, config_id = validate_location_code(code_input)
#
#               if valid:
#                   # Store location and config for use during registration
#                   set_temp_data(phone_number, {
#                       'location': location,
#                       'configuration': config_id
#                   })
#                   # Store location_code used
#                   set_temp_data(phone_number, {
#                       'location_code': code_input.upper() if code_input.upper() != 'OPEN' else None
#                   })
#                   if location != 'Unspecified':
#                       send_message(phone_number,
#                           f"✅ Location confirmed: *{location}*\n\nWhat is your name?"
#                       )
#                   else:
#                       send_message(phone_number,
#                           "Continuing without a location code. You can add one later.\n\n"
#                           "What is your name?"
#                       )
#                   set_temp_state(phone_number, 'awaiting_name')
#               else:
#                   send_message(phone_number,
#                       "❌ That code wasn't recognised.\n\n"
#                       "Please check your code and try again, or type *OPEN* to continue without one."
#                   )
#               return
#
# Then when saving the new user to MongoDB, include:
#   user_doc['location'] = temp_data.get('location', 'Unspecified')
#   user_doc['configuration'] = temp_data.get('configuration')
#   user_doc['location_code'] = temp_data.get('location_code')
#
# ─────────────────────────────────────────────────────────────────────────────
#
# NOTE: The exact implementation depends on how your bot currently manages
# new user state. Share your handle_message() function and I'll write the
# exact patch for your specific flow.
# ─────────────────────────────────────────────────────────────────────────────


@app.route('/api/quizzes/import-csv', methods=['POST'])
def import_quiz_questions():
    """Bulk import questions from JSON array (sent from the quiz editor frontend)."""
    try:
        if USE_MONGODB:
            from db_mongo import get_mongo_db
            mongo_db = get_mongo_db()
        
        data = request.json
        quiz_name = data.get('quiz')
        questions = data.get('questions', [])
        
        if not quiz_name or not questions:
            return jsonify({'error': 'quiz and questions are required'}), 400
        
        imported = 0
        for q in questions:
            qn = q.get('question_number', 1)
            doc = {
                'quiz':            quiz_name,
                'question_number': qn,
                'question':        q.get('question', ''),
                'options':         q.get('options', []),
                'answer':          q.get('answer', 'A'),
                'media_url':       q.get('media_url') or None,
            }
            if USE_MONGODB:
                mongo_db.questions.update_one(
                    {'quiz': quiz_name, 'question_number': qn},
                    {'$set': doc},
                    upsert=True
                )
            imported += 1
        
        return jsonify({'success': True, 'imported': imported})
    
    except Exception as e:
        logging.error(f'import_quiz_questions error: {e}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 80)
    print("EMPOWERBOT INITIALIZATION")
    print("=" * 80)
    
    if USE_MONGODB:
        print("🍃 USING MONGODB")
        print(f"✅ MongoDB URI configured: {os.getenv('MONGODB_URI')[:30]}...")
        from db_mongo import init_mongodb
        init_mongodb()
        try:
            test_user = db.get_user_by_phone("2348169686473")
            if test_user:
                print(f"✅ MongoDB connection verified - Found user: {test_user.get('name')}")
            print(f"✅ Bot will save all new data to MongoDB")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            print("⚠️  Falling back to SQLite")
            USE_MONGODB = False
    else:
        print("💾 USING SQLITE (Local Database)")
        print("⚠️  Set MONGODB_URI in .env to use MongoDB")
        init_db()
        populate_database_from_json_files()
    
    print("=" * 80)
    
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        print("🔄 Loading quiz visibility (after Flask reloader)...")
        try:
            load_quiz_visibility_from_db()
            loaded_visibility = app.config.get('QUIZ_VISIBILITY', {})
            print(f"✅ Loaded {len(loaded_visibility)} quiz statuses into memory")
            if loaded_visibility:
                enabled_count = sum(1 for v in loaded_visibility.values() if v)
                disabled_count = len(loaded_visibility) - enabled_count
                print(f"   📊 Enabled: {enabled_count} | Disabled: {disabled_count}")
                disabled_quizzes = [k for k, v in loaded_visibility.items() if not v]
                if disabled_quizzes:
                    print(f"   🚫 Disabled: {disabled_quizzes}")
        except Exception as e:
            print(f"❌ Error loading quiz visibility: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("⏭️  Skipping quiz visibility load (parent process - will load after reloader starts)")
    
    print("=" * 80)
    print("Starting Flask app...")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)