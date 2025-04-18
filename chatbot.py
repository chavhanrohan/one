import os
from flask import Blueprint, request, jsonify, current_app, render_template
import openai
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()

# Create Blueprint
bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

# Get API key from environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Mock response for testing when API is unavailable
MOCK_RESPONSES = {
    "services": "NEO Infrastructure offers comprehensive construction services including residential, commercial, and industrial construction. We specialize in project planning, execution, and management.",
    "projects": "We have completed numerous projects including residential complexes, commercial buildings, and industrial facilities. Each project showcases our commitment to quality and innovation.",
    "contact": "You can contact NEO Infrastructure at +91 9922535423 or email us at info@neoinfra.com. Our office is located at B, Jagat Housing Society, Bairamji Town, Nagpur, Maharashtra.",
    "default": "Thank you for your message. I'm an AI assistant for NEO Infrastructure. I can provide information about our construction services, projects, and general inquiries."
}

@bp.route('/chat', methods=['POST'])
def chat():
    """
    Handle chat requests and return responses from OpenAI API
    """
    try:
        # Log request data
        current_app.logger.info("Chat endpoint called")
        
        # Get message from request
        data = request.get_json()
        if not data:
            current_app.logger.error("No JSON data in request")
            return jsonify({'error': 'No JSON data provided'}), 400
            
        user_message = data.get('message', '')
        current_app.logger.info(f"Received message: {user_message}")
        
        if not user_message:
            current_app.logger.error("No message provided in request")
            return jsonify({'error': 'No message provided'}), 400
        
        # Check if API key is set
        if not OPENAI_API_KEY:
            current_app.logger.error("OpenAI API key is not set")
            return jsonify({'error': 'API key not configured'}), 500
            
        current_app.logger.info(f"Using API key (first 5 chars): {OPENAI_API_KEY[:5]}...")
        
        # Add context about the company
        system_prompt = """You are an assistant for NEO Infrastructure, a construction company. 
        Provide helpful information about our services, projects, and general construction inquiries. 
        Keep responses concise and professional."""
        
        try:
            # Create a completion with OpenAI (older API style)
            current_app.logger.info("Sending request to OpenAI API")
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            # Extract the response text
            current_app.logger.info("Received response from OpenAI API")
            response_text = response.choices[0].message['content'].strip()
            
            return jsonify({'response': response_text})
        except Exception as api_error:
            # Log API-specific error
            current_app.logger.error(f"OpenAI API error: {str(api_error)}")
            
            # Fall back to mock responses for testing/demo purposes
            lower_msg = user_message.lower()
            if "service" in lower_msg:
                mock_response = MOCK_RESPONSES["services"]
            elif "project" in lower_msg:
                mock_response = MOCK_RESPONSES["projects"]
            elif "contact" in lower_msg:
                mock_response = MOCK_RESPONSES["contact"]
            else:
                mock_response = MOCK_RESPONSES["default"]
                
            current_app.logger.info(f"Using mock response: {mock_response[:30]}...")
            return jsonify({'response': mock_response})
    
    except Exception as e:
        # Get detailed error information
        error_traceback = traceback.format_exc()
        current_app.logger.error(f"Error in chat endpoint: {str(e)}")
        current_app.logger.error(f"Traceback: {error_traceback}")
        return jsonify({'error': f"Error: {str(e)}"}), 500
        
# Add a route to test if the chatbot endpoint is working
@bp.route('/test', methods=['GET'])
def test():
    return jsonify({
        'status': 'Chatbot endpoint is working',
        'api_key_configured': bool(OPENAI_API_KEY),
        'api_key_first_chars': OPENAI_API_KEY[:5] if OPENAI_API_KEY else None
    }) 