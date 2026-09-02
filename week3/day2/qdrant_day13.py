#***************************************
# Part-1 IMPORTS AND ENVIRONMENT
#***************************************
import os
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from qdrant_client.models import Distance,VectorParams,PointStruct


#Load the variables from .env
load_dotenv()
Q_URL=os.getenv("QDRANT_URL")
Q_API_KEY=os.getenv("QDRANT_API_KEY")
my_api_key=os.getenv("GROQ_API_KEY")

#**************************************
#PART - 2 CONNECT TO QDRANT
#**************************************
client=QdrantClient(
    url=Q_URL,
    api_key=Q_API_KEY
)
print("Connected to Qdrant Client!")


#******************************************************************
#PART-3 CREATE QDRANT COLLECTIONS(JUST LIKE TABLES IN SQL)
#******************************************************************

COLLECTION_NAME="knowledge"
EMBEDDING_SIZE=384

#DELETE COLLECTIONS IF ALREADY EXITS
if client.collection_exists(COLLECTION_NAME):
    print(f"Deleting existing collections: {COLLECTION_NAME}")
    client.delete_collection(COLLECTION_NAME)


#CREATE COLLECTION
client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(
        size=EMBEDDING_SIZE,
        distance=Distance.COSINE,
    ),
)

print(f"Created collections : {COLLECTION_NAME}")
print(f"Vector size : {EMBEDDING_SIZE}")
print("Distance: COSINE")


#*********************************************************
#LOAD OUR KNOWLEDGE
#*********************************************************

with open("knowledge.txt","r",encoding="utf-8") as f:
    documents=[
        line.strip()
        for line in f
        if line.strip()
    ]
#This will create an array like this [line1,line2,etc]
print(f"Loaded {len(documents)} documents")


#********************************************
#Part 5 Create Embeddings
#*******************************************
print("Loading embedding model --->>>")
model=SentenceTransformer("all-MiniLM-L6-v2")
print("Embedding model ready")
embeddings=model.encode(documents)
print(f"Generated {len(embeddings)} embeddings")
print(f"Embedding size: {len(embeddings[0])}")


#***********************************************
#PART 6 - CREATE QDRANT POINTS
#*************************************************
points=[]
for i,embedding in enumerate(embeddings):
    point=PointStruct(
        id=i+1,
        vector=embedding.tolist(),
        payload={
            "text":documents[i]
        }
    )
    points.append(point)

#*******************************************
#part 7 - UPLOAD TO QDRANT
#*******************************************
client.upsert(
    collection_name=COLLECTION_NAME,
    points=points
)
print(f"Uploaded {len(points)} documents to Qdrant!")


#********************************************
#PART 8 - SEARCH QDRANT
#*********************************************
def search(query,top_k=3):
    #Convert the question into an embedding
    query_vector=model.encode(query).tolist()
    #search qdrant for similar vectors
    results=client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    ).points
    return results

#********************************************
#PART 9 TEST SEARCH
#********************************************
question="How many vacations do you get?"
results=search(question,top_k=3)
print("\nSearch results:")
for result in results:
    print(f"Score: {result.score:.3f}")
    print(result.payload["text"])
    print()


#***********************************************
#PART 10- CONNECT TO GROQ
#************************************************
groq_client=Groq(api_key=my_api_key)
groqmodel="openai/gpt-oss-20b"
#*******************************
#Part 11 ask the llm
#******************************
def ask_llm(question,context):
    prompt=f"""
    Answer the question using only the information provided below.
    Context:{context}
    Question:{question}
    If the answer is not present in the context, say:
    "I dont know based on the provided information."

    """

    response=groq_client.chat.completions.create(
            model=groqmodel,
            messages=[
                {
                    "role":"user",
                    "content":prompt
                }
            ]
        )
    return response.choices[0].message.content

#**************************
#PART 12 COMPLETE RAG PIPELINE
#******************************
context="\n".join(
    result.payload["text"]
    for result in results
)
answer=ask_llm(question,context)
print("\nFinal Answer: ")
print(answer)