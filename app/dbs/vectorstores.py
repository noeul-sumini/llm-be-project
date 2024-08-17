from langchain_chroma import Chroma
import uuid
import chromadb
from chromadb.config import Settings
from chromadb import Collection
from typing import List, Dict
from services.llms import embeddings
import asyncio
from servers.environment import get_server_env
from configs.chroma_config import chroma_configs
import time

class ChromaVectorStore:
    def __init__(self, host:str, port:int):
        self.client = None
        self.http_connect(host, port)
        

    def http_connect(self, host: str, port: int):
        """ChromaDB 서버에 HTTP로 연결합니다. 

        Args:
            host (str): chromaDB Host URL/IP
            port (int): chromaDB Port
        """
        while True:
            try:
                self.client = chromadb.HttpClient(host = host, port = port)
                self.client.heartbeat()
                break
            except Exception as e:
                print(host, port)
                print(chroma_configs)
                print(f"Error connecting to ChromaDB: {e}")
                time.sleep(5)  # 5초 대기 후 재시도
            
        
        print("Vector DB Connected - Host : {0}, Port : {1}".format(host, port))

    async def get_embedding_vector(self, texts: List[str]) -> List[List[float]]:
        """텍스트를 입력 받아서 Embedding vector를 추출(async 동작)

        Args:
            texts (List[str]): Embedding Vector로 변환할 Text List

        Returns:
            List[List[float]]: 변환된 Embedding Vector List
        """
        embedded_vectors = await embeddings.aembed_documents(texts)
        return embedded_vectors

    def create_collection(self, collection_name: str, collection_metadata:dict = None) -> str:
        """Collection을 생성하고, 생성한 Collection name을 반환
        
        Args:
            collection_name (str): 생성하고자하는 collection 이름
            collection_metadata (dict) : DB Parameter 설정을 위한 metadata dict 

        Returns:
            str: 생성한 Collection 이름
        """
        if collection_metadata:
            collection = self.client.create_collection(collection_name, metadata=collection_metadata)
        else:
            collection = self.client.create_collection(collection_name)
        return collection.name

    def delete_collection(self, collection_name: str):
        """Collection 삭제

        Args:
            collection_name (str): _description_
        """
        
        self.client.delete_collection(collection_name)

    def get_collection(self, collection_name: str) -> Collection:
        """Collection name을 인자값으로 받아서, Collection을 반환

        Args:
            collection_name (str): Collection 이름
        Returns:
            Collection : 조회한 Chroma Collection
        """
        return self.client.get_collection(collection_name)

    async def insert_documents(self, collection_name: str, texts: List[str], metadatas: List[Dict]):
        """_summary_

        Args:
            collection_name (str): VectorDB Collection 이름
            texts (List[str]): Insert할 Text List
            metadatas (List[Dict]): Insert할 Text에 대한 Meta정보 List
        """
        vectorstore = Chroma(client=self.client, collection_name=collection_name, embedding_function=embeddings)
        vectordb_doc_ids = await vectorstore.aadd_texts(texts=texts, metadatas=metadatas)
        
        return vectordb_doc_ids
    
    async def delete_documents(self, collection_name:str, doc_ids:List[str]):
        """_summary_

        Args:
            collection_name (str): Vector DB Collection 이름 
            doc_ids (List[str]): 삭제할 대상 Document ID List
        """
        vectorstore = Chroma(client=self.client, collection_name=collection_name)
        await vectorstore.adelete(doc_ids )
        
chroma_init_config = chroma_configs[get_server_env().lower()]
vector_store = ChromaVectorStore(host = chroma_init_config['host'], port = chroma_init_config['port'])