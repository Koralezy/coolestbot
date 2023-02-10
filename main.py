import discord  # pycord
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
from itertools import cycle
import threading
import time
from datetime import datetime
from lists import topics, foodgifs, killgifs
import random
import re
import json
#import ffmpeg (for music cmds)

bot = discord.Bot(intents=discord.Intents(guilds=True, messages=True, message_content=True, members=True))
statuslist = cycle(
  ['with Python', 'Absolutely Nothing', 'Fun Yo Mama Jokes', 'with your heart ;)', 'definitely 24/7',
   'with fire', 'God', 'amogus', 'with chainsaws', 'the guitar'])


@bot.event
async def on_ready():
  print("Your bot is ready")
  testguild = bot.get_channel(964992479277514832)
  rntime = datetime.now().timestamp()
  await testguild.send(f"**Bot online** as of <t:{int(rntime)}>! :D")
  global ragplas
  ragplas = await bot.fetch_user(367436292276879362)
  change_status.start()


# -------------------- Changes status --------------------
@tasks.loop(seconds=60)
async def change_status():
  await bot.change_presence(activity=discord.Game(next(statuslist)))


# -------------------- Commands --------------------


# -------------------- /purge --------------------

@bot.command(description="Clears a specific amount of messages. Needs MANAGE MESSAGES permission.", pass_context=True)
@has_permissions(manage_messages=True)
async def purge(ctx, limit: discord.Option(int, description="How many messages you want to delete")):
  await ctx.channel.purge(limit=limit + 1)
  await ctx.respond('Cleared by {}'.format(ctx.author.mention), delete_after=3)
  await ctx.message.delete()

# -------------------- /lockdown --------------------
@bot.command(description="Prevents members from talking in channel.")
@commands.has_permissions(manage_channels=True)
async def lockdown(ctx):
  await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
  await ctx.respond(
    ctx.channel.mention + " ***is now in lockdown.*** (Roles that have the [Send Messages] permission in this channel can still talk.)")


# -------------------- /unlock --------------------
@bot.command(description="Unlocks channel")
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
  try:
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.respond(f"<#{ctx.channel.id}> ***has been unlocked.***")
  except:
    await ctx.respond(ctx.channel.mention + "is not locked. Check the channel permissions.")

# -------------------- /setlogs --------------------

@bot.command(description="Set log channel.")
@commands.has_permissions(manage_channels=True)
async def setlogs(ctx):
  with open("logs.json", 'r') as f:
    data = json.load(f)

  data[f"{ctx.guild.id}"] = ctx.channel.id

  with open("logs.json", 'w') as f:
    json.dump(data, f)

  await ctx.respond(f"**{ctx.guild.name}** log channel set to **{ctx.channel.mention}!**")

# -------------------- /food --------------------
@bot.command(description="Hungry? Grab a bite!")
async def food(ctx):
  food = random.choice(foodgifs)
  print(food)

  wordlist = ["Bon appetit!", "Itadakimasu!", "Bone apple tea!", "Enjoy the digital meal!", "Yum!", "Tasty!", "Ooh, looks great!", "Here's your food!", "Enjoy your food!"]
  word = random.choice(wordlist)

  embed = discord.Embed(title=word, color=discord.Color.green())
  embed.set_image(url=food)

  await ctx.respond(embed=embed)

# -------------------- /suggestfood --------------------
@bot.command(description="(/food) Suggest a food gif to the dev.")
async def suggestfood(ctx, suggestion: discord.Option(str, required=True)):
  await ctx.defer()
  print(f"[/suggest food] Food Gif Suggestion: {suggestion} Suggester: {ctx.author}")
  await ragplas.send(f"*FOOD GIF SUGGESTION* | {ctx.author} gave a food gif suggestion: {suggestion}")
  await ctx.followup.send("We sent your food gif suggestion to the dev!")


# -------------------- Anti-raid --------------------


# -------------------- Detects mass channel deletion --------------------
channelsdel = 0


def channeltimer():
  time.sleep(10)
  global channelsdel
  channelsdel = 0


thread = threading.Thread(daemon=True, target=channeltimer)
thread.start()


@bot.event
async def on_guild_channel_delete(channel):
  inguild = channel.guild
  guild = bot.get_guild(channel.guild.id)
  entry = await inguild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1).get()
  pst_time = datetime.now().timestamp()

  embed = discord.Embed(title="Channel Deleted",
                        description="No punishment issued.",
                        color=discord.Color.red())
  embed.add_field(name="User", value=f"<@{entry.user.id}>", inline=True)
  embed.add_field(name="Action", value="Deleted a channel.", inline=True)
  embed.add_field(name="Channel", value=channel.name, inline=True)
  embed.add_field(name="Guild", value=inguild, inline=True)
  embed.add_field(name="Date", value=f"<t:{int(pst_time)}>", inline=True)

  with open("logs.json", 'r') as f:
    data = json.load(f)
  logch = int(data[str(channel.guild.id)])
  logs = bot.get_channel(logch)
  await logs.send(content=f"{entry.user} deleted {channel.name} in {channel.guild}!", embed=embed)
  await ragplas.send(content=f"{entry.user} deleted {channel.name} in {channel.guild}!", embed=embed)

  global channelsdel
  if channelsdel == 3:
    member = entry.user
    membid = guild.get_member(entry.user.id)
    if member != ragplas:

      try:
        for i in membid.roles:
          try:
            await membid.remove_roles(i)
          except:
            print(f"[Antiraid | Channels] Can't remove the role {i}")
        await member.send(
          f"Your roles were taken away in {inguild} because a raid was detected, sorry! *False punishment? Message <@367436292276879362>*")
        punish = "quarantined"

      except:
        print(f"[Antiraid | Channels] Could not find {member}'s roles")
        await member.send(
          f"You were kicked from {inguild} because a raid was detected, sorry! *False punishment? Message <@367436292276879362>*")
        await guild.kick(member, reason="Deleted multiple channels (Anti-raid)")
        punish = "kicked"

      embed = discord.Embed(title="Raid Detected",
                            description=f"Member {punish}.",
                            color=discord.Color.red())
      embed.add_field(name="User", value=f"<@{entry.user.id}>", inline=True)
      embed.add_field(name="Action", value="Deleted a channel.", inline=True)
      embed.add_field(name="Channel", value=channel.name, inline=True)
      embed.add_field(name="Guild", value=inguild, inline=True)
      embed.add_field(name="Date", value=f"<t:{int(pst_time)}>", inline=True)

      with open("logs.json", 'r') as f:
        data = json.load(f)
      logch = int(data[str(channel.guild.id)])
      logs = bot.get_channel(logch)
      await logs.send(content=f"**Raid detected** in {channel.guild}!", embed=embed)
      await ragplas.send(content=f"**Raid detected** in {channel.guild}!", embed=embed)
    channelsdel = 0

  else:
    channelsdel = channelsdel + 1
    print("[Antiraid | Channels] channelsdel:", channelsdel)


# -------------------- Detects @everyone spam --------------------
everyonepings = 0


def everyonetimer():
  time.sleep(10)
  global everyonepings
  everyonepings = 0


thread = threading.Thread(daemon=True, target=everyonetimer)
thread.start()


@bot.listen('on_message')
async def everyoneraid(message):
  mention = f'@everyone'
  if mention in message.content:
    inguild = message.guild
    guild = bot.get_guild(message.guild.id)
    pst_time = datetime.now().timestamp()

    global everyonepings
    if everyonepings == 3:
      member = message.author
      membid = guild.get_member(member)
      if member != ragplas:

        try:
          for i in membid.roles:
            try:
              await membid.remove_roles(i)
            except:
              print(f"[Antiraid | @everyone] Can't remove the role {i}")
          await member.send(
            f"Your roles were taken away in {inguild} because a raid was detected, sorry! *False punishment? Message <@367436292276879362>*")
          punish = "quarantined"
        except:
          print(f"[Antiraid | @everyone] Could not find {member}'s roles")
          await member.send(
            f"You were kicked from {inguild} because a raid was detected, sorry! *False punishment? Message <@367436292276879362>*")
          await guild.kick(member, reason="Spammed @everyone")
          punish = "kicked"

        embed = discord.Embed(title="Raid Detected",
                              description=f"Member {punish}.",
                              color=discord.Color.red())
        embed.add_field(name="User", value=f"<@{member.id}>", inline=True)
        embed.add_field(name="Action", value="Spammed @everyone.", inline=True)
        embed.add_field(name="Guild", value=inguild, inline=True)
        embed.add_field(name="Date", value=f"<t:{int(pst_time)}>", inline=True)

        with open("logs.json", 'r') as f:
          data = json.load(f)
        logch = int(data[str(message.guild.id)])
        logs = bot.get_channel(logch)
        await logs.send(content=f"**Raid detected** in {inguild}!", embed=embed)
        await ragplas.send(content=f"**Raid detected** in {inguild}!", embed=embed)
      everyonepings = 0

    else:
      everyonepings = everyonepings + 1
      print("[Antiraid | @everyone] everyonepings:", everyonepings)  

bot.run("OTc1ODM4NzkyODAxOTkyNzA0.GDDcPL.i-WMsXYJii6kx7iuU-Jn-d7t2z57boe_nsjTR8")    