import requests
from rss_parser import RSSParser
from requests import get
import psycopg2
from apscheduler.schedulers.background import BackgroundScheduler
import numpy as np
from numpy.linalg import norm
import ast
import hashlib
from openai import OpenAI

from db import helper_select_db, helper_insert_db

current_news_articles_db = None
uploaded_article = False

client = OpenAI()

# TODO if no new subscription has been made since last RSS update,
# then articles that have been found of no relevance these should be tagged,
# and not checked again with embedding.

def createEmbedding(str):
    response = client.embeddings.create(
        input=str,
        model="text-embedding-3-small"
        )
    
    return response.data[0].embedding





class WebRSS:
    pass


def check_rss_sites_to_fetch_articles(rss_sites):
    fetch_from_rss_sites = []

    for rss_site in rss_sites:
        if(add_or_update_rss_site(rss_site)):
            fetch_from_rss_sites.append(rss_site)
        else:
            continue

    print("break")
    return fetch_from_rss_sites
    

# avoid going through rss site if it hasn't changed.
# returns true if it adds rss site or updates the hash.
def add_or_update_rss_site(rss_site):

    html = requests.get(rss_site[1])
    page_hash = hashlib.sha256(html.text.encode("utf-8")).hexdigest()

    id,out_url,out_hash = rss_site

    if(out_hash == page_hash):
        print("same hash ignoring: ", rss_site[1])
        return False
    else:
        print("different hash, needs update: ", rss_site[1])
        helper_insert_db("UPDATE rss_sites SET hash=%s WHERE id=%s", (page_hash, id))
        return True 




def start_news_schedueler():
    scheduler = BackgroundScheduler()
    print("schedueling job for 1 minute...")
    job = scheduler.add_job(get_web_articles_rss, 'interval', minutes=1)
    scheduler.start()
    


# TODO Ai as a judge to exclude minor changes of an article, but this means the article itself has to be checked not only description and title.
# see if this article is already uploaded based on exact match (title + content + publisheddate).
def article_exists(new_title,new_publ,new_content):
    values=new_title,new_publ,new_content
    res = helper_select_db(f"SELECT 1 FROM news_articles_rss WHERE title=%s AND published_at=%s AND content=%s LIMIT 1", values)
    if res:
        print("article already exists.")
        return True
    else:
        return False



def get_web_articles_rss():

    rss_sites = helper_select_db("SELECT * FROM rss_sites",None)
    rss_sites_filtered = check_rss_sites_to_fetch_articles(rss_sites)

    for rss_site in rss_sites_filtered:

        print("getting web rss articles...")

        articles = []
        rss_url = rss_site[1]
        response = get(rss_url)
        rss_response = RSSParser.parse(response.text)

        for item in rss_response.channel.items:

            article = WebRSS()

            article.title = item.title.content if item.title else None
            article.published = item.pub_date.content if item.pub_date else None
            article.url = item.links[0].content if item.links else None
            article.descr = item.description.content if item.description else None


            # Avoid adding it if it already is in the db
            if(article_exists(article.title, article.published, article.descr)):
                continue

            articles.append(article)
            

        subscriptions = helper_select_db("SELECT id, embedding FROM news_subscriptions", None)

        

        for article in articles:
            
            if(article.title is None and article .descr is None):
                continue # skip this article for now.

            embedding_str = (article.title if article.title is not None else "") + (article.descr if article.descr is not None else "")
            article_embedding = createEmbedding(embedding_str)

            for id, subscription_embedding in subscriptions:
                
                # TODO typechecking must be made safer here
                sub_emb = ast.literal_eval(subscription_embedding)
                art_emb = article_embedding

            
                cosine = np.dot(art_emb, sub_emb) / (norm(art_emb)*norm(sub_emb))
                print("cosine is: ", cosine)

                if(cosine > 0.4):
                    print("inserting article that matched subscription...")
                    values = (id,None,article.title,article.published,article.url,article.descr,art_emb)
                    insert_query = ("INSERT INTO news_articles_rss (news_subscription_id, source, title, published_at, url, content, embedding) VALUES (%s,%s,%s,%s,%s,%s,%s)")
                    helper_insert_db(insert_query, values)

        pass

get_web_articles_rss()

#connection = psycopg2.connect(database="postgres", user="postgres", password="3166", host="localhost", port=5432)
#cursor = connection.cursor()
#insert_query = "INSERT INTO news_articles (source, title, published_at, url, content, embedding) VALUES (%s,%s,%s,%s,%s,%s)"

#for article in articles:
#    print("title", article.title)
#    print("pub", article.published)
#    print("url", article.url)
#    print("descr", article.descr)
#    cursor.execute(insert_query,(None,article.title,article.published,article.url,article.descr,None))

#connection.commit()
#print("inserted")
#cursor.close()
#connection.close()
#    id bigserial primary key,
#   source text,
#   title text,
#  published_at timestamp,
#  url text,
#  content text,
#  embedding vector(1536)

#chunking should be 200-800 tokens..., can start with one chunk intro.
