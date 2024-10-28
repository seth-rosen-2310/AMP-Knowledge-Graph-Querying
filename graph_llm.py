import os
import openai

API_KEY = os.getenv("API_KEY")

def build_ir(question, prompt):
    prompt.append({"role": "user", "content": question})
    openai.api_key = API_KEY
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      temperature=0.0,
      messages=prompt
    )
    return response['choices'][0]['message']['content'].strip()

