# ====================================
# IMPORTS AND INTENTS
# ====================================

import os
import discord
from discord.ext import commands
from config import Config
from state import default_state, save_state, load_state, get_all_players, calculate_base_stats
from narration import generate_narration
from utils import split_message
from relationships import seed_relationships
from data import load_all_lore
from scene_tracker import detect_scene, update_scene
from help import move_help, play_help, register_help

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)

# ====================================
# HELPER FUNCTIONS
# ====================================

class RegistrationCancelled(Exception):
    pass

async def ask(bot, dm, question, check):
    await dm.send(question)
    response = await bot.wait_for("message", check=check)
    if response.content.lower() == ".cancel":
        raise RegistrationCancelled
    return response.content

async def ask_integer(bot, dm, question, check, error_message):
    while True:
        answer = await ask(bot, dm, question, check)
        try:
            return int(answer)
        except ValueError:
            await dm.send(error_message)

async def ask_validated(bot, dm, question, check, valid_options, error_message):
    while True:
        answer = await ask(bot, dm, question, check)
        if answer.replace(" ", "_").lower() in valid_options:
            return answer.replace(" ", "_").lower()
        await dm.send(error_message)

async def hide_channel(guild, channel_id, member):
    channel = guild.get_channel(channel_id)
    await channel.set_permissions(member, read_messages=False, send_messages=False)

async def show_channel(guild, channel_id, member):
    channel = guild.get_channel(channel_id)
    await channel.set_permissions(member, read_messages = True, send_messages = True)

async def move_player(guild, member, old_location, location):
    if old_location:
        print(f"Hiding: {old_location}, channel ID: {Config.LOCATION_CHANNELS.get(old_location)}")
        await hide_channel(guild, Config.LOCATION_CHANNELS[old_location], member)
    print(f"Showing: {location}, channel ID: {Config.LOCATION_CHANNELS.get(location)}")
    await show_channel(guild, Config.LOCATION_CHANNELS[location], member)

async def post_to_log(discord_id, guild, message):
    log_channel = guild.get_channel(Config.LOG_CHANNELS[discord_id])
    if log_channel:
        await log_channel.send(message)

def get_players_in_channel(channel_name):
    players = []
    for discord_id in get_all_players():
        state = load_state(discord_id)
        if state["world_state"]["current_location"] == channel_name:
            players.append(discord_id)
    return players

# ====================================
# EVENTS
# ====================================

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass

@bot.event
async def on_ready():
    print("Bot is now online.")

# ====================================
# COMMANDS
# ====================================

# ======== PLAY =========
@bot.command()
async def play(ctx, *, player_input):
    if player_input.lower() == "help":
        print("Help has been sought.")
        await play_help(ctx)
        await ctx.message.delete()
        return
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("Please use this command in a server channel.")
        return
    if ctx.channel.id == Config.LOBBY_CHANNEL:
        await ctx.channel.send("You can't send that here! Please go to your location channel and try again.")
        return
    discord_id = ctx.author.id
    state = load_state(discord_id)
    waiting = await ctx.channel.send("...")
    response = await generate_narration(state, player_input)
    state["logs"]["chat_log"].append({
        "player": player_input,
        "narration": response
    })
    lore = load_all_lore()
    result = detect_scene(state, response, lore)
    if result:
        update_scene(state, result)
    save_state(state)
    split = split_message(response, 2000)
    await ctx.message.delete()
    await waiting.edit(content=f"> {player_input}")
    for chunk in split:
        await ctx.channel.send(chunk)
    current_channel_name = ctx.channel.name.replace('-', '_')
    guild = await bot.fetch_guild(Config.GUILD_ID)
    for discord_id in get_players_in_channel(current_channel_name):
        await post_to_log(int(discord_id), guild, f"> {player_input}")
        for chunk in split:
            await post_to_log(int(discord_id), guild, chunk)

# ======== MOVE =========

@bot.command()
async def move(ctx, *, player_input):
    if player_input.lower() == "help":
        print("Help has been sought.")
        await move_help(ctx)
        await ctx.message.delete()
        return
    state = load_state(ctx.author.id)
    name = state["identity"]["name"]
    old_location = ctx.channel
    location = player_input.replace(" ", "_").lower()
    if ctx.channel.id == Config.LOBBY_CHANNEL:
        await ctx.channel.send("You can't send that here! Please go to your location channel and try again.")
        await ctx.message.delete()
        return
    elif location not in Config.LOCATION_CHANNELS:
        await ctx.channel.send("That's not a valid location! Try again.")
        await ctx.message.delete()
        return
    else:
        print(f"Location input: {location}")
        print(f"In LOCATION_CHANNELS: {location in Config.LOCATION_CHANNELS}")
        print(f"Old location name: {old_location.name}")
        new_channel = ctx.guild.get_channel(Config.LOCATION_CHANNELS[location])
        print(f"New channel: {new_channel}")
        await ctx.message.delete()
        await old_location.send(f"{name} leaves {old_location.name.replace('_', ' ').replace('-', ' ').title()}.")
        await move_player(ctx.guild, ctx.author, old_location.name.replace('-', '_'), location)
        await new_channel.send(f"{name} arrives at {location.replace('_', ' ').replace('-', ' ').title()}.")
        state["world_state"]["current_location"] = location
        save_state(state)

# ======== REGISTER =========

@bot.command()
async def register(ctx, *, player_input):
    if player_input.lower() == "help":
        print("Help has been sought.")
        try:
            await register_help(ctx)
        except Exception as e:
            print(f"Error: {e}")
        await ctx.message.delete()
        return
    else:
        guild = await bot.fetch_guild(Config.GUILD_ID)
        discord_id = ctx.author.id
        member = await guild.fetch_member(discord_id)
        if os.path.exists(os.path.join(Config.SAVE_DIR, f"{discord_id}.json")):
            await ctx.send("You already have a registered character.")
            return
        dm = await ctx.author.create_dm()
        await dm.send("Thank you for registering your character with Jujutsu Kaisen Underground.")
        def check(message):
            return message.author == ctx.author and message.channel == dm
        try:
            name = await ask(bot, dm, "What is your character's name?", check)
            grade = await ask_validated(bot, dm, "What is their grade? Please type one of the following:\n* Grade 4\n* Grade 3\n* Grade 2\n* Grade 1\n* Special Grade", check, Config.GRADES, "You must type out one of the following exactly:\n* Grade 4\n* Grade 3\n* Grade 2\n* Grade 1\n* Special Grade")
            age = await ask_integer(bot, dm, "How old are they? Please respond with a whole number.", check, "You must send a numerical value for your character's age.")
            origin = await ask_validated(bot, dm, "Which of the following best describes how your character came about their powers? (Note: 'Clan' here refers to clan membership or heredity; in other words, they grew up around jujutsu and are familiar with it. Independent refers to a character who has been aware of their powers since childhood, but did not grow up in a clan. Awakened characters are older teenagers or adults who suddenly manifest a technique. Student refers to younger sorcerers who are still mastering their powers.)\n* Clan\n* Independent\n* Awakened\n* Student", check, Config.ORIGINS, "You must type out one of the following exactly:\n* Clan\n* Independent\n* Awakened\n* Student")
            technique_name_raw = await ask(bot, dm, "What is your character's technique called?", check)
            technique_name = technique_name_raw.replace(" ", "_").lower()
            core_effects = await ask(bot, dm, "Describe what your character's technique does.", check)
            limitations = await ask(bot, dm, "What are this technique's drawbacks?", check)
            power = await ask_integer(bot, dm, "On a scale from 1-100, how powerful is this technique in terms of its potential to deal damage?", check, "You must send a numerical value between 1 and 100.")
            personality_type = await ask_validated(bot, dm, "Which of the following personality types best fits your character?\n* Disciplined\n* Reserved\n* Inpulsive\n* Aggressive\n* Analytical\n* Peaceful", check, Config.PERSONALITIES, "Please respond with one of the listed personality types:\n* Disciplined\n* Reserved\n* Inpulsive\n* Aggressive\n* Analytical\n* Peaceful")
            personality = await ask(bot, dm, "Describe your character's personality.", check)
            appearance = await ask(bot, dm, "Describe your character's appearance.", check)
            backstory = await ask(bot, dm, "Describe your character's backstory.", check)
            seed_info = await ask(bot, dm, "What canon characters does your character know, if any? Describe their relationships in one or two sentences.", check)
        except RegistrationCancelled:
            await dm.send("Registration cancelled.")
            return
        await dm.send("Congratulations, you have finished registering. You will be able to play shortly.")
        #await dm.send("For a list of commands and brief explanations of how to use them, send `.help` here.")
        try:
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
            seed_relationships(state, seed_info)
            print(f"{state['world_state']['relationships']}")
        except Exception as e:
            print(f"Error: {e}")
        save_state(state)
        await show_channel(guild, Config.LOCATION_CHANNELS['tokyo_jujutsu_high'].replace("_", "-"), member)


# ====================================
# DEBUG COMMANDS
# ====================================    

@bot.command()
async def testcalc(ctx):
    result = calculate_base_stats("grade_3", "disciplined", "clan")
    await ctx.send(str(result))

bot.run(Config.TOKEN)