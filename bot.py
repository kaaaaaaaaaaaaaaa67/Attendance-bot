import discord
from discord.ext import commands, tasks
from datetime import datetime
import json
import os
import calendar

TOKEN = os.getenv("TOKEN")

REPORT_CHANNEL_ID = 1516194152633598103  # حطي رقم قناة التقارير هنا

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "data.json"


def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    monthly_report.start()


@bot.command()
async def حضور(ctx):
    data = load_data()
    user = str(ctx.author.id)

    if user not in data["users"]:
        data["users"][user] = {
            "name": ctx.author.name,
            "start": None,
            "hours": 0
        }

    if data["users"][user]["start"]:
        await ctx.send("❌ أنت مسجل حضور من قبل")
        return

    data["users"][user]["start"] = datetime.now().isoformat()
    save_data(data)

    await ctx.send(f"✅ تم تسجيل حضور {ctx.author.mention}")


@bot.command()
async def انصراف(ctx):
    data = load_data()
    user = str(ctx.author.id)

    if user not in data["users"] or not data["users"][user]["start"]:
        await ctx.send("❌ ما عندك تسجيل حضور")
        return

    start = datetime.fromisoformat(data["users"][user]["start"])
    end = datetime.now()

    hours = (end - start).total_seconds() / 3600

    data["users"][user]["hours"] += hours
    data["users"][user]["start"] = None

    save_data(data)

    await ctx.send(
        f"✅ تم تسجيل الانصراف\n⏱️ اشتغلت {round(hours,2)} ساعة"
    )


@tasks.loop(hours=24)
async def monthly_report():
    now = datetime.now()

    last_day = calendar.monthrange(now.year, now.month)[1]

    if now.day == last_day:

        channel = bot.get_channel(REPORT_CHANNEL_ID)

        if channel:
            data = load_data()

            msg = f"📊 تقرير شهر {now.month}/{now.year}\n\n"

            for user in data["users"].values():
                h = int(user["hours"])
                m = int((user["hours"] - h) * 60)

                msg += (
                    f"👤 {user['name']}\n"
                    f"⏱️ {h} ساعة و {m} دقيقة\n\n"
                )

            await channel.send(msg)

            for user in data["users"]:
                data["users"][user]["hours"] = 0

            save_data(data)


bot.run(TOKEN)
