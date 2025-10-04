import requests
import base64
from io import BytesIO
from config import GRADIO_API_URL
import logging

logger = logging.getLogger(__name__)

class GradioConnector:
    def __init__(self):
        self.api_url = GRADIO_API_URL
        self.is_available = False
        self.connect()
    
    def connect(self):
        try:
            if not self.api_url:
                logger.warning("GRADIO_API_URL not set - image generation will be unavailable")
                self.is_available = False
                return
            
            self.is_available = True
            logger.info(f"Connected to Automatic1111 API: {self.api_url}")
        except Exception as e:
            logger.error(f"Failed to connect to API: {e}")
            self.is_available = False
    
    def generate_image(self, prompt, negative_prompt, steps, cfg_scale, width, height, sampler, scheduler="Automatic",
                       seed=-1, subseed=-1, subseed_strength=0, restore_faces=False, tiling=False, batch_size=1):
        try:
            if not self.is_available:
                raise RuntimeError("Image generation is not available. Please configure GRADIO_API_URL in Cloud Run environment variables.")
            
            logger.info(f"Generating image with prompt: {prompt[:50]}...")
            
            payload = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "steps": int(steps),
                "cfg_scale": float(cfg_scale),
                "width": int(width),
                "height": int(height),
                "sampler_name": sampler,
                "sampler_index": sampler,
                "scheduler": scheduler,
                "seed": int(seed),
                "subseed": int(subseed),
                "subseed_strength": float(subseed_strength),
                "seed_resize_from_h": -1,
                "seed_resize_from_w": -1,
                "batch_size": int(batch_size),
                "n_iter": 1,
                "restore_faces": restore_faces,
                "tiling": tiling,
                "do_not_save_samples": True,
                "do_not_save_grid": True,
                "save_images": False
            }
            
            api_endpoint = f"{self.api_url}/sdapi/v1/txt2img"
            logger.info(f"Calling API endpoint: {api_endpoint}")
            logger.info(f"Payload: {payload}")
            
            response = requests.post(api_endpoint, json=payload, timeout=300)
            
            if response.status_code != 200:
                error_msg = f"API returned status {response.status_code}"
                try:
                    error_detail = response.json()
                    logger.error(f"API error detail: {error_detail}")
                    error_msg = f"{error_msg}: {error_detail.get('detail', 'Unknown error')}"
                except:
                    error_msg = f"{error_msg}: {response.text[:200]}"
                raise RuntimeError(error_msg)
            
            result = response.json()
            
            if 'images' in result and len(result['images']) > 0:
                image_data = base64.b64decode(result['images'][0])
                image_io = BytesIO(image_data)
                image_io.name = 'generated_image.png'
                image_io.seek(0)
                logger.info("Image generated successfully")
                return image_io
            else:
                raise RuntimeError("No images returned from API")
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise
