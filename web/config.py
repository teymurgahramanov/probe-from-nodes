import os
from dotenv import load_dotenv

load_dotenv()

class Config:

    APP_VERSION = 'v1.0.0'

    EXPORTER_PODS_LABEL_SELECTOR = os.getenv('EXPORTER_PODS_LABEL_SELECTOR',"app=kubeping-exporter")
    EXPORTER_PORT = 8080
    EXPORTER_PATH = '/probe'
    
    WEB_PROBE_TIMEOUT = int(os.getenv('WEB_PROBE_TIMEOUT','3'))
    WEB_SECRET_KEY = os.getenv('WEB_SECRET_KEY', 'secret_key')

config = Config()