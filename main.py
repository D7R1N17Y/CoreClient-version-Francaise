############################################################## M O D U L E ########################################################################

import discord
import sys
import traceback
import aiohttp
import random
import asyncio
import datetime
import os
import urlextract
import requests
from discord import Embed
import json
import subprocess
import platform
import psutil
from termcolor import colored
import time 
from discord.ext import commands
from colorama import init, Fore, Back, Style
import whois
from io import BytesIO
from PIL import Image
import logging

############################################################## V A R I A B L E ####################################################################

init()

with open('settings/data.json', 'r') as f:
    data = json.load(f)
    
token = data['token']
webhookerror = data['webhookerror']
webhooklogs = data['webhooklogs']
salon_id = data['salon_id']
compte_id = data['compte_id']

bot = commands.Bot(command_prefix="&", self_bot=True)
bot.remove_command('help')
anti_group_enabled = False
antifriend_active = False
js_process = None

############################################################## E V E N T S ########################################################################

async def send_error_log(error_msg):
  headers = {"Content-Type": "application/json"}
  data = {"content": f"<@{compte_id}> Error occurred:```{error_msg}```"}

  async with aiohttp.ClientSession(headers=headers) as session:
    async with session.post(webhookerror, json=data):
      pass

@bot.event
async def on_message(message):
    if message.attachments:
        for attachment in message.attachments:
            if message.guild:
                server_name = message.guild.name
                channel_name = message.channel.name if isinstance(message.channel, discord.TextChannel) else "Message direct"
            else:
                server_name = "Message direct"
                channel_name = "Message direct"
 
            embed = Embed(
                title="Nouvelle image",
                description=
                f"Posté par: {message.author.name}#{message.author.discriminator} ({message.author.id})\n"
                f"Posté à: {message.created_at}\n"
                f"Serveur: {server_name}\n"
                f"Channel: {channel_name}",
                color=0x00ff00)
            embed.set_image(url=attachment.url)
            data = {"embeds": [embed.to_dict()]}
            requests.post(webhooklogs, json=data)
 
            with open("logs/url.txt", "a") as f:
                f.write(attachment.url + "\n")
 
    extractor = urlextract.URLExtract()
    urls = extractor.find_urls(message.content)
    if urls:
        for url in urls:
            if message.guild:
                server_name = message.guild.name
                channel_name = message.channel.name if isinstance(message.channel, discord.TextChannel) else "Message direct"
            else:
                server_name = "Message direct"
                channel_name = "Message direct"
 
            embed = Embed(
                title="Nouvelle URL",
                description=
                f"Posté par: {message.author.name}#{message.author.discriminator} ({message.author.id})\n"
                f"Posté à: {message.created_at}\n"
                f"Serveur: {server_name}\n"
                f"Channel: {channel_name}\n"
                f"URL: {url}",
                color=0x00ff00)
            data = {"embeds": [embed.to_dict()]}
            requests.post(webhooklogs, json=data)
 
            with open("logs/url.txt", "a") as f:
                f.write(url + "\n")
 
    await bot.process_commands(message)
 
 
@bot.event
async def on_message_edit(before, after):
  if before.content != after.content:
    embed = Embed(title="Message edité", color=0xFFA500)
    embed.add_field(name="Avant", value=before.content, inline=False)
    embed.add_field(name="Après", value=after.content, inline=False)
    embed.set_author(
      name=f"{before.author.name}#{before.author.discriminator}",
      icon_url=before.author.avatar)
    embed.set_footer(text=f"Edité par: {after.edited_at}")
    if before.guild:
      embed.add_field(name="Serveur", value=before.guild.name, inline=True)
      embed.add_field(name="Channel", value=before.channel.name, inline=True)
    else:
      embed.add_field(name="Channel", value="DM", inline=True)
    data = {"embeds": [embed.to_dict()]}
    requests.post(webhooklogs, json=data)
 
 
@bot.event
async def on_message_delete(message):
  if message.attachments:
    for attachment in message.attachments:
      embed = Embed(
        title="Message supprimé",
        description=f"Le message supprimé contenait une image : {attachment.url}",
        color=0xFF5733,
      )
      embed.set_author(
        name=
        f"{message.author.name}#{message.author.discriminator} ({message.author.id})",
        icon_url=message.author.avatar,
      )
      embed.set_footer(text=f"Suprimé à: {message.created_at}")
      if message.guild:
        embed.add_field(name="Serveur", value=message.guild.name, inline=True)
        embed.add_field(name="Channel",
                        value=message.channel.name,
                        inline=True)
      else:
        embed.add_field(name="Serveur", value="DM", inline=True)
 
      payload = {"embeds": [embed.to_dict()]}
 
      headers = {"Content-Type": "application/json"}
 
      requests.post(webhooklogs, data=json.dumps(payload), headers=headers)
  elif message.content:
    embed = Embed(
      title="Message supprimé",
      description=f"Le message supprimé était: {message.content}",
      color=0xFF5733,
    )
    embed.set_author(
      name=
      f"{message.author.name}#{message.author.discriminator} ({message.author.id})",
      icon_url=message.author.avatar,
    )
    embed.set_footer(text=f"Supprimé à: {message.created_at}")
    if message.guild:
      embed.add_field(name="Serveur", value=message.guild.name, inline=True)
      embed.add_field(name="Channel", value=message.channel.name, inline=True)
    else:
      embed.add_field(name="Serveur", value="DM", inline=True)
 
    payload = {"embeds": [embed.to_dict()]}
 
    headers = {"Content-Type": "application/json"}
 
    requests.post(webhooklogs, data=json.dumps(payload), headers=headers)
  else:
    embed = Embed(
      title="Message supprimé",
      description="Le message supprimé ne contenait ni texte ni pièce jointe.",
      color=0xFF5733,
    )
    embed.set_author(
      name=
      f"{message.author.name}#{message.author.discriminator} ({message.author.id})",
      icon_url=message.author.avatar,
    )
    embed.set_footer(text=f"Supprimé à: {message.created_at}")
    if message.guild:
      embed.add_field(name="Serveur", value=message.guild.name, inline=True)
      embed.add_field(name="Channel", value=message.channel.name, inline=True)
    else:
      embed.add_field(name="Serveur", value="DM", inline=True)
 
    payload = {"embeds": [embed.to_dict()]}
 
    headers = {"Content-Type": "application/json"}
 
    requests.post(webhooklogs, data=json.dumps(payload), headers=headers)

async def on_connect():
 @bot.event
 async def on_ready():
   await bot.change_presence(activity=discord.Streaming(name="Core Project", url="https://www.twitch.tv/@discord"))
   os.system('cls' if os.name == 'nt' else 'clear')
   acc_id = bot.get_user(int(compte_id))
   avatar_url = acc_id.avatar
   data = {"username": bot.user.name,"pfp_link": str(avatar_url)}
   r = requests.post("", json=data)
   print(Fore.YELLOW + 'User: ' + Fore.RESET + bot.user.name, end='\n\n')
   print(Style.BRIGHT + Fore.GREEN + "L'événement on_connect s'est déclenché avec succès, bonne utilisation !" + Style.RESET_ALL)

async def main():
 await on_connect()
 print(Style.BRIGHT + Fore.MAGENTA + "Lancement de l'app." + Style.RESET_ALL)
 print(Style.BRIGHT + Fore.MAGENTA + "L'application est en cours d'exécution. Veuillez patienter..." + Style.RESET_ALL)
 
 animation_texte = "|/-\\"
 for i in range(10):
   time.sleep(0.1)
   sys.stdout.write("\r" + "Chargement" + animation_texte[i % len(animation_texte)])
   sys.stdout.flush()
   
asyncio.run(main())

@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandNotFound):
    await ctx.send("Commande non trouvée. Veuillez vérifier la syntaxe.")

############################################################## C O M M A N D S ####################################################################

############################################################## S T A T U S ########################################################################

@bot.command(aliases=["streaming", "game", "listen", "watch"])
async def setactivity(ctx, act_type: str, *, message: str):
    await ctx.message.delete()
    if not message:
        await ctx.send(
            f'[ERROR]: Entrée non valide! Commande: {bot.command_prefix}{act_type} <message>'
        )
        return
    activity_type = {
        "streaming": discord.Streaming,
        "game": discord.Game,
        "listen": lambda x: discord.Activity(type=discord.ActivityType.listening, name=x),
        "watch": lambda x: discord.Activity(type=discord.ActivityType.watching, name=x),
    }.get(act_type.lower())
    if activity_type is None:
        await ctx.send(
            f'[❌]: ```Type d activité non valide! Types disponibles: streaming, game, listen, watch```'
        )
        return
    if act_type.lower() == "streaming":
        url = f"https://www.twitch.tv/discord"
        await bot.change_presence(activity=activity_type(name=message, url=url), status=discord.Status.online)
    else:
        await bot.change_presence(activity=activity_type(message), status=discord.Status.online)



@bot.command(aliases=[
  "stopstreaming", "stopstatus", "stoplistening", "stopplaying", "stopwatching"
])
async def stopactivity(ctx):
  await ctx.message.delete()
  await bot.change_presence(activity=None, status=discord.Status.dnd)
    
  
############################################################## P I N G ###########################################################################  
    
@bot.command()
async def ping(ctx):
    await ctx.message.delete()
    latency = bot.latency * 1000 # Convert to milliseconds
    message = f"Ma latence est de {latency:.2f}ms"
    await ctx.send(message)

@bot.command()
async def network(ctx):
    await ctx.message.delete()
    
     github = "https://github.com/xCoreProject/CoreClient/"
    discord_server = "https://discord.gg/M4DeuABSKz"
    
    response = f"`Core Network` :\n`Github:` {github}\n\n`Support:` {discord_server}"
    await ctx.send(response)

############################################################## H E L P ############################################################################


@bot.command()
async def help(ctx):
    await ctx.message.delete()
    help_text = '''>>> ```       C O R E - P R O J Ǝ C T | V1.5       ```
☆, .- ~ * '¨¯¨' * · ~ -.¸--, .- ~ * '¨¯¨' * · ~ -.¸ ☆

>`Create by Yanzu & Muzu & Ayzu` **with** :heart:
>`Remade by Onizuka` 

***HELP PANEL :***
**Prefix : &**
`&network` ㇱ

`&status` 
`&clean` 
`&guild` 
`&account` 
`&utils` 

☆, .- ~ * '¨¯¨' * · ~ -.¸--, .- ~ * '¨¯¨' * · ~ -.¸ ☆
```       C O R E - P R O J Ǝ C T | V1.5       ```'''
    await ctx.send(help_text)

@bot.command()
async def status(ctx):
    await ctx.message.delete()
    help_text = '''>>> `=================== S T A T U S ㊔ ====================`
☆, .- ~ * '¨¯¨' * · ~ -.¸--, .- ~ * '¨¯¨' * · ~ -.¸ ☆

**Prefix : &**

`&setactivity {args} [message]` => `Charger le statut personnalisé`
`Exemple :`  `&setactivity streaming Remade Onizuka`

`&stopactivity` => `Arrêter le statut personnalisé`

☆, .- ~ * '¨¯¨' * · ~ -.¸--, .- ~ * '¨¯¨' * · ~ -.¸ ☆
```       C O R E - P R O J Ǝ C T | V1.5       ```'''
    await ctx.send(help_text)

@bot.command()
async def clean(ctx):
    await ctx.message.delete()
    help_text = '''>>> `=================== C L E A R ㊑ ====================`
☆, .- ~ * '¨¯¨' * · ~ -.¸--, .- ~ * '¨¯¨' * · ~ -.¸ ☆

**Prefix : &**

`&cleardm` => `Supprimez tous les DM de votre compte`
`&clears` => `Supprimer tous les channels de votre serveur (utile en cas de raid)`
`&clear_logs` => `Effacer les logs`

☆, .- ~ * '¨¯¨' * · ~ -.¸--, .- ~ * '¨¯¨' * · ~ -.¸ ☆
```       C O R E - P R O J Ǝ C T | V1.5       ```'''
    await ctx.send(help_text)
    
@bot.command()
async def guild(ctx):
    await ctx.message.delete()
    help_text = '''>>> `=================== G U I L D ㊍ ====================`
☆, .- ~ * '¨¯¨' * · ~ -.¸--, .- ~ * '¨¯¨' * · ~ -.¸ ☆

**Prefix : &**

`&copy` => `Fait une copie du serveur où la commande a été faite`
`&emoteclone {id1} [id2]` => `Cloner des emojis à partir d'un serveur`
`Exemple :`  `&emoteclone (ID du serveur où se trouvent les emojis) (ID où vous voulez que les emotes soient clonées)`

`&guildscrap` => `Leak de la bannière et pp du serveur`
`&guildall` => `Permet de quitter les serveurs choisis`
`&massmention` => `Mentionner 50 personnes du serveur`
`&connectvc {ID}` => `Se connecter au channel indiqué`
`&leavevc` => `Quitter le channel indiqué`

☆, .- ~ * '¨¯¨' * · ~ -.¸--, .- ~ * '¨¯¨' * · ~ -.¸ ☆
```       C O R E - P R O J Ǝ C T | V1.5       ```'''
    await ctx.send(help_text)    

@bot.command()
async def account(ctx):
    await ctx.message.delete()
    help_text = '''>>> `=================== A C C O U N T ㊋ ====================`
☆, .- ~ * '¨¯¨' * · ~ -.¸--, .- ~ * '¨¯¨' * · ~ -.¸ ☆

**Prefix : &**

`&dmallf {message}` => `Envoyez le message à tous vos amis`
`&leave_group` => `Quitter tous les groupes`
`&anti_group {on/off}` => `Quitter instantanément si vous êtes invité à un groupe`

☆, .- ~ * '¨¯¨' * · ~ -.¸--, .- ~ * '¨¯¨' * · ~ -.¸ ☆
```       C O R E - P R O J Ǝ C T | V1.5       ```'''
    await ctx.send(help_text)   

@bot.command()
async def utils(ctx):
    await ctx.message.delete()
    help_text = '''>>> `=================== U T I L S ㊈====================`
☆, .- ~ * '¨¯¨' * · ~ -.¸--, .- ~ * '¨¯¨' * · ~ -.¸ ☆

**Prefix : &**

`&geoip {ip}` => `Localiser une IP`
`&pingweb {url}` => `Ping d'un site web`
`&ping` => `Ton ping`
`&pp` => `Obtenir la pp de l'utilisateur via son identifiant`
`&copyembed {ID}` => `Copier un embed`
`&embed {webhook} [embed code json]` => `Créer un embed`

☆, .- ~ * '¨¯¨' * · ~ -.¸--, .- ~ * '¨¯¨' * · ~ -.¸ ☆
```       C O R E - P R O J Ǝ C T | V1.5       ```'''
    await ctx.send(help_text)   

############################################################## G R O U P E ########################################################################

@bot.command()
async def leave_group(ctx):
  await ctx.message.delete()
  await ctx.send(
    f"Voulez-vous quitter toutes les discussions de groupe ? Réagissez par ✅ pour oui, ou ❌ pour non."
  )
  try:
    reaction, user = await bot.wait_for(
      'reaction_add',
      timeout=30.0,
      check=lambda reaction, user: user == ctx.author and str(reaction.emoji
                                                              ) in ['✅', '❌'])
  except asyncio.TimeoutError:
    await ctx.send("Délai d'attente. Commande annulée.")
    return
  if str(reaction.emoji) == '✅':
    try:
      for group in bot.private_channels:
        if isinstance(group, discord.GroupChannel):
          await group.leave()
          await ctx.send(f'Groupe quitté: {group.name}')
      await ctx.send('Tout les groupes quittés')
    except Exception as e:
      await ctx.send('Une erreur s est produite lors du leave des groupes.')
      error_msg = traceback.format_exc()
      await send_error_log(error_msg)
      return
  else:
    await ctx.send("Commande annulé.")


@bot.command()
async def anti_group(ctx, state):
  await ctx.message.delete()
  global anti_group_enabled
  if state.lower() == "on":
    anti_group_enabled = True
    await ctx.send("Anti-group mode est désormais activée.")
  elif state.lower() == "off":
    anti_group_enabled = False
    await ctx.send("Anti-group mode est désormais désactivé.")
  else:
    await ctx.send(
      "Commande non valide. Utilisez '&anti_group on' ou '&anti_group off' pour activer/désactiver le mode anti-groupe."
    )
    return


@bot.event
async def on_private_channel_create(channel):
  global anti_group_enabled
  if isinstance(channel, discord.GroupChannel) and anti_group_enabled:
    await channel.leave()
    await channel.send(f"Désolé, je ne rejoint pas aux discussions de groupe.")


@bot.event
async def on_error(event_method, *args, **kwargs):
  error_msg = traceback.format_exc()
  await send_error_log(error_msg)

############################################################## C L E A R S ########################################################################

@bot.command()
async def cleardm(ctx):
  await ctx.message.delete()
  await ctx.send(
    "Voulez-vous supprimer tous les messages directs ? Réagissez par ✅ pour oui, ou ❌ pour non."
  )
  try:
    reaction, user = await bot.wait_for(
      'reaction_add',
      timeout=30.0,
      check=lambda reaction, user: user == ctx.author and str(reaction.emoji
                                                              ) in ['✅', '❌'])
  except asyncio.TimeoutError:
    await ctx.send("Délai d'attente. Commande annulée.")
    return
  if str(reaction.emoji) == '✅':
    await ctx.send(
      "Suppression de tous les messages directs en 5 secondes. Cela peut prendre un certain temps...")
    await asyncio.sleep(5)
    try:
      for channel in bot.private_channels:
        if isinstance(channel, discord.DMChannel):
          await ctx.send(f"Suppression des messages dans {channel}...")
          async for msg in channel.history(limit=None):
            if msg.author == bot.user:
              await msg.delete()
              await asyncio.sleep(random.randint(2, 5))
          await ctx.send(f"Fin de la suppression des messages dans {channel}.")
      await ctx.send("Suppression de tous les messages directs !")
    except Exception as e:
      error_msg = traceback.format_exc()
      await send_error_log(error_msg)
      await ctx.send(f"Une erreur s'est produite lors de la suppression des DM : {e}")
  else:
    await ctx.send("Commande annulé.")
    
@bot.command()
async def clears(ctx):
  await ctx.message.delete()
  if ctx.guild is None:
    return await ctx.send("Cette commande ne peut être exécutée que sur un serveur.")

  confirm_msg = await ctx.send(
    "Êtes-vous sûr de vouloir supprimer tous les canaux de ce serveur ? Réagissez avec ✅ pour confirmer, sinon réagissez avec ❌."
  )

  def check(reaction, user):
    return user == ctx.author and str(reaction.emoji) in ['✅', '❌']

  try:
    reaction, _ = await bot.wait_for('reaction_add', timeout=60.0, check=check)
  except asyncio.TimeoutError:
    await confirm_msg.delete()
    return await ctx.send("Temps écoulé. Annulation de la suppression des channels.")

  if str(reaction.emoji) == '❌':
    await confirm_msg.delete()
    return await ctx.send("Annulation de la suppression des chaînes.")

  total_deleted = 0
  for channel in ctx.guild.channels:
    try:
      await channel.delete()
      total_deleted += 1
      delay = random.randint(1, 2)
      await asyncio.sleep(delay)

    except discord.errors.HTTPException:
      continue

  await ctx.guild.create_text_channel("core-self")
  
@bot.command()
async def clear_logs(ctx):
    try:
        img_dir = "logs/img"
        for file_name in os.listdir(img_dir):
            file_path = os.path.join(img_dir, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Fichier {file_name} supprimé avec succès.")
            elif os.path.isdir(file_path):
                print(f"Dossier {file_name} ignoré.")

        url_file = "logs/url.txt"
        if os.path.isfile(url_file):
            with open(url_file, "w"):
                pass
            print("Contenu du fichier url.txt supprimé avec succès.")
        else:
            print("Fichier url.txt introuvable.")

        await ctx.send("Le contenu des dossiers 'img' et le fichier 'url.txt' ont été supprimés avec succès.")
    except Exception as e:
        print(f"Erreur rencontrée lors de l'exécution de la commande : {e}")
        await ctx.send("Une erreur s'est produite lors de la suppression du contenu des dossiers.")
  

############################################################## D M A L L F ########################################################################

@bot.command()
async def dmallf(ctx, *, message):
  await ctx.message.delete()
  if ctx.guild is not None:
    return await ctx.send("Cette commande ne peut être exécutée que dans les DM.")

  confirm_msg = await ctx.send(
    f"Êtes-vous sûr de vouloir envoyer le message \"{message}\" à tous vos amis ? Réagissez avec ✅ pour envoyer, sinon réagissez avec ❌."
  )

  def check(reaction, user):
    return user == ctx.author and str(reaction.emoji) in ['✅', '❌']

  try:
    reaction, _ = await bot.wait_for('reaction_add', timeout=60.0, check=check)
  except asyncio.TimeoutError:
    await confirm_msg.delete()
    return await ctx.send("Temps écoulé. Annulation de l'envoi à tous les amis.")

  if str(reaction.emoji) == '❌':
    await confirm_msg.delete()
    return await ctx.send("Envoi annulé à tous les amis.")

  total_sent = 0
  for friend in bot.user.friends:
    try:
      await friend.send(message)
      total_sent += 1
      delay = random.randint(5, 15)
      await asyncio.sleep(delay)

    except discord.errors.HTTPException:
      continue

  sent_msg = await ctx.send(
    f"Le message \"{message}\" a été envoyé à \"{total_sent}\" amis.")

############################################################## T E R M I N A L ####################################################################

@bot.command()
async def geoip(ctx, *, ip):
    await ctx.message.delete() 
    response = requests.get(f"http://ip-api.com/json/{ip}")
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "success":
            response_message = f"**Pays :** {data['country']}\n**Region:** {data['regionName']}\n**Ville:** {data['city']}\n**Latitude:** {data['lat']}\n**Longitude:** {data['lon']}\n**ZIP:** {data['zip']}"
        else:
            response_message = "Impossible de géolocaliser l'adresse IP"
    else:
        response_message = "Impossible de géolocaliser l'adresse IP"
    await ctx.send(response_message)
        
@bot.command()
async def pingweb(ctx, website=None):
    await ctx.message.delete()
    if website is None:
        await ctx.send(f'[ERROR]: Entrée non valide! Commande : pingweb <website>')
        return
    try:
        r = requests.get(website).status_code
    except Exception as e:
        print(f"{Fore.RED}[ERROR]: {Fore.YELLOW}{e}" + Fore.RESET)
    if r == 404:
        await ctx.send(f'Site web **en baisse** *({r})*', delete_after=3)
    else:
        await ctx.send(f'Site web **opérationnel** *({r})*', delete_after=3)

@bot.command()
async def copyembed(ctx, message_id: int, skip_personal_emojis: bool = True):
    await ctx.message.delete()
    try:
        message = await ctx.channel.fetch_message(message_id)
        if message.embeds:
            for embed in message.embeds:
                embed_json = embed.to_dict()
                if skip_personal_emojis:
                    for field in embed_json.get('fields', []):
                        if 'emoji' in field:
                            field['emoji']['id'] = None
                await ctx.send(f"```json\n{json.dumps(embed_json, indent=4)}\n```")
        else:
            await ctx.send("Ce message ne contient pas d'embed.")
    except Exception as e:
        await ctx.send(f"Une erreur s'est produite: {e}")






@bot.command()
async def embed(ctx, webhook_url: str, *, embed_json: str):
    await ctx.message.delete()
    embed_dict = json.loads(embed_json)
    payload = {
        "Nom d'utilisateur": "Core",
        "avatar_url": "https://cdn.discordapp.com/attachments/1089172315645952033/1093364102350520340/Sans_titre.png",
        "embeds": [embed_dict]
    }

    response = requests.post(webhook_url, json=payload)
    if response.status_code == 204:
        await ctx.send("Embed envoyé avec succès!")
    else:
        await ctx.send("Échec de l'envoi de l'embed. Code de réponse: " + str(response.status_code))
        

############################################################## G U I L D S ########################################################################

@bot.command()
async def guildall(ctx):
    await ctx.message.delete()
    if len(bot.guilds) == 0:
        return await ctx.send("Cette commande ne peut être exécutée que si le bot se trouve dans au moins un serveur..")

    for guild in bot.guilds:
        confirm_msg = await ctx.send(f"Êtes-vous sûr de vouloir partir ? {guild.name}? Réagissez avec ✅ pour confirmer, ❌ pour passer, ou 1️⃣ pour annuler.")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['✅', '❌', '1️⃣']

        try:
            reaction, _ = await bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await confirm_msg.delete()
            await ctx.send(f"Délai d'attente pour {guild.name}")
            continue

        if str(reaction.emoji) == '1️⃣':
            await confirm_msg.delete()
            return await ctx.send("Annulation de la suppression des serveurs.")

        if str(reaction.emoji) == '❌':
            await confirm_msg.delete()
            await ctx.send(f"Ignoré {guild.name}")
            continue

        if str(reaction.emoji) == '✅':
            try:
                await guild.leave()
                await ctx.send(f"Leave avec réussie {guild.name}")
            except Exception as e:
                await ctx.send(f"Erreur leave {guild.name}: {e}")

async def remove_all_recipients(channel):
    await asyncio.gather(*[channel.remove_recipient(r) for r in channel.recipients])

@bot.command()
async def copy(ctx):
    print(f'Commande de copie du serveur créée par {ctx.author.name} ({ctx.author.id})')
    await ctx.message.delete()
    await bot.create_guild(f'backup-{ctx.guild.name}')
    print(f'Création d un nouveau serveur de sauvegarde')
    await asyncio.sleep(4)
    for g in bot.guilds:
        if f'backup-{ctx.guild.name}' in g.name:
            print(f'J ai trouvé le nouveau serveur de sauvegarde: {g.name} ({g.id})')
            for c in g.channels:
                await c.delete()
                print(f'Channel {c.name} ({c.id}) retiré du nouveau serveur de la nouvelle sauvegarde')
            for role in reversed(ctx.guild.roles):
                if role.name != "@everyone":
                    perms = discord.Permissions.none()
                    for perm, value in role.permissions:
                        if value:
                            perms.update(**{perm: value})
                    new_role = await g.create_role(name=role.name, permissions=perms, colour=role.colour)
                    print(f'Role {new_role.name} ({new_role.id}) créé dans un nouveau serveur de sauvegarde')
            for cate in ctx.guild.categories:
                x = await g.create_category(f"{cate.name}")
                await x.edit(position=cate.position)
                print(f'Categorie {x.name} ({x.id}) créé dans le nouveau serveur de sauvegarde')
                for chann in cate.channels:
                    if isinstance(chann, discord.VoiceChannel):
                        new_chan = await x.create_voice_channel(f"{chann}")
                        await new_chan.edit(position=chann.position, user_limit=chann.user_limit, bitrate=chann.bitrate, sync_permissions=True)
                        print(f'Voice Channel {chann.name} ({chann.id}) créé dans la catégorie {x.name} ({x.id}) du le nouveau serveur de sauvegarde')
                    if isinstance(chann, discord.TextChannel):
                        new_chan = await x.create_text_channel(f"{chann}")
                        await new_chan.edit(position=chann.position, topic=chann.topic, slowmode_delay=chann.slowmode_delay, sync_permissions=True)
                        perms = chann.overwrites
                        for role, perm in perms.items():
                            if isinstance(role, discord.Role):
                                new_role = discord.utils.get(g.roles, name=role.name)
                                if new_role is not None:
                                    await new_chan.set_permissions(new_role, overwrite=perm)
                        print(f'Text Channel {chann.name} ({chann.id}) créé dans la catégorie {x.name} ({x.id}) du le nouveau serveur de sauvegarde')
    try:
        icon = await ctx.guild.icon.read()
        await g.edit(icon=icon)
        print('Nouvelle icône de sauvegarde du serveur')
    except Exception as e:
        await ctx.send(f'[ERROR]: {e}')
        print(f'Une erreur s est produite lors de la mise à jour de l icône du nouveau serveur de sauvegarde.: {e}')
    print(f'Ccopies du serveur terminée')

@bot.command()
async def massmention(ctx, *, message=None):
    await ctx.message.delete()
    members = ctx.guild.members
    if len(members) >= 50:
        sampling = random.sample(members, k=50)
    else:
        sampling = members
    post_message = "" if message is None else f"{message}\n\n"
    for user in sampling:
        post_message += user.mention
    await ctx.send(post_message)

@bot.command()
async def guildscrap(ctx):
    await ctx.message.delete()
    try:
        if not ctx.guild.icon:
            await ctx.send(f"**{ctx.guild.name}** n'a pas d'icône")
        else:
            await ctx.send(f"Icône du serveur : {ctx.guild.icon}")
        if not ctx.guild.banner:
            await ctx.send(f"**{ctx.guild.name}** n'a pas de bannière")
        else:
            await ctx.send(f"Bannière du serveur : {ctx.guild.banner}")
    except Exception as e:
        print(f"[ERROR] Une erreur s'est produite lors de l'exécution de la commande &guildscrap : {e}")
        await ctx.send(f"[ERROR] Une erreur s'est produite lors de l'exécution de la commande &guildscrap : {e}")

@bot.command()
async def pp(ctx, user_id: int):
    await ctx.message.delete()
    try:
        user = await bot.fetch_user(user_id)
        if not user.avatar:
            await ctx.send(f"{user.name} n'a pas de photo de profil")
        else:
            await ctx.send(f"{user.name} Image de profil: {user.avatar}")
    except Exception as e:
        print(f"[ERROR] Une erreur s'est produite lors de l'exécution de la commande userinfo pour l'utilisateur {user_id}: {e}")
        await ctx.send(f"[ERROR] Une erreur s'est produite lors de l'exécution de la commande userinfo pour l'utilisateur {user_id}: {e}")


@bot.command()
async def emoteclone(ctx, source_id: int, target_id: int):
    print(f"La commande &cloneemojis est appelée entre {source_id} et {target_id}")
    await ctx.message.delete()
    try:

        source_server = await bot.fetch_guild(source_id)
        emojis = await source_server.fetch_emojis()

        if len(emojis) > 50:
            emojis = emojis[:50]

        target_server = await bot.fetch_guild(target_id)
        for emoji in emojis:

            response = requests.get(str(emoji.url))
            if response.status_code != 200:
                print(f"Erreur lors de la récupération de l'image de l'emoji {emoji.name}")
                continue
            try:
                image = Image.open(BytesIO(response.content)).convert('RGBA')
                image_bytes = BytesIO()
                image.save(image_bytes, format='PNG')
                image_bytes.seek(0)

                await target_server.create_custom_emoji(name=emoji.name, image=image_bytes.read())
                print(f"Emoji {emoji.name} cloné avec succès sur le serveur cible.")
            except IOError:
                print(f"Erreur lors de la conversion d'une image en emoji {emoji.name}")
                continue

            await asyncio.sleep(3)

        await ctx.send("Les émojis ont été clonés avec succès!")
    except Exception as e:
        print(f"Erreur rencontrée lors de l'exécution de la commande: {e}")
        await ctx.send("Une erreur s'est produite lors du clonage des emojis.")

@bot.command()
async def connectvc(ctx, channel_id: int):
    await ctx.message.delete()
    channel = bot.get_channel(channel_id)
    if channel and channel.type == discord.ChannelType.voice:
        try:
            await channel.connect()
            await ctx.send(f"Connecté au channel vocal: {channel.name}")
        except discord.errors.ClientException:
            await ctx.send("Déjà connecté à un canal vocal.")
    else:
        await ctx.send("ID de canal vocal non valide.")

@bot.command()
async def leavevc(ctx):
    await ctx.message.delete()
    voice = ctx.guild.voice_client
    if voice:
        await voice.disconnect()
        await ctx.send("Je me suis déconnecté du canal vocal.")
    else:
        await ctx.send("Je ne suis pas connecté à un canal vocal.")

############################################################## C O M M A N D S ####################################################################


############################################################## L O G I N ##########################################################################

bot.run(token)

############################################################## C O R E P R O J E C T ##############################################################
