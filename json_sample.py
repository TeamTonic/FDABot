from llama_index.readers.json.base import JSONReader
from llama_index.core.schema import Document
from typing import Any, Dict, Generator, List, Optional

json_file = "/res/directory/articles.json"

reader = JSONReader()
documents:List[Document] = reader.load_data(json_file)



# query_engine = build_query_engine(data)