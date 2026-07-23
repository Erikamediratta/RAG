from sentence_transformers import SentenceTransformer

#Lazy loading the model so that web server is started succesfully before model is loaded
#solves memory issues on render deployment
model=None
def get_model():
    global model
    if model is None:
        model=SentenceTransformer("all-MiniLM-L6-v2")
    return model


def generate_embedding(text):
    model=get_model()
    return model.encode(text).tolist()

