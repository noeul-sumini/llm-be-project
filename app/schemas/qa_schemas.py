from pydantic import BaseModel


class QueryParamsModel(BaseModel):
    num_retrieval_docs: int
    score_threshold: float
    dense_retriever_weight: float

class QueryModel(BaseModel):
    user_id:str
    collection_name:str 
    query:str
    query_params:QueryParamsModel
