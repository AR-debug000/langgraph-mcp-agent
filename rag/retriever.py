import os

from dotenv import load_dotenv
from sklearn.feature_extraction.text import HashingVectorizer
from qdrant_client import QdrantClient


load_dotenv()


COLLECTION_NAME = "bscs_syllabus"
VECTOR_SIZE = 384


# Qdrant connection
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)


# Same vectorizer used during ingestion
vectorizer = HashingVectorizer(
    n_features=VECTOR_SIZE,
    alternate_sign=False,
    norm="l2",
    stop_words="english",
)


def retrieve_documents(question: str, limit: int = 3):

    # Convert user question into vector
    query_vector = vectorizer.transform(
        [question]
    ).toarray()[0].tolist()

    # Search Qdrant
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit,
        with_payload=True,
    ).points

    documents = []

    for result in results:

        documents.append({
            "text": result.payload["text"],
            "page": result.payload["page"],
            "source": result.payload["source"],
            "score": result.score,
        })

    return documents

