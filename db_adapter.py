import os
import logging
import sqlite3
from datetime import datetime

USE_MONGODB = os.getenv('MONGODB_URI') is not None

if USE_MONGODB:
    from db_mongo import (
        find_user_by_phone, create_user, update_user,
        save_response, get_user_responses, get_incorrect_responses,
        get_quiz_state, update_quiz_state, delete_quiz_state,
        get_users_collection, get_responses_collection, get_questions_collection
    )
    logging.info("🍃 Database Adapter: Using MongoDB")
else:
    logging.info("💾 Database Adapter: Using SQLite")

class DatabaseAdapter:
    """Universal database adapter for both SQLite and MongoDB"""
    
    def __init__(self):
        self.use_mongodb = USE_MONGODB
        self.db_file = 'user_data_bootcamp.db'  # SQLite database file
    
    def _get_sqlite_connection(self):
        """Get SQLite connection (internal use only)"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ==================== USER OPERATIONSS ====================
    
    def get_user_by_phone(self, phone_number):
        """Get user by phone number"""
        if self.use_mongodb:
            user = find_user_by_phone(phone_number)
            if user and '_id' in user:
                user['id'] = str(user['_id'])  # Add id for compatibility
            return user
        else:
            conn = self._get_sqlite_connection()
            try:
                return conn.execute("SELECT * FROM users WHERE phone_number = ?", (phone_number,)).fetchone()
            finally:
                conn.close()
    
    def create_new_user(self, phone_number, **kwargs):
        """Create new user"""
        if self.use_mongodb:
            user = create_user(phone_number, **kwargs)
            user['id'] = str(user['_id'])
            return user
        else:
            conn = self._get_sqlite_connection()
            try:
                conn.execute(
                    'INSERT INTO users (phone_number, state) VALUES (?, ?)',
                    (phone_number, kwargs.get('state', 'awaiting_full_info'))
                )
                conn.commit()
                return self.get_user_by_phone(phone_number)
            finally:
                conn.close()
    
    def update_user_field(self, phone_number, updates):
        """Update user fields"""
        if self.use_mongodb:
            return update_user(phone_number, updates)
        else:
            conn = self._get_sqlite_connection()
            try:
                # Build UPDATE query dynamically
                fields = ', '.join([f"{key} = ?" for key in updates.keys()])
                values = list(updates.values()) + [phone_number]
                conn.execute(f"UPDATE users SET {fields} WHERE phone_number = ?", values)
                conn.commit()
            finally:
                conn.close()
    
    # ==================== RESPONSE OPERATIONS ====================
    
    def save_user_response(self, user_id, quiz, question_number, response, correct):
        """Save quiz response"""
        if self.use_mongodb:
            return save_response(user_id, quiz, question_number, response, correct)
        else:
            conn = self._get_sqlite_connection()
            try:
                conn.execute(
                    "INSERT INTO responses (user_id, quiz, question_number, response, correct, timestamp) VALUES (?, ?, ?, ?, ?, datetime('now'))",
                    (user_id, quiz, question_number, response, int(correct))
                )
                conn.commit()
            finally:
                conn.close()
    
    def get_responses(self, user_id, quiz=None):
        """Get user responses"""
        if self.use_mongodb:
            return get_user_responses(user_id, quiz)
        else:
            conn = self._get_sqlite_connection()
            try:
                if quiz:
                    return conn.execute(
                        "SELECT * FROM responses WHERE user_id = ? AND quiz = ?",
                        (user_id, quiz)
                    ).fetchall()
                else:
                    return conn.execute(
                        "SELECT * FROM responses WHERE user_id = ?",
                        (user_id,)
                    ).fetchall()
            finally:
                conn.close()
    
    # ==================== QUIZ STATE OPERATIONS ====================
    
    def update_state(self, user_id, quiz_name, question_index):
        """Update quiz state"""
        if self.use_mongodb:
            return update_quiz_state(user_id, quiz_name, question_index)
        else:
            conn = self._get_sqlite_connection()
            try:
                conn.execute(
                    """INSERT OR REPLACE INTO quiz_states 
                       (user_id, quiz_name, question_index) 
                       VALUES (?, ?, ?)""",
                    (user_id, quiz_name, question_index)
                )
                conn.commit()
            finally:
                conn.close()
    
    # ==================== CONNECTION FOR LEGACY CODE ====================
    
    def get_connection(self):
        """Get database connection for legacy code that needs conn object"""
        if self.use_mongodb:
            # Return a mock connection object for MongoDB
            class MongoMockConnection:
                def execute(self, *args, **kwargs):
                    raise NotImplementedError("Use db.method() instead of conn.execute()")
                def commit(self):
                    pass  # MongoDB auto-commits
                def close(self):
                    pass  # MongoDB doesn't need closing
            return MongoMockConnection()
        else:
            return self._get_sqlite_connection()

# Global instance
db = DatabaseAdapter()