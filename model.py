
import modal
app = modal.App("sandbox")

image = (
    modal.Image.debian_slim(python_version="3.14")
    .pip_install("torch","transformers","bitsandbytes","accelerate","huggingface_hub")
)



hf_model = None
tokenizer = None

# modal run pyfile

@app.function(image=image, gpu="T4:1")
def run_model(model_name, prompt):

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
  
    quantization_config = BitsAndBytesConfig(load_in_4bit=True)

    global hf_model, tokenizer
    if hf_model is None:
        hf_model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto",
            quantization_config = quantization_config
        )
        tokenizer = AutoTokenizer.from_pretrained(model_name)

    
    messages = [
        {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(hf_model.device)

    generated_ids = hf_model.generate(
        **model_inputs,
        max_new_tokens=512
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return response

