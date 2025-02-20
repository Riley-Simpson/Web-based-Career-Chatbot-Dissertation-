import os
import json
import chromadb
from tqdm import tqdm
from uuid import uuid4
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
import fitz
from datetime import datetime, timedelta
import pickle
import shelve

class Dataset:
    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2', 
                 collection_name='career_data', 
                 predefined_directory_path=None,
                 persist_directory='datasets/chroma_langchain_db'):
        """
         Initialize Chromadb and create collection. 
         
         Args:
         	 model_name: name of the model to use
         	 collection_name: name of the collection to create defaults to career_data
         	 predefined_directory_path: path to directory where pre - defined data is
        """
        self.embedding_model = HuggingFaceEmbeddings(model_name=model_name)
        self.client = chromadb.Client()
        persistent_client = chromadb.PersistentClient()
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.predefined_directory_path = predefined_directory_path
        self.doc_length = None
        self.persist = persistent_client.get_or_create_collection(name = self.collection_name)
        self.collection = Chroma(
            collection_name=self.collection_name,
            client=persistent_client,
            embedding_function=self.embedding_model,
            persist_directory=self.persist_directory,
            collection_metadata={"hnsw:space": "cosine"})
        
    def rest(self):
        self.collection.reset_collection()
               
    def process_json(self,file):       
        """
         Processes JSON files and adds it to the collection. 
         Args:
         	 file: Path to the JSON file to process. Must be a file - like object that has a ` read ` method
         Returns: 
         	 True if successful False
        """
        try:
            with open(file, 'r') as f:
                json_file = json.load(f)
        except Exception as e:
            print(e)        
        
        
        documents = []
        
        for idx,doc in enumerate(json_file):
            try:
                documents.append(Document(
                    page_content=str(doc),
                    metadata= {"Source":file , "idx":idx},
                    id=str(uuid4())
                ))

            except Exception as e:
                print(e)
                
        uuids = [str(uuid4()) for _ in range(len(documents))]
        
        
        print(f"Adding: {file}\n")
        self.collection.add_documents(documents=documents,ids=uuids)               
        print(f'{file} Added')
    
    def process_pdf(self,file):
        try:
            doc = fitz.open(file)
            documents = []
            for i, page in enumerate(doc):
                text = page.get_text("text")
                if text:  # Ensures text on the page / Excludes blank pages. 
                    metadata = {
                        "source": file,
                        "page_number": i + 1
                    }
                    documents.append(Document(page_content=text, metadata=metadata))
            uuids = [str(uuid4()) for _ in range(len(documents))]
            self.collection.add_documents(documents=documents, ids=uuids)
        except Exception as e:
            print(f"Error processing {file}: {e}")
    
    
            
    def load_data(self, directory_path=None):
        # The directory path to the predefined directory.
        if directory_path is None:
            directory_path = self.predefined_directory_path
        # Error message if no directory path is provided
        if directory_path is None:
            return {"error": "No directory path provided"}, 400
        
        with shelve.open("doc_length") as dl:
            if "doc_length" in dl:
                self.doc_length = dl["doc_length"]
            else:
                print('Doc Length not found')
        
        if self.doc_length:
            if len(self.collection.get()["documents"]) == self.doc_length:
                return {"message": "Dataset already Loaded"}
        else:
            print("Changes detected , reloading dataset")
        

        try:                   
            # Load and process files
            print("\nEmbedding Files")
            print("-----------------")
            
            for root, _, files in os.walk(directory_path):                        
                input_files=[]                              
                # Process JSON files and add them to input_files
                for file in files:
                    # Process the file if it is a. json file.
                    if file.endswith(".json"):
                        print("Json file detected")
                        self.process_json(os.path.join(directory_path,file))
                    else:
                        input_files.append(os.path.join(directory_path,file))
                
                print("Adding Others")                
                for file in tqdm(input_files):
                    try:
                        self.process_pdf(file)
                    except Exception as e :
                        print(e)
                
                                
            print(f"\nCollection {self.collection_name} Loaded")           
            print("-----------------")
            
            with shelve.open('doc_length') as dl:
                dl["doc_length"] =  len(self.collection.get()["documents"])
                
            
            return {"message": "Dataset Loaded"}
        except Exception as e:
            return {"error": f"Error loading data: {e}"}

    def retrieve_documents(self, query_str, relevancy_threshold=1):
       
        documents = self.collection.similarity_search_with_score(query=query_str, k=3)
        
        relevant_docs=[]
        
        for doc,score in documents:
            if score <= relevancy_threshold: 
                relevant_docs.append(doc.page_content)
                
        print("-----------------")
        print(f"{len(documents)} Relevant Documents Found")
        print(f"{len(relevant_docs)} Filtered Docs")
        print("-----------------")
        
        return relevant_docs
        
""" #Example
if __name__ == "__main__":
    # Initialize the DocumentRetrieval class
    doc_retrieval = Dataset(predefined_directory_path=r'G:\My Drive\Dissertation_Database')

    # Load data into the collection
    load_response = doc_retrieval.load_data()
    print(load_response)

    # Retrieve documents based on a query
    #query = "Hello"
    query = "I want to start a career in engineering where should i start?"
    retrieve_response = doc_retrieval.retrieve_documents(query,relevancy_threshold=1)
    print(retrieve_response)
  """
 