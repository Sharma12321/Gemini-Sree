import os
import telebot
import google.generativeai as genai
from PIL import Image
from io import BytesIO

# API Key Handling
try:
    genai.configure(api_key="AIzaSyDZLQ1w0fLYAKAfSLosTPMjf-EnRmqOhFg")  # Replace with your actual API key
except Exception as e:
    print(f"Error configuring API key: {e}")

# Model Setup
try:
    pro_model = genai.GenerativeModel("gemini-pro")
    vision_model = genai.GenerativeModel("gemini-pro-vision")

except Exception as e:
    print(f"Error creating models: {e}")

# Telegram Bot Setup
try:
    bot = telebot.TeleBot("6696646368:AAGgTXhEV264cGPSCedYB-LGFJ67RlibXIw")  # Replace with your bot token
except Exception as e:
    print(f"Error creating Telegram bot: {e}")

# Global variable for storing the most recent image
img = None

# Content Generation Functions
def generate_pro_content(prompt):
    try:
        response = pro_model.generate_content([{"text": prompt}])
        response.resolve()  # Wait for completion if response is asynchronous
        return response.text  # Access text using the correct attribute
    except Exception as e:
        print(f"Error generating text content: {e}")
        return "Error processing request."

def generate_vision_content(image_data, prompt):
    try:
        response = vision_model.generate_content([{"mime_type": "image/jpeg", "data": image_data}, {"text": prompt}], stream=True)
        response.resolve()  # Wait for completion
        return response.text  # Access text using the correct attribute
    except Exception as e:
        print(f"Error generating vision content: {e}")
        return "Error processing request."

# Bot Commands
@bot.message_handler(commands=["start"])
def send_welcome(message):
    try:
        bot.reply_to(message, "Welcome to my Gemini Sree bot!\n Created by SreeHari\n Use /help for all available commands.")
    except Exception as e:
        print(f"Error sending welcome message: {e}")

# ... (previous code as provided)

@bot.message_handler(commands=["help"])
def send_help(message):
    try:
        bot.reply_to(message, "Available commands:\n"
                                "/pro - Ask questions to Gemini Sree\n"
                                "/vision - Describe an image with Gemini Vision\n"
                                "/ask - Ask a question about the most recent image\n"
                                "/imagine - Generate images from a prompt\n"
                                "/start - Start the bot\n"
                                "/help - Show this help message")
    except Exception as e:
        print(f"Error sending help message: {e}")

@bot.message_handler(commands=["pro"])
def handle_pro_command(message):
    try:
        prompt = message.text.split(" ", 1)[1] if len(message.text.split(" ")) > 1 else None
        if prompt:
            response = generate_pro_content(prompt)
            bot.reply_to(message, response)
        else:
            bot.reply_to(message, "Please provide a prompt after the /pro command.")
    except Exception as e:
        print(f"Error handling /pro command: {e}")
        bot.reply_to(message, "Error processing request.")

@bot.message_handler(commands=["vision"])
def handle_first_message(message):
    try:
        bot.send_message(message.chat.id, "Welcome to the image description bot! Please send me a photo to describe it.")
    except Exception as e:
        print(f"Error sending vision start message: {e}")
        bot.reply_to(message, "Error initiating image description.")

@bot.message_handler(content_types=['photo'])
def handle_image_message(message):
    try:
        # Send a loading message
        loading_message = bot.send_message(message.chat.id, "Processing the image, please wait...")

        global img

        image_file = bot.get_file(message.photo[-1].file_id)
        image_data = bot.download_file(image_file.file_path)
        img = Image.open(BytesIO(image_data))

        response = generate_vision_content(image_data, "Describe the photo.")  # Use corrected attribute order
        image_description = response

        bot.send_message(message.chat.id, f"{image_description}")
        bot.send_message(message.chat.id, "Now you can ask me questions about the photo using the /ask command.")

    except Exception as e:
        bot.send_message(message.chat.id, f"Error processing the image: {str(e)}")
    finally:
        bot.delete_message(message.chat.id, loading_message.message_id)

@bot.message_handler(commands=["ask"])
def handle_ask_command(message):
    global img

    if img:
        prompt = message.text.split(" ", 1)[1] if len(message.text.split(" ")) > 1 else None
        if prompt:
            try:
                img_bytes = BytesIO()
                img.save(img_bytes, format="JPEG")
                image_data = img_bytes.getvalue()

                response = generate_vision_content(image_data, prompt)
                bot.reply_to(message, response)
            except Exception as e:
                bot.reply_to(message, f"Error processing the image: {str(e)}")
        else:
            bot.reply_to(message, "Please provide a question after the /ask command.")
    else:
        bot.reply_to(message, "Please send an image first using the /vision command.")

@bot.message_handler(commands=["imagine"])
def handle_imagine_command(message):
    try:
        prompt = message.text.replace("/imagine", "")
        response = vision_model.generate_content([{"text": prompt}])  # Assuming max_images=1 is appropriate
        response.resolve()  # Wait for completion
        image_url = response.images[0].url
        bot.send_photo(chat_id=message.chat.id, photo=image_url)
    except Exception as e:
        bot.reply_to(message, f"Error generating image: {str(e)}")

# Start polling
try:
    bot.polling()
except Exception as e:
    print(f"Error starting bot polling: {e}")


