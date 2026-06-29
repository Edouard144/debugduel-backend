import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv('GROQ_API_KEY'))
MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')

def judge_submissions(buggy_code, submission1, submission2, language):
    prompt = f"""You are an expert code judge for a competitive coding platform called DebugDuel.

Two developers were given this buggy {language} code to fix:

```{language}
{buggy_code}
```

Developer 1 submitted this fix:
```{language}
{submission1}
```

Developer 2 submitted this fix:
```{language}
{submission2}
```

Evaluate each submission on these criteria (0.0 to 1.0 scale):
- correctness: Does the fix actually fix the bug?
- cleanliness: Is the code clean, readable, and well-structured?
- efficiency: Is the solution efficient?
- security: Are there any security issues?

Return ONLY valid JSON in this exact format (no markdown, no extra text):
{{
  "player1": {{
    "correctness": 0.0,
    "cleanliness": 0.0,
    "efficiency": 0.0,
    "security": 0.0,
    "score": 0.0,
    "feedback": "brief feedback string"
  }},
  "player2": {{
    "correctness": 0.0,
    "cleanliness": 0.0,
    "efficiency": 0.0,
    "security": 0.0,
    "score": 0.0,
    "feedback": "brief feedback string"
  }},
  "winner": "player1" or "player2" or "tie"
}}

The overall score for each player is the average of their four criteria scores.
Determine the winner based on who has the higher overall score. Use "tie" if scores are equal.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1024,
    )

    content = response.choices[0].message.content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        content = content.rsplit("```", 1)[0]

    result = json.loads(content)
    return result
