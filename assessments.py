# assessments.py

import json
import sqlite3
from typing import List


import json
import requests
import traceback

def handle_business_size_selection(phone_number, user, conn):
    list_message = {
        "type": "list",
        "header": {
            "type": "text",
            "text": "Business Size"
        },
        "body": {
            "text": "How many people work in your business?"
        },
        "footer": {
            "text": "Select an option below"
        },
        "action": {
            "button": "Select size",
            "sections": [{
                "title": "Available options",
                "rows": [
                    {"id": "micro", "title": "1-5 workers"},
                    {"id": "very_small", "title": "6-15 workers"},
                    {"id": "small", "title": "16-30 workers"},
                    {"id": "medium", "title": "31-50 workers"},
                    {"id": "large", "title": "51-100 workers"},
                    {"id": "very_large", "title": "More than 100 workers"}
                ]
            }]
        }
    }
    
    success, message = send_interactive_message(phone_number, list_message)
    
    if not success:
        log_image_event(f"Failed to send business size selection: {message}")
    return success, message
  
  
  

def handle_financial_status_selection(phone_number, user, conn):
    list_options = [
        {"id": "loss", "title": "Losing money most months"},
        {"id": "break_even", "title": "Breaking even (no profit/loss)"},
        {"id": "small_profit", "title": "Small profit most months"},
        {"id": "good_profit", "title": "Good profit consistently"},
        {"id": "growing", "title": "Growing profit each month"},
        {"id": "unstable", "title": "Profit changes a lot monthly"}
    ]
    
    list_message = {
        "type": "list",
        "header": {
            "type": "text",
            "text": "Financial Status"
        },
        "body": {
            "text": "How is your business doing with money?"
        },
        "action": {
            "button": "Select",
            "sections": [
                {
                    "title": "Choose one:",
                    "rows": list_options
                }
            ]
        }
    }
    
    success, message = send_interactive_message(phone_number, list_message)
    if not success:
        log_image_event(f"Failed to send financial status selection: {message}")

def handle_main_challenge_selection(phone_number, user, conn):
    list_options = [
        {"id": "cash_flow", "title": "Not enough cash for daily needs"},
        {"id": "marketing", "title": "Hard to get more customers"},
        {"id": "competition", "title": "Too many competitors"},
        {"id": "skills", "title": "Need better business skills"},
        {"id": "staff", "title": "Problems with workers"},
        {"id": "tech", "title": "Need better equipment/technology"}
    ]
    
    list_message = {
        "type": "list",
        "header": {
            "type": "text",
            "text": "Main Challenge"
        },
        "body": {
            "text": "What is your biggest business problem?"
        },
        "action": {
            "button": "Select",
            "sections": [
                {
                    "title": "Choose one:",
                    "rows": list_options
                }
            ]
        }
    }
    
    success, message = send_interactive_message(phone_number, list_message)
    if not success:
        log_image_event(f"Failed to send main challenge selection: {message}")

def handle_record_keeping_selection(phone_number, user, conn):
    list_options = [
        {"id": "none", "title": "No records kept"},
        {"id": "memory", "title": "Remember in my head"},
        {"id": "notes", "title": "Write in notebook"},
        {"id": "phone", "title": "Use phone notes/calculator"},
        {"id": "spreadsheet", "title": "Use Excel/spreadsheets"},
        {"id": "software", "title": "Use accounting software"}
    ]
    
    list_message = {
        "type": "list",
        "header": {
            "type": "text",
            "text": "Record Keeping"
        },
        "body": {
            "text": "How do you track your business money?"
        },
        "action": {
            "button": "Select",
            "sections": [
                {
                    "title": "Choose one:",
                    "rows": list_options
                }
            ]
        }
    }
    
    success, message = send_interactive_message(phone_number, list_message)
    if not success:
        log_image_event(f"Failed to send record keeping selection: {message}")

def handle_growth_goal_selection(phone_number, user, conn):
    list_options = [
        {"id": "more_sales", "title": "Make more sales"},
        {"id": "new_location", "title": "Open new location"},
        {"id": "new_products", "title": "Add new products"},
        {"id": "better_profit", "title": "Increase profit margins"},
        {"id": "equipment", "title": "Get better equipment"},
        {"id": "stable", "title": "Keep business stable"}
    ]
    
    list_message = {
        "type": "list",
        "header": {
            "type": "text",
            "text": "Growth Goals"
        },
        "body": {
            "text": "What is your main business goal?"
        },
        "action": {
            "button": "Select",
            "sections": [
                {
                    "title": "Choose one:",
                    "rows": list_options
                }
            ]
        }
    }
    
    success, message = send_interactive_message(phone_number, list_message)
    if not success:
        log_image_event(f"Failed to send growth goal selection: {message}")

def handle_funding_need_selection(phone_number, user, conn):
    list_options = [
        {"id": "urgent", "title": "Need money urgently"},
        {"id": "expansion", "title": "Money to grow bigger"},
        {"id": "equipment", "title": "Money for equipment"},
        {"id": "stock", "title": "Money for more stock"},
        {"id": "marketing", "title": "Money for marketing"},
        {"id": "none", "title": "Don't need money now"}
    ]
    
    list_message = {
        "type": "list",
        "header": {
            "type": "text",
            "text": "Funding Needs"
        },
        "body": {
            "text": "Do you need money for your business?"
        },
        "action": {
            "button": "Select",
            "sections": [
                {
                    "title": "Choose one:",
                    "rows": list_options
                }
            ]
        }
    }
    
    success, message = send_interactive_message(phone_number, list_message)
    if not success:
        log_image_event(f"Failed to send funding need selection: {message}")

def handle_product_selection(phone_number, user, conn, selected_product):
    user_id = user['id']
    cursor = conn.cursor()
    
    cursor.execute("SELECT selected_products FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    current_products = json.loads(result[0]) if result and result[0] else []
    
    if selected_product not in current_products:
        current_products.append(selected_product)
        
    cursor.execute(
        "UPDATE users SET selected_products = ? WHERE id = ?", 
        (json.dumps(current_products), user_id)
    )
    cursor.execute(
        "INSERT INTO user_products (user_id, product_name) VALUES (?, ?)",
        (user_id, selected_product)
    )
    conn.commit()
    
    if len(current_products) % 5 == 0:
        new_options = generate_product_options(user['business_type'], current_products)
        send_product_options(phone_number, new_options)
    else:
        message = {
            "type": "text",
            "text": f"Product '{selected_product}' added. Select more or type 'done' to finish."
        }
        send_message(phone_number, message)

def send_product_options(phone_number, options: List[str]):
    list_options = [{"id": f"product_{i}", "title": product} for i, product in enumerate(options)]
    list_options.append({"id": "done", "title": "Finished selecting products"})
    
    list_message = {
        "type": "list",
        "header": {
            "type": "text",
            "text": "Product Selection"
        },
        "body": {
            "text": "Select a product to add to your business or choose 'Finished' when done."
        },
        "action": {
            "button": "Select",
            "sections": [
                {
                    "title": "Choose one:",
                    "rows": list_options
                }
            ]
        }
    }
    
    success, message = send_interactive_message(phone_number, list_message)
    if not success:
        log_image_event(f"Failed to send product options: {message}")