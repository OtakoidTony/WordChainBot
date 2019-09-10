import random
import discord
import json
from alliteration import *

client = discord.Client()

with open('kkutu.txt', 'rt', encoding='utf-8') as f:
    s = f.read()

with open('user_info.json', 'r', encoding='utf-8') as file:
    user_info = json.load(file)
    user_card = user_info

with open('user_info.json', 'w', encoding='utf-8') as file:
    file.write(json.dumps(user_card, ensure_ascii=False, indent=4))

pat = re.compile('^[ㄱ-ㅎ가-힣]+$')
wordDict = dict()
hanbangSet = set()

for i in sorted([i for i in s.split() if pat.match(i) and len(i) >= 2], key=lambda x: -len(x)):
    if i[0] not in wordDict:
        wordDict[i[0]] = set()
    wordDict[i[0]].add(i)

delList = list()
for i in wordDict:
    for j in wordDict[i]:
        if j[-1] not in wordDict:
            delList.append(j)
for j in delList:
    hanbangSet.add(j)
    wordDict[j[0]].remove(j)


@client.event
async def on_ready():
    print('Korean_Game_Bot Online')

each_server = {
    "606362634131865602": {
        "alreadySet": set(),
        "round": 0,
        "win": 0,
        "lose": 0,
        "who": "CPU",
        "lastWord": "",
        "firstLetter": "",
        "firstTurn": True,
        "resetRound": False,
        "isPlaying": False
    }
}

def patch_data(dict, null_name, null_data):
    if not (null_name in dict):
        dict[null_name] = null_data

@client.event
async def on_message(message):
    channel = message.channel
    server_id = message.guild.id

    if not (str(server_id) in each_server):
        each_server[str(server_id)] = {
            "alreadySet": set(),
            "round": 0,
            "win": 0,
            "lose": 0,
            "who": "CPU",
            "lastWord": "",
            "firstLetter": "",
            "firstTurn": True,
            "resetRound": False,
            "isPlaying": False,
            "error": False
        }

    this_server = each_server[str(server_id)]



    if message.author.bot:
        return None

    if message.content in ['!끝말', '!끝말잇기', '!끝말카드']:
        if '!끝말' == message.content or '!끝말잇기' == message.content:
            embed = discord.Embed(title="끝말있기 채팅봇",
                                  description="Programmed by OtakoidTony")
            embed.add_field(name="시작", value="`!start` 또는 `!시작`", inline=True)
            embed.add_field(name="기권", value="`!exit`  또는 `!기권`", inline=True)
            embed.add_field(name="프로필 보기", value="`!끝말카드`", inline=False)
            await channel.send("", embed=embed)
        if message.content == "!끝말카드":
            if not (str(message.author.id) in user_card):
                user_card[str(message.author.id)] = {
                    "user": message.author.name,
                    "level": 1,
                    "word": 0,
                    "win": 0,
                    "length": 0
                }
            with open('user_info.json', 'w', encoding='utf-8') as file:
                file.write(json.dumps(user_card, ensure_ascii=False, indent=4))
            embed = discord.Embed(title=message.author.name,
                                  description=str(message.author.id))
            embed.add_field(name="레벨", value=str(user_card[str(message.author.id)]["level"]), inline=True)
            embed.add_field(name="승리", value=str(user_card[str(message.author.id)]["win"]), inline=True)
            embed.add_field(name="단어", value=str(user_card[str(message.author.id)]["word"]), inline=True)
            embed.add_field(name="글자", value=str(user_card[str(message.author.id)]["length"]), inline=True)
            await channel.send("", embed=embed)
    else:
        if message.channel.name == "끝말잇기":

            if not (str(message.author.id) in user_card):
                user_card[str(message.author.id)] = {
                    "user": message.author.name,
                    "level": 1,
                    "word": 0,
                    "win": 0,
                    "length": 0
                }

            with open('user_info.json', 'w', encoding='utf-8') as file:
                file.write(json.dumps(user_card, ensure_ascii=False, indent=4))

            if ('!start' == message.content or '!시작' == message.content) and (not this_server["isPlaying"]):
                this_server["round"] += 1

                embed = discord.Embed(title=str(this_server["round"]) + "라운드를 시작합니다. 현재 " + str(this_server["win"]) + "승 " + str(this_server["lose"]) + "패",
                                      description="기권하시려면 `!exit`  또는 `!기권`을 입력해주시기 바랍니다.")
                await channel.send("", embed=embed)

                this_server["lastWord"] = ''
                this_server["alreadySet"] = set()
                this_server["firstTurn"], this_server["resetRound"], this_server["isPlaying"] = True, False, True
                this_server["who"] = 'CPU'

            if this_server["isPlaying"] and this_server["who"] == 'CPU':
                if this_server["firstTurn"]:
                    this_server["lastWord"] = random.choice(list(wordDict[random.choice(list(wordDict.keys()))]))
                    this_server["alreadySet"].add(this_server["lastWord"])
                    await channel.send(' CPU : ' + this_server["lastWord"])
                    this_server["who"] = 'USER'
                    this_server["firstTurn"] = False

            if this_server["isPlaying"] and this_server["who"] == 'USER' and not message.author.bot and not this_server["firstTurn"]:
                yourWord = message.content
                if yourWord == '!exit' or yourWord == '!기권':
                    await channel.send('[결과] 당신은 기권했습니다. CPU의 승리입니다!')
                    this_server["resetRound"] = True
                    this_server["isPlaying"] = False
                    this_server["lose"] += 1
                    this_server["who"] = 'CPU'
                    this_server["error"] = False

                this_server["firstLetter"] = yourWord[0]
                if (this_server["firstLetter"] != this_server["lastWord"][-1]) and not checkDueum(this_server["lastWord"][-1], this_server["firstLetter"]):
                    await channel.send(" [오류] '" + this_server["lastWord"][-1] + "' (으)로 시작하는 단어를 입력하세요.")
                    this_server["who"] = 'USER'
                    this_server["error"] = True
                elif yourWord in hanbangSet:
                    await channel.send(' [오류] 한방단어는 사용할 수 없습니다.')
                    this_server["who"] = 'USER'
                    this_server["error"] = True
                elif yourWord in this_server["alreadySet"]:
                    await channel.send(' [오류] 이미 나온 단어입니다.')
                    this_server["who"] = 'USER'
                    this_server["error"] = True
                elif yourWord not in wordDict.get(this_server["firstLetter"], set()):
                    await channel.send(' [오류] 사전에 없는 단어입니다.')
                    this_server["who"] = 'USER'
                    this_server["error"] = True

                if not this_server["error"]:
                    this_server["who"] = 'CPU'
                    this_server["alreadySet"].add(yourWord)
                    this_server["lastWord"] = yourWord
                    user_card[str(message.author.id)]["word"] += 1
                    user_card[str(message.author.id)]["length"] += len(yourWord)
                    with open('user_info.json', 'w', encoding='utf-8') as file:
                        file.write(json.dumps(user_card, ensure_ascii=False, indent=4))
                    this_server["firstLetter"] = this_server["lastWord"][-1]
                    if not list(filter(lambda x: x not in this_server["alreadySet"], wordDict.get(this_server["firstLetter"], set()))):
                        # 라운드 종료
                        await channel.send('[결과] CPU가 기권했습니다. 당신의 승리입니다!')
                        this_server["who"] = 'CPU'
                        this_server["isPlaying"] = False
                        this_server["win"] += 1
                        user_card[str(message.author.id)]["win"] += 1
                        with open('user_info.json', 'w', encoding='utf-8') as file:
                            file.write(json.dumps(user_card, ensure_ascii=False, indent=4))
                    else:
                        nextWords = sorted(filter(lambda x: x not in this_server["alreadySet"], wordDict[this_server["firstLetter"]]),
                                           key=lambda x: -len(x))[
                                    :random.randint(20, 50)]
                        this_server["lastWord"] = nextWords[random.randint(0, random.randrange(0, len(nextWords)))]
                        this_server["alreadySet"].add(this_server["lastWord"])
                        await channel.send(' CPU : ' + this_server["lastWord"])
                        this_server["who"] = 'USER'

            if this_server["resetRound"] and not this_server["firstTurn"]:
                this_server["firstTurn"], this_server["resetRound"] = True, False
                this_server["who"] = 'CPU'

client.run('Token')

