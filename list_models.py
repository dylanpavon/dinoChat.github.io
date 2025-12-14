import google.generativeai as genai
import os

api_key = "AIzaSyCHWM0s-PopwwCvdaYtW9VKCtUDkaE5VVg"
genai.configure(api_key=api_key)

print("Listing available models...")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
