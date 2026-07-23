import os
from pdf_extract import extract
from text_splitter import split_documents

pdf_folder="pdfs"

for file in os.listdir(pdf_folder):
    pdf_path=os.path.join(pdf_folder,file)
    print(f"Currently, {file}")

    text=extract(pdf_path)
    print(f"{len(text)} number of characters in {file}")

    chunks=split_documents(text,file)
    print(f" Split into {len(chunks)} chunks")