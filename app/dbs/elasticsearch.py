from elasticsearch import Elasticsearch, helpers
from typing import List, Dict
from configs.elasticsearch_config import es_configs
from servers.environment import get_server_env
from langchain_community.vectorstores import ElasticsearchStore

class ESStore:
    def __init__(self, hosts:List[str], es_id:str = None, es_pw:str = None):
        self.hosts = hosts
        self.connect_es(hosts, es_id, es_pw)

    def connect_es(self, hosts: List[str], es_id: str = None, es_pw: str = None):
        """
        Elasticsearch 클라이언트 초기화
        :param hosts: Elasticsearch 호스트 리스트 (ex: ["http://localhost:9200"])
        """
        if es_id and es_pw:
            self.client = Elasticsearch(hosts, http_auth = (es_id, es_pw))
        else:
            self.client = Elasticsearch(hosts)

    def create_index(self, index_name: str, settings: Dict = None, mappings: Dict = None):
        """새로운 Index 생성

        Args:
            index_name (str): 생성할 인덱스 이름
            settings (Dict, optional): 인덱스 설정. Defaults to None.
            mappings (Dict, optional): 인덱스 매핑. Defaults to None.
        """

        if settings is None:
            settings = {
                "settings": {
                    "analysis": {
                        "analyzer": {
                            "my_nori_analyzer": { 
                            "type": "custom",
                            "tokenizer": "nori_tokenizer",
                            "filter": ["lowercase", "nori_readingform", "nori_part_of_speech"]
                            }
                        }
                    },
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                }
            }

        if mappings is None:
            mappings = {
                "mappings": {
                    "properties": {
                        "text": {"type": "text"},
                        "filename" : {"type": "text"},
                        "page_no": {"type": "integer"},
                        "chunk_no": {"type": "integer"},
                    }
                }
            }

        self.client.indices.create(index=index_name, body={**settings, **mappings}, ignore=400)

    def delete_index(self, index_name: str):
        """ 
        Index 삭제

        Args:
            index_name (str): 삭제할 인덱스 이름
        """
        self.client.indices.delete(index=index_name, ignore=[400, 404])

    async def insert_documents(self, index_name: str, texts:List[str], metadatas:List[Dict]):
        """_summary_

        Args:
            index_name (str): 추가할 Index 이름 
            texts (List[str]): 추가할 Text List
            metadatas (List[Dict]): 추가할 Metadata List
        """

        def merge_texts_and_metadatas(text:str, metadata:Dict) -> Dict:
            metadata['texts'] = text
            return metadata

        actions = [
            {
                "_index": index_name,
                "_source": merge_texts_and_metadatas(texts[idx], metadata)
            }
            for idx, metadata in enumerate(metadatas)
        ]

        helpers.bulk(self.client, actions)

    def update_document(self, index_name: str, document_id: str, document: Dict):
        self.client.update(index=index_name, id=document_id, body=document)

    def delete_document(self, index_name: str, document_id: str):
        """document 삭제

        Args:
            index_name (str): 삭제할 인덱스 이름
            document_id (str): 삭제할 문서 ID
        """
        self.client.delete(index=index_name, id=document_id)



es_hosts = es_configs[get_server_env().lower()]['hosts']
es_store = ESStore(es_hosts)