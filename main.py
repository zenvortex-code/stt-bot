from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import speech_recognition as sr
from pydub import AudioSegment
import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Constants
TEMP_DIR = os.getenv('TEMP_DIR', '/tmp')
PORT = int(os.getenv('PORT', 8080))

# Health check server for Render
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')

    def log_message(self, format, *args):
        # Suppress HTTP server logs
        pass

def run_health_check_server():
    server = HTTPServer(('0.0.0.0', PORT), HealthCheckHandler)
    logger.info(f"Health check server running on port {PORT}")
    server.serve_forever()

# Define the function that runs when a user types /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Hello {update.effective_user.first_name}! I am a bot.')

# Define the function that runs when a user types /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Available commands:\n"
        "/start - Start the bot and get a greeting\n"
        "/help - Show this help message\n"
        "/language <name> - Set recognition language (e.g., /language en, /language russian)\n\n"
        "Voice Messages:\n"
        "Send me a voice message and I'll transcribe it to text!"
    )
    await update.message.reply_text(help_text)

# Language mappings
LANGUAGE_MAP = {
    'en': 'en-US',
    'english': 'en-US',
    'ru': 'ru-RU',
    'russian': 'ru-RU',
    'es': 'es-ES',
    'spanish': 'es-ES',
    'fr': 'fr-FR',
    'french': 'fr-FR',
    'de': 'de-DE',
    'german': 'de-DE',
    'it': 'it-IT',
    'italian': 'it-IT',
    'pt': 'pt-PT',
    'portuguese': 'pt-PT',
    'zh': 'zh-CN',
    'chinese': 'zh-CN',
    'ja': 'ja-JP',
    'japanese': 'ja-JP',
    'ko': 'ko-KR',
    'korean': 'ko-KR',
}

# Define the function that runs when a user types /language
async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        current_locale = context.user_data.get('language', 'en-US')
        current_alias = next((k for k, v in LANGUAGE_MAP.items() if v == current_locale), current_locale)
        await update.message.reply_text(
            f"Current language: {current_alias}\n\n"
            "Usage: /language <name>\n"
            "Supported languages:\n"
            "  en/english, ru/russian, es/spanish\n"
            "  fr/french, de/german, it/italian\n"
            "  pt/portuguese, zh/chinese, ja/japanese, ko/korean"
        )
    else:
        alias = context.args[0].lower()
        if alias in LANGUAGE_MAP:
            locale = LANGUAGE_MAP[alias]
            context.user_data['language'] = locale
            await update.message.reply_text(f"Language set to: {alias}")
        else:
            await update.message.reply_text(
                f"Unknown language: {alias}\n"
                "Use /language to see supported languages."
            )


async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_path = None
    wav_path = None

    try:
        # Get the voice message file
        voice = update.message.voice
        voice_file = await context.bot.get_file(voice.file_id)

        # Download the voice file
        file_path = os.path.join(TEMP_DIR, f"voice_{voice.file_id}.ogg")
        await voice_file.download_to_drive(file_path)
        logger.info(f"Downloaded voice file: {file_path}")

        # Convert OGG to WAV using pydub
        audio = AudioSegment.from_ogg(file_path)
        wav_path = os.path.join(TEMP_DIR, f"voice_{voice.file_id}.wav")
        audio.export(wav_path, format="wav")
        logger.info(f"Converted to WAV: {wav_path}")

        # Recognize speech using Google Speech Recognition
        recognizer = sr.Recognizer()
        language = context.user_data.get('language', 'en-US')
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language=language)

        # Send the transcribed text back to the user
        await update.message.reply_text(f"Transcription:\n{text}")
        logger.info(f"Successfully transcribed message for user {update.effective_user.id}")

    except sr.UnknownValueError:
        logger.warning(f"Could not understand audio from user {update.effective_user.id}")
        await update.message.reply_text("Sorry, I couldn't understand the audio.")
    except sr.RequestError as e:
        logger.error(f"Speech recognition service error: {e}")
        await update.message.reply_text(f"Could not request results from speech recognition service; {e}")
    except Exception as e:
        logger.error(f"Error processing voice message: {e}", exc_info=True)
        await update.message.reply_text(f"An error occurred: {e}")
    finally:
        # Clean up files
        for path in [file_path, wav_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                    logger.debug(f"Removed temp file: {path}")
                except Exception as e:
                    logger.error(f"Failed to remove temp file {path}: {e}")



def get_token():
    """
    Get bot token from environment variable or file.
    Priority: TELEGRAM_BOT_TOKEN env var > TOKEN_FILE > token.txt
    """
    # First try environment variable
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if token:
        logger.info("Using token from TELEGRAM_BOT_TOKEN environment variable")
        return token

    # Fall back to file
    token_file = os.getenv('TOKEN_FILE', 'token.txt')
    try:
        with open(token_file, 'r') as f:
            token = f.readline().strip()
        logger.info(f"Using token from file: {token_file}")
        return token
    except FileNotFoundError:
        logger.error(f"Token file not found: {token_file}")
        raise
    except Exception as e:
        logger.error(f"Error reading token file: {e}")
        raise

if __name__ == '__main__':
    try:
        # Start health check server in background thread (for Render)
        health_thread = threading.Thread(target=run_health_check_server, daemon=True)
        health_thread.start()

        token = get_token()
        app = ApplicationBuilder().token(token).build()

        # Add handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("language", language_command))
        app.add_handler(MessageHandler(filters.VOICE, voice_handler))

        logger.info("Bot is running...")
        app.run_polling()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}", exc_info=True)
        raise