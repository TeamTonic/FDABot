import json
from typing import Any, Dict, List, Optional, Generator
from llama_index.core.schema import Document
from llama_index.core import VectorStoreIndex, Settings

from llama_index.llms.replicate import Replicate
from transformers import AutoTokenizer
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.openai import OpenAI
import os

os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN")



Settings.embed_model = HuggingFaceEmbedding(model_name = "Snowflake/snowflake-arctic-embed-l" , trust_remote_code=True)
# Settings.llm = Replicate(model="snowflake/snowflake-antic-instruct")
Settings.llm = Replicate(model="snowflake/snowflake-arctic-instruct")
# Settings.llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
Settings.tokenizer = AutoTokenizer.from_pretrained("huggyllama/llama-7b")
Settings.context_window = 3072
Settings.text_splitter = SentenceSplitter(chunk_size=450)
Settings.chunk_size = 450
Settings.chunk_overlap = 120



def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Loads a JSON file and returns its content as a dictionary.
    
    Args:
        file_path (str): The path to the JSON file.
        
    Returns:
        Dict[str, Any]: The content of the JSON file as a dictionary.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

# resp = Settings.llm.complete("Paul Graham is ")
x=0


# Example usage
# if __name__ == "__main__":
file_path = "res/directory/articles.json"
data = load_json_file(file_path)

data = data[:10]

data_documents:List[Document] = []

for datum in data:
    
    temp_document:Document = Document(
        text=datum['content'],
        extra_info={"url": datum['url']}
        )
    
    data_documents.append(temp_document)
    
    
index = VectorStoreIndex.from_documents(
    data_documents, transformations=[SentenceSplitter(chunk_size=512)]
)



node_parser = SentenceSplitter(chunk_size=1024, chunk_overlap=20)
alt_alt_nodes = node_parser.get_nodes_from_documents(data_documents)
sample_doc = []

for node in alt_alt_nodes:
    
    temp_document = Document(
        text=node.text,
        extra_info=node.extra_info,
    )
    
    sample_doc.append(temp_document)
    
vector_index = VectorStoreIndex(alt_alt_nodes)
query_engine = vector_index.as_query_engine()
sample = query_engine.query("FDA")

x=0
