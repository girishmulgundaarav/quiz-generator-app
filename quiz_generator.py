import json
import re
import openai


def generate_quiz(topic, difficulty, num_q):
    prompt = f"""
    Generate {num_q} multiple-choice questions on "{topic}".
    Difficulty: {difficulty}.

    STRICT JSON ONLY:
    [
      {{
        "question": "...?",
        "options": ["A", "B", "C", "D"],
        "answer": "B",
        "explanation": "short explanation"
      }}
    ]
    """

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content
    json_text = re.search(r"\[.*\]", content, re.DOTALL).group()
    return json.loads(json_text)
