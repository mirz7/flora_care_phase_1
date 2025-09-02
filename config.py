import os
import logging
import sys

class Config:
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    MODEL_PATH = "plant_disease_model_1_latest.pt"
    DISEASE_INFO_PATH = 'disease_info.csv'
    SUPPLEMENT_INFO_PATH = 'supplement_info.csv'
    
    @staticmethod
    def setup_logging():
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('app.log')
            ]
        )
        return logging.getLogger(__name__)