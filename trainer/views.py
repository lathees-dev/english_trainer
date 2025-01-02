import os
import logging
import json
import google.generativeai as genai
from django.shortcuts import render
from django.http import JsonResponse
import json
import re

# Set up logging
logger = logging.getLogger(__name__)

# Configure the Gemini API with an environment variable
genai.configure(api_key="AIzaSyBQhTgdeffYLYsH726KgHtvtF0i1YLjQ80")
model = genai.GenerativeModel("models/gemini-1.0-pro")

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
                "correct_answer": "on"
            }"""
            
    elif question_type == 'articles':
        prompt = """Act as an English teacher. You are conducting a test to practice the articles in english.
            Your task is to generate a question with a missing word which should be from articles .
            The question will be a multiple-choice question.
            Generate a question in the below JSON format: for example
            {
                "sentence": "I’m reading ___ book you recommended.",
                "options": ["a", "an", "the", "undefined"],
                "correct_answer": "the"
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
            "correct_answer": "The brown fox ran quickly."
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
              "correct_answer": "The ball was chased by the dog."
          }
        """
    elif question_type == 'direct_indirect':  # New question type
          prompt = """
            Act as an English teacher. Generate a multiple-choice question about converting direct speech to indirect speech. for example 
            example JSON format:
            {
                "sentence": "\\"I am going to the market,\\" she said.",
                "options": ["She said that she was going to the market.", "She said she is going to the market.", "She said she will go to the market.", "She told that she is going to the market."],
                "correct_answer": "She said that she was going to the market."
            }
    
        """
        
    elif question_type == 'vocabulary':  # New vocabulary question type
        prompt = """
          Act as an English teacher. Generate a multiple-choice question to test vocabulary knowledge.
          Provide a sentence with a missing word and multiple options, ensuring the correct answer is a commonly used word in English vocabulary.
          Generate a question in the below JSON format:
          {
              "sentence": "The chef prepared a _____ meal for the guests.",
              "options": ["delicious", "happy", "angry", "unprepared"],
              "correct_answer": "delicious"
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
                "answer": "on"
            }"""

    elif question_type == 'articles':
        prompt = """Act as an English teacher. Generate a fill-in-the-blank question to test the knowledge of articles.
            Provide a sentence with a blank for the article.
            Generate a question in the below JSON format: for example 
            {
                "sentence": "I have ___ dog.",
                "answer": "a"
            }"""
    elif question_type == 'sentence_formation':
        prompt = """
        Act as an English teacher. Generate a fill-in-the-blank question to test the knowledge of sentence formation.
        Provide a sentence with a blank where the student needs to arrange the words to correct the sentence.
            Generate a question in the below JSON format: for example 
            {
                "sentence": "Arrange the words to form a correct sentence: watch / likes / he / every / movies / weekend / to",
                "answer": "He likes to watch movies every weekend."
            }"""
    elif question_type == 'active_passive':
        prompt = """
            Act as an English teacher. Generate a fill-in-the-blank question to test the knowledge of active and passive voice.
            Provide a sentence in active or passive voice, with a blank where the student needs to fill with a word in active or passive voice.
            Generate a question in the below JSON format: for example
            {
            "sentence": "The cake _____ by me.(eat)",  
            "answer": "was eaten"
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
                "answer": "was"
            }
        """
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
