from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pdfplumber
from PIL import Image
import io
import base64

def get_splitter(chunk_size:int = 500):
    """
    Text split을 위한 Text Splitter Load

    Args:
        chunk_size (int): split chunking size
    Returns:
        text_splitter
    """
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size = chunk_size, chunk_overlap = chunk_size * 0.1
    )
    return text_splitter


def convert_table_as_markdown(table):
    """
    표를 Markdown 형식으로 변환

    Args:
        table : pdfplumber에서 추출한 table

    Returns:
        str: Converted Markdown Table Text
    """
    table_markdown = ""
    for row in table:
        row_text = "|"
        for cell in row:
            row_text += str(cell).replace("\n", "<br>") + "|"
        table_markdown += row_text + "\n"

    num_cols = len(table[0])
    header_separator = "|" + "|".join(["---"] * num_cols) + "|"
    table_markdown = header_separator + "\n" + table_markdown

    return table_markdown + "\n\n"

def pdf_parser(pdf_file_path:str) -> str:
    """
    PDF 파일에서 텍스트, 표, 이미지를 추출하고 Markdown으로 변환

    Args:
        pdf_file_path (str): 변환할 PDF 파일의 경로

    Returns:
        str: Converted Markdown Text
    """

    with pdfplumber.open(pdf_file_path) as pdf:
        markdown_text = ""

        for page_num, page in enumerate(pdf.pages):
            elements = []
            
            # 텍스트 추출 및 위치 기록
            if page.extract_text():
                for char in page.chars:
                    elements.append({
                        'type': 'text',
                        'text': char['text'],
                        'x0': char['x0'],
                        'top': char['top']
                    })
            
            # 표 추출 및 위치 기록
            for table in page.extract_tables():
                for row_num, row in enumerate(table):
                    for cell_num, cell in enumerate(row):
                        if cell is not None:
                            # 셀 좌표 계산
                            cell_bbox = page.extract_words()[0]['doctop']
                            elements.append({
                                'type': 'table',
                                'text': convert_table_as_markdown([row]),  
                                'x0': cell_bbox,
                                'top': page.bbox[1] + row_num * 10  
                            })

            # 요소를 페이지 내의 y좌표(상단 기준)로 정렬
            elements.sort(key=lambda e: (e['top'], e['x0']))

            # 정렬된 요소들을 기반으로 Markdown 생성
            page_markdown = ""
            current_type = None
            for element in elements:
                if element['type'] == 'text':
                    if current_type == 'table':
                        page_markdown += "\n\n"
                    page_markdown += element['text']
                elif element['type'] == 'table':
                    page_markdown += element['text']
                current_type = element['type']
            
            markdown_text += page_markdown + "\n---\n"  # 페이지 구분선 추가
    
    return markdown_text