import os
import logging
import json
import google.generativeai as genai
from django.shortcuts import render
from django.http import JsonResponse
import json
import re
from django.shortcuts import render, redirect
from django.contrib import messages
from pymongo import MongoClient
import bcrypt

# Set up logging
logger = logging.getLogger(__name__)

# Configure the Gemini API with an environment variable
genai.configure(api_key="AIzaSyBQhTgdeffYLYsH726KgHtvtF0i1YLjQ80")
model = genai.GenerativeModel("models/gemini-1.0-pro")


# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["english_trainer"]
collection = db["users"]


# Signup view
def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Check if user exists
        if collection.find_one({"username": username}):
            messages.error(request, "Username already exists!")
            return redirect("signup")

        # Hash the password and save user
        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        collection.insert_one({"username": username, "password": hashed_pw})
        messages.success(request, "Signup successful! Please login.")
        return redirect("login")

    return render(request, "signup.html")


# Login view
def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Find user in MongoDB
        user = collection.find_one({"username": username})
        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
            messages.success(request, "Login successful!")
            return redirect("home")  # Replace with your home view
        else:
            messages.error(request, "Invalid credentials!")
            return redirect("login")

    return render(request, "login.html")


def home(request):
    """Renders the home page."""
    return render(request, 'trainer/home.html')

def grammar_options(request):
    return render(request, 'trainer/grammar_options.html')

def vocab_options(request):
    return render(request, 'trainer/vocab_options.html')

def vocab_learn(request):
    return render(request, 'trainer/v_learn.html')

def exercise_options(request, exercise_type):
    context = {'exercise_type': exercise_type}
    return render(request, 'trainer/exercise_options.html', context)

def generate_question(question_type):
    
    if question_type == 'preposition':
        prompt = """Act as an English teacher. You are conducting a test to practice the prepositons.
            Your task is to generate a question with a missing word which should be from preposition .
            The question will be a multiple-choice question.
            Generate a question in the below JSON format: for example 
            {
                "sentence": "We will be meeting _____ Friday.",
                "options": ["at", "on", "from", "is"],
                "correct_answer": "on",
                "explanation": "We use 'on' with days of the week."
            }"""
            
    elif question_type == 'articles':
        prompt = """Act as an English teacher. You are conducting a test to practice the articles in english.
            Your task is to generate a question with a missing word which should be from articles .
            The question will be a multiple-choice question.
            Generate a question in the below JSON format: for example
            {
                "sentence": "I’m reading ___ book you recommended.",
                "options": ["a", "an", "the", "undefined"],
                "correct_answer": "the",
                "explanation": "The word 'the' is used when referring to a specific noun."
            }"""
            
    elif question_type == 'sentence_formation': # New question type
        prompt = """
        Act as an English teacher. You are conducting a test to practice the sentecnce formation.
            Your task is to generate a question with a missing word which should be from sentence formation .
            The question will be a multiple-choice question.
            Ensure the response is a valid JSON object without comments.
            ensure that the options contains the correct_answer
            example json format:
        {
            "sentence": "Arrange these words into a correct sentence: quickly, the, brown, fox, ran", 
            "options": ["The quickly brown fox ran.", "The brown fox ran quickly.", "Ran quickly the brown fox.", "Quickly the brown fox ran." ],
            "correct_answer": "The brown fox ran quickly.",
            "explanation": "The typical sentence structure in English is Subject + Verb + Object/Adverb."
        }
        """
    elif question_type == 'active_passive':  # New question type
        prompt = """
          Act as an English teacher. Generate a multiple-choice question to test knowledge of active and passive voice.
          Give a sentence in either active or passive voice and ask for the corresponding passive or active voice version.
          Generate a question in the below JSON format:
          {
              "sentence": "The dog chased the ball.",  
              "options": ["The ball was chased by the dog.", "The ball chased the dog.", "The dog was chased by the ball.", "The ball is chased by the dog."],
              "correct_answer": "The ball was chased by the dog.",
              "explanation": "The passive voice is formed with the verb 'to be' + past participle and in this case the ball is the subject."
          }
        """
    elif question_type == 'direct_indirect':  # New question type
          prompt = """
            Act as an English teacher. Generate a multiple-choice question about converting direct speech to indirect speech. for example 
            example JSON format:
            {
                "sentence": "\\"I am going to the market,\\" she said.",
                "options": ["She said that she was going to the market.", "She said she is going to the market.", "She said she will go to the market.", "She told that she is going to the market."],
                "correct_answer": "She said that she was going to the market.",
                "explanation": "In indirect speech, 'am' becomes 'was' and the quote is removed, and added that"
            }
    
        """
        
    elif question_type == 'conjunctions':
     prompt = """Act as an English teacher. You are conducting a test to practice conjunctions.
         Your task is to generate a question with a missing word which should be from conjunctions .
         The question will be a multiple-choice question.
         Generate a question in the below JSON format: for example 
         {
             "sentence": "I like tea, _____ I don't like coffee.",
             "options": ["and", "but", "or", "so"],
             "correct_answer": "but",
             "explanation": "'But' is a conjunction used to show contrast or opposition."
         }"""
    elif question_type == 'interjections':
            prompt = """Act as an English teacher. You are conducting a test to practice interjections.
            Your task is to generate a question with a missing word which should be from interjections .
            The question will be a multiple-choice question.
            Generate a question in the below JSON format: for example 
            {
                "sentence": "_____! That was a close call!",
                "options": ["Yes", "Wow", "Okay", "Well"],
                "correct_answer": "Wow",
                "explanation": "'Wow' is an interjection used to express surprise or amazement."
            }"""

    elif question_type == 'nouns':
        prompt = """Act as an English teacher. You are conducting a test to practice nouns.
            Your task is to generate a question with a missing word which should be from nouns .
            The question will be a multiple-choice question.
            Generate a question in the below JSON format: for example
            {
                "sentence": "The _____ jumped over the fence.",
                "options": ["running", "quickly", "dog", "eats"],
                "correct_answer": "dog",
                "explanation": "A noun is a word for a person, place, thing or idea and 'dog' is a word for an animal."
            }"""

    elif question_type == 'pronouns':
        prompt = """Act as an English teacher. You are conducting a test to practice pronouns.
            Your task is to generate a question with a missing word which should be from pronouns.
            The question will be a multiple-choice question.
            Generate a question in the below JSON format: for example
            {
                "sentence": "She gave the book to _____.",
                "options": ["him", "her", "I", "we"],
                "correct_answer": "him"
                "explanation": "'him' is an object pronoun used when the pronoun is on the object."
            }"""

    elif question_type == 'tenses':
            prompt = """Act as an English teacher. You are conducting a test to practice tenses.
                Your task is to generate a question with a missing word which should be from tenses.
                The question will be a multiple-choice question.
                Generate a question in the below JSON format: for example
                {
                    "sentence": "They _____ to the park yesterday.",
                    "options": ["go", "went", "going", "gone"],
                    "correct_answer": "went",
                    "explanation": "The past simple tense, 'went', is used to talk about an action that happened in the past."
                }"""

    elif question_type == 'verbs_adverbs':
            prompt = """Act as an English teacher. You are conducting a test to practice verbs and adverbs.
                Your task is to generate a question with a missing word which should be from verbs or adverbs .
                The question will be a multiple-choice question.
                Generate a question in the below JSON format: for example
                {
                    "sentence": "The dog runs ____.",
                    "options": ["quickly", "quick", "slowly", "slow"],
                    "correct_answer": "quickly",
                    "explanation": "'quickly' is an adverb modifying the verb 'runs'."
                }"""

    elif question_type == 'adjectives':
        prompt = """Act as an English teacher. You are conducting a test to practice adjectives.
                Your task is to generate a question with a missing word which should be from adjectives.
                The question will be a multiple-choice question.
                Generate a question in the below JSON format: for example
                {
                    "sentence": "She has a _____ dress.",
                    "options": ["runs", "beautiful", "eats", "quickly"],
                    "correct_answer": "beautiful",
                    "explanation": "'beautiful' is an adjective that describes the noun 'dress'."
                }"""
             
    elif question_type == 'vocabulary':  # New vocabulary question type
        prompt = """
          Act as an English teacher. Generate a multiple-choice question to test vocabulary knowledge.
          Provide a sentence with a missing word and multiple options, ensuring the correct answer is a commonly used word in English vocabulary.
          Generate a question in the below JSON format:
          {
              "sentence": "The chef prepared a _____ meal for the guests.",
              "options": ["delicious", "happy", "angry", "unprepared"],
              "correct_answer": "delicious",
              "explanation": "Delicious is an adjective used to refer to a very tasty meal."
          }
        """

    else:
        return None
    
    try:
        response = model.generate_content(prompt)
        raw_response = response.text.strip()
        print("Debugging: Raw Response Text:", raw_response)

        # Clean up improper quotes in the JSON
        # Escape inner quotes
        cleaned_response = re.sub(r'#.*', '', raw_response).strip()

        cleaned_response = re.sub(r'(?<!\\)"(.*?)"(?![:,])', r'"\1"', raw_response)
        cleaned_response = cleaned_response.replace('*', '').strip()
        # Ensure valid JSON format
        cleaned_response = cleaned_response.replace('""', '"').strip()

        # Parse JSON
        question_data = json.loads(cleaned_response)

        # Validate the structure
        if not all(key in question_data for key in ("sentence", "options", "correct_answer")):
            print("Invalid response structure:", question_data)
            return None

        print("Debugging: Parsed Question Data:", question_data)
        return question_data
    except json.JSONDecodeError as e:
        print("Error parsing response as JSON:", e)
        print("Response text for debugging:", raw_response)
        return None
    except Exception as e:
        print("Unexpected error:", e)
        return None

def handle_post_request(request, question_type):
    action = request.POST.get('action')
    question_data = None

    if action == 'try_again':
        try:
            question_data = json.loads(request.POST.get('question', '{}'))
            return render(request, f'trainer/{question_type}.html', {
                'question': question_data, 'message': "Try again!"
            })
        except json.JSONDecodeError:  # Handle potential JSON error
            print("Error parsing 'question' data from POST.")
            # Generate a new question if there's a parsing error
            question_data = generate_question(question_type)
            return render(request, f'trainer/{question_type}.html', {'question': question_data})

    elif action == 'next_question':
        question_data = generate_question(question_type)

    if question_data is None:  # Handle cases where generation fails
        return render(request, f'trainer/{question_type}.html', {'question': None, 'error': "Could not generate a question. Please try again."})  # Error message
    else:
        return render(request, f'trainer/{question_type}.html', {'question': question_data})

def preposition(request):
    if request.method == 'POST':
        return handle_post_request(request, 'preposition')  # Use helper
    question_data = generate_question('preposition')
    return render(request, 'trainer/preposition.html', {'question': question_data})

def articles(request):
    if request.method == 'POST':
        return handle_post_request(request, 'articles')  # Use helper
    question_data = generate_question('articles')
    return render(request, 'trainer/articles.html', {'question': question_data})

def sentence_formation(request):
    if request.method == 'POST':
        return handle_post_request(request, 'sentence_formation')
    question_data = generate_question('sentence_formation')
    return render(request, 'trainer/sentence_formation.html', {'question': question_data})

def active_passive(request):
    if request.method == 'POST':
        return handle_post_request(request,'active_passive')
    question_data = generate_question('active_passive')
    return render(request, 'trainer/active_passive.html', {'question': question_data})

def direct_indirect(request):
    if request.method == 'POST':
        return handle_post_request(request, 'direct_indirect')  # Use helper
    question_data = generate_question('direct_indirect')
    return render(request, 'trainer/direct_indirect.html', {'question': question_data})

def conjunctions(request):
    if request.method == 'POST':
        return handle_post_request(request, 'conjunctions')
    question_data = generate_question('conjunctions')
    return render(request, 'trainer/conjunctions.html', {'question': question_data})

def interjections(request):
    if request.method == 'POST':
        return handle_post_request(request, 'interjections')
    question_data = generate_question('interjections')
    return render(request, 'trainer/interjections.html', {'question': question_data})

def nouns(request):
    if request.method == 'POST':
        return handle_post_request(request, 'nouns')
    question_data = generate_question('nouns')
    return render(request, 'trainer/nouns.html', {'question': question_data})

def pronouns(request):
    if request.method == 'POST':
        return handle_post_request(request, 'pronouns')
    question_data = generate_question('pronouns')
    return render(request, 'trainer/pronouns.html', {'question': question_data})

def tenses(request):
     if request.method == 'POST':
         return handle_post_request(request, 'tenses')
     question_data = generate_question('tenses')
     return render(request, 'trainer/tenses.html', {'question': question_data})

def verbs_adverbs(request):
     if request.method == 'POST':
          return handle_post_request(request, 'verbs_adverbs')
     question_data = generate_question('verbs_adverbs')
     return render(request, 'trainer/verbs_adverbs.html', {'question': question_data})

def adjectives(request):
    if request.method == 'POST':
        return handle_post_request(request, 'adjectives')
    question_data = generate_question('adjectives')
    return render(request, 'trainer/adjectives.html', {'question': question_data})

def vocabulary(request):
    if request.method == "POST":
        return handle_post_request(request, "vocabulary")  # Use helper
    question_data = generate_question("vocabulary")
    return render(request, "trainer/vocabulary.html", {"question": question_data})

def learn_exercise(request, exercise_type):
    template_name = f"trainer/L_{exercise_type.capitalize()}.html"
    return render(request, template_name)

def generate_fillup_question(question_type):
    if question_type == 'preposition':
        prompt = """Act as an English teacher. Generate a fill-in-the-blank question to test the knowledge of prepositions.
            Provide a sentence with a blank for the preposition.
            Generate a question in the below JSON format: for example 
            {
                "sentence": "The cat is sitting _____ the table.",
                "answer": "on",
                "explanation": "The preposition 'on' is used to indicate something is located on the surface of something."
            }"""

    elif question_type == 'articles':
        prompt = """Act as an English teacher. Generate a fill-in-the-blank question to test the knowledge of articles.
            Provide a sentence with a blank for the article.
            Generate a question in the below JSON format: for example 
            {
                "sentence": "I have ___ dog.",
                "answer": "a",
                "explanation": "The article 'a' is used before a consonant sound."
            }"""
            
    elif question_type == 'sentence_formation':
        prompt = """
        Act as an English teacher. Generate a fill-in-the-blank question to test the knowledge of sentence formation.
        Provide a sentence with a blank where the student needs to arrange the words to correct the sentence.
            Generate a question in the below JSON format: for example 
            {
                "sentence": "Arrange the words to form a correct sentence: watch / likes / he / every / movies / weekend / to",
                "answer": "He likes to watch movies every weekend.",
                "explanation": "The correct sentence formation is Subject + Verb + Object."
            }"""
            
    elif question_type == 'active_passive':
        prompt = """
            Act as an English teacher. Generate a fill-in-the-blank question to test the knowledge of active and passive voice.
            Provide a sentence in active or passive voice, with a blank where the student needs to fill with a word in active or passive voice.
            Generate a question in the below JSON format: for example
            {
            "sentence": "The cake _____ by me.(eat)",  
            "answer": "was eaten",
            "explanation":"The passive voice is formed using 'was' + past participle of the verb"
            }
        """
        
    elif question_type == 'direct_indirect':
        prompt = """
          Act as an English teacher. Generate a fill-in-the-blank question to test the knowledge of direct and indirect speech.
     Provide a sentence in direct speech and its corresponding indirect speech with a blank.
     Ensure the output contains both the direct and indirect speech sentences on separate lines using a newline character '\\n'. The indirect speech sentence will have a blank to be filled.
     Generate a question in the below JSON format: for example
         {
           "sentence": "Direct speech: She said, \\"I am studying now.\\"\\nIndirect speech: She said that she __________ studying then.",
            "answer": "was",
            "explanation": "In indirect speech, the tense of the verb changes from present to past."
        }"""
        
    elif question_type == 'conjunctions':
     prompt = """Act as an English teacher. Generate a fill-in-the-blank question to test the knowledge of conjunctions.
         Provide a sentence with a blank for the conjunction.
          Generate a question in the below JSON format: for example 
         {
             "sentence": "I was tired, _____ I still went to the party.",
             "answer": "but",
             "explanation": "The conjunction 'but' is used to show a contrast or exception."
         }"""
         
    elif question_type == 'interjections':
        prompt = """Act as an English teacher. Generate a fill-in-the-blank question to test the knowledge of interjections.
        Provide a sentence with a blank for the interjection.
            Generate a question in the below JSON format: for example 
            {
                "sentence": "_____, that’s a fantastic idea!",
                "answer": "Wow",
                "explanation": "'Wow' is an interjection used to show amazement."
            }"""

    elif question_type == 'nouns':
        prompt = """
        Act as an English teacher. Generate a fill-in-the-blank question to test the knowledge of nouns.
        Provide a sentence with a blank for the noun.
            Generate a question in the below JSON format: for example 
            {
                "sentence": "The _____ in the park is very beautiful.",
                "answer": "tree",
                 "explanation":"A noun is a word that is used to identify a person, place or thing and 'tree' is used to identify a thing."
                
            }"""

    elif question_type == 'pronouns':
        prompt = """
        Act as an English teacher. Generate a fill-in-the-blank question to test the knowledge of pronouns.
        Provide a sentence with a blank for the pronoun.
            Generate a question in the below JSON format: for example 
            {
                "sentence": "He gave the book to _____.",
                "answer": "me",
                 "explanation": "'me' is a pronoun used to represent the person on which action is performed"
            }"""

    elif question_type == 'tenses':
        prompt = """
            Act as an English teacher. Generate a fill-in-the-blank question to test the knowledge of tenses.
            Provide a sentence with a blank for the tense-related verb form.
            Generate a question in the below JSON format: for example
            {
                "sentence": "I _____ to the store yesterday.",
                "answer": "went",
                "explanation":"The past simple tense 'went' is used to indicate that the action happened in the past"
            }"""

    elif question_type == 'verbs_adverbs':
        prompt = """
        Act as an English teacher. Generate a fill-in-the-blank question to test the knowledge of verbs or adverbs.
            Provide a sentence with a blank for the verb or adverb.
            Generate a question in the below JSON format: for example
            {
                "sentence": "The cat jumped ______ on the table.",
                "answer": "quickly",
                "explanation":"'quickly' is an adverb used to indicate how a verb has been performed"
            }"""

    elif question_type == 'adjectives':
        prompt = """
            Act as an English teacher. Generate a fill-in-the-blank question to test the knowledge of adjectives.
            Provide a sentence with a blank for the adjective.
            Generate a question in the below JSON format: for example
            {
                "sentence": "It was a _____ day.",
                "answer": "sunny",
                "explanation": "'sunny' is an adjective used to describe the noun 'day'."
            }"""
            
    else:
        return None
    
    try:
        response = model.generate_content(prompt)
        raw_response = response.text.strip()
        print("Debugging: Raw Fillup Response Text:", raw_response)

        # Clean up improper quotes in the JSON
        cleaned_response = re.sub(r'#.*', '', raw_response).strip()

        cleaned_response = re.sub(r'(?<!\\)"(.*?)"(?![:,])', r'"\1"', raw_response)

        cleaned_response = cleaned_response.replace('\\n', '').strip()    
        cleaned_response = cleaned_response.replace('*', '').strip()
        # Ensure valid JSON format
        cleaned_response = cleaned_response.replace('""', '"').strip()

        # Parse JSON
        question_data = json.loads(cleaned_response)

        # Validate the structure
        if not all(key in question_data for key in ("sentence", "answer")):
            print("Invalid fill-up response structure:", question_data)
            return None

        print("Debugging: Parsed Fill-up Question Data:", question_data)
        return question_data
    except json.JSONDecodeError as e:
        print("Error parsing fill-up response as JSON:", e)
        print("Fill-up response text for debugging:", raw_response)
        return None
    except Exception as e:
        print("Unexpected fill-up error:", e)
        return None

def handle_fillup_post_request(request, question_type):
        if request.method == 'POST':
           action = request.POST.get('action')
           question_data = None

           if action == 'try_again':
              try:
                question_data = json.loads(request.POST.get('question', '{}'))
                return render(request, f'trainer/fillup.html', {
                    'question': question_data, 'message': "Try again!"
                })
              except json.JSONDecodeError:
                  print("Error parsing 'question' data from POST.")
                  question_data = generate_fillup_question(question_type)
                  return render(request, f'trainer/fillup.html', {'question': question_data})
           
           elif action == 'next_question':
                question_data = generate_fillup_question(question_type)
           if question_data is None:
              return render(request, f'trainer/fillup.html', {'question': None, 'error': "Could not generate fill-up question. Please try again."})
           else:
              return render(request, f'trainer/fillup.html', {'question': question_data})

def fillup(request, question_type):
        if request.method == 'POST':
             return handle_fillup_post_request(request,question_type)
        question_data = generate_fillup_question(question_type)
        return render(request, 'trainer/fillup.html', {'question': question_data})

def speaking(request):
     """Renders the speaking exercise page."""
     return render(request, 'trainer/speaking.html')
 
def generate_speaking_statement(request):
     """Generates a statement for speaking practice using Gemini."""
     prompt = """Act as an English teacher. Generate a simple, short, and common sentence for a student to speak for communication practice.
     the sentence should be used to check the pronunication of the user, avoid preamble and avoid printing like this for example [student's name],[candidate's name],[user's name]"""
     try:
         response = model.generate_content(prompt)
         statement = response.text.strip()
          # Clean the statement 
         statement = re.sub(r'#.*', '', statement).strip()
         return JsonResponse({'statement': statement})
     except Exception as e:
         print("Error generating speaking statement:", e)
         return JsonResponse({'error': 'Failed to generate statement.'}, status=500)