from fastembed import TextEmbedding

model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

def generate_embedding(text):
    embedding = list(model.embed([text]))[0]
    return embedding.tolist()



