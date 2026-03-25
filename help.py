mover = """The `.move` command is used to change locations in the `Jujutsu Kaisen : Underground` server, moving you from one location channel to another.

To use the `.move` command, go to a location channel and send `.move location`, substituting `location` with the name of the channel to which you want to travel.

`List of Travel Locations:`
🔴 `Tokyo Districts`
* `shibuya`
* `shinjuku`
* `harajuku`
* `roppongi`
* `chiyoda`
* `nerima`
* `nakano`
* `minato`

🟠 `Tokyo Landmarks`
* `shibuya crossing`
* `shibuya station`
* `shinjuku station`
* `kabuchiko`
* `roppongi hills`
* `meiji shrine`

🟡 `Other Locales`
* `kyoto`
* `sendai`
* `gachinko fight club`

🟢 `Jujutsu Society`
* `tokyo jujutsu high`
* `kyoto jujutsu high`
* `gojo estate`
* `zenin estate`
* `kamo estate`

Please note that these are not the *only* possible locations to visit, but why give away everything at once?
"""

player = """The `.play` command is used to submit roleplay that you want to be preserved in your log channel and used to keep your save state up-to-date on your actions and movements.

To use the `.play` command, simply type `.play` in a location channel before writing a normal roleplay reply.
For example:

`.play Yuji clenched his fist and punched Mahito directly in his stupid face.`

This will be preserved as:

> Yuji clenched his fist and punched Mahito directly in his stupid face.
"""

registerer = """The `.register` command is used to create your character.
When you send `.register`, either in the server or in a DM with the Narrator, you will be asked a series of questions about your character.

These questions include:
* `What is your character's name?`
* `What is their grade?`
* `How old are they?`
* `What was their path in obtaining and honing their powers?` ( Clan / Independent / Awakened / Student )
* `What is your character's technique called?` 
* `Describe what your character's technique does.`
* `What are this technique's drawbacks?` 
* `Which of the following personality types best describes your character?` ( Disciplined / Reserved / Impulsive / Aggressive / Analytical / Peaceful )
* `Describe your character's personality.`
* `Describe your character's backstory.`

You can cancel the registration process at any time using the command `.cancel` in your DM conversation with the Narrator.
"""

statser = """Send `.stats` in any server channel or in a DM with the Narrator for your character's stats.
These include:
`Grade`
`Age`
`Health`
`Injuries`
`Cursed Energy`
`Control`
`Stability`
"""

helper = """## List of commands
* `play`: Used before each reply in solo roleplay sessions with the Narrator to ensure it reads your reply and gives a response.
Proper use:
> `.play Akira stares down at the curse as it hisses at him from its vulnerable position in the center of the factory floor.`

* `move`: Used to move location channels. This command will shut off permissions to the channel you were in originally and grant permissions to the new channel. There is no need to worry about capitalization, dashes, or underscores.
Proper use:
> `.move shibuya` or `.move tokyo jujutsu tech`

* `register`: Used to register a new character with the bot. For more detailed information on what you're asked by the bot, submit `.register help`. Otherwise, just send `.register` in a channel on the server or in a DM with the Narrator.

* `stats`: Displays the player's stats for them to view. This feature is a work in progress.
"""

async def stat(state):
    name = state["identity"]["name"]
    grade = state["identity"]["grade"]
    if not grade:
        grade_display = "None"
    else:
        grade_display = grade.replace('_', ' ').title()
    age = state["identity"]["age"]
    health = state["stats"]["health"]
    injuries = state["stats"]["injuries"]
    if not injuries:
        injuries_display = "None"
    else:
        injuries_display = ", ".join(injuries).replace('_', ' ').title()
    ce = state["stats"]["cursed_energy"]
    max_ce = state["stats"]["max_cursed_energy"]
    control = state["stats"]["control"]
    stability = state["stats"]["stability"]
    try:
        stats_message = f"""
    **__{name}'s Stats Sheet__**
    **Grade:** {grade_display}
    **Age:** {age}
    **Health:** {health}/100
    **Injuries:** {injuries_display}
    **Cursed Energy:** {ce}/{max_ce}
    **Control:** {control}/100
    **Stability:** {stability}/10
    """
    except Exception as e:
        print(f"Exception: {e}")
    return stats_message

async def move_help(ctx):
    dm = await ctx.author.create_dm()
    await dm.send(mover)
   
async def play_help(ctx):
    dm = await ctx.author.create_dm()
    await dm.send(player)

async def register_help(ctx):
    dm = await ctx.author.create_dm()
    await dm.send(registerer)

async def stats_help(ctx):
    dm = await ctx.author.create_dm()
    await dm.send(statser)

async def help(ctx):
    print("About to create DM")
    dm = await ctx.author.create_dm()
    print("About to send helper")
    await dm.send(helper)

async def help_default(ctx):
    dm = await ctx.author.create_dm()
    await dm.send(helper)