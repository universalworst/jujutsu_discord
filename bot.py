# ====================================
# IMPORTS AND INTENTS
# ====================================

import json
import discord
from discord.ext import commands
from config import Config
from state import default_state, save_state, load_state
from narration import generate_narration
from state import load_state, save_state, calculate_base_stats
from utils import split_message

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)

# ====================================
# EVENTS
# ====================================

@bot.event
async def on_ready():
    print("Bot is now online.")

# ====================================
# SIMPLE COMMANDS
# ====================================

@bot.command()
async def play(ctx, *, player_input):
    #if ctx.channel == Config.LOBBY_CHANNEL():
    #    await ctx.channel.send("You can't send that here! Please go to your location channel and try again.")
    #    return
    discord_id = ctx.author.id
    state = load_state(discord_id)
    waiting = await ctx.channel.send("...")
    response = await generate_narration(state, player_input)
    state["logs"]["chat_log"].append({
        "player": player_input,
        "narration": response
    })
    save_state(state)
    split = split_message(response, 2000)
    await ctx.message.delete()
    await waiting.edit(content=f"> {player_input}")
    for chunk in split:
        await ctx.channel.send(chunk)

# ====================================
# LONG-FORM COMMANDS
# ====================================

@bot.command()
async def register(ctx):
    discord_id = ctx.author.id
    dm = await ctx.author.create_dm()
    await dm.send("Thank you for registering your character with Jujutsu Kaisen Underground. What is your character's name?")
    def check(message):
        return message.author == ctx.author and message.channel == dm
    response = await bot.wait_for("message", check=check)
    name = response.content
    await dm.send("What is their grade? Please type one of the following:\n* Grade 4\n* Grade 3\n* Grade 2\n* Grade 1\n* Special Grade")
    while True:
        response = await bot.wait_for("message", check=check)
        grade = response.content.replace(" ", "_").lower()
        if grade in Config.GRADES:
            break
        else:
            await dm.send("You must type out one of the following exactly:\n* Grade 4\n* Grade 3\n* Grade 2\n* Grade 1\n* Special Grade")
    await dm.send("How old are they? Please respond with a whole number.")
    while True:
        response = await bot.wait_for("message", check=check)
        try:
            age = int(response.content)
            break
        except ValueError:
            await dm.send("You must send a numerical value for your character's age.")
    await dm.send("Which of the following best describes how your character came about their powers? (Note: 'Clan' here refers to clan membership or heredity; in other words, they grew up around jujutsu and are familiar with it. Independent refers to a character who has been aware of their powers since childhood, but did not grow up in a clan. Awakened characters are older teenagers or adults who suddenly manifest a technique. Student refers to younger sorcerers who are still mastering their powers.)\n* Clan\n* Independent\n* Awakened\n* Student")
    while True:
        response = await bot.wait_for("message", check=check)
        origin = response.content.lower()
        if origin in Config.ORIGINS:
            break
        else:
            await dm.send("You must type out one of the following exactly:\n* Clan\n* Independent\n* Awakened\n* Student")
    await dm.send("What is your character's technique called?")
    response = await bot.wait_for("message", check=check)
    technique_name = response.content.replace(" ", "_").lower()
    await dm.send("Describe what your character's technique does.")
    response = await bot.wait_for("message", check=check)
    core_effects = response.content
    await dm.send("What are this technique's drawbacks?")
    response = await bot.wait_for("message", check=check)
    limitations = response.content
    await dm.send("On a scale from 1-100, how powerful is this technique in terms of its potential to deal damage?")
    while True:
        response = await bot.wait_for("message", check=check)
        try:
            power = int(response.content)
            break
        except ValueError:
            await dm.send("You must send a numerical value between 1 and 100.")
    await dm.send("Which of the following personality types best fits your character?\n* Disciplined\n* Reserved\n* Inpulsive\n* Aggressive\n* Analytical\n* Peaceful")
    while True:
        response = await bot.wait_for("message", check=check)
        personality_type = response.content.lower()
        if personality_type in Config.PERSONALITIES:
            break
        else:
            await dm.send("Please respond with one of the listed personality types:\n* Disciplined\n* Reserved\n* Inpulsive\n* Aggressive\n* Analytical\n* Peaceful")
    await dm.send("Describe your character's personality.")
    response = await bot.wait_for("message", check=check)
    personality = response.content
    await dm.send("Describe your character's appearance.")
    response = await bot.wait_for("message", check=check)
    appearance = response.content
    await dm.send("Describe your character's backstory.")
    response = await bot.wait_for("message", check=check)
    backstory = response.content
    #await dm.send("What canon characters does your character know, if any? Describe their relationships in one or two sentences.")
    #response = await bot.wait_for("message", check=check)
    #seed_info = response.content
    await dm.send("Congratulations, you have finished registering. You will be able to play shortly.")
    #await dm.send("For a list of commands and brief explanations of how to use them, send `.help` here.")
    state = default_state(name, discord_id)
    state["identity"]["grade"] = grade
    state["identity"]["age"] = age
    state["identity"]["origin"] = origin
    state["identity"]["personality_type"] = personality_type
    state["identity"]["personality"] = personality
    state["identity"]["appearance"] = appearance
    state["identity"]["backstory"] = backstory
    state["technique"]["technique_name"] = technique_name
    state["technique"]["core_effects"] = core_effects
    state["technique"]["limitations"] = limitations
    state["technique"]["power"] = power
    state["stats"].update(calculate_base_stats(grade, personality_type, origin))
    save_state(state)

bot.run(Config.TOKEN)