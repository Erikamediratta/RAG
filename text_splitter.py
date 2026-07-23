from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def split_documents(text,source_name):
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200
    )
    doc=Document(page_content=text,metadata={"source":source_name})
    chunks=splitter.split_documents([doc])
    print(f"Created {len(chunks)} chunks")
    return chunks

if __name__=="__main__":
    sample_text="This is a test sentence"*300
    chunks=split_documents(sample_text,"test.pdf")
    print("First chunk:", chunks[0].page_content[:100])
    print("First chunk metadata:", chunks[0].metadata)