# Code Generator Web App

This project was built using [Cursor](https://cursor.sh/), an AI-first code editor. It's a web application that generates and executes Python code using Google's Gemini AI model.

## Features

- Web interface for code generation requests
- Uses Google's Gemini AI model for code generation
- Automatically executes generated code in iTerm2
- Displays both generated code and execution output
- MacOS-optimized code generation
- Real-time output capture

## Prerequisites

- MacOS 15 (Sonoma) or later
- Python 3.x
- iTerm2 installed
- Google API key for Gemini

## Setup

1. Clone this repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create an API key file:
```bash
echo "your-google-api-key" > ~/api_key
```

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

3. Enter your code request in the text box and click "Generate and Run Code"

## How It Works

1. The web interface accepts natural language requests for code generation
2. Sends the request to Google's Gemini AI model with MacOS-specific optimization prompts
3. Receives and cleans the generated code
4. Saves the code to a temporary file
5. Executes the code in a new iTerm2 window
6. Captures and displays the output

## Project Structure

- `app.py`: Main Flask application and Gemini AI integration
- `templates/index.html`: Web interface template
- `requirements.txt`: Python dependencies
- `README.md`: Project documentation

## Dependencies

- Flask: Web framework
- google-generativeai: Google's Gemini AI API client
- python-dotenv: Environment variable management
- httpx: HTTP client library

## Built With

- [Cursor](https://cursor.sh/): AI-first code editor
- [Flask](https://flask.palletsprojects.com/): Web framework
- [Google Gemini AI](https://deepmind.google/technologies/gemini/): Code generation model
- [iTerm2](https://iterm2.com/): Terminal emulator for MacOS

## Notes

- The application is designed specifically for MacOS environments
- Requires iTerm2 for code execution
- Generated code is saved in the `/tmp` directory
- Output is captured and displayed in real-time

## Attribution

This project was entirely built using [Cursor](https://cursor.sh/), demonstrating the capabilities of AI-assisted development. Cursor's AI pair programming features were used throughout the development process, from initial code generation to documentation. 