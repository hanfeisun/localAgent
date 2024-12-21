from flask import Flask, render_template, request, session
import google.generativeai as genai
import os
import subprocess
import tempfile
import time
import re
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Initialize Gemini API
api_key_path = os.path.expanduser("~/api_key")
try:
    with open(api_key_path) as f:
        genai.configure(api_key=f.read().strip())
except FileNotFoundError:
    print(f"Error: API key file not found at {api_key_path}")
    exit(1)

# Configure the model
MODEL_NAME = "Gemini 2.0 Flash Experimental"
model = genai.GenerativeModel('gemini-2.0-flash-exp')

def clean_code_response(text):
    # Remove markdown code block if present
    text = re.sub(r'^```\w*\n', '', text)  # Remove opening ```python or similar
    text = re.sub(r'\n```$', '', text)     # Remove closing ```
    return text.strip()

def run_code(code):
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir='/tmp', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        # Run the code and capture output
        result = subprocess.run(['python3', temp_file], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)  # 10 second timeout
        output = result.stdout
        if result.stderr:
            output += "\nErrors:\n" + result.stderr
        return output
    except subprocess.TimeoutExpired:
        return "Execution timed out after 10 seconds"
    except Exception as e:
        return f"Error executing code: {str(e)}"
    finally:
        # Clean up temporary file
        try:
            os.remove(temp_file)
        except:
            pass

@app.route('/', methods=['GET', 'POST'])
def index():
    # Initialize history in session if it doesn't exist
    if 'history' not in session:
        session['history'] = []
    
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

PATH HANDLING RULES:
- When using home directory with "~", ALWAYS use os.path.expanduser() or Path.home()
- INCORRECT: Path("~/Downloads")  # This won't expand the tilde
- CORRECT: Path.home() / "Downloads"  # This is the proper way
- CORRECT: Path(os.path.expanduser("~/Downloads"))  # This also works
- For temporary files, use the /tmp directory
- For current directory, use Path.cwd() or os.getcwd()

Example of correct output format:
from pathlib import Path
downloads = Path.home() / "Downloads"
print(list(downloads.glob("*.txt")))

Example of INCORRECT output format:
```python
from pathlib import Path
downloads = Path("~/Downloads")  # Won't work!
print(list(downloads.glob("*.txt")))
```
"""
            
            # Make API request to Gemini
            response = model.generate_content([
                system_prompt,
                f"Generate Python code for: {prompt}. Remember, output ONLY the raw code without any markdown or formatting."
            ])
            
            # Extract and clean the code from the response
            code = clean_code_response(response.text)
            
            # Run the code and get output
            output = run_code(code)
            
            # Add to history with timestamp
            history_item = {
                'prompt': prompt,
                'code': code,
                'output': output,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'model': MODEL_NAME
            }
            session['history'].insert(0, history_item)  # Add to beginning of history
            
            # Keep only the last 20 items in history
            if len(session['history']) > 20:
                session['history'] = session['history'][:20]
            
            session.modified = True  # Ensure session is saved
            
            return render_template('index.html', 
                                history=session['history'],
                                model_name=MODEL_NAME)
            
        except Exception as e:
            return render_template('index.html', 
                                error=str(e),
                                history=session['history'],
                                model_name=MODEL_NAME)
    
    return render_template('index.html', history=session['history'], model_name=MODEL_NAME)

if __name__ == '__main__':
    app.run(debug=True)
