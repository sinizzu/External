# app/api/v1/__init__.py
from .paper import endpoints as paper_endpoints
from .translate import endpoints as trans_endpoints
from .ocr import endpoints as ocr_endpoints
from .keyword import endpoints as keyword_endpoints
from .chatbot import endpoints as chatbot_endpoints
from .topic import endpoints as topic_endpoints
from .weaviate import endpoints as weaviate_endpoints
from .translate import endpoints as translate_endpoints