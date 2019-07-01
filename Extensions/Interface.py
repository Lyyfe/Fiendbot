#import discord
from discord.ext import commands
from time import time
from requests import get, post
from asyncio import TimeoutError
from json import load, dump, dumps

class Interface(commands.Cog):
    def __init__(self, client):
        self.client = client

    #lmao this G A R B A G E isn't scalable or flexible, and doesnt check which message the user is reacting to
    #if there are 2 messages with scrolling reactions, and the user reacts to either one, B O T H will change their position in the list
    #what an absolute pile of wank
    async def scroll_reactions(self, items, ctx): 
        msg = await ctx.send(items[0])
        await msg.add_reaction("◀")
        await msg.add_reaction("⏹")
        await msg.add_reaction("▶")
        timeout = time()+60
        cycle = 0
        while time() < timeout:
            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=60.0)
            except TimeoutError:
                break
            if user == ctx.message.author and reaction.message == msg:
                if reaction.emoji == "◀":
                    if cycle == 0:
                        cycle = len(items)-1
                    else:
                        cycle -= 1
                    await msg.remove_reaction("◀", user)
                    await msg.edit(content=items[cycle])

                elif reaction.emoji == "▶":
                    if cycle == len(items)-1:
                        cycle = 0
                    else:
                        cycle += 1

                    await msg.remove_reaction("▶", user)
                    await msg.edit(content=items[cycle])

                elif reaction.emoji == "⏹":
                    await self.client.delete_message(msg)
                    break
        await msg.clear_reactions()

    @commands.command(aliases = ["wiki"])
    async def wikipedia(self, ctx):
        #removes the '~wiki'
        SEARCHTERM = " ".join((ctx.message.clean_content).split(" ")[1:])
        DATA = get(url="https://en.wikipedia.org/w/api.php", params={
            'action':"query",
            'list':"search",
            'srsearch': SEARCHTERM,
            'format':"json"
        }).json()

        links = []
        for i in DATA['query']['search']: 
            links.append(f"{i['title']}\nhttps://en.wikipedia.org/wiki/{i['title'].replace(' ','_')}")
        if len(links) == 0:
            await ctx.send(f"Sorry, no results were found for `{SEARCHTERM}`")
        else:
            await self.scroll_reactions(links, ctx)


    async def get_spotify_token(self):
        with open(r"Fiendbot\Files\API_keys.json", "r") as file:
            keys = load(file)
            if keys["Spotify"]["Temp_EXPIRY"] < time():
                client_id = keys["Spotify"]["Client_ID"]
                client_secret = keys["Spotify"]["Client_SECRET"]
                grant_type = ('client_credentials')
                body_params = {'grant_type': grant_type}
                url = ('https://accounts.spotify.com/api/token')
                response = post(url,
                data=body_params,
                auth = (client_id, client_secret)
                                        ).json()
                token = response['access_token']
                keys["Spotify"]["Temp_TOKEN"] = token
                keys["Spotify"]["Temp_EXPIRY"] = time() + response["expires_in"]
                with open(r"Fiendbot\Files\API_keys.json", "w") as filedump:
                    dump(keys, filedump)
            else:
                token = keys["Spotify"]["Temp_TOKEN"]

            return token

    async def get_spotify_list(self, query, request_type):
        token = await self.get_spotify_token()
        result = get(url='https://api.spotify.com/v1/search',
                         headers={ 'authorization': "Bearer " + token},
                         params={ 'q': query, 'type': request_type, "limit":20 }).json()
        links = []
        try:
            for i in result[f"{request_type}s"]["items"]:
                links.append(i["external_urls"]["spotify"])
        except Exception as e:
            print(e)
            
        return links

    @commands.command()
    async def spotify(self, ctx):
        args = (ctx.message.content).split(" ")[1:]
        if len(list(args)) == 0:
            await self.client.say("i got you fam...\nhttps://open.spotify.com/track/2xLMifQCjDGFmkHkpNLD9h\n(enter a search term next time)")
        elif args[0].lower() in ["artist", "artists", "musician", "musicians"]:
            q = " ".join(args[1:])
            r = "artist"
        elif args[0].lower() in ["album", "albums"]:
            q = " ".join(args[1:])
            r = "album"
        elif args[0].lower() in ["song", "songs", "track", "tracks"]:
            q = " ".join(args[1:])
            r = "track"
        else:
            q = " ".join(args)
            r = "track"
        
        links = await self.get_spotify_list(q, r)

        if len(links) == 0:
            await ctx.send(f"Sorry, no results were found for `{q}`")
        else:
            await self.scroll_reactions(links, ctx)

    @commands.command(aliases = ["yt"])
    async def youtube(self,ctx):
        with open(r"Fiendbot\Files\API_keys.json") as file:
            keys = load(file)
            devKey = keys["Youtube"]["DeveloperKey"]
            client_id = keys["Youtube"]["client_id"]
            client_secret = keys["Youtube"]["client_secret"]
        
        splitstring = ctx.message.clean_content.replace("`","").split(" ")
        yt_type = splitstring[1]
        content = " ".join(splitstring[2:])
        
        yt_types_index = {
            "video": {
                "index": "videoId",
                "url": "https://youtu.be/{}",
            },
            "channel": {
                "index": "channelId",
                "url": "https://www.youtube.com/channel/{}",
            },
            "playlist": {
                "index": "playlistId",
                "url": "https://www.youtube.com/playlist?list={}",
            }
        }
        if not content or yt_type not in yt_types_index:
            content = f"{yt_type} {content}".strip(" ")
            yt_type = "video"

        r = get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part": "snippet",
                "maxResults": 20,
                "key": devKey,
                "type": yt_type,
                "q": content,
            },
            headers={
                "User-Agent": dumps({"client_id":client_id, "client_secret":client_secret}),
                "Content-Type": "application/json",
            }
        )

        items = []
        if r.status_code == 200 and r.json()["pageInfo"]["totalResults"] != 0:
            for search_result in r.json()["items"]:
                response = search_result["id"][
                    yt_types_index[yt_type]["index"]]
                full_link =  yt_types_index[yt_type]["url"].format(response)
                items.append(full_link)
         
        if len(items) > 0:
            await self.scroll_reactions(items, ctx)
        else:
            await ctx.send(f"Sorry, there were no results for {content}")


def setup(client):
    client.add_cog(Interface(client))
    print("Loaded: Interface")