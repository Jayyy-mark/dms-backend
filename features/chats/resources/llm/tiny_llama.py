from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch

model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

tinyLLma_tokenizer = AutoTokenizer.from_pretrained(model_id)

tinyLLma_model = AutoModelForCausalLM.from_pretrained(
    model_id, quantization_config=bnb_config, device_map="auto"
)

# messages = [
#     {"role": "user", "content": "Who are you?"},
# ]

# inputs = tokenizer.apply_chat_template(
#     messages,
#     add_generation_prompt=True,
#     tokenize=True,
#     return_dict=True,
#     return_tensors="pt",
# ).to(model.device)

# outputs = model.generate(**inputs)

# input_length = inputs["input_ids"].shape[-1]

# answer = tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True)

# print(answer)
