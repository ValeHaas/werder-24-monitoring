# FastAPI server for monitoring water leakage

from fastapi import FastAPI
from pydantic import BaseModel, SecretStr, field_validator
from pydantic_settings import BaseSettings
import telegram
from telegram import Bot
from telegram.error import TelegramError
from pathlib import Path
from typing import List
import logging


# Constants
logger = logging.getLogger("uvicorn")
CONFIG_FILE = Path(__file__).parent / "server.env"


# Load environment variables from .env file
class Settings(BaseSettings):
    TELEGRAM_API_KEY: SecretStr
    TELEGRAM_CHAT_IDS: List[int]  # Semicolon-separated list of chat IDs

    SERVER_AUTH_TOKEN: SecretStr  # Token for authenticating requests

    class Config:
        env_file = CONFIG_FILE

    @field_validator("TELEGRAM_CHAT_IDS", mode="before")
    @classmethod
    def validate_telegram_chat_ids(cls, v):
        if isinstance(v, str):
            return [int(chat_id) for chat_id in v.split(";") if chat_id.isdigit()]
        elif isinstance(v, list):
            return [
                int(chat_id)
                for chat_id in v
                if isinstance(chat_id, str) and chat_id.isdigit()
            ]
        elif isinstance(v, int):
            return [v]
        return v


settings = Settings()
app = FastAPI()
bot = Bot(token=settings.TELEGRAM_API_KEY.get_secret_value())
chat_ids = settings.TELEGRAM_CHAT_IDS
id_strings = ", ".join(map(str, chat_ids))
logger.info(f"Loaded chat IDs: {id_strings}")
logger.info("Telegram bot initialized")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/ug/rohrbruch/startup")
async def startup(auth_token: str):
    if auth_token != settings.SERVER_AUTH_TOKEN.get_secret_value():
        logger.warning("Unauthorized access attempt")
        return {"error": "Unauthorized"}, 401

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


@app.get("/ug/rohrbruch/alarm")
async def alarm(auth_token: str):
    if auth_token != settings.SERVER_AUTH_TOKEN.get_secret_value():
        logger.warning("Unauthorized access attempt")
        return {"error": "Unauthorized"}, 401

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
