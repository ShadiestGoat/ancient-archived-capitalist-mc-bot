import discord
from discord.ext import commands, tasks, menus
from discord.utils import get
import asyncio
import aiomysql
import random
import datetime
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import os
import praw
from disputils import BotEmbedPaginator, BotConfirmation, BotMultipleChoice
import json
import aiohttp
import async_timeout
import validators
import math
import typing
import copy
import wavelink



reddit = praw.Reddit(client_id="",
                     client_secret=".", password=".",
                     user_agent=".:com.example.CapitalistMC:v1.2.3 (by u/.)", username=".")

client = commands.Bot(command_prefix=commands.when_mentioned_or('-'))
client.remove_command('help')

class WrongChan(commands.CommandError):
  pass

def init(setting):
    with open("config/config.json", "r+b") as outfile:
        config = json.loads(outfile.read())
        value = config["init"][str(setting)]
        return value
async def config(setting):
    with open("config/config.json", "r+b") as outfile:
        config = json.loads(outfile.read())
        value = config[str(setting)]
        return str(value)
async def config_two(folder, setting):
    with open("config/config.json", "r+b") as outfile:
        config = json.loads(outfile.read())
        value = config[str(folder)][str(setting)]
        return str(value)
async def config_j(setting):
    with open("config/config.json", "r+b") as outfile:
        config = json.loads(outfile.read())
        value = config[str(setting)]
        return value
async def config_two_j(folder, setting):
    with open("config/config.json", "r+b") as outfile:
        config = json.loads(outfile.read())
        value = config[str(folder)][str(setting)]
        return value
async def gembed(desc, tit="\n", col = 0x216ade):
    EE = discord.Embed(color=col, title=tit, description = desc)
    usr = client.get_user(376079696489742338)
    EE.set_footer(text="Bot made by Shady Goat, on shadygoat.eu", icon_url=usr.avatar_url)
    return EE
async def error_emb(msg="\n", dict_format=None):
    if dict_format is None:
        e = await gembed(col=0xff0000, tit=await config_two("Errors", "Title"), desc=await config_two("Errors", msg))
    else:
        e = await gembed(col=0xff0000, tit=await config_two("Errors", "Title"), desc=str(await config_two("Errors", msg)).format_map(dict_format))
    return e
async def newfield(desc, embed, tit="\n", colum=False):
    embed.add_field(name=tit, value=desc, inline=colum)
    return embed
async def newlist(string):
    return string.strip('][').replace("'", "").split(', ')
async def botchan(ctx):
    return ctx.channel.id==int(await config("Bot Spam ID"))

server = client.get_guild(init("Guild ID"))
staff_id = init("Staff Role ID")
god_id = init("God Role ID")
CAT_API_KEY = init("CAT_API_KEY")
DOG_API_KEY = init("DOG_API_KEY")
sqloginz = init("sql login")
pa = sqloginz["password"]
aa = sqloginz["user"]
ho = sqloginz["host"]
token= init("token")


async def sqlogin():
    return await aiomysql.connect(host=f'{ho}', port=3306, user=f'{aa}', password=f'{pa}', db='s72_statz',)


async def db_get(table, varname, var):
    conn = await sqlogin()
    async with conn.cursor() as cur:
        await cur.execute(f"SELECT * FROM {table} WHERE {varname} = %s", (var,))
        result = await cur.fetchall()
        conn.close()
        return result
async def removereaction(payload):
    chan = client.get_channel(payload.channel_id)
    msg = await chan.fetch_message(payload.message_id)
    await msg.remove_reaction(payload.emoji, payload.member)
async def jsonify(string):
    return json.loads(string)
async def request(url, headers=None):
    if headers is None:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()
    else:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                return await response.text()

async def balance(user):
    ur = user.id
    raw = None
    uuid = ""
    acc = await db_get("discordsrv_accounts", "discord", ur)
    uuid = acc[0][2]

    checks = await config_two_j("balance", "checks")

    cache = {}

    for check in checks:
        check_name = check
        table_name = "statz_" + check_name
        check_mul = float(checks[check])
        raw = await db_get(table_name, "uuid", uuid)
        value = 0
        for coocked in raw:
            value += float(coocked[2]) * float(check_mul)
        cache[check_name] = value

    totbal = eval(str(await config_two("balance", "Equation")).format_map(cache))
    raw = await db_get("bal", "uuid", uuid)
    spentbalance = 0
    boughtbal = 0
    for spent in raw:
        spentbalance += spent[1]
        boughtbal += spent[2]

    bal = totbal/2 - spentbalance + boughtbal
    return bal, spentbalance, boughtbal, uuid
async def warn(author, user, reason):
    conn = await sqlogin()

    async with conn.cursor() as cur:
        warnau=str(author.id)
        warnus=str(user.id)
        await cur.execute("INSERT INTO warnings (author, user, reason) VALUES (%s, %s, %s)", (warnau, warnus, reason))
        await conn.commit()

    EwarnedE = await gembed(col=0xff0000, tit=await config_two("Moderation", "Warning Title"), desc =str(await config_two("Moderation", "Warning Description")).format(author=author.mention, reason=reason))
    await user.send(embed=EwarnedE)
    conn.close()

async def shop(name, payload):
    channels = await config_j("Channel IDs")
    consolechan = client.get_channel(channels["Console"])

    conn = await sqlogin()
    shop = await config_j("shop")
    emoji_id = shop["emoji id"]
    ign = payload.member.display_name

    role = server.get_role(shop["roles"][name])
    price = shop["prices"][name]
    mc = shop["MC"][name]
    message = shop["Msg"][name]

    bal = await balance(payload.member)

    uuid = bal[3]
    spentbalance = bal[1]
    totbal = bal[0]

    async with conn.cursor() as cur:
        if role in payload.member.roles:
            if totbal > price:
                await consolechan.send(f"upc setGroups {ign} {mc}")
                await payload.member.send(f"Congrats! You were upgraded to the {name} role! You should be able to see it updated in a max of 10 minutes, if not, please DM Shady Goat")
                addedbal = spentbalance + price
                await cur.execute("UPDATE bal SET spentbal = %s WHERE uuid = %s", (addedbal, uuid))
                await conn.commit()
            else:
                await payload.member.send(f"Ooo.. sorry, you dont have the funds to do this :/\n You have {round(int(totbal), 2)} / {price}")
        else:
            await payload.member.send(f"Oo.. Not good. You need the {role.name} to buy this")
    conn.close()

#--------------------------------------------------------------------------------------------------------
#setup
#--------------------------------------------------------------------------------------------------------

@client.event
async def on_ready():
    global server
    global staff_id
    global CAT_API_KEY
    global DOG_API_KEY
    global pa
    global aa
    global ho
    global god_id
    activity = discord.Activity(name="with your mum's __", type=discord.ActivityType.playing)
    await client.change_presence(activity=activity)
    server = client.get_guild(init("Guild ID"))
    staff_id = init("Staff Role ID")
    CAT_API_KEY = init("CAT_API_KEY")
    DOG_API_KEY = init("DOG_API_KEY")
    sqlogin = init("sql login")
    pa = sqlogin["password"]
    aa = sqlogin["user"]
    ho = sqlogin["host"]
    god_id = init("God Role ID")
    membercount.start()
    servercount.start()
    print('Ready')

@client.command()
@commands.is_owner()
async def reload(ctx):
    global server
    global staff_id
    global CAT_API_KEY
    global DOG_API_KEY
    global pa
    global aa
    global ho
    global god_id
    server = client.get_guild(init("Guild ID"))
    staff_id = init("Staff Role ID")
    CAT_API_KEY = init("CAT_API_KEY")
    DOG_API_KEY = init("DOG_API_KEY")
    sqlogin = init("sql login")
    pa = sqlogin["password"]
    aa = sqlogin["user"]
    ho = sqlogin["host"]
    god_id = init("God Role ID")
    activity = discord.Activity(name=await config("status"), type=discord.ActivityType.custom)
    await client.change_presence(activity=activity)

#--------------------------------------------------------------------------------------------------------
#stats
#--------------------------------------------------------------------------------------------------------

@tasks.loop(seconds=600)
async def membercount():
    Count = 0
    for member in server.members:
        if not member.bot:
            Count += 1
    STATchan = client.get_channel(709382029174636546)
    print(Count)
    await STATchan.edit(name=f'Capitalists: {Count}')

@tasks.loop(seconds=600)
async def servercount():
    onlinechan = client.get_channel(741163498863722497)
    server_info = await request("https://api.mcsrvstat.us/2/play.capitalistmc.com")
    server = await jsonify(server_info)
    amo = server["players"]["online"]
    print(amo)
    await onlinechan.edit(name=f'Online Players: {amo}')

#--------------------------------------------------------------------------------------------------------
#debug stuff
#--------------------------------------------------------------------------------------------------------

@client.command()
async def avatar(ctx, mem: discord.Member):
    await ctx.send(f"bitch, here: {mem.avatar_url}")

@client.command()
@commands.has_role(staff_id)
async def react(ctx, msg:discord.Message, urmum):
    await msg.add_reaction(urmum)

#--------------------------------------------------------------------------------------------------------
#trial
#--------------------------------------------------------------------------------------------------------

@client.command()
@commands.has_role(staff_id)
async def trial(ctx, command, userHere = None):
    trial_msg = await config_j("trial messages")
    roles = trial_msg["roles"]
    JDrole = ctx.guild.get_role(roles["Judge"])
    Prole = ctx.guild.get_role(roles["Prosecution"])
    Drole = ctx.guild.get_role(roles["Defense"])
    Lrole = ctx.guild.get_role(roles["Lawyer"])
    ANOUNCEMENTchannel = client.get_channel(await config_two_j("Channel IDs", "Trial Announcements"))
    if command == 'claim':

        await ctx.channel.send('Who is on trial?')
        def TRcheck(m):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id and m.mentions
        TRmsg = await client.wait_for('message', check=TRcheck, timeout=60.0)
        TRmember = TRmsg.mentions[0]


        await ctx.channel.send('Who is the Prosecution?')
        def PRcheck(m):
                return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id and m.mentions
        PRmsg = await client.wait_for('message', check=PRcheck, timeout=60.0)
        PRmember = PRmsg.mentions[0]

        await ctx.channel.send('What are the charges?')
        def CHARGEcheck(m):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
        CHARGEmsg = await client.wait_for('message', check=CHARGEcheck, timeout=60.0)
        CHARGE = CHARGEmsg.content
        ATRmember = TRmember.mention
        APRmember = PRmember.mention

        EapplicationE = await gembed(tit=trial_msg["Claim"]["Title"], desc=str(trial_msg["Claim"]["Description"]).format(prosecution=APRmember, defense=ATRmember, charge=CHARGE))
        EapplicationE.add_field(name="Legal notice", value=trial_msg["Claim"]["Legal Notice"], inline=False)


        APPmsg = await ANOUNCEMENTchannel.send(f"Attention all! Especially {ATRmember} and {APRmember},", embed=EapplicationE)

        await APPmsg.add_reaction("🇵")
        await APPmsg.add_reaction("🇩")
        await APPmsg.add_reaction("🇯")
        await APPmsg.add_reaction("🇺")
        conn = await sqlogin()
        async with conn.cursor() as cur:
            PR = PRmember.id
            TR = TRmember.id
            print(PR)
            await cur.execute("SELECT MAX(id) FROM trial")
            raw = await cur.fetchall()
            raw = int(raw[0][0]) + 1
            a = 1
            await cur.execute("INSERT INTO trial (id, open, pro, def, charge) VALUES (%s, %s, %s, %s, %s)", (raw, a, PR, TR, CHARGE))
            await conn.commit()
    elif command == 'start':
        if userHere is None:
            EE = await gembed(col=0xff0000, tit=f'You didnt enter id!', desc = f'You must enter the id. `-trials` to see them all :D')
        ID = userHere
        conn = await sqlogin()
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM trial WHERE id = %s", (int(userHere)))
            raw = await cur.fetchall()
            if raw == ():
                EE = await gembed(col=0xff0000, tit=f'No trial found under that ID!', desc= f'You have to type a valid ID. Do see IDs of open trials, do `-trials`')
                await ctx.send(EE)
                return
            elif int(raw[0][1]) == 2:
                EE = await gembed(col=0xff0000, tit=f'Trial already started, stoopid!', desc = f'Stupid ass bitch')
                await ctx.send(embed=EE)
                return
            else:
                raw = raw[0]
                await ctx.channel.send('Who is the Judge?')
                def JDcheck(m):
                    return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id and m.mentions
                JDmsg = await client.wait_for('message', check=JDcheck, timeout=60.0)
                JDmember = JDmsg.mentions[0]


                await ctx.channel.send('Who is the Defence Lawyer?')
                def L_Dcheck(m):
                    return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id and m.mentions
                L_Dmsg = await client.wait_for('message', check=L_Dcheck, timeout=60.0)
                L_Dmember = L_Dmsg.mentions[0]


                await ctx.channel.send('Who is the Prosecution Lawyer?')
                def L_Pcheck(m):
                    return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id and m.mentions
                L_Pmsg = await client.wait_for('message', check=L_Pcheck, timeout=60.0)
                L_Pmember = L_Pmsg.mentions[0]

                await ctx.channel.send('When is the Trial happening?')
                def TIMEcheck(m):
                    return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
                TIMEmsg = await client.wait_for('message', check=TIMEcheck, timeout=60.0)
                TIME = TIMEmsg.content

                pro = ctx.guild.get_member(raw[2])
                defns = ctx.guild.get_member(raw[4])

                EanouncementE = await gembed(tit=trial_msg["Start"]["Title"], desc=str(trial_msg["Start"]["Description"]).format(prosecution=pro.mention, defense=defns.mention, charges=raw[7], time=TIME, judge=JDmember.mention, lawer_defense=L_Dmember.mention, lawer_prosecution=L_Pmember.mention))

                EanouncementE.add_field(name="Legal notice", value=trial_msg["Start"]["Legal Notice"], inline=False)

                await ANOUNCEMENTchannel.send(f"@everyone, especially {pro.mention} and {defns.mention},", embed=EanouncementE)

                await cur.execute("UPDATE trial SET prosec = %s, defsec = %s, judge = %s, open = '2' WHERE id = %s", (L_Pmember.id, L_Dmember.id, JDmember.id, ID))

                await conn.commit()

                await L_Dmember.add_roles(Lrole, Drole)
                await L_Pmember.add_roles(Lrole, Prole)
                await defns.add_roles(Drole)
                await pro.add_roles(Prole)
                await JDmember.add_roles(JDrole)

    elif command == 'stop':
        if userHere is None:
            await ctx.send("You didnt enter id!\nYou must enter the id. `-trials` to see them all :D")
            return
        ID = userHere
        conn = await sqlogin()
        raw = await db_get("trial", "id", int(userHere))
        if raw == ():
            EE = await error_emb("Trial ID bad")
            return
        elif int(raw[0][1]) == 1:
            await cur.execute("DELETE FROM trial WHERE id = %s", (int(userHere)))
            await conn.commit()
            await ctx.send(embed=await gembed("Donzo! Trial deleted :D"))
            return
        elif int(raw[0][1]) == 2:
            raw = raw[0]


            pro = ctx.guild.get_member(raw[2])
            defn = ctx.guild.get_member(raw[4])
            Dlaw = ctx.guild.get_member(raw[5])
            Plaw = ctx.guild.get_member(raw[3])
            Judg = ctx.guild.get_member(raw[6])
            Judg.remove_roles(JDrole)
            Plaw.remove_roles(Lrole, Prole)
            Dlaw.remove_roles(Lrole, Drole)
            defn.remove_roles(Drole)
            pro.remove_roles(Prole)


            await ctx.channel.send('Who won the case? (P/D)')

            def WINcheck(m):
                return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
            WINmsg = await client.wait_for('message', check=WINcheck)

            if WINmsg.content == "P":
                WINNERS = f"The Prosecution ({pro.mention} and {Plaw.mention})"
                LOOSER = ATRmember
                await ctx.channel.send('What is the punishment? (By order of the ICG, the looser will __)')
                def PUNcheck(m):
                    return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

                PUNmsg = await client.wait_for('message', check=PUNcheck)
                punishment = PUNmsg.content

            elif WINmsg.content == "D":

                WINNERS = f"The Defense, ({defn.mention} and {Dlaw.mention})"
                LOOSER = APRmember
                punishment = await config("TPC pun")

            EWanouncementE = await gembed(f"Heya,\n{WINNERS} won this case. The judge has given a fair punishment to {LOOSER}. By order of the ICG, the {LOOSER} will {punishment}.")

            await ANOUNCEMENTchannel.send(embed=EWanouncementE)

@client.command()
@commands.has_role(staff_id)
async def trials(ctx):
    conn = await aiomysql.connect(host=f'{ho}', port=3306,
                                            user=f'{aa}', password=f'{pa}',
                                        db='s72_statz',)
    async with conn.cursor() as cur:

        await cur.execute("SELECT * FROM trial WHERE open = '1' OR open = '2'",)
        raw = await cur.fetchall()
        if raw == ():
            await ctx.send(embed=await error_emb("No Trials"))
            return

        pros = ""
        prosecs = ""
        defs = ""
        defsecs = ""
        judgs = ""
        chrgs = ""
        embeds = []
        for item in raw:

            pros = ""
            prosecs = ""
            defs = ""
            defsecs = ""
            judgs = ""
            chrgs = ""

            usrE = await gembed(tit="Trials Currently Open", desc=f"Trial ID: {item[0]}")

            pros += f'{ctx.guild.get_member(int(item[2])).mention}'
            if item[3] == None:
                prosecs += "Un-decided"
            else:
                prosecs += f'{ctx.guild.get_member(int(item[3])).mention}'
            defs += f'{ctx.guild.get_member(int(item[4])).mention}'
            if item[5] == None:
                defsecs += f"Un-decided"
            else:
                defsecs += f"{ctx.guild.get_member(int(item[5])).mention}"
            if item[6] == None:
                judgs += "Un-deided"
            else:
                judgs += f"{ctx.guild.get_member(int(item[6])).mention}"
            chrgs += f"{item[7]}\n"
            usrE.add_field(name='Prosecution', value=f'{pros}\n{prosecs}', inline=True)
            usrE.add_field(name='Defense', value=f'{defs}\n{defsecs}', inline=True)
            usrE.add_field(name='Judge', value=f'{judgs}', inline=True)
            usrE.add_field(name='Charge', value=f'{chrgs}', inline=False)
            embeds.append(usrE)
        paginator = BotEmbedPaginator(ctx, embeds)
        await paginator.run()

#--------------------------------------------------------------------------------------------------------
#general
#--------------------------------------------------------------------------------------------------------
@client.command()
@commands.cooldown(1,30, commands.BucketType.user)
async def help(ctx):

    EE = await gembed(desc="Prefix: '-' or @mention the bot.\n(optional), <required>. Dont use the brackets")
    if False:
        async def sppconf(setting):
            with open("config/config.json", "r+b") as outfile:
                config = json.loads(outfile.read())
                value = config["Help"]["Help Staff"][str(setting)]
                return value
        for field in await config_two_j("Help", "Help Staff"):
            field_t = ""
            for command in await sppconf(field):
                field_t += f"{command}\n"
            print(len(field) + len(field_t))
            EE.add_field(name=field, value=field_t, inline=False)
    else:
        async def spconf(setting):
            with open("config/config.json", "r+b") as outfile:
                config = json.loads(outfile.read())
                value = config["Help"]["Normal Field"][str(setting)]
                return value
        for field in await config_two_j("Help", "Normal Field"):
            field_t = ""
            for command in await spconf(field):
                field_t += f"{command}\n"
            print(len(field) + len(field_t))
            EE.add_field(name=field, value=field_t, inline=False)

    await ctx.send(embed=EE)

#--------------------------------------------------------------------------------------------------------
#staff
#--------------------------------------------------------------------------------------------------------

@client.command()
@commands.has_role(god_id)
async def announce(ctx, *, anouncement = None):
    if anouncement is None:
        await ctx.send("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA you forgot to put the announcement")
        return
    chann = client.get_channel(await config_two_j("Channel IDs", "Announcements"))
    EanounceE = await gembed(desc=anouncement)
    await chann.send(embed=EanounceE)

@client.command()
@commands.cooldown(1,60, commands.BucketType.user)
@commands.has_role(staff_id)
async def stask(ctx, who, *, task):
    EtaskE = await gembed(col=0xff0000, desc=f"For: {who}", tit=f"{task}")
    taskchan = client.get_channel(await config_two_j("Channel IDs", "Tasks"))
    task = await taskchan.send(embed=EtaskE)
    reac = await config_j("Tasks")
    await task.add_reaction(reac["Claim"])
    await task.add_reaction(reac["Done"])
    await task.add_reaction(reac["Drop"])


@client.command()
@commands.has_role(staff_id)
async def embed(ctx, chann: discord.TextChannel, *, urmum):
    EE = await gembed(desc=urmum)
    await chann.send(embed=EE)

#--------------------------------------------------------------------------------------------------------
#jobs
#--------------------------------------------------------------------------------------------------------

@client.command()
@commands.has_role(578173649195106306)
async def sjob(ctx, command, *, job):
    conn = await sqlogin()
    if command == 'open':
        async with conn.cursor() as cur:
            jobss = await db_get("jobs", "job", job)

            if jobss == ():
                await cur.execute("INSERT INTO jobs (open, job) VALUES ('open', %s)", (job))
                await conn.commit()
                EE = await gembed(desc=f"Nice! Job {job} has been opened!")
                await ctx.send(embed=EE)
                return
            else:
                jobs = jobss[0]
                if jobs[0] == 'open':
                    EalropE = await error_emb("Job Open")
                    await ctx.send(embed=EalropE)
                    return
                elif jobs[0] == 'closed':
                    await cur.execute("UPDATE jobs SET open = 'open' WHERE job = %s", (job))
                    await conn.commit()
                    EE = await gembed(desc=f"Nice! Job {job} has been opened!")
                    await ctx.send(embed=EE)
                    return
    elif command == 'close':
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM jobs WHERE job = %s", (job))
            jobss = await cur.fetchall()
            if jobss == ():
                EE = await error_emb("No Job")
                await ctx.send(embed=EE)
                return
            else:
                jobs = jobss[0]
                if jobs[0] == 'closed':
                    EalropE = await error_emb("Job Closed")
                    await ctx.send(embed=EalropE)
                    return
                elif jobs[0] == 'open':
                    await cur.execute("UPDATE jobs SET open = 'closed' WHERE job = %s", (job))
                    await conn.commit()

                    return


@client.command()
@commands.cooldown(3, 300, commands.BucketType.user)
async def job(ctx, command, *, job=None):
    conn = await sqlogin()
    async with conn.cursor() as cur:
        if command == 'list':
            await cur.execute("SELECT * FROM jobs WHERE open = 'open'")
            jobss = await cur.fetchall()
            jobs = jobss
            joblist = ''
            for job in jobs:
                joblist += f'➤ {job[1]}\n'
            joblist += f'------------------------\n'
            EjobsE = await gembed(tit=f"List of open jobs", desc=joblist)
            await ctx.send(embed=EjobsE)

        elif command == 'apply':
                if job is None:
                    raise commands.MissingRequiredArgument
                jobss = await db_get("jobs", "job", job)
                jobs = jobss[0]
                #BELOW DO THIS
                if jobs[0] == 'open':
                    EappE = await gembed(tit="Job Open!", desc=config("InterviewQ"))
                    EappE.add_field(name="NOTE", value="A new channel will be made once you react with the :white_check_mark: on this msg", inline=False)
                    EappE.timestamp = datetime.datetime.now()
                    await ctx.author.send(content = "Jobxyz2420", embed=EappE)
                    return
                elif jobs[0] == 'closed':
                    EE = await error_emb(await config("Jclose"))
                    await ctx.author.send(embed=EE)

@client.command()
@commands.has_role(god_id)
async def app(ctx, an, user: discord.Member = None, *, reason):
    if an == 'accept':
        EanE = await gembed(tit=f"You were accepted!", desc=await config("JaccACC"))
        await user.send(embed=EanE)
        await user.add_roles(ctx.guild.get_role(staff_id_role))

    elif an == 'deny':
        EanE = gembed(col=0xff0000, tit=f"You weren't accepted!", desc= f"Sorry! You were not accepted for your new job :(\nThe reason for this is {reason}")
        await user.send(embed=EanE)

#--------------------------------------------------------------------------------------------------------
#moderation
#--------------------------------------------------------------------------------------------------------

@client.command()
@commands.has_role(staff_id)
async def warn(ctx, user: discord.Member, *, reason="reasons"):
    await warn(ctx.author, user, reason)

@client.command()
async def warnings(ctx, user: discord.Member = None):
    if not user:
        user = ctx.author
    user = user.id

    warnings = await db_get("warnings", "user", user)
    warntot = len(warnings)
    desc = f"**Amount: {warntot}**\n\n\n"
    for warning in warnings:
        author = ctx.guild.get_member(int(warning[0]))
        desc += f"**From:** {author.name} **because** {warning[2]}\n"
    EwarningsE = await gembed(tit="Your warnings", desc='\n')
    EwarningsE.description = desc
    await ctx.send(embed=EwarningsE)

@client.command()
@commands.cooldown(1, 20, commands.BucketType.user)
async def report(ctx, remem: discord.Member, *, reason):
    rprtchan = client.get_channel(int(await config_two("Channel IDs", "Reports")))
    rprtchan.send(f"{ctx.autor.mention} reported {remem.mention} for {reason}")

@client.command()
@commands.has_role(staff_id)
async def mute(ctx, mutemember: discord.Member, reason="no reason provided"):
    MUTErole = ctx.guild.get_role(int(await config_two("Moderation", "Muted Role ID")))
    await mutemember.add_roles(MUTErole)
    EmuteE = await gembed(col=0xff0000, desc=str(await config_two("Moderation", "Muted Message")).format(author=ctx.author.mention, reason=reason))
    await mutemember.send(embed=EmuteE)

@client.command()
@commands.has_role(staff_id)
async def unmute(ctx, unmutemember: discord.Member):
    MUTErole = ctx.guild.get_role(int(await config_two("Moderation", "Muted Role ID")))
    await unmutemember.remove_roles(MUTErole)
    msg = await newlist(await config("unmuted"))
    EmuteE = await gembed(desc=await config_two("Moderation", "Unmuted Message"))
    await unmutemember.send(embed=EmuteE)

@client.command()
@commands.has_role(god_id)
async def poll(ctx, *, thing):
    chann = client.get_channel(int(await config_two("Channel IDs", "Poll")))
    aa = thing.split(sep=" | ", maxsplit=1)
    pollopF = await newlist(aa[1])

    emojiList = ["\U0001f1e6", "\U0001f1e7", "\U0001f1e8", "\U0001f1e9", "\U0001f1ea", "\U0001f1eb", "\U0001f1ec", "\U0001f1ed", "\U0001f1ee", "\U0001f1ef", "\U0001f1f0", "\U0001f1f1", "\U0001f1f2", "\U0001f1f3", "\U0001f1f4", "\U0001f1f5", "\U0001f1f6", "\U0001f1f7", "\U0001f1f8", "\U0001f1f9", "\U0001f1fa", "\U0001f1fb", "\U0001f1fc", "\U0001f1fd", "\U0001f1fe", "\U0001f1ff"]
    EpolldescE = "\nOptions:\n\n\n"

    for option in pollopF:
        EpolldescE += f"{emojiList[pollopF.index(option)]} - {option}\n\n"

    EE = await gembed(desc=EpolldescE, tit=aa[0])

    POLL = await chann.send(await config_two("Moderation", "Poll msg"), embed=EE)

    for option in pollopF:
        Finemoji = emojiList[pollopF.index(option)]
        await POLL.add_reaction(f"{Finemoji}")

@client.command()
@commands.has_role(god_id)
async def ezpoll(ctx, *, ezpollq):
    chann = client.get_channel(int(await config_two("Channel IDs", "Poll")))
    EezpollE = await gembed(tit=f"{ezpollq}", desc = "Options:\n\n:white_check_mark: - Yes\n\n:x: - No")
    ezpollmsg = await chann.send(await config_two("Moderation", "Poll msg"), embed = EezpollE)
    await ezpollmsg.add_reaction("❌")
    await ezpollmsg.add_reaction("✅")


@client.command()
@commands.guild_only()
@commands.has_role(god_id)
async def ban(ctx, user: discord.Member, reason = None):
    if reason == None:
        reason = await config_two("Moderation", "Default Ban Reason")
    await ctx.guild.ban(user, reason=reason)


@client.command()
@commands.guild_only()
@commands.has_role(god_id)
async def kick(ctx, user: discord.Member):
    await ctx.guild.kick(user)


@client.command()
@commands.has_role(staff_id)
async def purge(ctx, limit: int):
    await ctx.message.delete()
    await ctx.channel.purge(limit=limit)


#--------------------------------------------------------------------------------------------------------
#Mc integration
#--------------------------------------------------------------------------------------------------------
@client.command()
@commands.guild_only()
@commands.cooldown(1,5, commands.BucketType.user)
async def bal(ctx, user: discord.Member = None):

    if user == None:
        user = ctx.author

    bal = await balance(user)

    EE = await gembed(desc=f"{user.mention}'s balance is {round(int(bal[0]), 2)}", tit=f"\n")
    await ctx.channel.send(embed=EE)



#--------------------------------------------------------------------------------------------------------
#fun
#--------------------------------------------------------------------------------------------------------

@client.command()
@commands.cooldown(1,5, commands.BucketType.user)
async def mcbuild(ctx, list = None):
    Things = await config_j("mc build")

    theme = random.choice(Things["Ltheme"])
    build = random.choice(Things["Lbuild"])
    Btime = random.choice(Things["Ltime"])

    EbuildE = await gembed(tit="Your build idea!", desc = f"A {theme}-themed {build} from the {Btime}")

    await ctx.channel.send(embed=EbuildE)

    if list == 'list':
        EbuildE = await gembed(desc = f"**A list of things**")
        EbuildthameE = ''
        for thame in theme:
            EbuildthameE += f"{theme[theme.index(thame)]}\n"
        EbuildbuildE = ''
        for balt in build:
            EbuildbuildE += f"{build[build.index(balt)]}\n"
        EbuildtameE = ''
        for tame in Btime:
            EbuildtameE += f"{Btime[Btime.index(tame)]}\n"

        EbuildE.add_field(name="Theme", value=f"{EbuildthameE}", inline=True)
        EbuildE.add_field(name="Build", value=f"{EbuildbuildE}", inline=True)
        EbuildE.add_field(name="Time", value=f"{EbuildtameE}", inline=True)

        await ctx.channel.send(embed=EbuildE)


@client.command()
@commands.cooldown(1,20, commands.BucketType.guild)
async def fact(ctx):
    factss = [1, 2]
    e = random.choice(factss)
    if e == 1:
        facts = [facta.title for facta in reddit.subreddit("funfacts").hot(limit=30)]
        EfactE = await gembed(desc="Presented by CapistalistMC", tit=random.choice(facts))
    elif e == 2:
        facts = [facta.title for facta in reddit.subreddit("RandomFacts").hot(limit=30)]
        EfactE = await gembed(desc="Presented by CapistalistMC", tit=f"Fun Fact: {random.choice(facts)}")
    await ctx.send(embed=EfactE)

@client.command()
@commands.cooldown(3,60, commands.BucketType.user)
async def meme(ctx, format, *, text = None):
    formats = await config_j("formats")
    print(type(formats))
    if format == 'formats' or format == 'templates':
        desc = ''
        for form in formats:
            desc += f'{form}\n'
        EformE = await gembed(tit=f"FORMATS", desc = f"Here are the available formats:\n{desc}")
        await ctx.send(embed=EformE)
        return
    if not format.lower() in formats:
        desc = ''
        for form in formats:
            desc += f'{form}\n'
        EformE = await error_emb("Wrong Format", {"formats": desc})
        await ctx.send(embed=EformE)
        return
    aa = text.split(sep='; ', maxsplit=1)
    text = ""
    longer =''
    if len(aa) == 2:
        for line in aa:
            text += f"{line}\n\n"
        if len(aa[0]) > len (aa[1]):
            longer = aa[0]
        else:
            longer = aa[1]
    else:
        longer = aa[0]
        text = aa[0]

    img = Image.open(f"{format}.png")
    draw = ImageDraw.Draw(img)
    fontsize = 1
    font = ImageFont.truetype("sans.ttf", fontsize)
    while font.getsize(longer)[0] < 0.9*img.size[0]:
        fontsize += 1
        font = ImageFont.truetype("sans.ttf", fontsize)
    fontsize -= 1
    if fontsize > img.size[0]/15:
        fontsize = img.size[0]/15
    font = ImageFont.truetype("sans.ttf", int(fontsize))
    draw.text((10, 10),f"{text}",(0,0,0),font=font)
    img.save(f'memeOut/{ctx.author.id}-{format}.png')
    # EmemeE.set_image(url=f"attachment://image.png")
    file = discord.File(f"memeOut/{ctx.author.id}-{format}.png", filename=f"{ctx.author.id}-{format}.png")
    await ctx.send(file=file)

    file = f'{ctx.author.id}-{format}.png'
    location = f"{os.getcwd()}/memeOut"
    path = os.path.join(location, file)
    os.remove(path)


# @client.command()
# @commands.cooldown(2,30, commands.BucketType.user)
# async def imgsearch(ctx, *, img):
#     login = {
#             'Authorization': 'Client-ID '
#         }
#     animalz = await request(f"https://api.imgur.com/3/gallery/search?q={img.replace(' ', '%20')}", headers=login)
#     animalzz = await jsonify(animalz)
#     try:
#         img = animalzz["data"][0]
#     except IndexError:
#         e = await gembed("No results were found! D:")
#         await ctx.send(embed=e)
#         return
#     except:
#         e = await gembed(f"Some error happened, DM shady about it!")
#         await ctx.send(embed=e)
#         return

#     print(img)
#     # if img["type"].startswith("video"):
#     #     e = await gembed("No good results were found! D:", col=0xff0000)
#     #     await ctx.send(embed=e)
#     #     return

#     # url = img["link"]

#     # print(url)
#     # e = await gembed(desc="\n")
#     # e.set_image(url=url)
#     # await ctx.send(embed=e)


@client.command()
@commands.cooldown(2,30, commands.BucketType.user)
async def inspire(ctx):
    animalz = await request(f"https://www.affirmations.dev")
    animalzz = await jsonify(animalz)
    response = animalzz["affirmation"]
    await ctx.send(response)

@client.command()
@commands.cooldown(2,15, commands.BucketType.user)
async def nerd(ctx, animal=None):
    e = random.randint(0, 500)
    s = await request(f"http://numbersapi.com/{e}")
    await ctx.send(embed=await gembed(s))

@client.command()
@commands.cooldown(2,15, commands.BucketType.user)
async def animal(ctx, animal=None):
    animals= ["foxes", "cats", "dogs", "birds", "fox", "cat", "dog", "bird", "panda", "pandas", "koala", "koalas", "goat", "goats"]
    trueanimal = ["foxes", "cats", "dogs", "birds", "pandas", "koalas", "goats"]

    if animal is None:
        animal = random.choice(animals)

    elif animal == "list":
        desc = "Here is the list of supported animals:"
        for ass in trueanimal:
            desc += f"{ass}\n"
        ee = await gembed(desc)
        await ctx.send(embed=ee)
        return

    animal = animal.lower()

    if animal not in animals:
        await ctx.send("Sadly, thats not an animal supported yet. Dw tho, here is a random picture of an animal")
        animal = random.choice(animals)


    if animal == "fox" or animal == "foxes":
        fox = await request("https://randomfox.ca/floof/")
        foxes = await jsonify(fox)
        url = foxes["image"]
    elif animal == "cat" or animal == "cats":
        log= {
        'X-API-KEY': CAT_API_KEY,
        }
        cat = await request("https://api.thecatapi.com/v1/images/search?limit=1", headers=log)
        catlist = await newlist(cat)
        cats = await jsonify(catlist[0])
        url = cats["url"]
    elif animal == "dog" or animal == "dogs":
        animalz = await request("https://some-random-api.ml/img/dog")
        animalzz = await jsonify(animalz)
        url = animalzz["link"]
    elif animal == "bird" or animal == "birds":
        animalz = await request("https://shibe.online/api/birds")
        lists = await newlist(animalz)

        url = lists[0].replace("'", "").replace("\"", "")

    elif animal == "panda" or animal == "pandas":
        animalz = await request("https://some-random-api.ml/img/panda")
        animalzz = await jsonify(animalz)
        url = animalzz["link"]
    elif animal == "koala" or animal == "koalas":
        animalz = await request("https://some-random-api.ml/img/koala")
        animalzz = await jsonify(animalz)
        url = animalzz["link"]
    elif animal == "goat" or animal == "goats":
        login = {
            'Authorization': 'Client-ID'
        }
        animalz = await request("https://api.imgur.com/3/gallery/search?q=goats", headers=login)
        animalzz = await jsonify(animalz)
        result = random.randint(0, 25)
        img = animalzz["data"][result]["images"][0]

        while (img["is_ad"] or img["type"] == "video/mp4"):
            result = random.randint(0, 50)
            img = animalzz["data"][result]["images"][0]


        print(img["type"])
        url = img["link"]

    print(url)
    e = await gembed(desc="\n")
    e.set_image(url=url)
    await ctx.send(embed=e)

@client.command()
async def quote(ctx, link: discord.Message):
    quote = link.content
    aut = link.author
    time = link.created_at

    e = await gembed(desc=f"*\"{quote}\"* - {aut.mention}, {time.strftime('%A %d. %B %Y')}")
    await ctx.send(embed=e)
    chan = client.get_channel(744230941894901810)
    await chan.send(embed=e)

#--------------------------------------------------------------------------------------------------------
#events
#--------------------------------------------------------------------------------------------------------
@client.event
async def on_member_join(member):
    roles = await config_j("join roles")
    for role in roles:
        roli = server.get_role(role)
        await member.add_roles(roli)
        print(roli.name)
    print("Obama is here :)")

@client.event
async def on_message(m):
    words = await config_two_j("Moderation", "bad words")
    channel_ids = await config_j("Channel IDs")
    if m.author.id == client.user.id:
        return
    if m.content == '-purge':
        await client.process_commands(m)
        return
    if m.channel.id == int(channel_ids["Suggestions"]):
        EsuggE = await gembed(tit=m.content, desc="Dont forget that :white_check_mark: is to agree, and :x: is to dis agree")
        EsuggE.set_author(name=f"{m.author.name}", icon_url=f"{m.author.avatar_url}")
        sugchan = client.get_channel(int(channel_ids["Suggestions"]))
        sug = await sugchan.send(embed=EsuggE)
        await m.delete()
        await sug.add_reaction("✅")
        await sug.add_reaction("❌")
    if any(word in m.content.lower() for word in words):
        if m.guild.get_role(staff_id) in m.author.roles:
            return
        if m.channel.id == channel_ids["Console"]:
            return
        if m.channel.id == channel_ids["Server Chat"]:
            return
        await m.delete()

        await warn(client.user, m.author, str(await config_two("Moderation", "Bad Word Reason")))
    if m.channel.id == int(channel_ids["Chat With Bot"]):
        if m.content.startswith("> "):
            return
        animalz = await request(f"https://some-random-api.ml/chatbot?message={m.content}")
        animalzz = await jsonify(animalz)
        response = animalzz["response"]
        e = await gembed(desc=f"To {m.author.mention}, {response}")
        await m.channel.send(embed=e)

    await client.process_commands(m)

@client.event
async def on_raw_reaction_add(payload):
    channels = await config_j("Channel IDs")
    if payload.guild_id is None and str(payload.emoji) == "\u2705":
        channel = await client.fetch_channel(payload.channel_id)
        msgggg = await channel.fetch_message(payload.message_id)
        if msgggg.content == 'Jobxyz2420' and int(msgggg.author.id) == 701768118531522631:

            await msgggg.edit(content="")

            boardrole = server.get_role(staff_id)
            member = server.get_member(payload.user_id)
            overwrites = {
                server.default_role: discord.PermissionOverwrite(read_messages=False),
                member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                boardrole: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            jobzebra = await config_j("jobs")
            channel = await server.create_text_channel(f'Application - {member.name}', category=client.get_channel(719291231787679746), overwrites=overwrites)
            EappE = await gembed(jobzebra["application"], tit="Application!")
            await channel.send("@everyone, a new application!", embed=EappE)
            return
        else:
            await removereaction()
            print("Big Tits")
            return
    if payload.member.id == client.user.id:
        return
    if payload.channel_id == channels["Suggestions"]:
        await removereaction()
        return
    elif payload.channel_id == channels["Tasks"]:
        emojizz = await config_j("Tasks")
        jz_claim = emojizz["Claim"]
        jz_done = emojizz["Done"]
        jz_drop = emojizz["Drop"]
        channel = client.get_channel(payload.channel_id)
        logchan = client.get_channel(channels["Task Log"])
        task = await channel.fetch_message(payload.message_id)
        if str(payload.emoji) == jz_claim:
            EclaimE = task.embeds[0]
            if len(EclaimE.fields) == 1:
                return
            EclaimE.color = 0xff0000
            EclaimE.add_field(name="Claimed", value=f"Claimed by: {payload.member.mention}", inline=False)
            await task.edit(content=f"{payload.member.id}",embed=EclaimE)
            await logchan.send(embed=EclaimE, content=f"{payload.member} took this task")
            await task.remove_reaction(jz_claim, payload.member)
            return
        if str(payload.emoji) == jz_done:
            if not int(payload.member.id) == int(task.content):
                await task.remove_reaction(jz_done, payload.member)
                return
            EclaimE = task.embeds[0]
            await logchan.send(embed=EclaimE, content=f"This task has been doned")
            await task.delete()
            return
        if str(payload.emoji) == jz_drop:
            if not payload.member.id == int(task.content):
                await task.remove_reaction(jz_drop, payload.member)
                return
            EclaimE = task.embeds[0]
            if len(EclaimE.fields) == 0:
                return
            EclaimE.color = 0x00ff00
            EclaimE.clear_fields()
            await task.edit(content=f"",embed=EclaimE)
            await logchan.send(embed=EclaimE, content=f"This task has been freed")
            await task.remove_reaction(jz_drop, payload.member)
            return
        return
    elif payload.channel_id == channels["Poll"]:
        await removereaction()
        return
    elif payload.channel_id == channels["Buy Ranks"]:
        msgs = await config_two_j("shop", "Msg")
        if payload.message_id == msgs["WorkingClass"]:
            await shop("WorkingClass", payload)
        elif payload.message_id == msgs["RichBoi"]:
            await shop("WorkingClass", payload)
        elif payload.message_id == msgs["Pasta"]:
            await shop("WorkingClass", payload)

        await removereaction()
        return


#--------------------------------------------------------------------------------------------------------
# music, taken from the example of wavelink
#--------------------------------------------------------------------------------------------------------

class NoChannelProvided(commands.CommandError):
    """Error raised when no suitable voice channel was supplied."""
    pass
class IncorrectChannelError(commands.CommandError):
    """Error raised when commands are issued outside of the players session channel."""
    pass
class Track(wavelink.Track):
    """Wavelink Track object with a requester attribute."""

    __slots__ = ('requester', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args)

        self.requester = kwargs.get('requester')
class Player(wavelink.Player):
    """Custom wavelink Player class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.context: commands.Context = kwargs.get('context', None)
        if self.context:
            self.dj: discord.Member = self.context.author

        self.queue = asyncio.Queue()
        self.controller = None

        self.waiting = False
        self.updating = False

        self.pause_votes = set()
        self.resume_votes = set()
        self.skip_votes = set()
        self.shuffle_votes = set()
        self.stop_votes = set()

    async def do_next(self) -> None:
        if self.is_playing or self.waiting:
            return

        # Clear the votes for a new song...
        self.pause_votes.clear()
        self.resume_votes.clear()
        self.skip_votes.clear()
        self.shuffle_votes.clear()
        self.stop_votes.clear()

        try:
            self.waiting = True
            with async_timeout.timeout(300):
                track = await self.queue.get()
        except asyncio.TimeoutError:
            # No music has been played for 5 minutes, cleanup and disconnect...
            return await self.teardown()

        await self.play(track)
        self.waiting = False

        # Invoke our players controller...
        await self.invoke_controller()

    async def invoke_controller(self) -> None:
        """Method which updates or sends a new player controller."""
        if self.updating:
            return

        self.updating = True

        if not self.controller:
            self.controller = InteractiveController(embed=self.build_embed(), player=self)
            await self.controller.start(self.context)

        elif not await self.is_position_fresh():
            try:
                await self.controller.message.delete()
            except discord.HTTPException:
                pass

            self.controller.stop()

            self.controller = InteractiveController(embed=self.build_embed(), player=self)
            await self.controller.start(self.context)

        else:
            embed = self.build_embed()
            await self.controller.message.edit(content=None, embed=embed)

        self.updating = False

    def build_embed(self) -> None:
        """Method which builds our players controller embed."""
        track = self.current
        if not track:
            return

        channel = self.bot.get_channel(int(self.channel_id))
        qsize = self.queue.qsize()

        usr = client.get_user(376079696489742338)
        embed = discord.Embed(title=f'Music Controller | {channel.name}', colour=0x216ade)
        embed.set_footer(text="Bot made by Shady Goat, on shadygoat.eu", icon_url=usr.avatar_url)
        embed.description = f'Now Playing:\n**`{track.title}`**\n\n'
        embed.set_thumbnail(url=track.thumb)
        embed.add_field(name='Duration', value=str(datetime.timedelta(milliseconds=int(track.length))))
        embed.add_field(name='Volume', value=f'**`{self.volume}%`**')
        embed.add_field(name='Requested By', value=track.requester.mention)
        return embed

    async def is_position_fresh(self) -> bool:
        """Method which checks whether the player controller should be remade or updated."""
        try:
            async for message in self.context.channel.history(limit=5):
                if message.id == self.controller.message.id:
                    return True
        except (discord.HTTPException, AttributeError):
            return False

        return False

    async def teardown(self):
        """Clear internal states, remove player controller and disconnect."""
        try:
            await self.controller.message.delete()
        except discord.HTTPException:
            pass

        self.controller.stop()

        try:
            await self.destroy()
        except KeyError:
            pass
class InteractiveController(menus.Menu):
    """The Players interactive controller menu class."""

    def __init__(self, *, embed: discord.Embed, player: Player):
        super().__init__(timeout=None)

        self.embed = embed
        self.player = player

    def update_context(self, payload: discord.RawReactionActionEvent):
        """Update our context with the user who reacted."""
        ctx = copy.copy(self.ctx)
        ctx.author = payload.member

        return ctx

    def reaction_check(self, payload: discord.RawReactionActionEvent):
        if payload.event_type == 'REACTION_REMOVE':
            return False

        if not payload.member:
            return False
        if payload.member.bot:
            return False
        if payload.message_id != self.message.id:
            return False
        if payload.member not in self.bot.get_channel(int(self.player.channel_id)).members:
            return False

        return payload.emoji in self.buttons

    async def send_initial_message(self, ctx: commands.Context, channel: discord.TextChannel) -> discord.Message:
        return await channel.send(embed=self.embed)

    @menus.button(emoji='\u25B6')
    async def resume_command(self, payload: discord.RawReactionActionEvent):
        """Resume button."""
        ctx = self.update_context(payload)

        command = self.bot.get_command('resume')
        ctx.command = command

        await self.bot.invoke(ctx)

    @menus.button(emoji='\u23F8')
    async def pause_command(self, payload: discord.RawReactionActionEvent):
        """Pause button"""
        ctx = self.update_context(payload)

        command = self.bot.get_command('pause')
        ctx.command = command

        await self.bot.invoke(ctx)

    @menus.button(emoji='\u23F9')
    async def stop_command(self, payload: discord.RawReactionActionEvent):
        """Stop button."""
        ctx = self.update_context(payload)

        command = self.bot.get_command('stop')
        ctx.command = command

        await self.bot.invoke(ctx)

    @menus.button(emoji='\u23ED')
    async def skip_command(self, payload: discord.RawReactionActionEvent):
        """Skip button."""
        ctx = self.update_context(payload)

        command = self.bot.get_command('skip')
        ctx.command = command

        await self.bot.invoke(ctx)

    @menus.button(emoji='\U0001F500')
    async def shuffle_command(self, payload: discord.RawReactionActionEvent):
        """Shuffle button."""
        ctx = self.update_context(payload)

        command = self.bot.get_command('shuffle')
        ctx.command = command

        await self.bot.invoke(ctx)

    @menus.button(emoji='\u2795')
    async def volup_command(self, payload: discord.RawReactionActionEvent):
        """Volume up button"""
        ctx = self.update_context(payload)

        command = self.bot.get_command('vol_up')
        ctx.command = command

        await self.bot.invoke(ctx)

    @menus.button(emoji='\u2796')
    async def voldown_command(self, payload: discord.RawReactionActionEvent):
        """Volume down button."""
        ctx = self.update_context(payload)

        command = self.bot.get_command('vol_down')
        ctx.command = command

        await self.bot.invoke(ctx)

    @menus.button(emoji='\U0001F1F6')
    async def queue_command(self, payload: discord.RawReactionActionEvent):
        """Player queue button."""
        ctx = self.update_context(payload)

        command = self.bot.get_command('queue')
        ctx.command = command

        await self.bot.invoke(ctx)
class PaginatorSource(menus.ListPageSource):
    """Player queue paginator class."""

    def __init__(self, entries, *, per_page=8):
        super().__init__(entries, per_page=per_page)

    async def format_page(self, menu: menus.Menu, page):
        embed = await gembed("temp", tit="Coming up...")
        embed.description = '\n'.join(f'`{index}. {title}`' for index, title in enumerate(page, 1))

        return embed

    def is_paginating(self):
        # We always want to embed even on 1 page of results...
        return True

class Music(commands.Cog, wavelink.WavelinkMixin):
    """Music Cog."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        if not hasattr(bot, 'wavelink'):
            bot.wavelink = wavelink.Client(bot=bot)

        bot.loop.create_task(self.start_nodes())

    async def start_nodes(self) -> None:
        """Connect and intiate nodes."""
        await self.bot.wait_until_ready()

        if self.bot.wavelink.nodes:
            previous = self.bot.wavelink.nodes.copy()

            for node in previous.values():
                await node.destroy()

        nodes = {'MAIN': {'host': '.',
                          'port': 12,
                          'rest_uri': '.',
                          'password': '.',
                          'identifier': 'MAIN',
                          'region': 'europe'
                          }}

        for n in nodes.values():
            await self.bot.wavelink.initiate_node(**n)

    @wavelink.WavelinkMixin.listener()
    async def on_node_ready(self, node: wavelink.Node):
        print(f'Node {node.identifier} is ready!')

    @wavelink.WavelinkMixin.listener('on_track_stuck')
    @wavelink.WavelinkMixin.listener('on_track_end')
    @wavelink.WavelinkMixin.listener('on_track_exception')
    async def on_player_stop(self, node: wavelink.Node, payload):
        await payload.player.do_next()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member.bot:
            return

        player: Player = self.bot.wavelink.get_player(member.guild.id, cls=Player)

        if not player.channel_id or not player.context:
            player.node.players.pop(member.guild.id)
            return

        channel = self.bot.get_channel(int(player.channel_id))

        if member == player.dj and after.channel is None:
            for m in channel.members:
                if m.bot:
                    continue
                else:
                    player.dj = m
                    return

        elif after.channel == channel and player.dj not in channel.members:
            player.dj = member

    async def cog_command_error(self, ctx: commands.Context, error: Exception):
        """Cog wide error handler."""
        if isinstance(error, IncorrectChannelError):
            return

        if isinstance(error, NoChannelProvided):
            return await ctx.send('You must be in a voice channel or provide one to connect to.')

    async def cog_check(self, ctx: commands.Context):
        """Cog wide check, which disallows commands in DMs."""
        if not ctx.guild:
            await ctx.send('Music commands are not available in Private Messages.')
            return False

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        """Coroutine called before command invocation.
        We mainly just want to check whether the user is in the players controller channel.
        """
        player: Player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player, context=ctx)

        if player.context:
            if player.context.channel != ctx.channel:
                await ctx.send(f'{ctx.author.mention}, you must be in {player.context.channel.mention} for this session.')
                raise IncorrectChannelError

        if ctx.command.name == 'connect' and not player.context:
            return
        elif self.is_privileged(ctx):
            return

        if not player.channel_id:
            return

        channel = self.bot.get_channel(int(player.channel_id))
        if not channel:
            return

        if player.is_connected:
            if ctx.author not in channel.members:
                await ctx.send(f'{ctx.author.mention}, you must be in `{channel.name}` to use voice commands.')
                raise IncorrectChannelError

    def required(self, ctx: commands.Context):
        """Method which returns required votes based on amount of members in a channel."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)
        channel = self.bot.get_channel(int(player.channel_id))
        required = math.ceil((len(channel.members) - 1) / 2.5)

        if ctx.command.name == 'stop':
            if len(channel.members) - 1 == 2:
                required = 2

        return required

    def is_privileged(self, ctx: commands.Context):
        """Check whether the user is an Admin or DJ."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        return player.dj == ctx.author or ctx.author.guild_permissions.kick_members

    @commands.command()
    async def connect(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None):
        """Connect to a voice channel."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if player.is_connected:
            return

        channel = getattr(ctx.author.voice, 'channel', channel)
        if channel is None:
            raise NoChannelProvided

        await player.connect(channel.id)

    @commands.command()
    async def play(self, ctx: commands.Context, *, query: str):
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            await ctx.invoke(self.connect)

        query = query.strip('<>')
        if not validators.url(query):
            query = f'ytsearch:{query}'

        tracks = await self.bot.wavelink.get_tracks(query)
        if not tracks:
            return await ctx.send(embed=await error_emb('Nothing found'), delete_after=15)



        if isinstance(tracks, wavelink.TrackPlaylist):
            for track in tracks.tracks:
                track = Track(track.id, track.info, requester=ctx.author)
                await player.queue.put(track)

            await ctx.send(embed=await gembed(f'Added the playlist {tracks.data["playlistInfo"]["name"]}\nwith {len(tracks.tracks)} songs to the queue'), delete_after=15)
        else:
            track = Track(tracks[0].id, tracks[0].info, requester=ctx.author)
            await ctx.send(embed=await gembed(f'Added {track.title} to the Queue'), delete_after=15)
            await player.queue.put(track)

        if not player.is_playing:
            await player.do_next()

    @commands.command()
    async def pause(self, ctx: commands.Context):
        """Pause the currently playing song."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if player.is_paused or not player.is_connected:
            return

        if self.is_privileged(ctx):
            await ctx.send(embed=await gembed('An admin or DJ has paused the player.'), delete_after=10)
            player.pause_votes.clear()

            return await player.set_pause(True)

        required = self.required(ctx)
        player.pause_votes.add(ctx.author)

        if len(player.pause_votes) >= required:
            await ctx.send(embed= await gembed('Vote to pause passed. Pausing player.'), delete_after=10)
            player.pause_votes.clear()
            await player.set_pause(True)
        else:
            await ctx.send(embed=await gembed(f'{ctx.author.mention} has voted to pause the player.'), delete_after=15)

    @commands.command()
    async def resume(self, ctx: commands.Context):
        """Resume a currently paused player."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_paused or not player.is_connected:
            return

        if self.is_privileged(ctx):
            await ctx.send(embed=await gembed('An admin or DJ has resumed the player.'), delete_after=10)
            player.resume_votes.clear()

            return await player.set_pause(False)

        required = self.required(ctx)
        player.resume_votes.add(ctx.author)

        if len(player.resume_votes) >= required:
            await ctx.send(embed=await gembed('Vote to resume passed. Resuming player.'), delete_after=10)
            player.resume_votes.clear()
            await player.set_pause(False)
        else:
            await ctx.send(embed=await gembed(f'{ctx.author.mention} has voted to resume the player.'), delete_after=15)

    @commands.command()
    async def skip(self, ctx: commands.Context):
        """Skip the currently playing song."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        if self.is_privileged(ctx):
            await ctx.send(embed=await gembed('An admin or DJ has skipped the song.'), delete_after=10)
            player.skip_votes.clear()

            return await player.stop()

        if ctx.author == player.current.requester:
            await ctx.send(embed=await gembed('The song requester has skipped the song.'), delete_after=10)
            player.skip_votes.clear()

            return await player.stop()

        required = self.required(ctx)
        player.skip_votes.add(ctx.author)

        if len(player.skip_votes) >= required:
            await ctx.send(embed=await gembed('Vote to skip passed. Skipping song.'), delete_after=10)
            player.skip_votes.clear()
            await player.stop()
        else:
            await ctx.send(embed=await gembed(f'{ctx.author.mention} has voted to skip the song.'), delete_after=15)

    @commands.command()
    async def stop(self, ctx: commands.Context):
        """Stop the player and clear all internal states."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        if self.is_privileged(ctx):
            await ctx.send(embed=await gembed('An admin or DJ has stopped the player.'), delete_after=10)
            return await player.teardown()

        required = self.required(ctx)
        player.stop_votes.add(ctx.author)

        if len(player.stop_votes) >= required:
            await ctx.send(embed=await gembed('Vote to stop passed. Stopping the player.'), delete_after=10)
            await player.teardown()
        else:
            await ctx.send(embed=await gembed(f'{ctx.author.mention} has voted to stop the player.'), delete_after=15)

    @commands.command(aliases=['v', 'vol'])
    async def volume(self, ctx: commands.Context, *, vol: int):
        """Change the players volume, between 1 and 100."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        if not self.is_privileged(ctx):
            raise commands.MissingRole

        if not 0 < vol < 101:
            return await ctx.send(embed=await error_emb("1-100 needed"))

        await player.set_volume(vol)
        await ctx.send(embed=await gembed(f'Set the volume to **{vol}**%'), delete_after=7)

    @commands.command(aliases=['mix'])
    async def shuffle(self, ctx: commands.Context):
        """Shuffle the players queue."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        if player.queue.qsize() < 3:
            return await ctx.send(embed=await error_emb("More Songs Shuffle"), delete_after=15)

        if self.is_privileged(ctx):
            await ctx.send(embed=await gembed('An admin or DJ has shuffled the playlist.'), delete_after=10)
            player.shuffle_votes.clear()
            return random.shuffle(player.queue._queue)

        required = self.required(ctx)
        player.shuffle_votes.add(ctx.author)

        if len(player.shuffle_votes) >= required:
            await ctx.send(embed=await gembed('Vote to shuffle passed. Shuffling the playlist.'), delete_after=10)
            player.shuffle_votes.clear()
            random.shuffle(player.queue._queue)
        else:
            await ctx.send(embed=await gembed(f'{ctx.author.mention} has voted to shuffle the playlist.'), delete_after=15)

    @commands.command(hidden=True)
    async def vol_up(self, ctx: commands.Context):
        """Command used for volume up button."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        elif self.is_privileged(ctx):
            raise commands.MissingRole


        vol = int(math.ceil((player.volume + 10) / 10)) * 10

        if vol > 100:
            vol = 100
            await ctx.send(embed=await error_emb("Max Vol"), delete_after=7)

        await player.set_volume(vol)

    @commands.command(hidden=True)
    async def vol_down(self, ctx: commands.Context):
        """Command used for volume down button."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected or not self.is_privileged(ctx):
            return

        vol = int(math.ceil((player.volume - 10) / 10)) * 10

        if vol < 0:
            vol = 0
            await ctx.send(embed=await error_emb('Min Vol'), delete_after=10)

        await player.set_volume(vol)

    @commands.command(aliases=['eq'])
    async def equalizer(self, ctx: commands.Context, *, equalizer: str):
        """Change the players equalizer."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        if not self.is_privileged(ctx):
            raise commands.MissingRole

        eqs = {'flat': wavelink.Equalizer.flat(),
               'metal': wavelink.Equalizer.metal(),
               'piano': wavelink.Equalizer.piano()}

        eq = eqs.get(equalizer.lower(), None)

        if not eq:
            joined = "\n".join(eqs.keys())
            return await ctx.send(embed=await error_emb(f'EQ error', {"eqs": joined}))

        await ctx.send(embed=await gembed(f'Successfully changed equalizer to {equalizer}'), delete_after=15)
        await player.set_eq(eq)

    @commands.command(aliases=['q', 'que'])
    async def queue(self, ctx: commands.Context):
        """Display the players queued songs."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        if player.queue.qsize() == 0:
            return await ctx.send(embed=await error_emb("Queue Empty"), delete_after=15)

        entries = [track.title for track in player.queue._queue]
        pages = PaginatorSource(entries=entries)
        paginator = menus.MenuPages(source=pages, timeout=None, delete_message_after=True)

        await paginator.start(ctx)

    @commands.command(aliases=['np', 'now_playing', 'current'])
    async def nowplaying(self, ctx: commands.Context):
        """Update the player controller."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        await player.invoke_controller()

    @commands.command(aliases=['swap'])
    async def swap_dj(self, ctx: commands.Context, *, member: discord.Member = None):
        """Swap the current DJ to another member in the voice channel."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        if not self.is_privileged(ctx):
            raise commands.MissingAnyRole

        members = self.bot.get_channel(int(player.channel_id)).members

        if member and member not in members:
            return await ctx.send(embed=await error_emb(f'Not on VC', {"member": member}), delete_after=15)

        if member and member == player.dj:
            return await ctx.send(embed=await error_emb('Alr DJ'), delete_after=15)

        if len(members) <= 2:
            return await ctx.send(embed=await error_emb("No more DJ"), delete_after=15)

        if member:
            player.dj = member
            return await ctx.send(embed=await gembed(f'{member.mention} is now the DJ.'))

        for m in members:
            if m == player.dj or m.bot:
                continue
            else:
                player.dj = m
                return await ctx.send(embed=await gembed(f'{member.mention} is now the DJ.'))

client.add_cog(Music(client))

#--------------------------------------------------------------------------------------------------------
#erorrz
#--------------------------------------------------------------------------------------------------------

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        EE =await error_emb("Missing an argument")
    elif isinstance(error, commands.MissingRole) or isinstance(error, commands.MissingAnyRole):
        EE =await error_emb("Missing Role")
    elif isinstance(error, commands.CommandNotFound):
        EE =await error_emb("Missing Command")
    elif isinstance(error, commands.CommandOnCooldown):
        EE =await error_emb("Cooldown")
    elif isinstance(error, WrongChan):
        EE =await error_emb("Not Bot Spam")
    elif isinstance(error, commands.NoPrivateMessage):
        EE = await error_emb("No Private Chan")
    elif isinstance(error, NameError):
        EE = await error_emb("Bad Code")
    else:
        raise error
    await ctx.send(embed=EE, delete_after=3)


client.run(token)
