import os
import base64
from dotenv import load_dotenv
import logging
import json
from lxml import html, etree
import requests
import google.generativeai as genai

# Only load .env if NOT running on Render
if os.getenv("RENDER") != "true":
    from dotenv import load_dotenv
    load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# OpenAI initialization
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Gemini initialization
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Determine which AI provider to use based on environment variable
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()  # Default to OpenAI if not specified

def format_output(html_content):
    """Ensure HTML content is properly formatted for Streamlit display"""
    return html_content

def call_ai_model(prompt):
    """
    Call the appropriate AI model based on the AI_PROVIDER environment variable.
    
    Args:
        prompt (str): The prompt to send to the AI model
        
    Returns:
        str: The response from the AI model
    """
    # Try primary provider first
    if AI_PROVIDER == "gemini":
        raw_result = call_gemini(prompt)
        # If Gemini fails, fallback to OpenAI
        if raw_result is None:
            logger.info("Gemini API call failed, falling back to OpenAI")
            raw_result = call_openai(prompt)
    else:
        # OpenAI as primary
        raw_result = call_openai(prompt)
        # If OpenAI fails, fallback to Gemini
        if raw_result is None:
            logger.info("OpenAI API call failed, falling back to Gemini")
            raw_result = call_gemini(prompt)
    
    # Process the raw result to ensure HTML is correctly formatted
    try:
        # Clean up any escaped HTML tags
        cleaned_result = raw_result.replace("<", "<").replace(">", ">")
        
        # Make sure the HTML is well-formed
        if "<h3" in cleaned_result and "</h3>" not in cleaned_result:
            cleaned_result = cleaned_result.replace("<h3", "</h3><h3")
        
        if "<li>" in cleaned_result and "</li>" not in cleaned_result:
            cleaned_result = cleaned_result.replace("<li>", "<li>").replace("\n<li>", "</li>\n<li>")
            if not cleaned_result.endswith("</li>"):
                cleaned_result += "</li>"
        
        if "<ul>" in cleaned_result and "</ul>" not in cleaned_result:
            cleaned_result += "</ul>"
            
        return cleaned_result
    except Exception as e:
        logger.error(f"Error processing HTML result: {str(e)}")
        return raw_result  # Return the original result if processing fails

def call_gemini(prompt):
    """
    Call the Gemini API with the given prompt.
    
    Args:
        prompt (str): The prompt to send to the Gemini API
        
    Returns:
        str: The response from the Gemini API
    """
    try:
        # Configure the model
        model = genai.GenerativeModel('gemini-2.5-pro-preview-03-25')
        
        # Call Gemini API
        response = model.generate_content(prompt)
        
        # Return the content of the response
        return response.text
        
    except Exception as e:
        logger.error(f"Error calling Gemini API: {str(e)}")
        # Return None to trigger fallback
        return None

def call_gemini_vision(prompt, image_data_list):
    """
    Call Gemini with image data and prompt.
    
    Args:
        prompt (str): The prompt to send to Gemini
        image_data_list (list): List of base64-encoded image data
        
    Returns:
        str: The response from Gemini
    """
    try:
        # Configure the model for vision tasks
        model = genai.GenerativeModel('gemini-2.5-pro-preview-03-25')
        
        # Prepare content parts
        content_parts = [prompt]
        
        # Add image parts
        for img_data in image_data_list:
            content_parts.append({
                "mime_type": "image/jpeg",
                "data": img_data
            })
        
        # Call Gemini API with multimodal content
        response = model.generate_content(content_parts)
        
        # Return the content of the response
        return response.text
        
    except Exception as e:
        logger.error(f"Error calling Gemini Vision API: {str(e)}")
        # Return None to trigger fallback
        return None

def call_openai(prompt):
    """
    Call the OpenAI API with the given prompt.
    
    Args:
        prompt (str): The prompt to send to the OpenAI API
        
    Returns:
        str: The response from the OpenAI API
    """
    try:
        from openai import OpenAI
        import os
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")

        logger.info(f"OPENAI_API_KEY length: {len(api_key) if api_key else 'None'}")
        logger.info(f"OPENAI_API_KEY prefix: {api_key[:8] if api_key else 'None'}")


        if not api_key:
            error_msg = "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
            logger.error(error_msg)
            return f"<div class='error'>{error_msg}</div>"
            
        # Create a client with just the API key
        client = OpenAI(api_key=api_key)
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a luxury fashion authentication expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=800
        )
        
        # Return the content of the response
        return response.choices[0].message.content
        
    except Exception as e:
        error_msg = f"Error calling OpenAI API: {str(e)}"
        logger.error(error_msg)
        return f"<div class='error'>{error_msg}</div>"

def call_anthropic(prompt):
    """
    Call the Anthropic API with the given prompt.
    
    Args:
        prompt (str): The prompt to send to the Anthropic API
        
    Returns:
        str: The response from the Anthropic API
    """
    try:
        from anthropic import Anthropic
        
        # Initialize Anthropic client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            error_msg = "Anthropic API key not found. Please set the ANTHROPIC_API_KEY environment variable."
            logger.error(error_msg)
            return f"<div class='error'>{error_msg}</div>"
            
        client = Anthropic(api_key=api_key)
        
        # Call Anthropic API
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=800,
            system="You are a luxury fashion authentication expert. Provide clear, accurate, and helpful responses about counterfeit detection.",
            messages=[
                {"role": "user", "content": prompt}
            ],
        )
        
        # Return the content of the response
        return response.content[0].text
        
    except Exception as e:
        error_msg = f"Error calling Anthropic API: {str(e)}"
        logger.error(error_msg)
        return f"<div class='error'>{error_msg}</div>"

def call_vision_model(prompt, image_base64):
    """
    Call a vision-capable AI model with the given prompt and image.
    Currently uses OpenAI's GPT-4o model for vision capabilities.
    
    Args:
        prompt (str): The prompt to send to the vision model
        image_base64 (str): Base64-encoded image
        
    Returns:
        str: The response from the vision model
    """
    try:
        from openai import OpenAI
        
        # Initialize OpenAI client with only the API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            error_msg = "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
            logger.error(error_msg)
            return f"<div class='error'>{error_msg}</div>"
        
        # Create client with only the required API key    
        client = OpenAI(api_key=api_key)
        
        # Format the messages with the image
        messages = [
            {
                "role": "system",
                "content": "You are a luxury fashion authentication expert specializing in visual analysis. Format your response in clean, properly nested HTML."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ]
        
        # Call OpenAI API with GPT-4o
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.4,
            max_tokens=1000
        )
        
        # Access the response content
        raw_result = response.choices[0].message.content
        
        # Process the result to fix HTML rendering issues
        processed_result = process_html_result(raw_result)
        
        return processed_result
        
    except Exception as e:
        error_msg = f"Error calling vision model: {str(e)}"
        logger.error(error_msg)
        return f"<div class='error'>{error_msg}</div>"
    
def call_openai_vision_multi(content_array):
    """
    Call OpenAI with multiple images.
    This is a wrapper for your existing OpenAI vision code.
    """
    # Copy your existing OpenAI vision code here
    from openai import OpenAI
    
    # Initialize OpenAI client
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # Call OpenAI API with GPT-4o
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a luxury fashion authentication expert."
            },
            {
                "role": "user",
                "content": content_array
            }
        ],
        temperature=0.4,
        max_tokens=1000
    )
    
    return response.choices[0].message.content

def call_vision_model_multi(content_array):
    """
    Call a vision-capable AI model with the given prompt and multiple images.
    Uses GPT-4o which can handle up to 16 images in a single request.
    
    Args:
        content_array (list): Array of content objects including text and images
        
    Returns:
        str: The response from the vision model
    """
    try:
        # Extract text prompt and images from content_array
        text_prompt = ""
        image_data_list = []
        
        for item in content_array:
            if item.get("type") == "text":
                text_prompt = item.get("text", "")
            elif item.get("type") == "image_url":
                # Extract base64 data from image URL
                img_url = item.get("image_url", {}).get("url", "")
                if img_url.startswith("data:image/jpeg;base64,"):
                    img_data = img_url.split("base64,")[1]
                    image_data_list.append(img_data)
        
        # Try primary provider first
        if AI_PROVIDER == "gemini":
            result = call_gemini_vision(text_prompt, image_data_list)
            
            # Fallback to OpenAI if Gemini fails
            if result is None:
                logger.info("Gemini Vision API call failed, falling back to OpenAI")
                result = call_openai_vision_multi(content_array)
        else:
            # OpenAI as primary
            result = call_openai_vision_multi(content_array)
            
            # Fallback to Gemini if OpenAI fails
            if result is None:
                logger.info("OpenAI Vision API call failed, falling back to Gemini")
                result = call_gemini_vision(text_prompt, image_data_list)
        
        # Process the result for HTML formatting
        processed_result = process_html_result(result)
        
        return processed_result
        
    except Exception as e:
        logger.error(f"Error calling vision model: {str(e)}")
        return f"<div class='error'>Error analyzing images: {str(e)}</div>"

def process_html_result(html_content):
    """
    Process the HTML content to ensure it renders properly in Streamlit using lxml for validation.
    
    Args:
        html_content (str): Raw HTML content from the AI
        
    Returns:
        str: Processed and validated HTML content
    """
    try:
        # Check if the content starts with ```html or similar code block markers
        if "```html" in html_content:
            # Extract the HTML from the code block
            start_idx = html_content.find("```html") + 7
            end_idx = html_content.rfind("```")
            if end_idx > start_idx:
                html_content = html_content[start_idx:end_idx].strip()
        
        # Replace any escaped HTML characters
        html_content = html_content.replace('<', '<').replace('>', '>')
        
        # Use lxml to parse and validate HTML
        parser = etree.HTMLParser(recover=True)  # Recover from malformed HTML
        try:
            # Parse the HTML content
            tree = etree.fromstring(html_content, parser)
            if tree is None:
                # If parsing fails, wrap in a div
                html_content = f"<div>{html_content}</div>"
                tree = etree.fromstring(html_content, parser)
            
            # Clean and serialize the HTML
            cleaned_html = etree.tostring(tree, method='html', encoding='unicode')
            
            # Ensure the HTML is wrapped in a div if not already
            if not cleaned_html.strip().startswith('<div'):
                cleaned_html = f"<div>{cleaned_html}</div>"
            
            return cleaned_html
        except etree.ParseError as parse_error:
            logger.warning(f"HTML parsing error: {str(parse_error)}. Falling back to wrapped content.")
            return f"<div>{html_content}</div>"
        
    except Exception as e:
        logger.error(f"Error processing HTML result: {str(e)}")
        return f"""
        <div style="color: red;">
            Error processing HTML. Raw content:
            <pre>{html_content}</pre>
        </div>
        """