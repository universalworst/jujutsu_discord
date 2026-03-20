import discord
from discord.ext import commands
from config import Config
from narration import generate_narration
from state import load_state, save_state


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)

@bot.event
async def on_ready():
    print("Bot is now online.")

@bot.command()
async def play(ctx, *, player_input):
    #if ctx.channel == Config.LOBBY_CHANNEL():
    #    await ctx.channel.send("You can't send that here! Please go to your location channel and try again.")
    #    return
    waiting = await ctx.channel.send("Waiting...")
    discord_id = ctx.author.id
    state = load_state(discord_id)
    response = await generate_narration(state, player_input)
    state["logs"]["chat_log"].append({
        "player": player_input,
        "narration": response
    })
    save_state(state)
    await ctx.message.delete()
    await waiting.edit(content=f"> {player_input}\n\n{response}")

bot.run(Config.TOKEN)