import requests
import os
from dotenv import load_dotenv

load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

def query_together(prompt, model="mistralai/Mixtral-8x7B-Instruct-v0.1", max_tokens=2048):
    url = "https://api.together.xyz/v1/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": 0.3,
        "top_p": 0.9
    }
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    if response.status_code != 200:
        raise RuntimeError(f"LLM API error: {response.status_code} - {response.text}")
    return response.json()["choices"][0]["text"].strip()

if __name__ == "__main__":
    test_prompt = "Classify this slide content: 'Our team has 10 years of experience in fintech product development.' Return only one category from: Problem, Solution, Market, Business Model, Competition, Team, Financials, Traction, Funding Ask."
    try:
        result = query_together(test_prompt)
        print("LLM Response:", result)
    except Exception as e:
        print("Error:", e)

