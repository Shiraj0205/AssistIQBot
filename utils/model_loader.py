import os
import sys
from dotenv import load_dotenv
from utils.config_loader import load_config
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
#from langchain_openai import ChatOpenAI
from logger.custom_logger import CustomLogger
from exception.custom_exception import AssistIQAppException


log = CustomLogger().get_logger(__name__)


class ModelLoader:
    """
    A class to load models and configurations for the Document Portal application.
    This class handles the loading of configurations from a YAML file and initializes
    the necessary models such as embeddings and language models (LLMs).
    """
    def __init__(self):
        load_dotenv()
        self._validate_env()
        self.config = load_config()
        log.info("ModelLoader initialized with config: %s", self.config)

   
    def _validate_env(self):
        """Validates the environment variables required for the application.
        Ensure Api keys and other necessary configurations are set."""
        required_env_vars = ["GROQ_API_KEY", "google_api_key"]
        self.api_keys = {
            key: os.getenv(key) for key in required_env_vars
            }

        missing_vars = [key for key, value in self.api_keys.items() if not value]
        
        if missing_vars:
            log.error("Missing required environment variables: %s", missing_vars)
            raise AssistIQAppException("Missing required environment variables.", sys)


    def load_embeddings(self):
        """This method loads the embeddings model based on the configuration. 
        GoogleGenerativeAIEmbeddings: An instance of the embeddings model."""
        try:
            model_name = self.config["embedding_model"]["model_name"]
            return GoogleGenerativeAIEmbeddings(model=model_name)
        except Exception as e:
            log.error("Error loading embeding model", error=str(e))
            raise AssistIQAppException(error_message="Failed to load embeddings", error_details=sys)


    def load_llm(self):
        """Load LLM Model based on Provider"""
        llm_block = self.config["llm"]

        # Read Provider from config
        provider_key = os.getenv("LLM_PROVIDER", "groq") # Default model provider is groq
        if provider_key not in llm_block:
            log.error("LLM Provider not defined in config", provider_key=provider_key)
            raise ValueError(f"LLM Provider {provider_key} not found in config")
        
        llm_config = llm_block[provider_key]
        provider = llm_config.get("provider")
        model_name = llm_config.get("model_name")
        temperature = llm_config.get("temperature", 0.2)
        max_tokens = llm_config.get("max_tokens", 2048)

        log.info("Loading LLM", provider=provider, model=model_name, temperature=temperature, max_tokens=max_tokens)

        if provider == "google":
            llm = ChatGoogleGenerativeAI(
                model=model_name, 
                temperature=temperature, 
                max_tokens=max_tokens
                )
            return llm
            
        if provider == "groq":
            llm = ChatGroq(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return llm

        # if provider == "openai":
        #     llm = ChatOpenAI(
        #         model=model_name, 
        #         temperature=temperature, 
        #         max_tokens=max_tokens
        #         )
        # return llm
        else:
            log.error("Unsupported LLM provider", provider=provider)
            raise ValueError(f"Unsupported LLM provider: {provider}")


if __name__ == "__main__":
    loader = ModelLoader()
    embeddings = loader.load_embeddings()
    embedding_result = embeddings.embed_query("Hello World")
    print(f"Embedding Result : {embedding_result}")

    llm = loader.load_llm()
    result = llm.invoke("What is the capital of USA?")
    print(f"LLM Result : {result.content}")
    log.info("Embeddings and LLM loaded successfully.")