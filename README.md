# Telegram Speech-to-Text Bot

A Telegram bot that transcribes voice messages to text using Google Speech Recognition.

## Features

- Transcribe voice messages in multiple languages
- Support for 10+ languages (English, Russian, Spanish, French, German, Italian, Portuguese, Chinese, Japanese, Korean)
- Docker support for easy deployment

## Commands

- `/start` - Start the bot and get a greeting
- `/help` - Show help message with available commands
- `/language [code]` - Set recognition language (e.g., `/language en`, `/language russian`)

## Deployment to Render

### Quick Deploy

1. **Fork/Clone this repository**

2. **Sign up for Render** at [render.com](https://render.com)

3. **Create New Blueprint Instance**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`

4. **Set Environment Variable**
   - In the Render dashboard, go to your service
   - Navigate to "Environment" tab
   - Add secret:
     - Key: `TELEGRAM_BOT_TOKEN`
     - Value: Your bot token from [@BotFather](https://t.me/BotFather)

5. **Deploy**
   - Render will automatically deploy your bot
   - Auto-deploys on every push to master branch

## Local Development

### Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) package manager
- ffmpeg (for audio processing)

### Setup

1. **Install dependencies**
   ```bash
   uv sync
   ```

2. **Create token file**
   ```bash
   echo "YOUR_BOT_TOKEN" > token.txt
   ```

3. **Run the bot**
   ```bash
   uv run python main.py
   ```

## Docker Deployment

### Using Docker Compose

1. **Create token file**
   ```bash
   echo "YOUR_BOT_TOKEN" > token.txt
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **View logs**
   ```bash
   docker-compose logs -f
   ```

### Using Docker directly

```bash
docker build -t stt-bot .
docker run -e TELEGRAM_BOT_TOKEN=your_token_here stt-bot
```

## Configuration

The bot supports multiple ways to provide the bot token (in priority order):

1. `TELEGRAM_BOT_TOKEN` environment variable
2. `TOKEN_FILE` environment variable (path to token file)
3. `token.txt` file in the project root

## Supported Languages

- English (en/english)
- Russian (ru/russian)
- Spanish (es/spanish)
- French (fr/french)
- German (de/german)
- Italian (it/italian)
- Portuguese (pt/portuguese)
- Chinese (zh/chinese)
- Japanese (ja/japanese)
- Korean (ko/korean)

## License

MIT
