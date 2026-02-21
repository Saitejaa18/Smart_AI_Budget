import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env file
load_dotenv()

# Initialize client only if API key is available
api_key = os.environ.get("GROQ_API_KEY")
if api_key:
    client = Groq(api_key=api_key)
else:
    client = None

def budget_ai_agent(expense_summary_text):
    prompt = f"""
    You are a Senior Financial Analyst & Budget Advisor.
    
    Here is the user's current expense summary:
    -------------------------------------------
    {expense_summary_text}
    -------------------------------------------

    Your task:
    1.  **Analyze**: Briefly identify 1-2 key patterns or concerns (e.g., spending too much in one category).
    2.  **Actionable Advice**: Provide 3 concrete, realistic tips to reduce spending in the top categories.
    3.  **Tone**: Professional yet encouraging. Start with a "Big Picture" comment.
    
    Keep your response concise (under 200 words).
    """
    return _call_groq_api(prompt)

def chat_with_data(context_text, user_question):
    prompt = f"""
    Context:
    {context_text}
    
    User Question: {user_question}
    
    Answer the user's question directly based on the context provided. Be helpful and specific.
    """
    return _call_groq_api(prompt)

def generate_savings_plan(context_text):
    prompt = f"""
    Context:
    {context_text}
    
    Task: Create a Savings Strategy.
    1. Apply the 50/30/20 rule (Needs/Wants/Savings) ideally, or suggest adjustments if they are overspending.
    2. Suggest specific categories to cut down on to reach saving goals.
    3. Project potential savings if they follow this advice.
    
    Format nicely with bullet points.
    """
    return _call_groq_api(prompt)

def _call_groq_api(prompt):
    try:
        if not client:
            yield "⚠️ AI Connection Error: GROQ_API_KEY environment variable not set.\nPlease set your GROQ_API_KEY to use the AI features."
            return
        
        stream = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        
        for chunk in stream:
            yield chunk.choices[0].delta.content or ""
            
    except Exception as e:
        yield f"⚠️ AI Connection Error: {str(e)}\nPlease ensure your GROQ_API_KEY is set in environment variables."
