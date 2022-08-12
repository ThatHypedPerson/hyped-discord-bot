import os
import disnake
from disnake.ext import commands

import details

token = os.environ["token"]

intents = disnake.Intents.all() # should prob lower intent level

class DiscordBot(commands.Bot):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.member_id = 947987042208481301
		self.server = disnake.Guild
		self.notif_channel = disnake.TextChannel
		self.role_message_id = int
		self.notif_warn_id = int

		self.twitch_url = "https://www.twitch.tv/thathypedperson" # doesn't need to be declared lol
		self.youtube_url = str
		self.stream_title = str
		self.custom_message = str

		self.emoji_to_role = {
			disnake.PartialEmoji(name="🔴"): 1007625160066617394,  # ID of the role associated with unicode emoji '🔴'.
			disnake.PartialEmoji(name="🟡"): 949407352728203365,  # ID of the role associated with unicode emoji '🟡'.
			# disnake.PartialEmoji(
			# 	name="green", id=0
			# ): 0,  # ID of the role associated with a partial emoji's ID.
		}

	async def on_ready(self):
		print("ready")
		self.server = self.get_guild(947964970384109649)
		self.notif_channel = self.server.get_channel(951576624099393546)
		self.role_message_id = await self.send_react_message()  # ID of the message that can be reacted to to add/remove a role.

	async def send_react_message(self):
		# need a better name
		try:
			file = open("react_message.txt", "r+")
		except:
			file = open("react_message.txt", "w+")
		
		try:
			message = await self.notif_channel.fetch_message(int(file.readline()))
		except:
			notif_role = self.server.get_role(1007625160066617394)
			text = f"React to this message to recieve the {notif_role.mention} role to know when Hyped goes live or uploads a video."
			message = await self.notif_channel.send(text)
			await message.add_reaction(disnake.PartialEmoji(name="🔴"))
			await message.add_reaction(disnake.PartialEmoji(name="🟡"))
		
		# clear file
		file.truncate()
		file.seek(0)

		file.write(str(message.id))
		file.close()
		return message.id

	# https://github.com/DisnakeDev/disnake/blob/master/examples/reaction_roles.py
	async def on_raw_reaction_add(self, payload: disnake.RawReactionActionEvent):
		"""Gives a role based on a reaction emoji."""
		if payload.guild_id is None or payload.member is None:
			return

		if payload.member.id == self.member_id:
			return
		
		# Make sure that the message the user is reacting to is the one we care about.
		if payload.message_id != self.role_message_id:
			if payload.message_id != self.notif_warn_id:
				return
			else:
				await self.confirm_notification(payload)

		guild = self.get_guild(payload.guild_id)
		if guild is None:
			# Check if we're still in the guild and it's cached.
			return

		try:
			role_id = self.emoji_to_role[payload.emoji]
		except KeyError:
			# If the emoji isn't the one we care about then exit as well.
			return

		role = guild.get_role(role_id)
		if role is None:
			# Make sure the role still exists and is valid.
			return

		try:
			# Finally, add the role.
			await payload.member.add_roles(role)
		except disnake.HTTPException:
			# If we want to do something in case of errors we'd do it here.
			pass

	async def on_raw_reaction_remove(self, payload: disnake.RawReactionActionEvent):
		"""Removes a role based on a reaction emoji."""
		if payload.guild_id is None:
			return
		# Make sure that the message the user is reacting to is the one we care about.
		if payload.message_id != self.role_message_id:
			return

		guild = self.get_guild(payload.guild_id)
		if guild is None:
			# Check if we're still in the guild and it's cached.
			return

		try:
			role_id = self.emoji_to_role[payload.emoji]
		except KeyError:
			# If the emoji isn't the one we care about then exit as well.
			return

		role = guild.get_role(role_id)
		if role is None:
			# Make sure the role still exists and is valid.
			return

		# The payload for `on_raw_reaction_remove` does not provide `.member`
		# so we must get the member ourselves from the payload's `.user_id`.
		member = guild.get_member(payload.user_id)
		if member is None:
			# Make sure the member still exists and is valid.
			return

		try:
			# Finally, remove the role.
			await member.remove_roles(role)
		except disnake.HTTPException:
			# If we want to do something in case of errors we'd do it here.
			pass

	async def confirm_notification(self, payload: disnake.RawReactionActionEvent):
		guild = self.get_guild(payload.guild_id)
		if guild is None:
			# Check if we're still in the guild and it's cached.
			return

		if payload.emoji == disnake.PartialEmoji(name="✔️"):
			notif_role = guild.get_role(1007625160066617394) # better to get actual role than hoping to ping it
			
			notif = str

			if self.custom_message == "":
				notif = f"**Hyped is now live!** {notif_role.mention}"
			else:
				notif = self.custom_message

			notif += f"\n{self.stream_title}\n\n"
			notif += f"Come watch the stream at:\nTwitch: {self.twitch_url}\nYouTube: {self.youtube_url}"
			await self.notif_channel.send(notif)
		# change to mod channel
		await self.notif_channel.get_partial_message(self.notif_warn_id).delete()

intents = disnake.Intents.default()
intents.members = True

bot = DiscordBot(intents=intents)

@bot.slash_command()
@commands.default_member_permissions(manage_guild=True, moderate_members=True)
async def stream(
				inter: disnake.ApplicationCommandInteraction,
				twitch: str = "https://www.twitch.tv/thathypedperson",
				youtube: str = "",
				message: str = ""):
	"""
	Ping @Notifications With a New Stream

	Parameters
	----------
	twitch: Twitch Stream Link
	youtube: YouTube Stream Link
	message: Replace Default Notifier (You Need to Include @Notifications)
	"""
	
	# title = "【game】title | Hyped"
	# warning_message = f"Are these all correct?\nTitle: {title}\nTwitch: {twitch}\nYouTube: {youtube}"

	if youtube != "":
		youtube = details.get_youtube_alt_stream(youtube)
		if youtube == None:
			await inter.response.send_message("bro what kind of youtube link did you put", ephemeral=True)
			return
	else:
		youtube = details.get_youtube_stream()

	warning_message = f"Are these all correct?\n\n"
	warning_message += f"Title: {youtube['title']}\nTwitch: {twitch}\nYouTube: {youtube['url']}"
	await inter.response.send_message(warning_message, delete_after=300)
	
	msg: disnake.Message
	async for msg in inter.channel.history(): # look for the sent message
		if msg.content == warning_message:
			notif_warn = msg
			break
	
	await notif_warn.add_reaction(disnake.PartialEmoji(name="✔️"))
	await notif_warn.add_reaction(disnake.PartialEmoji(name="❌"))
	bot.notif_warn_id = notif_warn.id # Warning Notification Message ID
	
	if "🔴" in youtube["title"] or "⚫" in youtube["title"]:
		youtube["title"] = youtube["title"][1:]

	bot.twitch_url = twitch
	bot.youtube_url = youtube['url']
	bot.stream_title = youtube['title']
	bot.custom_message = message

	# notif_role = bot.server.get_role(949407352728203365)
	# await bot.notif_channel.send("abuh" + notif_role.mention)

bot.run(token)