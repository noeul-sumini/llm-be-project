# 마이데이터 Agent 구현 과제
- 마이데이터 공식 문서를 기반으로 정책, 기술사양 등을 답변하는 Agent 구현 과제입니다.
- Agent구현을 위한 백엔드 서버를 구성하였으며, Docker를 사용하여 서버 구성을 실행할 수 있습니다.

## 요구사항(필수)
- Link된 페이지의 파일 기반으로 RAG Agent를 구현
  - https://www.mydatacenter.or.kr:3441/cmmn/fileBrDownload?id=JHuKqjlWK0e%2FH9Yi7ed09GsZWL6TiRKp9yg4qGj%2FKFmV9RC6j8RJdh6I8JAqzoFv&type=2
  - https://www.mydatacenter.or.kr:3441/cmmn/fileBrDownload?id=dKi%2B7cAM4PO8JA4z7jwm4AoM07vmQIbSKQ9EvM0DPRYokFCd%2BhLigsDUZ0hQopjD&type=2
- LLM Model을 사용하여 Agent를 구현 (ChatGPT, LLaMA등) : Closed, OpenSource LLM 무관
- User Input을 받아 테스트할 수 있는 형태로 구현
  - 서버형태로 프로젝트가 실행되어야 한다.

## 요구사항(Optional)
- Langchain, LLamaIndex 등 프레임워크 사용
- Multi-turn Agent 구현
- Multimodal 지원
- 확장가능한 형태의 프로젝트
- 동시성 해결
- 모델 토큰 제한 해결

## 기술스택
- Docker / Docker-compose
- Python 3.11
- FastAPI
- Gunicorn
- Langchain
- Elasticsearch
- ChromaDB

## 주요특징
- RAG Retrieval 성능 향상을 위해 Hybrid Search 구현
  - ChromaDB + Elasticsearch(BM25)를 Ensemble하여 사용
    - Elasticsearch는 한국어 성능 향상을 위해 nori 형태소 분석기 적용
- Multiturn 구현을 위한 user_id별 history chain 기능 구현 (In-memory)
- UX 향상을 위한 Streaming Response 구현
- PDF Parsing성능을 위해 PDF to Markdown parser 구현
  - table 추출 기능 구현
- Docker-compose로 container기반 서버 동작 구현
- LLM Model
  - Embedding(OpenAI / text-embedding-ada-002)
  - LLM Model(OpenAI / chatgpt-4o)
    

## 구현기능 
  1. File Upload 
    - File을 User가 조회하기를 원하는 문서를 업로드하여 Embedding하고, Collection을 리턴하는 형태로 구현
    - File Upload후 Temporary File 상태에서 PDF to Markdown 변환 후 Chroma, Elasticsearch 각각에 Data저장
      - Temporary File은 DB Insert후 바로 삭제
  2. Query 
    - user_id, collection_name, query, query_parameter를 입력받아 Query 수행
      - query_parameter는 개별 선택이 가능하도록, retriever 검색기의 문서 검색 개수, 유사도 임계치 값, retirever ensemble 비율 등을 입력
    - Query의 Response는 Streaming Response로 처리

## 디렉토리 구조
```bash
llm-be-project/
│
├── app/
│ ├── .env # 환경 변수 설정 파일
│ ├── main.py # 애플리케이션의 진입점
│ ├── main_router.py # 주요 라우터 설정 파일
│ ├── test.py # 테스트 스크립트
│ ├── routers/ # 라우터 설정
│ │ ├── init.py # routers 모듈 초기화 파일
│ │ ├── common.py # 공통 라우터 설정 파일
│ │ └── qa.py # QA 관련 라우터 설정 파일
│ ├── services/ # 서비스 관련 로직
│ │ ├── llms.py # LLM 서비스 관련 파일
│ │ └── prompts.py # 프롬프트 처리 관련 파일
│ ├── dbs/ # 데이터베이스 관련 로직
│ │ ├── init.py # dbs 모듈 초기화 파일
│ │ ├── elasticsearch.py # Elasticsearch 데이터베이스 관련 파일
│ │ ├── retrievers.py # 검색기 로직
│ │ ├── utils.py # 데이터베이스 유틸리티 함수
│ │ └── vectorstores.py # 벡터 스토어 관련 파일
│ ├── schemas/ # 데이터 스키마
│ │ └── qa_schemas.py # QA 관련 스키마
│ ├── servers/ # 서버 관련 설정
│ │ ├── environment.py # 환경 설정 파일
│ │ ├── exceptions.py # 예외 처리 파일
│ │ └── loggers.py # 로깅 설정 파일
│ ├── configs/ # 설정 파일을 저장하는 디렉터리
│ │ ├── init.py # configs 모듈 초기화 파일
│ │ ├── chroma_config.py # ChromaDB 관련 설정 파일
│ │ ├── command.py # 명령어 처리 관련 설정 파일
│ │ └── elasticsearch_config.py # Elasticsearch 관련 설정 파일
│ └── utils/ # 유틸리티 함수
│ └── configparser.py # 설정 파일 파서
│
├── docker-compose.yml # Docker Compose 설정 파일
├── docker-compose.override.yml # Docker Compose 오버라이드 설정 파일
├── Dockerfile_BE # 백엔드 서버를 위한 Dockerfile
├── Dockerfile_ES # Elasticsearch를 위한 Dockerfile
└── README.md # 프로젝트 설명서
```



## 실행 방법

1. [이 저장소를 클론](https://github.com/noeul-sumini/llm-be-project.git):
    ```bash
    git clone https://github.com/noeul-sumini/llm-be-project.git
    ```

2. 프로젝트 디렉토리로 이동:
    ```bash
    cd llm-be-project
    ```

3. Docker Compose를 사용하여 프로젝트를 빌드하고 실행:
    ```bash
    docker-compose up
    ```

    이 명령어는 `docker-compose.yml` 파일과 `docker-compose.override.yml` 파일을 사용하여 필요한 모든 서비스(LLM 백엔드, Elasticsearch, ChromaDB)를 설정하고 실행

4. 서버가 실행되면 웹 브라우저에서 애플리케이션에 접근 가능
  LLM 백엔드 서버는 http://localhost:8080 으로 동작


## 테스트 코드 실행 방법
  
  ```bash
  pytest app/test.py
  ```
  llm-be-project 최상위에서 실행합니다


## 문의

프로젝트 관련 문의사항은 [ysm0482@naver.com](mailto:ysm0482@naver.com)으로 연락 부탁드립니다.

