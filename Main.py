import discord
from discord.ext import commands
from time import time
from os import listdir
from json import load as jsonload
client = commands.Bot(command_prefix="~", case_insensitive=True)

owners = [206890605865992192, 144866444730040321]

with open(r"Fiendbot\Files\API_keys.json") as file:
            keys = jsonload(file)
            TOKEN = keys["Discord"]["TOKEN"]


@client.event
async def on_message(message):
    print("{}: {}".format(message.author, message.clean_content))
    await client.process_commands(message)
    

@client.command()
async def kill(ctx):
    print(ctx.message.author.id)
    if ctx.message.author.id == 206890605865992192:
        await ctx.send("Bai")
        await client.close()


@client.command()
async def ping(ctx):
    msg = await ctx.send(":ping_pong:")
    msgping = round(1000*(msg.created_at - ctx.message.created_at).total_seconds())
    discordping = round(client.latency*1000)
    await msg.edit(content=f"Message Ping: {msgping}ms\nDiscord Connection Ping: {discordping}ms")


@client.command()
async def load(ctx):
    if ctx.message.author.id in owners:
        split = ctx.message.clean_content.split(" ")
        if len(split) == 1:
            await ctx.send("Needs an extension to load")
        else:
            ext = split[1].replace("`", "").title()
        try:
            if f"Extensions.{ext}" in client.extensions:
                client.unload_extension(f"Extensions.{ext}")
            client.load_extension(f"Extensions.{ext}")
            await ctx.send(f"Loaded: {ext}")
        except Exception as e:
            await ctx.send(f"Failed to load {ext}.\nReason: {e}")


@client.command()
async def unload(ctx, extension):
    if ctx.message.author.id in owners:
        split = ctx.message.clean_content.split(" ")
        if len(split) == 1:
            await ctx.send("Needs an extension to load")
        else:
            ext = split[1].replace("`", "").title()
        try:
            if f"Extensions.{ext}" in client.extensions:
                client.unload_extension(f"Extensions.{ext}")
                await ctx.send(f"Unloaded: {ext}.")
            else:
                await ctx.send(f"{ext} was not loaded.")
        except Exception as e:
            await ctx.send(f"Failed to load {ext}.\nReason: {e}")


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="Loading Extensions"))
    for extension in listdir(r"Fiendbot\Extensions"):
        if extension.endswith(".py"):
            client.load_extension(f"Extensions.{extension[:-3]}")
    await client.change_presence(activity=discord.Game(name="Beans >:)"))

    print("B) I'm in")


client.run(TOKEN)
