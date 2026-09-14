from openai import OpenAI
from src.config.config import HF_BASE_URL, HF_MODEL, HF_TOKEN

client = OpenAI(
    api_key=HF_TOKEN,
    base_url=HF_BASE_URL,
)

MODEL_NAME = HF_MODEL