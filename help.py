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

async def move_help(ctx):
    dm = await ctx.author.create_dm()
    await dm.send(mover)
   
async def play_help(ctx):
    dm = await ctx.author.create_dm()
    await dm.send(player)

async def register_help(ctx):
    dm = await ctx.author.create_dm()
    await dm.send(registerer)
