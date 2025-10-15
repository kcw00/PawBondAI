from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get credentials from environment
ELASTIC_ENDPOINT = os.getenv("ELASTIC_ENDPOINT")
ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")

# Connect to Elasticsearch
es = Elasticsearch(ELASTIC_ENDPOINT, api_key=ELASTIC_API_KEY)

# Test connection
try:
    if es.ping():
        print("✅ Connected to Elasticsearch!")
        info = es.info()
        print(f"Cluster name: {info['cluster_name']}")
        print(f"Elasticsearch version: {info['version']['number']}")
    else:
        print("❌ Connection failed")
except Exception as e:
    print(f"❌ Error: {e}")
