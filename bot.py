import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, ConversationHandler
from config import TELEGRAM_BOT_TOKEN, QUALITY_PRESETS, PRESET_SIZES
from user_sessions import get_or_create_session
from keyboards import (
    get_main_menu_keyboard, get_quality_keyboard, get_size_keyboard,
    get_advanced_keyboard, get_sampler_keyboard, get_scheduler_keyboard
)
from gradio_connector import GradioConnector
from fastapi import FastAPI, Request
import uvicorn

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

gradio_client = GradioConnector()

WAITING_STEPS, WAITING_CFG, WAITING_WIDTH, WAITING_HEIGHT, WAITING_SEED, WAITING_NEGATIVE = range(6)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    await update.message.reply_text(
        "Welcome! 🎨\n\n"
        "Send me any text prompt to generate an image.\n"
        "For example: 'sunset over mountains, 4k, detailed'\n\n"
        "After sending your prompt, you'll get options to adjust settings!"
    )

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.message or not update.message.text:
        return
    user_id = update.effective_user.id
    prompt = update.message.text.strip()
    
    session = get_or_create_session(user_id)
    session.prompt = prompt
    
    await update.message.reply_text(
        f"✨ Prompt saved: '{prompt}'\n\n"
        f"Current settings:\n"
        f"• Quality: {session.steps} steps, CFG {session.cfg_scale}\n"
        f"• Size: {session.width}x{session.height}\n"
        f"• Sampler: {session.sampler}\n\n"
        f"What would you like to do?",
        reply_markup=get_main_menu_keyboard()
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or not update.effective_user or not query.data:
        return
    await query.answer()
    
    user_id = update.effective_user.id
    session = get_or_create_session(user_id)
    data = query.data
    
    if data == "generate":
        if not gradio_client.is_available:
            await query.edit_message_text(
                "❌ Image generation is not configured yet.\n\n"
                "To enable image generation:\n"
                "1. Set up your Stable Diffusion API (e.g., Google Colab)\n"
                "2. Add GRADIO_API_URL to Cloud Run environment variables\n"
                "3. Redeploy your bot\n\n"
                "The bot works for everything else!",
                reply_markup=get_main_menu_keyboard()
            )
            return
        
        await query.edit_message_text("🎨 Generating your image... This may take a moment.")
        
        try:
            params = session.get_params()
            result = gradio_client.generate_image(
                prompt=params["prompt"],
                negative_prompt=params["negative_prompt"],
                steps=params["steps"],
                cfg_scale=params["cfg_scale"],
                width=params["width"],
                height=params["height"],
                sampler=params["sampler"],
                scheduler=params["scheduler"],
                seed=params["seed"],
                subseed=params["subseed"],
                subseed_strength=params["subseed_strength"],
                restore_faces=params["restore_faces"],
                tiling=params["tiling"],
                batch_size=params["batch_size"]
            )
            
            await context.bot.send_photo(
                chat_id=user_id,
                photo=result,
                caption=f"Prompt: {params['prompt']}\n"
                        f"Steps: {params['steps']}, CFG: {params['cfg_scale']}, "
                        f"Size: {params['width']}x{params['height']}"
            )
            
            await query.edit_message_text(
                "✅ Image generated successfully!\n\n"
                "Send another prompt to generate more images.",
                reply_markup=None
            )
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            error_msg = str(e)
            if len(error_msg) > 200:
                error_msg = error_msg[:200] + "..."
            
            await query.edit_message_text(
                f"❌ Generation failed: {error_msg}\n\n"
                "Make sure your Colab is running and try again.",
                reply_markup=get_main_menu_keyboard()
            )
    
    elif data == "menu:quality":
        await query.edit_message_text(
            "Select a quality preset:",
            reply_markup=get_quality_keyboard()
        )
    
    elif data == "menu:size":
        await query.edit_message_text(
            "Select image size:",
            reply_markup=get_size_keyboard()
        )
    
    elif data == "menu:advanced":
        await query.edit_message_text(
            f"Advanced Settings:\n\n"
            f"Steps: {session.steps}\n"
            f"CFG Scale: {session.cfg_scale}\n"
            f"Sampler: {session.sampler}",
            reply_markup=get_advanced_keyboard()
        )
    
    elif data == "menu:sampler":
        await query.edit_message_text(
            "Select sampler:",
            reply_markup=get_sampler_keyboard()
        )
    
    elif data == "menu:scheduler":
        await query.edit_message_text(
            f"Select scheduler (current: {session.scheduler}):",
            reply_markup=get_scheduler_keyboard()
        )
    
    elif data == "view_settings":
        params = session.get_params()
        seed_text = "random" if params['seed'] == -1 else str(params['seed'])
        await query.edit_message_text(
            f"📊 Current Settings:\n\n"
            f"Prompt: {params['prompt'][:50]}{'...' if len(params['prompt']) > 50 else ''}\n"
            f"Negative: {params['negative_prompt'][:50]}{'...' if len(params['negative_prompt']) > 50 else ''}\n"
            f"Steps: {params['steps']}\n"
            f"CFG Scale: {params['cfg_scale']}\n"
            f"Size: {params['width']}x{params['height']}\n"
            f"Sampler: {params['sampler']}\n"
            f"Scheduler: {params['scheduler']}\n"
            f"Seed: {seed_text}\n"
            f"Restore Faces: {'ON' if params['restore_faces'] else 'OFF'}\n"
            f"Tiling: {'ON' if params['tiling'] else 'OFF'}",
            reply_markup=get_main_menu_keyboard()
        )
    
    elif data.startswith("quality:"):
        preset_name = data.replace("quality:", "")
        preset = QUALITY_PRESETS[preset_name]
        session.update_params(**preset)
        
        await query.edit_message_text(
            f"✓ Quality preset applied: {preset_name}\n"
            f"Steps: {session.steps}, CFG: {session.cfg_scale}",
            reply_markup=get_main_menu_keyboard()
        )
    
    elif data.startswith("size:"):
        size_name = data.replace("size:", "")
        width, height = PRESET_SIZES[size_name]
        session.update_params(width=width, height=height)
        
        await query.edit_message_text(
            f"✓ Size set to: {size_name} ({width}x{height})",
            reply_markup=get_main_menu_keyboard()
        )
    
    elif data.startswith("sampler:"):
        sampler = data.replace("sampler:", "")
        session.update_params(sampler=sampler)
        
        await query.edit_message_text(
            f"✓ Sampler changed to: {sampler}",
            reply_markup=get_advanced_keyboard()
        )
    
    elif data.startswith("scheduler:"):
        scheduler = data.replace("scheduler:", "")
        session.update_params(scheduler=scheduler)
        
        await query.edit_message_text(
            f"✓ Scheduler changed to: {scheduler}",
            reply_markup=get_advanced_keyboard()
        )
    
    elif data == "steps:inc":
        session.steps = min(session.steps + 5, 150)
        await query.edit_message_text(
            f"Steps: {session.steps}",
            reply_markup=get_advanced_keyboard()
        )
    
    elif data == "steps:dec":
        session.steps = max(session.steps - 5, 5)
        await query.edit_message_text(
            f"Steps: {session.steps}",
            reply_markup=get_advanced_keyboard()
        )
    
    elif data == "cfg:inc":
        session.cfg_scale = min(session.cfg_scale + 0.5, 20.0)
        await query.edit_message_text(
            f"CFG Scale: {session.cfg_scale}",
            reply_markup=get_advanced_keyboard()
        )
    
    elif data == "cfg:dec":
        session.cfg_scale = max(session.cfg_scale - 0.5, 1.0)
        await query.edit_message_text(
            f"CFG Scale: {session.cfg_scale}",
            reply_markup=get_advanced_keyboard()
        )
    
    elif data == "back:main":
        await query.edit_message_text(
            "What would you like to do?",
            reply_markup=get_main_menu_keyboard()
        )
    
    elif data == "back:advanced":
        await query.edit_message_text(
            f"Advanced Settings:\n\n"
            f"Steps: {session.steps}\n"
            f"CFG Scale: {session.cfg_scale}\n"
            f"Sampler: {session.sampler}",
            reply_markup=get_advanced_keyboard()
        )
    
    elif data == "custom:steps":
        await query.edit_message_text("Send me the number of steps (5-150):")
        return WAITING_STEPS
    
    elif data == "custom:cfg":
        await query.edit_message_text("Send me the CFG scale (1.0-20.0):")
        return WAITING_CFG
    
    elif data == "custom:width":
        await query.edit_message_text("Send me the width in pixels (64-2048):")
        return WAITING_WIDTH
    
    elif data == "custom:height":
        await query.edit_message_text("Send me the height in pixels (64-2048):")
        return WAITING_HEIGHT
    
    elif data == "custom:seed":
        await query.edit_message_text("Send me a seed number (-1 for random, or any positive number):")
        return WAITING_SEED
    
    elif data == "custom:negative":
        await query.edit_message_text(f"Current negative prompt:\n{session.negative_prompt}\n\nSend me the new negative prompt:")
        return WAITING_NEGATIVE
    
    elif data == "toggle:restore_faces":
        session.restore_faces = not session.restore_faces
        await query.edit_message_text(
            f"✓ Restore faces: {'ON' if session.restore_faces else 'OFF'}",
            reply_markup=get_advanced_keyboard()
        )
    
    elif data == "toggle:tiling":
        session.tiling = not session.tiling
        await query.edit_message_text(
            f"✓ Tiling: {'ON' if session.tiling else 'OFF'}",
            reply_markup=get_advanced_keyboard()
        )

async def receive_steps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.message or not update.message.text:
        return ConversationHandler.END
    
    user_id = update.effective_user.id
    session = get_or_create_session(user_id)
    
    try:
        steps = int(update.message.text)
        if 5 <= steps <= 150:
            session.steps = steps
            await update.message.reply_text(
                f"✓ Steps set to {steps}",
                reply_markup=get_advanced_keyboard()
            )
        else:
            await update.message.reply_text(
                "Steps must be between 5 and 150. Try again:",
            )
            return WAITING_STEPS
    except ValueError:
        await update.message.reply_text("Please send a valid number:")
        return WAITING_STEPS
    
    return ConversationHandler.END

async def receive_cfg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.message or not update.message.text:
        return ConversationHandler.END
    
    user_id = update.effective_user.id
    session = get_or_create_session(user_id)
    
    try:
        cfg = float(update.message.text)
        if 1.0 <= cfg <= 20.0:
            session.cfg_scale = cfg
            await update.message.reply_text(
                f"✓ CFG scale set to {cfg}",
                reply_markup=get_advanced_keyboard()
            )
        else:
            await update.message.reply_text(
                "CFG scale must be between 1.0 and 20.0. Try again:",
            )
            return WAITING_CFG
    except ValueError:
        await update.message.reply_text("Please send a valid number:")
        return WAITING_CFG
    
    return ConversationHandler.END

async def receive_width(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.message or not update.message.text:
        return ConversationHandler.END
    
    user_id = update.effective_user.id
    session = get_or_create_session(user_id)
    
    try:
        width = int(update.message.text)
        if 64 <= width <= 2048:
            session.width = width
            await update.message.reply_text(
                f"✓ Width set to {width}px",
                reply_markup=get_main_menu_keyboard()
            )
        else:
            await update.message.reply_text(
                "Width must be between 64 and 2048. Try again:",
            )
            return WAITING_WIDTH
    except ValueError:
        await update.message.reply_text("Please send a valid number:")
        return WAITING_WIDTH
    
    return ConversationHandler.END

async def receive_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.message or not update.message.text:
        return ConversationHandler.END
    
    user_id = update.effective_user.id
    session = get_or_create_session(user_id)
    
    try:
        height = int(update.message.text)
        if 64 <= height <= 2048:
            session.height = height
            await update.message.reply_text(
                f"✓ Height set to {height}px",
                reply_markup=get_main_menu_keyboard()
            )
        else:
            await update.message.reply_text(
                "Height must be between 64 and 2048. Try again:",
            )
            return WAITING_HEIGHT
    except ValueError:
        await update.message.reply_text("Please send a valid number:")
        return WAITING_HEIGHT
    
    return ConversationHandler.END

async def receive_seed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.message or not update.message.text:
        return ConversationHandler.END
    
    user_id = update.effective_user.id
    session = get_or_create_session(user_id)
    
    try:
        seed = int(update.message.text)
        session.seed = seed
        seed_text = "random" if seed == -1 else str(seed)
        await update.message.reply_text(
            f"✓ Seed set to {seed_text}",
            reply_markup=get_advanced_keyboard()
        )
    except ValueError:
        await update.message.reply_text("Please send a valid number:")
        return WAITING_SEED
    
    return ConversationHandler.END

async def receive_negative(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.message or not update.message.text:
        return ConversationHandler.END
    
    user_id = update.effective_user.id
    session = get_or_create_session(user_id)
    
    session.negative_prompt = update.message.text
    await update.message.reply_text(
        f"✓ Negative prompt updated",
        reply_markup=get_main_menu_keyboard()
    )
    
    return ConversationHandler.END

async def cancel_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Cancelled.",
        reply_markup=get_main_menu_keyboard()
    )
    return ConversationHandler.END

app = FastAPI()
application = None
bot_ready = False

async def setup_application():
    global application, bot_ready
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not set")
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_callback)],
        states={
            WAITING_STEPS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_steps)],
            WAITING_CFG: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_cfg)],
            WAITING_WIDTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_width)],
            WAITING_HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_height)],
            WAITING_SEED: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_seed)],
            WAITING_NEGATIVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_negative)],
        },
        fallbacks=[CommandHandler("cancel", cancel_input)],
        per_message=False
    )
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    await application.initialize()
    await application.start()
    
    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        await application.bot.set_webhook(url=f"{webhook_url}/webhook")
        logger.info(f"Webhook set to {webhook_url}/webhook")
    
    bot_ready = True
    logger.info("Bot initialized and ready")

@app.on_event("startup")
async def startup():
    await setup_application()

@app.on_event("shutdown")
async def shutdown():
    if application:
        await application.stop()
        await application.shutdown()

@app.post("/webhook")
async def webhook(request: Request):
    if not bot_ready or application is None:
        logger.warning("Webhook called before bot initialization complete")
        return {"ok": False, "error": "Bot not ready"}, 503
    
    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.update_queue.put(update)
        return {"ok": True}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"ok": False, "error": str(e)}, 500

@app.get("/")
async def health():
    return {
        "status": "healthy" if bot_ready else "initializing",
        "bot": "ready" if bot_ready else "starting"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
