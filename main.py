import discord  # pycord
from discord import Option
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
from itertools import cycle
import threading
import time
from datetime import datetime, timedelta
from lists import foodgifs, catpics
import random
import json
from dotenv import load_dotenv
import os
#import ffmpeg (for music cmds)

bot = discord.Bot(intents=discord.Intents(guilds=True, messages=True, message_content=True, members=True))


@bot.event
async def on_ready():
  print("Your bot is ready")
  testguild = bot.get_channel(964992479277514832)
  rntime = datetime.now().timestamp()
  await testguild.send(f"**Bot online** as of <t:{int(rntime)}>! :D")
  global ragplas
  ragplas = await bot.fetch_user(367436292276879362)
  await bot.change_presence(activity=discord.Game("/help"))
  #change_status.start()


# -------------------- Changes status --------------------
@tasks.loop(seconds=60)
async def change_status():
  await bot.change_presence(activity=discord.Game(next(statuslist)))


# -------------------- Commands --------------------


# -------------------- /help --------------------

@bot.command(description="Shows all the commands")
async def help(ctx):
  embed = discord.Embed(title="Commands", description="Hey there! Here are my commands.",
                        color=0x0400ff)
  embed.add_field(name="/mute [member] [reason] [duration]", value="Mutes someone for a certain amount of time.", inline=False)
  embed.add_field(name="/unmute [member] [reason]", value="Unmutes someone.", inline=False)
  embed.add_field(name="/kick [member] [reason]", value="Kicks someone.", inline=False)
  embed.add_field(name="/ban [member] [reason]", value="Bans someone.", inline=False)
  embed.add_field(name="/unban", value="Unbans someone.", inline=False)
  embed.add_field(name="/purge [amount]", value="Deletes a specified amount of messages.", inline=False)
  embed.add_field(name="/lockdown", value="Prevents members from talking in channel (All roles with SEND MESSAGES as / or X in the channel will not be able to talk.).", inline=False)
  embed.add_field(name="/unlock", value="Unlocks channel.", inline=False)
  embed.add_field(name="/setlogs", value="Set the logs channel.", inline=False)
  embed.add_field(name="/food", value="Hungry? Grab a bite!", inline=False)
  embed.add_field(name="/cat", value="Get a cat pic!", inline=False)
  embed.add_field(name="/suggestfood [suggestion]", value="Suggest a food gif to the dev.", inline=False)
  embed.add_field(name="/suggestcat [suggestion]", value="Suggest a cat pic to the dev.", inline=False)

  await ctx.send_response(embed=embed)

# -------------------- /mute --------------------

@bot.command(description="Mutes someone for a certain amount of time.", pass_context=True)
@has_permissions(moderate_members=True)
async def mute(ctx, member: Option(discord.Member, description="Who you want to mute", required=True), reason: Option(str, required=False), days: Option(int, required=False), hours: Option(int, required=False), minutes: Option(int, required=False)):
  if member.id == ctx.author.id:
    await ctx.send_response("You can't mute yourself!")
    return
  elif member.guild_permissions.manage_channels and not ctx.author.guild_permissions.manage_channels:
    await ctx.send_response("I think this is a staff member...")
    return  

  check=0
  if reason != None:
    r = f"`{reason}`"
  else:
    r = "`unspecified reason`"
    reason = "unspecified reason"

  if days != None:
    d = f" {days} days,"
  else:
    d = ""
    days = 0
    check = check+1

  if hours != None:
    h = f" {hours} hours"
  else:
    h = ""
    hours = 0
    check = check+1

  if minutes != None:
    m = f" {minutes} minutes"
  else:
    m = ""
    minutes = 0
    check=check+1
  
  if check == 3:
    await ctx.send_response("**Mute unsuccessful!** Did you put in a duration?")
    check=0
    return
  
  check=0
  duration = timedelta(days=days, hours=hours, minutes=minutes)
  try:
    await member.timeout_for(duration, reason=reason)
  except:
    await ctx.send_response("I could not mute this member!")
    return
  embed = discord.Embed(title="Member Muted", color=discord.Color.red(), timestamp=datetime.utcnow())
  embed.add_field(name="Member", value=f"{member.mention}", inline=True)
  embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=True)
  embed.add_field(name="Duration", value=f"{d}{h}{m}", inline=True)
  embed.add_field(name="Reason", value=f"{reason}", inline=True)

  with open("logs.json", 'r') as f:
    data = json.load(f)
  logch = int(data[str(ctx.guild.id)])
  print(logch)
  logs = bot.get_channel(logch)
  await logs.send(content=f"**Member muted** in <#{ctx.channel.id}> !", embed=embed)

  await ctx.send_response(f"{member.mention} has been timed out for**{d}{h}{m}** for **{r}.**")

# -------------------- /unmute --------------------

@bot.command(description="Unmutes someone.", pass_context=True)
@has_permissions(moderate_members=True)
async def unmute(ctx, member: Option(discord.Member, description="Who you want to unmute", required=True), reason: Option(str, required=False)):
  try:
    await member.remove_timeout(reason=reason)
  except:
    await ctx.send_response("I could not unmute this member!")
    return
  if reason == None:
    reason="unspecified reason"
  embed = discord.Embed(title="Member Unuted", color=discord.Color.green(), timestamp=datetime.utcnow())
  embed.add_field(name="Member", value=f"{member.mention}", inline=True)
  embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=True)
  embed.add_field(name="Reason", value=f"{reason}", inline=True)

  with open("logs.json", 'r') as f:
    data = json.load(f)
  logch = int(data[str(ctx.guild.id)])
  print(logch)
  logs = bot.get_channel(logch)
  await logs.send(content=f"**Member unmuted** in <#{ctx.channel.id}> !", embed=embed)

  await ctx.send_response(f"{member.mention} has been unmuted for **{reason}.**")

# -------------------- /kick --------------------

@bot.command(description="Kicks someone.", pass_context=True)
@has_permissions(kick_members=True)
async def kick(ctx, member: Option(discord.Member, description="Who you want to kick", required=True), reason: Option(str, required=False)):
  if member.id == ctx.author.id:
    await ctx.send_response("You can't kick yourself!")
    return
  if member.guild_permissions.manage_channels and not ctx.author.guild_permissions.manage_channels:
    await ctx.send_response("I think this is a staff member...")
    return
  if reason==None:
    reason="unspecified reason"

  try:
    await member.kick(reason=reason)
  except:
    await ctx.send_response("I could not kick this member!")  
    return

  embed = discord.Embed(title="Member Kicked", color=discord.Color.red(), timestamp=datetime.utcnow())
  embed.add_field(name="Member", value=f"{member.mention}", inline=True)
  embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=True)
  embed.add_field(name="Reason", value=f"{reason}", inline=True)


  with open("logs.json", 'r') as f:
    data = json.load(f)
  logch = int(data[str(ctx.guild.id)])
  logs = bot.get_channel(logch)
  await logs.send(content=f"**Member kicked** in <#{ctx.channel.id}> !", embed=embed)

  await ctx.send_response(f"{member.mention} has been **kicked** for `{reason}`!")
  
# -------------------- /ban --------------------

@bot.command(description="Bans someone.", pass_context=True)
@has_permissions(ban_members=True)
async def ban(ctx, member: Option(discord.Member, description="Who you want to ban", required=True)):
  if member.id == ctx.author.id:
    await ctx.send_response("You can't ban yourself!")
    return
  if member.guild_permissions.manage_channels and not ctx.author.guild_permissions.manage_channels:
    await ctx.send_response("I think this is a staff member...")
    return
  if reason==None:
    reason="unspecified reason"

  try:
    await member.ban(reason=reason)
  except:
    await ctx.send_response("I could not ban this member!")
    return  

  embed = discord.Embed(title="Member Banned", color=discord.Color.red(), timestamp=datetime.utcnow())
  embed.add_field(name="Member", value=f"{member.mention}", inline=True)
  embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=True)
  embed.add_field(name="Reason", value=f"{reason}", inline=True)


  with open("logs.json", 'r') as f:
    data = json.load(f)
  logch = int(data[str(ctx.guild.id)])
  logs = bot.get_channel(logch)
  await logs.send(content=f"**Member banned** in <#{ctx.channel.id}> !", embed=embed)

  await ctx.send_response(f"{member.mention} has been **banned** for `{reason}`!")

# -------------------- /unban --------------------

@bot.command(description="Unmutes someone.", pass_context=True)
@has_permissions(moderate_members=True)
async def unban(ctx, member: Option(discord.Member, description="Who you want to unmute", required=True), reason: Option(str, required=False)):
  try:
    await member.unban(reason=reason)
  except:
    await ctx.send_response("I could not unban this member!")
    return
  if reason == None:
    reason="unspecified reason"
  embed = discord.Embed(title="Member Unbanned", color=discord.Color.green(), timestamp=datetime.utcnow())
  embed.add_field(name="Member", value=f"{member.mention}", inline=True)
  embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=True)
  embed.add_field(name="Reason", value=f"{reason}", inline=True)

  with open("logs.json", 'r') as f:
    data = json.load(f)
  logch = int(data[str(ctx.guild.id)])
  print(logch)
  logs = bot.get_channel(logch)
  await logs.send(content=f"**Member unbanned** in <#{ctx.channel.id}> !", embed=embed)

  await ctx.send_response(f"{member.mention} has been unbanned for **{reason}.**")

# -------------------- /purge --------------------

@bot.command(description="Clears a specific amount of messages. Needs MANAGE MESSAGES permission.", pass_context=True)
@has_permissions(manage_messages=True)
async def purge(ctx, limit: Option(int, description="How many messages you want to delete")):
  await ctx.channel.purge(limit=limit + 1)
  await ctx.send_response('Cleared by {}'.format(ctx.author.mention), delete_after=3)
  await ctx.message.delete()

# -------------------- /lockdown --------------------
@bot.command(description="Prevents members from talking in channel.")
@commands.has_permissions(manage_channels=True)
async def lockdown(ctx):
  await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)

  embed = discord.Embed(title="Channel Locked", color=discord.Color.red(), timestamp=datetime.utcnow())
  embed.add_field(name="Channel", value=f"{ctx.channel.mention}", inline=True)
  embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=True)


  with open("logs.json", 'r') as f:
    data = json.load(f)
  logch = int(data[str(ctx.guild.id)])
  logs = bot.get_channel(logch)
  await logs.send(content=f"<#{ctx.channel.id}> was locked!", embed=embed)

  await ctx.send_response(
    ctx.channel.mention + " ***is now in lockdown.*** (Roles that have the [Send Messages] permission in this channel can still talk.)")

# -------------------- /unlock --------------------
@bot.command(description="Unlocks channel")
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
  try:
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)

    embed = discord.Embed(title="Channel Unlocked", color=discord.Color.green(), timestamp=datetime.utcnow())
    embed.add_field(name="Channel", value=f"{ctx.channel.mention}", inline=True)
    embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=True)

    with open("logs.json", 'r') as f:
      data = json.load(f)
    logch = int(data[str(ctx.guild.id)])
    logs = bot.get_channel(logch)
    await logs.send(content=f"<#{ctx.channel.id}> was unlocked!", embed=embed)
    await ctx.send_response(f"<#{ctx.channel.id}> ***has been unlocked.***")
  except:
    await ctx.send_response(ctx.channel.mention + "is not locked. Check the channel permissions.")

# -------------------- /setlogs --------------------

@bot.command(description="Set log channel.")
@commands.has_permissions(manage_channels=True)
async def setlogs(ctx):
  with open("logs.json", 'r') as f:
    data = json.load(f)

  data[f"{ctx.guild.id}"] = ctx.channel.id

  with open("logs.json", 'w') as f:
    json.dump(data, f)

  await ctx.send_response(f"**{ctx.guild.name}** log channel set to **{ctx.channel.mention}!**")

# -------------------- /food --------------------
@bot.command(description="Hungry? Grab a bite!")
async def food(ctx):
  food = random.choice(foodgifs)

  wordlist = ["Bon appetit!", "Itadakimasu!", "Bone apple tea!", "Enjoy the digital meal!", "Yum!", "Tasty!", "Ooh, looks great!", "Here's your food!", "Enjoy your food!"]
  word = random.choice(wordlist)

  embed = discord.Embed(title=word, color=discord.Color.green())
  embed.set_image(url=food)

  await ctx.send_response(embed=embed)

# -------------------- /cat --------------------
@bot.command(description="Get a cat pic!")
async def cat(ctx):
  gato = random.choice(catpics)

  embed = discord.Embed(title="Cat!", color=discord.Color.purple())
  embed.set_image(url=gato)

  await ctx.send_response(embed=embed)

# -------------------- /suggestfood --------------------
@bot.command(description="(/food) Suggest a food gif to the developer.")
async def suggestfood(ctx, suggestion: Option(str, required=True)):
  await ctx.defer()
  await ragplas.send(f"*FOOD GIF SUGGESTION* | {ctx.author} gave a food gif suggestion: {suggestion}")
  await ctx.send_followup("We sent your food gif suggestion to the dev!")

# -------------------- /suggestcats --------------------
@bot.command(description="(/cat) Suggest a cat pic to the developer.")
async def suggestcat(ctx, suggestion: Option(str, required=True)):
  await ctx.defer()
  await ragplas.send(f"*CAT PIC SUGGESTION* | {ctx.author} gave a cat pic suggestion: {suggestion}")
  await ctx.send_followup("We sent your cat pic suggestion to the dev!")

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
  embed.add_field(name="User", value=f"{entry.user.mention}", inline=True)
  embed.add_field(name="Action", value="Deleted a channel.", inline=True)
  embed.add_field(name="Channel", value=channel.name, inline=True)
  embed.add_field(name="Guild", value=inguild, inline=True)
  embed.add_field(name="Date", value=f"<t:{int(pst_time)}>", inline=True)

  with open("logs.json", 'r') as f:
    data = json.load(f)
  logch = int(data[str(channel.guild.id)])
  logs = bot.get_channel(logch)
  await logs.send(content=f"{entry.user} deleted {channel.name} in {channel.guild}!", embed=embed)

  global channelsdel
  if channelsdel == 5:
    member = entry.user
    membid = guild.get_member(entry.user.id)
    try:
      for i in membid.roles:
        try:
          await membid.remove_roles(i)
        except:
          print(f"[Antiraid | Channels] Can't remove the role {i}")
      await member.send(
        f"Your roles were taken away in {inguild} because a raid was detected!")
      punish = "quarantined"

    except:
      print(f"[Antiraid | Channels] Could not find {member}'s roles")
      await member.send(
        f"You were kicked from {inguild} because a raid was detected!")
      await guild.kick(member, reason="Deleted multiple channels (Anti-raid)")
      punish = "kicked"

    embed = discord.Embed(title="Raid Detected",
                          description=f"Member {punish}.",
                          color=discord.Color.red())
    embed.add_field(name="User", value=f"{entry.user.mention}", inline=True)
    embed.add_field(name="Action", value="Deleted a channel.", inline=True)
    embed.add_field(name="Channel", value=channel.name, inline=True)
    embed.add_field(name="Guild", value=inguild, inline=True)
    embed.add_field(name="Date", value=f"<t:{int(pst_time)}>", inline=True)

    with open("logs.json", 'r') as f:
      data = json.load(f)
    logch = int(data[str(channel.guild.id)])
    logs = bot.get_channel(logch)
    await logs.send(content=f"**Raid detected** in {channel.guild}!", embed=embed)
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
    if everyonepings == 5:
      member = message.author
      membid = guild.get_member(member)

      try:
        for i in membid.roles:
          try:
            await membid.remove_roles(i)
          except:
            print(f"[Antiraid | @everyone] Can't remove the role {i}")
        await member.send(
          f"Your roles were taken away in {inguild} because a raid was detected!")
        punish = "quarantined"
      except:
        print(f"[Antiraid | @everyone] Could not find {member}'s roles")
        await member.send(
          f"You were kicked from {inguild} because a raid was detected!")
        await guild.kick(member, reason="Spammed @everyone")
        punish = "kicked"

      embed = discord.Embed(title="Raid Detected",
                            description=f"Member {punish}.",
                            color=discord.Color.red())
      embed.add_field(name="User", value=f"{member.mention}", inline=True)
      embed.add_field(name="Action", value="Spammed @everyone.", inline=True)
      embed.add_field(name="Guild", value=inguild, inline=True)
      embed.add_field(name="Date", value=f"<t:{int(pst_time)}>", inline=True)

      with open("logs.json", 'r') as f:
        data = json.load(f)
      logch = int(data[str(message.guild.id)])
      logs = bot.get_channel(logch)
      await logs.send(content=f"**Raid detected** in {inguild}!", embed=embed)
      everyonepings = 0

    else:
      everyonepings = everyonepings + 1
      print("[Antiraid | @everyone] everyonepings:", everyonepings)  

load_dotenv()
bot.run(os.environ["token"])    