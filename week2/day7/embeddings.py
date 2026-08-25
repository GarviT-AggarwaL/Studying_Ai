import numpy as np
import os
from pathlib import Path
from groq import Groq
from sentence_transformers import SentenceTransformer
def cosine_similarity(a,b):
    return np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b))
model=SentenceTransformer("all-MiniLM-L6-v2")#384 shape
#text="Machine learning is fun."
#embedding=model.encode(text)
#print(embedding.shape)
t1="I love to do business."
t2="Virat is an indian cricketer."
v1=model.encode(t1)
v2=model.encode(t2)
print(cosine_similarity(v1,v2))
