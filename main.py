from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import modal

run_model = modal.Function.from_name("sandbox","run_model")

app = FastAPI()

prompt = "Give me a short introduction to large language model."
model_name = "Qwen/Qwen2.5-1.5B-Instruct"
#model_name="HuggingFaceTB/SmolLM-360M-Instruct"

# modal deploy model.py
async def get_model_response(model_name: str, prompt: str) -> str:
    return await run_model.remote.aio(model_name, prompt)

@app.get("/response")
async def root():
    response : str = await get_model_response(model_name, prompt)
    return {"message": response}


app.mount("/", StaticFiles(directory="static", html=True), name="static")

    #http://127.0.0.1:8000 