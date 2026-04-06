
# 8,191 input tokens the embedding supports
# can try to chunk 200-800 tokens... maybe 400 tokens.

from openai import OpenAI

import db
import trafilatura
import hashlib
CHUNK_LENGTH = 400

client = OpenAI()

from math import ceil

news_articles_rss = db.helper_select_db("SELECT * FROM news_articles_rss", None)

# TODO make db return key value pairs instead.


def createEmbedding(str):
    response = client.embeddings.create(
        input=str,
        model="text-embedding-3-small"
        )
    
    return response.data[0].embedding

  

def update_or_add_full_news_articles_from_rss():
    for id,news_subscription_id,source,title,published_at,url,content,embedding in news_articles_rss:

        downloaded = trafilatura.fetch_url(url)
        article_text = trafilatura.extract(downloaded)
        hash = hashlib.sha256(article_text.encode("utf-8")).hexdigest()

        # does this article already exist?
        out = db.helper_select_db("SELECT * FROM news_articles_full WHERE url=%s", (url, ))
        
        # if yes, compare hash
        if(out):
            full_article_id,full_article_rss_id,full_article_url,full_article_text,full_article_hash = out[0]
            print("full article already exists comparing hash...")
            old_hash = full_article_hash
            print("old hash: ", old_hash)
            print("new hash", hash)
            if(old_hash == hash):
                print("hash the same no update.")
                continue
            else:
                print("hash has changed need update.")
        else:
            print("full article does not exist... adding... ")
        

        
        values = (id, url, article_text, hash)
        # TODO should be made in a single query
        db.helper_insert_db("INSERT INTO news_articles_full (article_rss_id, url, full_text, hash) VALUES (%s, %s, %s, %s)", values)

        id_article_full, article_rss_id, article_url, article_full_text, article_hash = db.helper_select_db("SELECT * FROM news_articles_full WHERE url=%s", (url,))[0]
        
        
        chunk_article(id_article_full, article_full_text)


# TODO should hash each chunk aswell??

def chunk_article(id_article, article_full_text):
    tokens = len(article_full_text)
    print("article tokens is", tokens)
    nr_chunks = ceil(tokens/CHUNK_LENGTH)
    print(f'need {nr_chunks} chunks')

    chunks = []
    for i in range(0, tokens, CHUNK_LENGTH):
        chunks.append(article_full_text[i:i+CHUNK_LENGTH])

    for i, chunk in enumerate(chunks):
        embedding = createEmbedding(chunk)
        values = (id_article,i,chunk,len(chunk),embedding)
        db.helper_insert_db("INSERT INTO news_articles_full_chunks (article_full_id,chunk_index,chunk_text,token_count,embedding) VALUES (%s,%s,%s,%s,%s)", values)
    

update_or_add_full_news_articles_from_rss()