import os
from dotenv import load_dotenv
from openai import OpenAI

def load_environment():
    load_dotenv()
    return os.getenv('OPENAI_API_KEY'), os.getenv('OPENAI_MODEL')

def get_ai_response(prompt, model):
    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
    
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    api_key, model = load_environment()
    
    while True:
        user_prompt = input("\nEnter your prompt (or 'quit' to exit): ")
        
        if user_prompt.lower() == 'quit':
            break
            
        response = get_ai_response(user_prompt, model)
        print("\nAI Response:")
        print(response)

if __name__ == "__main__":
    main() 
