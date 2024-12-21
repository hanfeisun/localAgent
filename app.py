from flask import Flask, render_template, request
import google.generativeai as genai
import os
import subprocess
import tempfile
import time
import re
from pathlib import Path

app = Flask(__name__)

# Initialize Gemini API
api_key_path = os.path.expanduser("~/api_key")
try:
    with open(api_key_path) as f:
        genai.configure(api_key=f.read().strip())
except FileNotFoundError:
    print(f"Error: API key file not found at {api_key_path}")
    exit(1)

# Configure the model
model = genai.GenerativeModel('gemini-2.0-flash-exp')

def clean_code_response(text):
    # Remove markdown code block if present
    text = re.sub(r'^```\w*\n', '', text)  # Remove opening ```python or similar
    text = re.sub(r'\n```$', '', text)     # Remove closing ```
    return text.strip()

def run_in_iterm(command, temp_file):
    # Create a temporary file to store the output
    output_file = f"{temp_file}.output"
    
    # Create AppleScript to run the command in iTerm and capture output
    apple_script = f'''
        tell application "iTerm2"
            create window with default profile
            tell current session of current window
                write text "python3 \\"{temp_file}\\" > \\"{output_file}\\" 2>&1"
            end tell
        end tell
    '''
    
    # Run the AppleScript
    subprocess.run(['osascript', '-e', apple_script])
    
    # Wait a bit for the command to complete
    time.sleep(2)
    
    # Read the output if file exists
    try:
        with open(output_file, 'r') as f:
            output = f.read()
        # Clean up output file
        os.remove(output_file)
        return output
    except FileNotFoundError:
        return "Output not available yet. Check iTerm2 window for results."

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            prompt = request.form['prompt']
            
            # Prepare the system message and user prompt
            system_prompt = """You are a Python code generator. Your task is to generate ONLY pure Python code.

IMPORTANT RULES:
- DO NOT include any markdown formatting (no ``` blocks)
- DO NOT include any comments or explanations
- Output ONLY the raw Python code that can be directly executed
- Include all necessary imports at the top
- Code must be compatible with MacOS 15 (Sonoma) and Python 3
- Use MacOS-specific paths and features when needed
- Handle file paths using os.path or pathlib
- Use UTF-8 encoding for file operations
- If using GUI, use native MacOS solutions (tkinter, PyQt)

Example of correct output format:
import os
print('Hello World')

Example of INCORRECT output format:
```python
import os
print('Hello World')
```
"""
            
            # Make API request to Gemini
            response = model.generate_content([
                system_prompt,
                f"Generate Python code for: {prompt}. Remember, output ONLY the raw code without any markdown or formatting."
            ])
            
            # Extract and clean the code from the response
            code = clean_code_response(response.text)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir='/tmp', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Run in iTerm and get output
            output = run_in_iterm(code, temp_file)
            
            return render_template('index.html', 
                                result=f"Code saved to {temp_file} and executed in iTerm2.",
                                code=code,
                                output=output)
            
        except Exception as e:
            return render_template('index.html', error=str(e))
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
