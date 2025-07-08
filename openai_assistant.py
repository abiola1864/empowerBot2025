# import os
# import openai
# from dotenv import load_dotenv
# import textwrap
# import time
# import logging
# from functools import lru_cache

# # Load environment variables from .env file
# load_dotenv()

# # Set the OpenAI API key
# openai.api_key = os.getenv("OPENAI_API_KEY")

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Global flag to indicate if the quota has been exceeded
# quota_exceeded = False

# def call_openai_api_with_retries(api_function, retries=5, backoff_in_seconds=1, **kwargs):
#     global quota_exceeded
#     if quota_exceeded:
#         logger.warning("Quota has been exceeded. No further API calls will be made.")
#         return None
    
#     for attempt in range(retries):
#         try:
#             response = api_function(**kwargs)
#             return response
#         except openai.error.RateLimitError:
#             logger.warning(f"Rate limit exceeded. Retrying in {backoff_in_seconds} seconds... Attempt {attempt + 1}/{retries}")
#             time.sleep(backoff_in_seconds)
#             backoff_in_seconds *= 2  # Exponential backoff
#         except openai.error.InsufficientQuotaError:
#             logger.error("Insufficient quota. Stopping further API calls.")
#             quota_exceeded = True
#             break
#         except Exception as e:
#             logger.error(f"An error occurred: {e}")
#             break
#     return None

# @lru_cache(maxsize=128)
# def check_question_relevance_cached(question):
#     """
#     Checks if the given question is related to record-keeping or digital marketing for small businesses.
#     Uses caching to avoid repeated API calls for the same question.
#     """
#     return check_question_relevance(question)

# def check_question_relevance(question):
#     """
#     Checks if the given question is related to record-keeping or digital marketing for small businesses.
#     """
#     messages = [
#         {"role": "system", "content": "You are a helpful assistant to determine if a question is related to record-keeping or digital marketing for small businesses."},
#         {"role": "user", "content": f"Is the following question related to record-keeping or digital marketing for small businesses?\n\nQuestion: {question}"}
#     ]
#     response = call_openai_api_with_retries(
#         openai.ChatCompletion.create,
#         model="gpt-3.5-turbo",
#         messages=messages,
#         max_tokens=64,
#         n=1,
#         stop=None,
#         temperature=0.7,
#     )
#     if response:
#         result = response.choices[0].message['content'].strip().lower()
#         return result == "related"
#     return False

# @lru_cache(maxsize=128)
# def handle_question_cached(question):
#     """
#     Handles the user's question using caching to avoid repeated API calls for the same question.
#     """
#     return handle_question(question)

# def handle_question(question, additional_prompt=None):
#     """
#     Send the user's question to the OpenAI API and return the response.
#     """
#     prompt = (
#         "You are a knowledgeable local tutor in Lagos, explaining concepts to small business owners with little or no education in a conversational manner using simple language. Keep your responses under 80 words."
#     )
#     messages = [
#         {"role": "system", "content": prompt},
#         {"role": "user", "content": question}
#     ]
#     response = call_openai_api_with_retries(
#         openai.ChatCompletion.create,
#         model="gpt-3.5-turbo",
#         messages=messages,
#         max_tokens=200,
#         n=1,
#         stop=None,
#         temperature=0.7,
#     )
#     if response:
#         answer = response.choices[0].message['content'].strip()
#         conversation = f"Person: {question}\nTutor: {answer}"
#         wrapped_conversation = textwrap.fill(conversation, width=80)
#         return wrapped_conversation
#     return "Failed to get a response from OpenAI API."

# # Example usage
# question = "How can I use social media to promote my small business?"
# if check_question_relevance_cached(question):
#     print(handle_question_cached(question))
# else:
#     print("The question is not related to record-keeping or digital marketing for small businesses.")
