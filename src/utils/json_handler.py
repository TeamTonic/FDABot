from typing import Any, Dict, List
import json

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