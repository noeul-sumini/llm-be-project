from langchain_community.retrievers import ElasticSearchBM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_chroma.vectorstores import Chroma
from dbs.vectorstores import vector_store
from dbs.elasticsearch import es_store
from services.llms import embeddings
from typing import List, Dict
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_community.document_transformers.long_context_reorder import LongContextReorder
from langchain.retrievers import ContextualCompressionRetriever

class CustomElasticSearchBM25Retriever(ElasticSearchBM25Retriever):
    search_args = {}

    def __init__(self, **search_args):
        super().__init__(**search_args)
        self.search_args = search_args

    def get_metadata(self, source):
        del source['texts']
        return source
        
    def _get_relevant_documents(
        self, query: str, run_manager: CallbackManagerForRetrieverRun, **kwargs
    ) -> List[Document]:
        query_dict = {"query": {"match": {"texts": query}}}

        size = -1
        if "search_args" in self.search_args and "k" in self.search_args["search_args"]:
            size = self.search_args["search_args"]["k"]

        res = self.client.search(index=self.index_name, body=query_dict)

        docs = []
        for i, r in enumerate(res["hits"]["hits"]):
            docs.append(Document(page_content=r["_source"]["texts"], metadata=self.get_metadata(r['_source'])))
            if -1 < size <= i + 1:
                break
        return docs


class Retriever:
    def __init__(self, collection_name : str = None):
        self.elastic_store = es_store
        self.vector_store = vector_store
        self.collection_name = collection_name

    def get_sparse_retriever(self, num_retrieval_docs:int = 3) :
        index_name = self.collection_name

        sparse_retriever =  CustomElasticSearchBM25Retriever(
            client=es_store.client,
            index_name = index_name,
            search_args={"k" : num_retrieval_docs}
            )
        return sparse_retriever

    
    def get_dense_retriever(self,  score_thresh:float = 0.7, num_retrieval_docs:int = 3):
        chroma = Chroma(client = vector_store.client, collection_name = self.collection_name, embedding_function=embeddings)
        dense_retriever = chroma.as_retriever(
                search_type = "similarity_score_threshold",
                search_kwargs = {"score_threshold": score_thresh, "k" : num_retrieval_docs}
            )
        return dense_retriever


    def get_ensemble_retriever(self, score_thresh:float = 0.7, num_retrieval_docs:int = 3, weight:float = 0.5, reorder:bool = True):
        ## Get Sparse/Dense Retriever
        sparse_retriever = self.get_sparse_retriever(num_retrieval_docs)
        dense_retriever = self.get_dense_retriever(score_thresh, num_retrieval_docs)

        ## Retriever Ensemble
        ensemble_retriever = EnsembleRetriever(
            retrievers = [dense_retriever, sparse_retriever],
            weights = [weight, 1-weight],
            search_type = "similarity"
        )

        return ensemble_retriever

    
