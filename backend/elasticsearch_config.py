import os
from elasticsearch import Elasticsearch

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL")
es = Elasticsearch([ELASTICSEARCH_URL])
