import discord
from discord.ext import commands, tasks
import requests
import datetime
import pytz
import os
TOKEN = os.getenv("MTQ0MTk3NzQyODczNzEzMDYyOA.Ge9AtN.nb-nI92F8EnIWc9qGfC8bm7sGZ07kpw9tTdJZs")



CHANNEL_ID = 1445631237258477683

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

SGT = pytz.timezone("Asia/Singapore")


# ---------------- GET EPIC FREE GAMES ----------------
def get_free_epic_games():
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
    response = requests.get(url).json()

    games = response["data"]["Catalog"]["searchStore"]["elements"]
    free_games = []

    for g in games:
        price_info = g.get("price", {}).get("totalPrice", {})
        promo = g.get("promotions")

        if not promo:
            continue
        
        if price_info.get("discountPrice", 1) != 0:
            continue

        offers = promo["promotionalOffers"]
        if not offers:
            continue

        end_date = offers[0]["promotionalOffers"][0]["endDate"]

        free_games.append({
            "title": g["title"],
            "desc": g.get("description", "No description."),
            "link": f'https://store.epicgames.com/en-US/p/{g["productSlug"]}',
            "end_date": end_date,
            "image": g["keyImages"][0]["url"]
        })

    return free_games


# ---------------- DAILY TASK AT 11AM SGT ----------------
@tasks.loop(time=datetime.time(hour=11, minute=0, tzinfo=SGT))
async def daily_post():
    channel = bot.get_channel(CHANNEL_ID)
    free_games = get_free_epic_games()

    if not free_games:
        await channel.send("@everyone ❌ No free games today.")
        return

    for game in free_games:
        embed = discord.Embed(
            title=f"🎁 FREE GAME: {game['title']}",
            description=f"🔥 **{game['title']}** is now FREE on Epic Games!\n\n{game['desc']}",
            color=discord.Color.green(),
        )

        embed.add_field(name="🔗 Get it Here", value=game['link'], inline=False)
        embed.add_field(name="⏳ Free Until", value=game['end_date'], inline=False)
        embed.set_image(url=game["image"])
        embed.set_footer(text="Epic Games Free Giveaway • Updated Daily")
        embed.timestamp = datetime.datetime.now()

        await channel.send("@everyone", embed=embed)


# ---------------- READY EVENT ----------------
@bot.event
async def on_ready():
    print(f"{bot.user} is online ✔")
    daily_post.start()


bot.run(TOKEN)


