"""Slash command handlers."""
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from database import settings as db_settings
from database import messages as db_messages
from config.settings import DEFAULT_MODEL, DEFAULT_DURATION, DEFAULT_RESOLUTION

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command."""
    await message.answer(
        "👋 Welcome to the Video Generation Bot!\n\n"
        "Send me a text prompt and I'll generate a video for you using Google Veo API.\n\n"
        "Use /help to see all available commands."
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command."""
    help_text = """
📖 Available Commands:

/start - Welcome message
/help - Show this help message
/settings - View current settings
  /setmodel [model] - Set Veo model
  /setduration [seconds] - Set video duration
  /setresolution [resolution] - Set video resolution
/reset - Reset settings to defaults
/stats - View usage statistics

💡 Usage:
Just send me a text prompt and I'll generate a video for you!

Example: <code>A beautiful sunset over the ocean</code>
    """
    await message.answer(help_text)


@router.message(Command("settings"))
async def cmd_settings(message: Message):
    """Handle /settings command."""
    user_settings = db_settings.get_user_settings(message.from_user.id)
    
    settings_text = f"""
⚙️ Your Current Settings:

Model: <code>{user_settings['model']}</code>
Duration: <code>{user_settings['duration']}</code> seconds
Resolution: <code>{user_settings['resolution']}</code>

Use /setmodel to change the model.
Use /setduration to change the duration.
Use /setresolution to change the resolution.
Use /reset to restore defaults.
    """
    await message.answer(settings_text)


@router.message(Command("setmodel"))
async def cmd_setmodel(message: Message):
    """Handle /setmodel command."""
    # Extract model from command arguments
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "❌ Please specify a model.\n\n"
            "Usage: /setmodel [model]\n\n"
            "Example:\n"
            "<code>/setmodel veo-3.1-generate-001</code>\n\n"
            "📋 Available models (Veo 3.0 and 3.1 only):\n\n"
            "<b>Veo 3.1 models:</b>\n"
            "  • <code>veo-3.1-generate-001</code>\n"
            "  • <code>veo-3.1-fast-generate-001</code>\n\n"
            "💡 Use /help to explore other commands."
        )
        return
    
    model = parts[1].strip()
    
    # Validate model name (only veo 3 and 3.1 models are supported)
    valid_models = [
        "veo-3.1-generate-001",
        "veo-3.1-fast-generate-001",
    ]
    
    if model not in valid_models:
        await message.answer(
            f"❌ Invalid model: <code>{model}</code>\n\n"
            "📋 Please use one of the supported models:\n\n"
            "\n".join(f"  • <code>{m}</code>" for m in valid_models) + "\n\n"
            "💡 Use /help to explore other commands."
        )
        return
    
    # Update settings
    db_settings.set_user_settings(message.from_user.id, model=model)
    await message.answer(f"✅ Model set to: <code>{model}</code>")


@router.message(Command("setduration"))
async def cmd_setduration(message: Message):
    """Handle /setduration command."""
    # Get current user settings to show model-specific options
    user_settings = db_settings.get_user_settings(message.from_user.id)
    model = user_settings["model"]
    
    # Valid durations for Veo 3 models (both 3.0 and 3.1)
    valid_durations = [4, 6, 8]
    
    # Extract duration from command arguments
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            f"❌ Please specify a duration.\n\n"
            f"Usage: /setduration [seconds]\n\n"
            f"Example:\n"
            f"<code>/setduration 8</code>\n\n"
            f"📋 Valid durations:\n"
            f"  • <code>4</code> seconds\n"
            f"  • <code>6</code> seconds\n"
            f"  • <code>8</code> seconds(default)\n\n"
            f"Your current model: <code>{model}</code>\n"
            f"Your current duration: <code>{user_settings['duration']}</code> seconds\n\n"
            f"💡 Use /help to explore other commands."
        )
        return
    
    try:
        duration = int(parts[1].strip())
    except ValueError:
        await message.answer(
            f"❌ Invalid duration. Please provide a number.\n\n"
            f"Usage: /setduration [seconds]\n\n"
            f"Valid durations:\n"
            f"  • <code>4</code> seconds\n"
            f"  • <code>6</code> seconds\n"
            f"  • <code>8</code> seconds\n\n"
            f"💡 Use /help to explore other commands."
        )
        return
    
    # Validate duration - Veo 3 models only support 4, 6, or 8
    if duration not in valid_durations:
        await message.answer(
            f"❌ Invalid duration: <code>{duration}</code> seconds\n\n"
            f"📋 Valid durations:\n"
            f"  • <code>4</code> seconds\n"
            f"  • <code>6</code> seconds\n"
            f"  • <code>8</code> seconds\n\n"
            f"Your current model: <code>{model}</code>\n\n"
            f"💡 Use /help to explore other commands."
        )
        return
    
    # Update settings
    db_settings.set_user_settings(message.from_user.id, duration=duration)
    await message.answer(
        f"✅ Duration set to: <code>{duration}</code> seconds\n\n"
        f"Model: <code>{model}</code>\n"
        f"Duration: <code>{duration}</code> seconds"
    )


@router.message(Command("setresolution"))
async def cmd_setresolution(message: Message):
    """Handle /setresolution command."""
    # Extract resolution from command arguments
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "❌ Please specify a resolution.\n\n"
            "Usage: /setresolution [resolution]\n\n"
            "Example:\n"
            "<code>/setresolution 1080p</code>\n\n"
            "Valid resolutions:\n"
            "- <code>720p</code> (default)\n"
            "- <code>1080p</code>\n\n"
            "💡 Use /help to explore other commands."
        )
        return
    
    resolution = parts[1].strip().lower()
    
    # Validate resolution
    valid_resolutions = ["720p", "1080p"]
    
    if resolution not in valid_resolutions:
        await message.answer(
            f"❌ Invalid resolution: <code>{resolution}</code>\n\n"
            "Please use one of the supported resolutions:\n" +
            "\n".join(f"- <code>{r}</code>" for r in valid_resolutions) + "\n\n"
            "💡 Use /help to explore other commands."
        )
        return
    
    # Check if resolution is supported by the current model
    user_settings = db_settings.get_user_settings(message.from_user.id)
    model = user_settings["model"]
    
    # Update settings first
    db_settings.set_user_settings(message.from_user.id, resolution=resolution)
    
    # 1080p is only supported by Veo 3 models
    if resolution == "1080p" and "veo-3" not in model:
        await message.answer(
            f"⚠️ Warning: <code>1080p</code> resolution is only supported by Veo 3 models.\n"
            f"Your current model is: <code>{model}</code>\n\n"
            f"✅ Resolution set to: <code>{resolution}</code>\n"
            f"Consider using a Veo 3 model (e.g., <code>/setmodel veo-3.1-generate-001</code>) for 1080p support."
        )
    else:
        await message.answer(f"✅ Resolution set to: <code>{resolution}</code>")


@router.message(Command("reset"))
async def cmd_reset(message: Message):
    """Handle /reset command."""
    db_settings.reset_user_settings(message.from_user.id)
    await message.answer(
        f"✅ Settings reset to defaults:\n\n"
        f"Model: <code>{DEFAULT_MODEL}</code>\n"
        f"Duration: <code>{DEFAULT_DURATION}</code> seconds\n"
        f"Resolution: <code>{DEFAULT_RESOLUTION}</code>"
    )


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Handle /stats command."""
    stats = db_messages.get_stats()
    
    stats_text = f"""
📊 Usage Statistics:

Total Messages: {stats['total_messages']}
Unique Users: {stats['unique_users']}
Successful: {stats['successful_messages']}
Failed: {stats['failed_messages']}
Total Cost: ${stats['total_cost']:.4f}
Total Prompt Tokens: {stats['total_prompt_tokens']:,}
Total Output Tokens: {stats['total_output_prompt_tokens']:,}
    """
    await message.answer(stats_text)

