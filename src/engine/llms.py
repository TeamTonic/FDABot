# src/engine/llms.py

import replicate
# from llama_index.llms.replicate import Replicate

# llm = Replicate(
#     model="snowflake/snowflake-antic-instruct"
# )


class SnowflakeModel:
    """
    This class provides an interface to interact with the Snowflake model via the replicate API.
    """
    
    def __init__(self, model_name="snowflake/snowflake-antic-instruct", temperature=0.5):
        """
        Initializes the SnowflakeModel instance with a given model and temperature.
        
        :param model_name: str, the name of the model to use.
        :param temperature: float, the randomness in the output generation (lower is less random).
        """
        self.model_name = model_name
        self.temperature = temperature

    def run_query(self, prompt):
        """
        Executes a given prompt on the Snowflake model and streams back the results.
        
        :param prompt: str, the prompt to send to the model.
        """
        input_data = {
            "prompt": prompt,
            "temperature": self.temperature
        }

        events = replicate.stream(self.model_name, input=input_data)
        for event in events:
            print(event, end="")

# # Example usage
# if __name__ == "__main__":
#     # Create an instance of SnowflakeModel 
#     snowflake_model = SnowflakeModel()

#     # Perform a query using the model
#     snowflake_model.run_query("Write fizz buzz in SQL")