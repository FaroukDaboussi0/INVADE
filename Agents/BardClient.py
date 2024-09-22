import base64
import httpx
import os
import google.generativeai as genai
import time
import re  

class BardClient:
    def __init__(self, api_key=None):
        # Configure the generative AI client
        self.api_key = api_key or os.environ.get('GOOGLE_API_KEY')
        genai.configure(api_key=self.api_key)
        
        # Define safety settings
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"}
        ]
        
        # Initialize the generative model
        self.model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=self.safety_settings)
    
    def bard(self, text):
        """Generate content using the generative model with retry logic."""
        for attempt in range(3):
            try:
                # Generate content
                response = self.model.generate_content(text)
                time.sleep(5)
                
                # Check if response is valid
                if not response or not hasattr(response, 'text'):
                    raise ValueError("Invalid operation: The `response.text` quick accessor requires the response to contain a valid `Part`, but none were returned. Please check the `candidate.safety_ratings` to determine if the response was blocked.")
                
                return response.text
            except ValueError as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt == 2:
                    print("Continuing after 3 failed attempts.")
                    return None

    def extract_substring(self, text, left_delimiter, right_delimiter):
        """
        Extracts the first substring from the given text that is enclosed between the specified left and right delimiters.

        :param text: The input string containing the text with delimiters
        :param left_delimiter: The delimiter used to start the substring
        :param right_delimiter: The delimiter used to end the substring
        :return: The first substring found between the left and right delimiters, or None if no match is found
        """
        # Construct the regular expression pattern
        pattern = fr'{re.escape(left_delimiter)}(.*?){re.escape(right_delimiter)}'
        
        # Find the first match in the input text
        match = re.search(pattern, text, re.DOTALL)
        
        if match:
            return match.group(1)  # Return the captured substring
        else:
            return text  # Return None if no match is found

