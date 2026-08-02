import os
from dotenv import load_dotenv
load_dotenv()

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client=QdrantClient(
    url=os.environ["QDRANT_URL_NAME"],
    api_key=os.environ["QDRANT_API_KEY"]
)
client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)