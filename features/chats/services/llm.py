from openai import OpenAI
from typing import Optional
from ..resources.llm.tiny_llama import (
    tinyLLma_model,
    tinyLLma_tokenizer
)

import requests


class LLMService:

    def __init__(
        self,
        client: OpenAI,
        model_name: str,
    ):
        self.client = client
        self.model_name = model_name
        self.tokenizer = tinyLLma_tokenizer
        self.model = tinyLLma_model

    def generate(
        self,
        system_prompt: str,
        user_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            }
        ]

        if user_prompt:
            messages.append(
                {
                    "role": "user",
                    "content": user_prompt,
                }
            )

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content.strip()

    def local_generate(
        self,
        system_prompt: str,
        user_prompt: Optional[str] = None,
        temperature: float = 0.2,
    ):

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            }
        ]

        if user_prompt:
            messages.append(
                {
                    "role": "user",
                    "content": user_prompt,
                }
            )

        inputs = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self.model.device)

        outputs = self.model.generate(**inputs)

        input_length = inputs["input_ids"].shape[-1]

        answer = self.tokenizer.decode(
            outputs[0][input_length:], skip_special_tokens=True
        )

        return answer


    def colab_generate(       
        self,
        system_prompt: str,
        user_prompt: Optional[str] = None,
        temperature: float = 0.2
    ):
        
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            }
        ]

        if user_prompt:
            messages.append(
                {
                    "role": "user",
                    "content": user_prompt,
                }
            )

        url = "https://f673-35-198-252-206.ngrok-free.app/generate/"  # <-- your ngrok URL

        payload = {
            "messages": messages
        }

        response = requests.post(url, json=payload)

        if response.status_code == 200:
            return response.json()["text"]
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")