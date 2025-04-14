from dotenv import load_dotenv;
import os

load_dotenv()

VIDEOS_PATH     = os.getenv('VIDEOS_PATH') + '/'
AZURE_STORAGE = os.getenv('AZURE_STORAGE')
AZURE_CONTAINER = os.getenv('AZURE_CONTAINER')
AZURE_SPEECH_SERVICE = os.getenv('AZURE_SPEECH_SERVICE_KEY')
AZURE_TRANSLATOR = os.getenv('AZURE_TRANSLATOR_KEY')
REGION = os.getenv('REGION')