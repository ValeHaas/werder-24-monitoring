# FastAPI server for monitoring water leakage

from fastapi import FastAPI, logger
from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings
import telegram
from telegram import Bot
from telegram.error import TelegramError


# Constants
CONFIG_FILE = "server.env"


# Load environment variables from .env file
class Settings(BaseSettings):
    TELEGRAM_API_KEY: SecretStr
    TELEGRAM_CHAT_IDS: str  # Semicolon-separated list of chat IDs

    class Config:
        env_file = CONFIG_FILE


settings = Settings()
app = FastAPI()
bot = Bot(token=settings.TELEGRAM_API_KEY.get_secret_value())
chat_ids = [int(chat_id) for chat_id in settings.TELEGRAM_CHAT_IDS.split(";")]
logger.setLevel("INFO")
logger.info(f"Loaded chat IDs: {", ".join(map(str, chat_ids))}")
logger.info("Telegram bot initialized")


@app.route("/monitoring/ug/rohrbruch/startup")
async def startup():
    logger.info("Server started")
    # Send a message to all chat IDs
    for chat_id in chat_ids:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text="""Überwachungssystem gestartet.
Das System überwacht nun den Feuchtigkeitssensor im Keller.
Bei einem Wasseralarm erhalten Sie eine Benachrichtigung.
Ein Alarm kann durch Drücken des Reset-Knopfes am Sensor zurückgesetzt werden.                                   

Bleiben Sie trocken!""",
            )
        except TelegramError as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")
    return {"message": "Server started"}


@app.route("/monitoring/ug/rohrbruch/alarm")
async def alarm():
    logger.warning("Water alarm triggered!")
    # Send a message to all chat IDs
    for chat_id in chat_ids:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text="""🚨 Wasseralarm im Keller! Bitte überprüfen Sie den Feuchtigkeitssensor. 🚨
                Ein Alarm kann durch Drücken des Reset-Knopfes am Sensor zurückgesetzt werden.""",
            )
        except TelegramError as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")
    return {"message": "Alarm triggered"}
