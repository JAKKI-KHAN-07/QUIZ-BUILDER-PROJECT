import json
import re
import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


def clean_json_response(text):
    text = text.strip()

    text = text.replace("```json", "")
    text = text.replace("```", "")

    match = re.search(r"\[.*\]", text, re.DOTALL)

    if match:
        text = match.group()

    return json.loads(text)


def generate_quiz(topic, difficulty, num_questions):

    prompt = f"""
Create EXACTLY {num_questions} multiple choice questions.

Topic:
{topic}

Difficulty:
{difficulty}

Rules:
- Exactly {num_questions} questions
- 4 options per question
- One correct answer
- Return ONLY JSON

[
 {{
   "question":"",
   "options":["","","",""],
   "answer":""
 }}
]
"""

    try:
        response = model.generate_content(prompt)

        return clean_json_response(response.text)

    except Exception as e:
        print("Gemini Error:", e)
        return []


def generate_quiz_from_text(
    text_data,
    difficulty,
    num_questions
):

    text_data = text_data[:15000]

    prompt = f"""
    Create EXACTLY {num_questions} multiple choice questions
    from the study material below.

    Difficulty:
    {difficulty}

    Rules:
    - Exactly {num_questions} questions
    - 4 options per question
    - One correct answer
    - Questions must come only from the study material
    - Return ONLY JSON

    Study Material:
    {text_data}

    Format:

    [
    {{
        "question":"",
        "options":["","","",""],
        "answer":""
    }}
    ]
"""

    try:

        response = model.generate_content(
            prompt
        )

        quiz = clean_json_response(
            response.text
        )

        if len(quiz) < num_questions:

            extra_prompt = f"""
Generate EXACTLY
{num_questions - len(quiz)}
more MCQs from the same study material.

Return ONLY JSON.
"""

            extra_response = model.generate_content(
                extra_prompt
            )

            extra_quiz = clean_json_response(
                extra_response.text
            )

            quiz.extend(extra_quiz)

        return quiz[:num_questions]

    except Exception as e:

        print(
            "Gemini Error:",
            e
        )

        return []