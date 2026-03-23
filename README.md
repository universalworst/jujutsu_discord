<h2>Jujutsu Discord</h2>

<h3>Purpose</h3>

`Jujutsu Kaisen discord bot roleplaying tool and partner.`

<h3>Setup</h3>
<a href="https://discordpy.readthedocs.io/en/stable/discord.html"><strong>Discord Bot Creation Guide</strong></a>
<p></p>
<p>While creating the bot:</p>
<ul>
  <li>During step 7 of the 'Creating a bot account' section, be sure to save the Token you copy somewhere safe. Do not share it with anyone else.
  <li>During step 6 of the 'Invite your Bot' section of setup, be sure to grant it <strong>administrator</strong> permissions.
</ul>

<h3>Functionality</h3>
<p>For this bot to work, you will need to create a server for it to live in. That server should have at least three different types of channels, preferrably in different categories. These are:</p>
<ol>
  <li>A lobby channel. You can call this whatever you want, but it is an out of character channel where roleplay commands such as move and play will not work.</li>
  <li>Location channels. These are the backbone of your roleplay. You can put these in a single category or several, but you will need to make note of all of them. Some locations may include Tokyo Jujutsu High, Shibuya Station, Gachinko Fight Club, or others. They can be as broad or as specific as you want. The build-in locations that come with this bot are visible in the files <strong>locations.json</strong> and <strong>mission_sites.json</strong>: in other words, these locations already have data about them built into the bot. If you want to add different locations of your own, I'd recommend adding them to the existing json files using the same format. Please note that mission sites are included as locations and will be traveled in and out of accordingly.</li>
  <li>Log channels. These are channels where a log of each player's roleplay will be maintained without the sloppiness of channel movements.</li>
</ol>
<hr>
<p>Next, open the folder you downloaded from GitHub. It should contain a number of files in its base level ending with python (.py) tags, as well as a "requirements.txt" file. Using any simple text editor (not Microsoft word, but something simpler like TextEdit) or VSCode if you have it, create a file and name it</p>

`.env`

<p>Inside that file, you will write these lines:</p>

`API_KEY =`

`TOKEN =`

<p>Paste the Token you saved when creating your Discord bot after TOKEN =</p>
