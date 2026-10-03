from sklearn.feature_extraction.text import HashingVectorizer


VECTOR_SIZE = 384


def create_embeddings(texts):
    vectorizer = HashingVectorizer(
        n_features=VECTOR_SIZE,
        alternate_sign=False,
        norm="l2",
        stop_words="english"
    )

    vectors = vectorizer.transform(texts)

    return vectors.toarray()