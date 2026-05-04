from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from pydantic import BaseModel
import modal
from rss import get_web_articles_rss
from openai import OpenAI
import db
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
client = OpenAI()

def createEmbedding(str):
    response = client.embeddings.create(
        input=str,
        model="text-embedding-3-small"
        )
    
    return response.data[0].embedding


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[db.origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

run_model = modal.Function.from_name("sandbox","run_model")



prompt = "Give me a short introduction to large language model."
model_name = "Qwen/Qwen3-4B-Instruct-2507"
#model_name="HuggingFaceTB/SmolLM-360M-Instruct"

# modal deploy model.py
async def get_model_response(model_name: str, prompt: str) -> str:
    return await run_model.remote.aio(model_name, prompt)

@app.get("/response")
async def root():
    response : str = await get_model_response(model_name, prompt)
    return {"message": response}


class Subscription(BaseModel):
    title: str
    description: str


# initialisations here, runs before application starts.
@app.on_event("startup")
async def startup_event():
    job = scheduler.add_job(get_web_articles_rss, 'interval', minutes=1)
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_schedueler():
    scheduler.shutdown()

@app.get("/newsubscription")
def get_subscriptions():
    connection = psycopg2.connect(database="postgres", user="postgres", password=db.DATABASE_PASSWORD, host=db.DATABASE_HOST, port=db.DATABASE_PORT)
    cursor = connection.cursor()
    select_query = "SELECT id, title, description FROM news_subscriptions"
    cursor.execute(select_query)
    connection.commit()
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return data

@app.post("/newsubscription")
async def create_subscription(sub: Subscription):
    connection = psycopg2.connect(database="postgres", user="postgres", password=db.DATABASE_PASSWORD, host=db.DATABASE_HOST, port=db.DATABASE_PORT)
    cursor = connection.cursor()

    # query expansion
    prompt = f"""
    You are expanding a news subscription query for article retrieval.

    Subscription:
    "{sub.title + sub.description}"

    
    Return ONLY a JSON array of strings.

    Rules:
    - Do NOT repeat the main keyword from the subscription.
    - Return modifiers that can be combined with the main keyword.
    - Do NOT create full search queries.
    - Do NOT add unrelated topics.
    - Do NOT add old events unless explicitly mentioned.
    - Prefer terms like sources, event types, roles, organizations, actions, and formats.
    - Return at most 8 strings.
    - If no useful modifiers exist, return [].

    Example:
    Subscription: "everything new about Trump"
    Output:
    ["Truth Social", "administration", "statement", "interview", "press conference", "executive order", "White House"]

    Example:
    Subscription: "Ukraine war"
    Output:
    ["drone attack", "missile strike", "peace talks", "front line", "air defense", "Kyiv", "Donetsk"]

    Example:
    Subscription: "Tesla layoffs"
    Output:
    ["job cuts", "workforce reduction", "employees", "factory", "Elon Musk"]

    JSON only.
    """

    query_expansion : str = await get_model_response(model_name, prompt)
    #print("query expansion is: ", query_expansion)

    embedding = createEmbedding(sub.title+sub.description+query_expansion)

    insert_query = "INSERT INTO news_subscriptions (title, description, embedding) VALUES (%s,%s, %s)"
    cursor.execute(insert_query, (sub.title, sub.description, embedding))
    connection.commit()
    cursor.close()
    connection.close()
    return {"message": "added to database"}



@app.delete("/newsubscription/{id}")
def delete_subscription(id: int):
    delete_query = f"DELETE FROM news_subscriptions WHERE id = {id}"
    connection = psycopg2.connect(database="postgres", user="postgres", password=db.DATABASE_PASSWORD, host=db.DATABASE_HOST, port=db.DATABASE_PORT)
    cursor = connection.cursor()
    cursor.execute(delete_query)
    connection.commit()
    cursor.close()
    connection.close()


@app.get("/newsubscription/{id}")
def edit_subscription(id: int):
    select_query = f"SELECT * FROM news_subscriptions WHERE id = {id}"
    connection = psycopg2.connect(database="postgres", user="postgres", password=db.DATABASE_PASSWORD, host=db.DATABASE_HOST, port=db.DATABASE_PORT)
    cursor = connection.cursor()
    cursor.execute(select_query)
    connection.commit()
    data = cursor.fetchone()
    cursor.close()
    connection.close()
    return data

@app.post("/editsubscription/{id}")
async def edit_subscription_page(id: int, request: Request):

    data = await request.json()

    embedding = createEmbedding(data["title"]+data["description"])

    select_query = "UPDATE news_subscriptions SET title=%s, description=%s, embedding=%s WHERE id = %s"
    connection = psycopg2.connect(database="postgres", user="postgres", password=db.DATABASE_PASSWORD, host=db.DATABASE_HOST, port=db.DATABASE_PORT)
    cursor = connection.cursor()
    cursor.execute(select_query, (data["title"], data["description"], embedding, id))
    connection.commit()
    return {"id":id}

app.mount("/", StaticFiles(directory="static", html=True), name="static")

    #http://127.0.0.1:8000 


