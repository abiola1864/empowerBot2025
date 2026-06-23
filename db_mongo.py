import os
import logging
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from datetime import datetime
from bson import ObjectId

logger = logging.getLogger(__name__)

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI')

# Global client cache
_mongo_client = None

def get_mongo_client():
    """Get MongoDB client with improved error handling"""
    global _mongo_client
    
    if not MONGODB_URI:
        raise ValueError("MONGODB_URI not set in environment variables")
    
    # Return cached client if it exists and is healthy
    if _mongo_client is not None:
        try:
            _mongo_client.admin.command('ping', maxTimeMS=2000)
            return _mongo_client
        except:
            logger.warning("Cached MongoDB client unhealthy, reconnecting...")
            _mongo_client = None
    
    try:
        logger.info("Connecting to MongoDB Atlas...")
        
        # Create client with optimized settings
        _mongo_client = MongoClient(
            MONGODB_URI,
            # Timeout settings (shorter for faster failure detection)
            serverSelectionTimeoutMS=10000,  # 10 seconds
            connectTimeoutMS=10000,
            socketTimeoutMS=20000,
            
            # Retry and reliability
            retryWrites=True,
            retryReads=True,
            w='majority',
            
            # SSL/TLS (explicit configuration)
            tls=True,
            tlsAllowInvalidCertificates=False,
            tlsAllowInvalidHostnames=False,
            
            # Connection pool
            maxPoolSize=50,
            minPoolSize=10,
            maxIdleTimeMS=45000
        )
        
        # Test connection with explicit timeout
        _mongo_client.admin.command('ping', maxTimeMS=5000)
        logger.info("✅ Connected to MongoDB successfully")
        
        return _mongo_client
        
    except ServerSelectionTimeoutError as e:
        error_msg = str(e)
        if 'SSL' in error_msg or 'TLS' in error_msg:
            logger.error("❌ SSL/TLS handshake failed with MongoDB Atlas")
            logger.error("→ Check: Network Access whitelist in MongoDB Atlas")
            logger.error("→ Add: 0.0.0.0/0 or Render.com IPs to whitelist")
        else:
            logger.error(f"❌ MongoDB connection timeout: {error_msg[:200]}")
        raise
        
    except ConnectionFailure as e:
        logger.error(f"❌ MongoDB connection failed: {str(e)[:200]}")
        raise
        
    except Exception as e:
        logger.error(f"❌ Unexpected MongoDB error: {str(e)[:200]}")
        raise

def get_mongo_db():
    """Get MongoDB database"""
    client = get_mongo_client()
    db_name = os.getenv('MONGODB_DB_NAME', 'empowerbot_db')
    return client[db_name]

# Collections
def get_users_collection():
    db = get_mongo_db()
    return db.users

def get_responses_collection():
    db = get_mongo_db()
    return db.responses

def get_quiz_states_collection():
    db = get_mongo_db()
    return db.quiz_states

def get_questions_collection():
    db = get_mongo_db()
    return db.questions

def get_conversation_history_collection():
    db = get_mongo_db()
    return db.conversation_history

def get_followup_questions_collection():
    db = get_mongo_db()
    return db.followup_questions

def get_user_scores_collection():
    db = get_mongo_db()
    return db.user_scores

# Initialize MongoDB
def init_mongodb():
    """Initialize MongoDB collections with indexes"""
    try:
        db = get_mongo_db()
        
        logger.info("Creating MongoDB indexes...")
        
        # Create indexes
        db.users.create_index("phone_number", unique=True)
        db.users.create_index("name")
        
        db.responses.create_index([("user_id", 1), ("quiz", 1)])
        db.responses.create_index("timestamp")
        
        db.quiz_states.create_index([("user_id", 1), ("quiz_name", 1)], unique=True)
        
        db.questions.create_index([("quiz", 1), ("question_number", 1)], unique=True)
        
        db.user_scores.create_index("user_id", unique=True)
        db.user_scores.create_index("score")
        
        logger.info("✅ MongoDB indexes created successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ MongoDB initialization failed: {e}")
        return False

# User operations
def find_user_by_phone(phone_number):
    """Find user by phone number"""
    users = get_users_collection()
    return users.find_one({"phone_number": phone_number})

def create_user(phone_number, name=None, **kwargs):
    """Create new user"""
    users = get_users_collection()
    user_data = {
        "phone_number": phone_number,
        "name": name,
        "created_at": datetime.utcnow(),
        "state": kwargs.get("state", "awaiting_full_info"),
        **kwargs
    }
    result = users.insert_one(user_data)
    user_data["_id"] = result.inserted_id
    return user_data

def update_user(phone_number, updates):
    """Update user by phone number"""
    users = get_users_collection()
    updates["updated_at"] = datetime.utcnow()
    return users.update_one(
        {"phone_number": phone_number},
        {"$set": updates}
    )

def delete_user_completely(phone_number):
    """Delete user and ALL associated data"""
    try:
        db = get_mongo_db()
        
        user = find_user_by_phone(phone_number)
        if not user:
            return {"error": "User not found"}
        
        user_id = str(user["_id"])
        
        deletion_summary = {}
        deletion_summary["responses"] = db.responses.delete_many({"user_id": user_id}).deleted_count
        deletion_summary["quiz_states"] = db.quiz_states.delete_many({"user_id": user_id}).deleted_count
        deletion_summary["conversation_history"] = db.conversation_history.delete_many({"user_id": user_id}).deleted_count
        deletion_summary["followup_questions"] = db.followup_questions.delete_many({"user_id": user_id}).deleted_count
        deletion_summary["user_scores"] = db.user_scores.delete_many({"user_id": user_id}).deleted_count
        deletion_summary["users"] = db.users.delete_one({"phone_number": phone_number}).deleted_count
        
        logger.info(f"✅ Deleted user {phone_number}: {deletion_summary}")
        return {"success": True, "summary": deletion_summary}
        
    except Exception as e:
        logger.error(f"❌ Error deleting user: {e}")
        return {"error": str(e)}

# Response operations
def save_response(user_id, quiz, question_number, response, correct):
    """Save quiz response"""
    responses = get_responses_collection()
    response_data = {
        "user_id": user_id,
        "quiz": quiz,
        "question_number": question_number,
        "response": response,
        "correct": correct,
        "timestamp": datetime.utcnow()
    }
    return responses.insert_one(response_data)

def get_user_responses(user_id, quiz=None):
    """Get user's responses"""
    responses = get_responses_collection()
    query = {"user_id": user_id}
    if quiz:
        query["quiz"] = quiz
    return list(responses.find(query).sort("timestamp", 1))

def get_incorrect_responses(user_id, quiz=None):
    """Get user's incorrect responses"""
    responses = get_responses_collection()
    query = {"user_id": user_id, "correct": False}
    if quiz:
        query["quiz"] = quiz
    return list(responses.find(query).sort("question_number", 1))

# Quiz state operations
def get_quiz_state(user_id, quiz_name):
    """Get quiz state"""
    quiz_states = get_quiz_states_collection()
    return quiz_states.find_one({"user_id": user_id, "quiz_name": quiz_name})

def update_quiz_state(user_id, quiz_name, question_index):
    """Update or create quiz state"""
    quiz_states = get_quiz_states_collection()
    return quiz_states.update_one(
        {"user_id": user_id, "quiz_name": quiz_name},
        {"$set": {"question_index": question_index, "updated_at": datetime.utcnow()}},
        upsert=True
    )

def delete_quiz_state(user_id, quiz_name):
    """Delete quiz state"""
    quiz_states = get_quiz_states_collection()
    return quiz_states.delete_one({"user_id": user_id, "quiz_name": quiz_name})

# Question operations
def get_questions_for_quiz(quiz_name):
    """Get all questions for a quiz"""
    questions = get_questions_collection()
    return list(questions.find({"quiz": quiz_name}).sort("question_number", 1))

def get_question_by_number(quiz_name, question_number):
    """Get specific question"""
    questions = get_questions_collection()
    return questions.find_one({"quiz": quiz_name, "question_number": question_number})



def init_mongodb():
    """Initialize MongoDB collections with indexes"""
    try:
        db = get_mongo_db()
        
        logger.info("Creating MongoDB indexes...")
        
        # Existing indexes
        db.users.create_index("phone_number", unique=True)
        db.users.create_index("name")
        
        db.responses.create_index([("user_id", 1), ("quiz", 1)])
        db.responses.create_index("timestamp")
        
        db.quiz_states.create_index([("user_id", 1), ("quiz_name", 1)], unique=True)
        
        db.questions.create_index([("quiz", 1), ("question_number", 1)], unique=True)
        
        db.user_scores.create_index("user_id", unique=True)
        db.user_scores.create_index("score")
        
        # ✅ NEW indexes
        db.quiz_status.create_index("quiz", unique=True)
        db.processed_messages.create_index("message_id", unique=True)
        db.followup_questions.create_index([("user_id", 1), ("quiz_name", 1)])
        db.explanation_history.create_index([("user_id", 1), ("quiz", 1), ("question_number", 1)])
        db.post10_quizzes.create_index([("user_id", 1), ("quiz_number", 1)])
        db.post10_quiz_responses.create_index("quiz_id")
        db.records.create_index("user_id")
        
        logger.info("✅ MongoDB indexes created successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ MongoDB initialization failed: {e}")
        return False