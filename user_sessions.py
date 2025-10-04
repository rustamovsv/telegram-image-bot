from config import SD_DEFAULTS
from typing import Dict

class UserSession:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.prompt = ""
        self.negative_prompt = SD_DEFAULTS["negative_prompt"]
        self.steps = SD_DEFAULTS["steps"]
        self.cfg_scale = SD_DEFAULTS["cfg_scale"]
        self.width = SD_DEFAULTS["width"]
        self.height = SD_DEFAULTS["height"]
        self.sampler = SD_DEFAULTS["sampler"]
        self.scheduler = "Automatic"
        self.seed = -1
        self.subseed = -1
        self.subseed_strength = 0
        self.restore_faces = False
        self.tiling = False
        self.batch_size = 1
    
    def update_params(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def get_params(self) -> Dict:
        return {
            "prompt": self.prompt,
            "negative_prompt": self.negative_prompt,
            "steps": self.steps,
            "cfg_scale": self.cfg_scale,
            "width": self.width,
            "height": self.height,
            "sampler": self.sampler,
            "scheduler": self.scheduler,
            "seed": self.seed,
            "subseed": self.subseed,
            "subseed_strength": self.subseed_strength,
            "restore_faces": self.restore_faces,
            "tiling": self.tiling,
            "batch_size": self.batch_size
        }

sessions: Dict[int, UserSession] = {}

def get_or_create_session(user_id: int) -> UserSession:
    if user_id not in sessions:
        sessions[user_id] = UserSession(user_id)
    return sessions[user_id]
