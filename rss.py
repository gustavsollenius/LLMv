from pyexpat import ExpatError
from rss_parser import RSSParser
from requests import get
import hashlib
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone, timedelta
from chunkNewsArticles import update_or_add_full_news_articles_from_rss
from openai import OpenAI

from db import helper_select_db, helper_insert_db, helper_insert_many_db

current_news_articles_db = None
uploaded_article = False
dt_old_rss_fetch_update = None

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




# Fetches recent articles from known RSS sites. 
def get_web_articles_rss():

    global dt_old_rss_fetch_update

    # Removes articles older than a full day.
    helper_insert_db("delete from news_articles_rss WHERE published_at < (NOW() - '1 days'::interval);", None)

    rss_sites = helper_select_db("SELECT * FROM rss_sites",None)

    articles = []
    insert_queries = []

    for rss_site in rss_sites:

        print("Fetching RSS article...")
        rss_url = rss_site[1]
        response = get(rss_url)

        str_builder = ""
        articles_per_rss = []
        

        try:
            rss_response = RSSParser.parse(response.text)
        except ExpatError as e:
            print(f"Skipping feed {rss_url}: invalid XML/RSS. Error: {e}")
            continue
        except Exception as e:
            print(f"skipping {rss_url}, unkown error")
            continue

        for item in rss_response.channel.items:

            article = WebRSS()

            article.title = item.title.content if item.title else None
            article.published = item.pub_date.content if item.pub_date else None
            article.url = item.links[0].content if item.links else None
            article.descr = item.description.content if item.description else None

            str_builder+=(article.title if not None else "" + article.published if not None else "" + article.url if not None else "" + article.descr if not None else "")
            articles_per_rss.append(article)
        
        new_hash = hashlib.sha256(str_builder.encode("utf-8")).hexdigest()
        old_hash = rss_site[2]

        if(new_hash == old_hash):
            print("rss: " + rss_site[1] + "same hash ignoring articles.")
        else:
            print("rss changed: " + rss_site[1] + " adding articles. ")
            
            articles.extend(articles_per_rss)

            # updating db hash
            values = (new_hash, rss_site[1])
            insert_query = "UPDATE rss_sites SET hash=%s WHERE url=%s"
            insert_queries.append((insert_query,values))

    helper_insert_many_db(insert_queries)

    # now go through articles on the rss sites on which the articles has been changed.
    # and select those that are close in time
    insert_queries = []
    for article in articles:

        # Skip articles without published dates for now.
        if article.published is None:
            continue

        # Also skip articles with no title or description
        if(article.title is None and article .descr is None):
            continue 

        # TODO might instead use global time update indicator in db
        if dt_old_rss_fetch_update is None:
            dt_old_rss_fetch_update = datetime.now(timezone.utc)-timedelta(minutes=5)

        # only add articles that are new
        try:
            # RFC 2822
            dt_article = parsedate_to_datetime(article.published)
        except Exception:
            # ISO 8601
            dt_article = datetime.fromisoformat(article.published)

        # keep everything in utc format.
        dt_article = dt_article.astimezone(timezone.utc)
        

        if( (dt_article > dt_old_rss_fetch_update) and dt_article > (datetime.now(timezone.utc)-timedelta(minutes=5))):
            print("New article found")
        else:
            continue

        # If date does not exist, check if it is already added.
        if(article_exists(article.title, article.published, article.descr)):
            print("Tried to add article that already exists.")
            continue

        print("inserting the new article...")
        
        embedding_str = (article.title if article.title is not None else "") + (article.descr if article.descr is not None else "")
        art_emb = createEmbedding(embedding_str)

        values = (None,article.title,article.published,article.url,article.descr,art_emb)
        insert_query = ("INSERT INTO news_articles_rss (source, title, published_at, url, content, embedding) VALUES (%s,%s,%s,%s,%s,%s)")
        insert_queries.append((insert_query,values))


    helper_insert_many_db(insert_queries)
            
       

    dt_old_rss_fetch_update = datetime.now(timezone.utc)


    # adding full article text and chunking it.
    update_or_add_full_news_articles_from_rss()


get_web_articles_rss()
'''
        subscriptions = helper_select_db("SELECT id, embedding FROM news_subscriptions", None)


           

            for id, subscription_embedding in subscriptions:
                
                # TODO typechecking must be made safer here
                sub_emb = ast.literal_eval(subscription_embedding)
                art_emb = article_embedding

            
                cosine = np.dot(art_emb, sub_emb) / (norm(art_emb)*norm(sub_emb))
                print("cosine is: ", cosine)

                if(cosine > 0.4):


'''