from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import QUALITY_PRESETS, PRESET_SIZES, SAMPLERS

def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎨 Generate Image", callback_data="generate")],
        [
            InlineKeyboardButton("⚡ Quality Preset", callback_data="menu:quality"),
            InlineKeyboardButton("📐 Size", callback_data="menu:size")
        ],
        [
            InlineKeyboardButton("🎛️ Advanced", callback_data="menu:advanced"),
            InlineKeyboardButton("📊 View Settings", callback_data="view_settings")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_quality_keyboard():
    keyboard = []
    for preset_name in QUALITY_PRESETS.keys():
        keyboard.append([InlineKeyboardButton(preset_name, callback_data=f"quality:{preset_name}")])
    keyboard.append([InlineKeyboardButton("« Back", callback_data="back:main")])
    return InlineKeyboardMarkup(keyboard)

def get_size_keyboard():
    keyboard = []
    for size_name in PRESET_SIZES.keys():
        keyboard.append([InlineKeyboardButton(size_name, callback_data=f"size:{size_name}")])
    keyboard.append([InlineKeyboardButton("✏️ Custom Width", callback_data="custom:width"), InlineKeyboardButton("✏️ Custom Height", callback_data="custom:height")])
    keyboard.append([InlineKeyboardButton("« Back", callback_data="back:main")])
    return InlineKeyboardMarkup(keyboard)

def get_advanced_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔄 Sampler", callback_data="menu:sampler"), InlineKeyboardButton("⏱️ Scheduler", callback_data="menu:scheduler")],
        [InlineKeyboardButton("Steps: -5", callback_data="steps:dec"), InlineKeyboardButton("Steps: +5", callback_data="steps:inc"), InlineKeyboardButton("✏️ Custom", callback_data="custom:steps")],
        [InlineKeyboardButton("CFG: -0.5", callback_data="cfg:dec"), InlineKeyboardButton("CFG: +0.5", callback_data="cfg:inc"), InlineKeyboardButton("✏️ Custom", callback_data="custom:cfg")],
        [InlineKeyboardButton("🎲 Seed", callback_data="custom:seed"), InlineKeyboardButton("💬 Negative Prompt", callback_data="custom:negative")],
        [InlineKeyboardButton("🔧 Restore Faces", callback_data="toggle:restore_faces"), InlineKeyboardButton("🔁 Tiling", callback_data="toggle:tiling")],
        [InlineKeyboardButton("« Back", callback_data="back:main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_sampler_keyboard():
    keyboard = []
    for i in range(0, len(SAMPLERS), 2):
        row = []
        row.append(InlineKeyboardButton(SAMPLERS[i], callback_data=f"sampler:{SAMPLERS[i]}"))
        if i + 1 < len(SAMPLERS):
            row.append(InlineKeyboardButton(SAMPLERS[i+1], callback_data=f"sampler:{SAMPLERS[i+1]}"))
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("« Back", callback_data="back:advanced")])
    return InlineKeyboardMarkup(keyboard)

def get_scheduler_keyboard():
    schedulers = ["Automatic", "Karras", "Exponential", "Polyexponential", "SGM Uniform", "Simple", "Normal", "DDIM", "Beta"]
    keyboard = []
    for i in range(0, len(schedulers), 2):
        row = []
        row.append(InlineKeyboardButton(schedulers[i], callback_data=f"scheduler:{schedulers[i]}"))
        if i + 1 < len(schedulers):
            row.append(InlineKeyboardButton(schedulers[i+1], callback_data=f"scheduler:{schedulers[i+1]}"))
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("« Back", callback_data="back:advanced")])
    return InlineKeyboardMarkup(keyboard)
