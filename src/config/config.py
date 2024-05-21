# src/config/config.py

from llama_index.core import VectorStoreIndex, Settings
# from src.engine.rag import embed_model
from llama_index.llms.replicate import Replicate
from transformers import AutoTokenizer
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


# setup RAG pipeline
Settings.embed_model = HuggingFaceEmbedding(model_name = "Snowflake/snowflake-arctic-embed-l" , trust_remote_code=True)
Settings.llm = Replicate(model="snowflake/snowflake-antic-instruct")
Settings.tokenizer = AutoTokenizer.from_pretrained("huggyllama/llama-7b")
Settings.context_window = 3072
Settings.text_splitter = SentenceSplitter(chunk_size=450)
Settings.chunk_size = 450
Settings.chunk_overlap = 120
