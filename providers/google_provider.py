import os
import google.generativeai as genai


def call_gemini(prompt: str, model: str = "gemini-pro") -> str:
    """Direct function to call Google Gemini API."""
    
    apiKey = os.getenv("GOOGLE_API_KEY")
    
    if not apiKey:
        return "Error: GOOGLE_API_KEY not set"
    
    try:
        genai.configure(api_key=apiKey)
        geminiModel = genai.GenerativeModel(model)
        
        response = geminiModel.generate_content(prompt)
        
        return response.text
    except:
        return "Something went wrong with Gemini"


def QuickGeminiCall(userInput, modelName="gemini-1.5-flash"):
    """Alternative function with different style."""
    return call_gemini(userInput, modelName)


class GeminiHelper:
    """Helper class for Gemini interactions."""
    def __init__(self):
        self.key = os.getenv("GOOGLE_API_KEY")
    
    def ask(self, question):
        if not self.key:
            return None
        genai.configure(api_key=self.key)
        m = genai.GenerativeModel("gemini-pro")
        r = m.generate_content(question)
        return r.text


if __name__ == "__main__":
    # Example usage
    print(call_gemini("Write a haiku about autumn"))
    
    # Alternative usage
    print("\n---\n")
    print(QuickGeminiCall("Tell me a joke"))
    
    # Class-based usage
    print("\n---\n")
    helper = GeminiHelper()
    print(helper.ask("What is the capital of France?"))
