from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai.chat_models import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from typing import List
from services.prompts import qa_prompt
import os
from operator import itemgetter


embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

class LLMs:
    def __init__(self, llm_model_name:str = "gpt-4o"):            
        self.llm_model = ChatOpenAI(model_name = llm_model_name, temperature = 0)
        
    def get_llm_chain(self, retriever):
        """ 
        llm_chain을 만드는 함수
        Args:
            retriever : RAG구현을 위한 Retriever를 입력으로 사용

        Returns:
            llm_chain
        """
        
        

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        store = {}
        history_chain = ( 
            {
                "context": itemgetter("input") | retriever,
                "input": itemgetter("input"),
                "chat_history": itemgetter("chat_history"),
            }
            | qa_prompt | self.llm_model)

        def get_session_history(session_ids:str):
            if session_ids not in store:
                store[session_ids] = ChatMessageHistory()
            return store[session_ids]
        

        
        llm_chain = (
            RunnableWithMessageHistory( 
                history_chain,
                get_session_history, 
                input_messages_key="input", 
                history_messages_key="chat_history",  
            )
        ) 

        return llm_chain
    
    def set_llm_chain(self, retriever ):
        """llm_chain을 LLMs instance의 self변수에 할당

        Args:
            retriever : RAG구현을 위한 Retriever를 입력으로 사용
        """
        self.llm_chain = self.get_llm_chain(retriever)

    
    async def query_stream(self, query:str, user_id:str) :
        """_summary_

        Args:
            query (str): llm_chain에 query 수행
            user_id (str) : qa history 기록을 위한 user_id

        Yields:
            fastapi에서 StreamingResponse로 추출가능한 dataformat 으로 Yield 수행
        """

        async for chunk in self.llm_chain.astream({"input": query}, config={"configurable": {"session_id": user_id} }):
            yield "data: {0}\n\n".format(chunk.content)
        