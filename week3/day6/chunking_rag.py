from langchain_text_splitters import(
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter)
text="""fdujfvbjfv. hdsbvhb .vdbvhvbhjbjhdvbjdvbnjkdn fjvnvjf fjkvnfdkjv vjdfnbjkfnbjk djknfdj. fdbvdjhbj. dbfvdfhjsb """
fixed=CharacterTextSplitter(
    separator="",
    chunk_size=100,
    chunk_overlap=0
)
print("********FIXED**********")
for i,chunk in enumerate(fixed.split_text(text),1):
    print(f"\nChunk {i}:")
    print(chunk)
    print("------------------------------")

paragraph=CharacterTextSplitter(
    separator="\n\n",
    chunk_size=100,
    chunk_overlap=0
)
print("**********PARAGRAPH*********")
for i,chunk in enumerate(fixed.split_text(text),1):
    print(f"\nChunk {i}:")
    print(chunk)
    print("------------------------------")

recursive=RecursiveCharacterTextSplitter(
    
    chunk_size=100,
    chunk_overlap=20)
print("*********recursive************")
for i,chunk in enumerate(fixed.split_text(text),1):
    print(f"\nChunk {i}:")
    print(chunk)
    print("------------------------------")

