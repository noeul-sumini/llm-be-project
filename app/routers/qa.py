
from fastapi import APIRouter, Request, File, UploadFile, HTTPException, Response, Form
from fastapi.responses import StreamingResponse
from fastapi_utils.cbv import cbv
import io
import asyncio
import shutil
import tempfile
from typing import List, Union

import os


from dbs.utils import pdf_parser, get_splitter
from dbs.vectorstores import ChromaVectorStore, vector_store
from dbs.elasticsearch import es_store
from dbs.retrievers import Retriever
from services.llms import LLMs
from servers.exceptions import HTTPExceptions
from servers.loggers import logger
from schemas.qa_schemas import QueryModel
import uuid

router = APIRouter(prefix="/qa")

@cbv(router)
class QA:
    def __init__(self):
        self.vector_store = vector_store
        self.es_store = es_store


    @router.post("/upload", status_code = 200, response_model= None)
    async def file_upload(self, request:Request, collection_name:str = Form(), files:List[UploadFile] = File()) -> Union[Response, dict, None]:
        try:
            if collection_name == "":
                collection_name = uuid.uuid4() 

            texts, metadatas = [], []

            tasks = [asyncio.create_task(process_uploaded_file(file, texts, metadatas)) for file in files]
            await asyncio.gather(*tasks)

            
            if texts:  # 텍스트가 존재하는 경우에만 삽입
                index_name = collection_name
                await self.vector_store.insert_documents(collection_name=collection_name, texts=texts, metadatas=metadatas)
                await self.es_store.insert_documents(index_name=index_name, texts=texts, metadatas=metadatas)


            filenames = [file.filename for file in files]
            
            return {"collection_name" : collection_name, "filenames" : filenames, "status_msg" : "File Upload Success"}

        except Exception as e:
            logger.error("Error : ", e)
            raise HTTPExceptions.internal_server_error()
        


    @router.post("/query", status_code = 200, response_model = None)
    async def query(self, request:Request, query_model:QueryModel):
        collection_name = query_model.collection_name
        user_id = query_model.user_id
        query = query_model.query
        query_params = query_model.query_params
        num_retrieval_docs = query_params.num_retrieval_docs
        score_threshold = query_params.score_threshold
        dense_retriever_weight = query_params.dense_retriever_weight
        
        try:
            retriever = Retriever(collection_name)
            ensemble_retriever = retriever.get_ensemble_retriever(score_thresh=score_threshold, num_retrieval_docs=num_retrieval_docs, weight = dense_retriever_weight)
            llm = LLMs()
            llm.set_llm_chain(ensemble_retriever)
            return StreamingResponse(llm.query_stream(query = query, user_id=user_id), media_type="text/event-stream")

        
        except Exception as e:
            logger.error("Error : ", e)
            raise HTTPExceptions.internal_server_error()
        


            
async def process_uploaded_file(file: UploadFile, all_md_texts, all_md_metas):
    print("File Processing start")
    with tempfile.NamedTemporaryFile(delete=True) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = temp_file.name
        file_name = file.filename
        print("File Processing Finished")
        await extract_and_append_data(temp_file_path, file_name, all_md_texts, all_md_metas)
        print("Data extracted and appended")


async def extract_and_append_data(file_path: str, file_name: str, all_md_texts, all_md_metas):
    parsed_contents = await asyncio.to_thread(pdf_parser, file_path)
    md_contents = parsed_contents.split("\n---\n")
    text_splitter = get_splitter(chunk_size=1000)

    prev_chunk_is_table = False
    last_line = ""
    
    md_texts, md_metas = zip(*[
        (
            (last_line + "\n" + splitted_content.splitlines()[0] if prev_chunk_is_table else splitted_content)
            if j == 0 else splitted_content,
            {"page_no": i + 1, "chunk_no": j, "file_name": file_name}
        )
        for i, content in enumerate(md_contents)
        for j, splitted_content in enumerate(
            [
                "\n".join(
                    [splitted_content.splitlines()[0]] +
                    [line for line in splitted_content.splitlines()[1:]]
                )
                for splitted_content in text_splitter.split_text(content)
            ]
        )
        if not (
            prev_chunk_is_table := ('|' in (last_line := splitted_content.splitlines()[-1]))
        )
    ])

    all_md_texts.extend(md_texts)
    all_md_metas.extend(md_metas)
