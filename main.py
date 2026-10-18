from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import speech_recognition as sr
from pydub import AudioSegment
import os

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

# Define the function that handles voice messages
async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Get the voice message file
        voice = update.message.voice
        voice_file = await context.bot.get_file(voice.file_id)

        # Download the voice file
        file_path = f"voice_{voice.file_id}.ogg"
        await voice_file.download_to_drive(file_path)

        # Convert OGG to WAV using pydub

        audio = AudioSegment.from_ogg(file_path)
        wav_path = f"voice_{voice.file_id}.wav"
        audio.export(wav_path, format="wav")

        # Recognize speech using Google Speech Recognition
        recognizer = sr.Recognizer()
        language = context.user_data.get('language', 'en-US')
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language=language)

        # Send the transcribed text back to the user
        await update.message.reply_text(f"Transcription:\n{text}")

        # Clean up files
        os.remove(file_path)
        os.remove(wav_path)

    except sr.UnknownValueError:
        await update.message.reply_text("Sorry, I couldn't understand the audio.")
    except sr.RequestError as e:
        await update.message.reply_text(f"Could not request results from speech recognition service; {e}")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")
        # Clean up files even on error
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)



def read_token(file: str=None):
    if file is None:
        file = os.getenv('TOKEN_FILE', 'token.txt')
    with open(file, 'r') as f:
        token: str = f.readline().strip()
    return token

if __name__ == '__main__':
    # Replace 'YOUR_TOKEN' with the token you got from BotFather
    token = read_token()
    app = ApplicationBuilder().token(token).build()

    # Add a handler to trigger the 'start' function
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("language", language_command))

    # Add handler for voice messages
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))

    print("Bot is running...")
    app.run_polling()