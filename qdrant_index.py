import os
from dotenv import load_dotenv
load_dotenv()

from qdrant_client import QdrantClient
from qdrant_client.models import PayloadSchemaType

client = QdrantClient(
    url=os.environ["QDRANT_URL_NAME"],
    api_key=os.environ["QDRANT_API_KEY"]
)

client.create_payload_index(
    collection_name="documents",
    field_name="document_name",
    field_schema=PayloadSchemaType.KEYWORD
)
