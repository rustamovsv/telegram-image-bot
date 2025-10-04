import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GRADIO_API_URL = os.getenv("GRADIO_API_URL")

SD_DEFAULTS = {
    "steps": 20,
    "cfg_scale": 7.0,
    "width": 512,
    "height": 512,
    "sampler": "Euler a",
    "negative_prompt": "ugly, blurry, low quality, distorted"
}

SAMPLERS = [
    "Euler a", "Euler", "DPM++ 2M Karras", "DPM++ 2M",
    "DPM++ SDE Karras", "DPM++ SDE", "DPM++ 2M SDE Karras",
    "DPM++ 2M SDE", "DPM++ 3M SDE Karras", "DPM++ 3M SDE",
    "DPM2 Karras", "DPM2", "DPM2 a Karras", "DPM2 a",
    "Heun", "LMS", "LMS Karras", "DDIM", "PLMS",
    "UniPC", "DPM fast", "DPM adaptive"
]

PRESET_SIZES = {
    "Square 512x512": (512, 512),
    "Square 768x768": (768, 768),
    "Portrait 512x768": (512, 768),
    "Landscape 768x512": (768, 512),
    "HD 1024x768": (1024, 768),
}

QUALITY_PRESETS = {
    "Fast (10 steps)": {"steps": 10, "cfg_scale": 7.0},
    "Balanced (20 steps)": {"steps": 20, "cfg_scale": 7.0},
    "Quality (30 steps)": {"steps": 30, "cfg_scale": 7.5},
    "High Detail (50 steps)": {"steps": 50, "cfg_scale": 8.0},
}
