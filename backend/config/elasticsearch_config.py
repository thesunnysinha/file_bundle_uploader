from elasticsearch import Elasticsearch
from config.config import ELASTICSEARCH_PASSWORD,ELASTICSEARCH_URL,ELASTICSEARCH_USERNAME


es = Elasticsearch(
    [ELASTICSEARCH_URL],
    http_auth=(ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD)
)


index_name = "files"

if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name)