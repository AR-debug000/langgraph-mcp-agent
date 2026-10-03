import os
from uuid import uuid4

from dotenv import load_dotenv
from pypdf import PdfReader

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams


load_dotenv()


# -----------------------------
# Configuration
# -----------------------------

PDF_PATH = "data/document/BSCS_Syllabus.pdf"
COLLECTION_NAME = "bscs_syllabus"


# -----------------------------
# Qdrant
# -----------------------------

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)


# -----------------------------
# Read PDF
# -----------------------------

reader = PdfReader(PDF_PATH)

pages = []

for page_number, page in enumerate(reader.pages, start=1):

    text = page.extract_text()

    if text:
        pages.append({
            "page": page_number,
            "text": text
        })


print(f"PDF pages loaded: {len(pages)}")


# -----------------------------
# Create chunks
# -----------------------------

chunks = []

chunk_size = 800
chunk_overlap = 100

for page in pages:

    text = page["text"]

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append({
                "text": chunk,
                "page": page["page"]
            })

        start += chunk_size - chunk_overlap


print(f"Total chunks created: {len(chunks)}")


# -----------------------------
# Create TF-IDF embeddings
# -----------------------------

texts = [chunk["text"] for chunk in chunks]

from sklearn.feature_extraction.text import HashingVectorizer

VECTOR_SIZE = 384

vectorizer = HashingVectorizer(
    n_features=VECTOR_SIZE,
    alternate_sign=False,
    norm="l2",
    stop_words="english"
)

vectors = vectorizer.transform(texts).toarray()

print(f"Embedding vectors created: {len(vectors)}")


# -----------------------------
# Create Qdrant collection
# -----------------------------

existing_collections = [
    collection.name
    for collection in client.get_collections().collections
]


if COLLECTION_NAME in existing_collections:

    print(f"Collection already exists: {COLLECTION_NAME}")

else:

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE,
        ),
    )

    print(f"Created collection: {COLLECTION_NAME}")


# -----------------------------
# Prepare Qdrant points
# -----------------------------

points = []

for chunk, vector in zip(chunks, vectors):

    points.append(
        PointStruct(
            id=str(uuid4()),

            vector=vector.tolist(),

            payload={
                "text": chunk["text"],
                "page": chunk["page"],
                "source": "BSCS_Syllabus.pdf",
            },
        )
    )


# -----------------------------
# Upload
# -----------------------------

client.upsert(
    collection_name=COLLECTION_NAME,
    points=points,
)


print()
print("===================================")
print("PDF successfully uploaded to Qdrant!")
print("===================================")
print(f"Collection: {COLLECTION_NAME}")
print(f"Vectors uploaded: {len(points)}")