import torch
import torch.nn as nn
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import pandas as pd
from PIL import Image
import torchvision.transforms.functional as TF
import numpy as np
import logging
import CNN  # Make sure this is in your directory

logger = logging.getLogger(__name__)

class PlantDiseaseModel:
    def __init__(self, model_path):
        self.model = CNN.CNN(39)
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()
    
    def predict(self, image_path):
        image = Image.open(image_path)
        image = image.resize((224, 224))
        input_data = TF.to_tensor(image)
        input_data = input_data.view((-1, 3, 224, 224))
        output = self.model(input_data)
        output = output.detach().numpy()
        return np.argmax(output)

class GuideGenerator:
    def __init__(self):
        self.generator = None
        self.logger = logging.getLogger(__name__)
        try:
            self._initialize_model()
        except Exception as e:
            self.logger.error(f"Failed to initialize model: {str(e)}")
    
    def _initialize_model(self):
        """Initialize a smaller model that's more likely to work"""
        try:
            # Use a smaller model that's more reliable
            model_name = "facebook/opt-125m"  # Much smaller model
            
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float32,  # Use float32 instead of float16
                low_cpu_mem_usage=True
            )
            
            self.generator = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer
            )
            self.logger.info("Model initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Model initialization error: {str(e)}")
            raise
    
    def generate_guide(self, plant_name):
        """Generate plant care guide"""
        if not self.generator:
            try:
                self._initialize_model()
            except Exception as e:
                self.logger.error(f"Failed to initialize model on retry: {str(e)}")
                return "Sorry, plant guide generation is temporarily unavailable."
        
        try:
            prompt = self._create_guide_prompt(plant_name)
            
            response = self.generator(
                prompt,
                max_length=500,  # Reduced length
                min_length=100,
                num_return_sequences=1,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.generator.tokenizer.eos_token_id
            )
            
            generated_text = response[0]['generated_text']
            cleaned_text = generated_text[len(prompt):].strip()
            
            if not cleaned_text:
                return "Could not generate guide. Please try again."
                
            return cleaned_text
            
        except Exception as e:
            self.logger.error(f"Guide generation error: {str(e)}")
            return "An error occurred while generating the guide. Please try again."
        
        finally:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
    
    @staticmethod
    def _create_guide_prompt(plant_name):
        return f"""Create a plant care guide for {plant_name}.

Basic Information:
[Basic facts about the plant]

Light Requirements:
[Light needs]

Watering Schedule:
[Water needs]

Soil Type:
[Soil requirements]

Temperature and Humidity:
[Climate needs]

Common Problems:
[Common issues and solutions]"""