import time
from elasticsearch import Elasticsearch
from config.config import ELASTICSEARCH_PASSWORD, ELASTICSEARCH_URL, ELASTICSEARCH_USERNAME

def connect_to_elasticsearch():
    while True:
        try:
            es = Elasticsearch(
                [ELASTICSEARCH_URL],
                http_auth=(ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD)
            )

            if es.ping():
                print("Connected to Elasticsearch")
                return es
            else:
                print("Elasticsearch is not reachable. Retrying in 5 seconds...")
        except Exception as e:
            print(f"Error connecting to Elasticsearch: {e}. Retrying in 5 seconds...")

        time.sleep(5)

es = connect_to_elasticsearch()

index_name = "files"

if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name)
