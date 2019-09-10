import re
import random
import discord
import json

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

for i in sorted([i for i in s.split() if pat.match(i) and len(i) >= 2], key=lambda x:-len(x)):
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

alreadySet = set()
round, win, lose = 0, 0, 0
who, lastWord, firstLetter = "CPU", '', ''
firstTurn, resetRound, isPlaying = True, False, False

def patch_data(dict, null_name, null_data):
    if not (null_name in dict):
        dict[null_name] = null_data

def decompositeHangul(hangulLetter):
    cho_list = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
    jung_list = 'ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ'
    jong_list = ' ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ'

    hangulCode = ord(hangulLetter)
    cho_index = (hangulCode - 0xAC00) // 21 // 28
    jung_index = (hangulCode - 0xAC00 - (cho_index * 21 * 28)) // 28
    jong_index = hangulCode - 0xAC00 -(cho_index * 21 * 28) - (jung_index * 28)
    
    return (cho_list[cho_index], jung_list[jung_index], jong_list[jong_index])

def checkDueum(last_lastWord, first_yourWord):
    hangulRegex = re.compile("[가-힣]")
    if not pat.match(last_lastWord) and not pat.match(first_yourWord):
        return False

    lastWordDecompose = decompositeHangul(last_lastWord)
    yourWordDecompose = decompositeHangul(first_yourWord)

    if lastWordDecompose[0] in 'ㄴㄹ':
        if (lastWordDecompose[1] in 'ㅏㅐㅗㅚㅜㅡ') and lastWordDecompose[0] == 'ㄹ':
            if (yourWordDecompose[1:] == lastWordDecompose[1:]) and yourWordDecompose[0] == 'ㄴ':
                return True
            else:
                return False
        elif lastWordDecompose[1] in 'ㅑㅕㅛㅠㅣ':
            if (yourWordDecompose[1:] == lastWordDecompose[1:]) and yourWordDecompose[0] == 'ㅇ':
                return True
            else:
                return False
    else:
        return False

@client.event
async def on_message(message):
    global isPlaying, round, win, lose, firstLetter
    global who, lastWord, alreadySet, firstTurn, resetRound

    channel = message.channel

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
            else:
                patch_data(user_card[str(message.author.id)], "length", 0)

            with open('user_info.json', 'w', encoding='utf-8') as file:
                file.write(json.dumps(user_card, ensure_ascii=False, indent=4))

            if ('!start' == message.content or '!시작' == message.content) and (not isPlaying):
                round += 1
                if not (str(message.author.id) in user_card):
                    user_card[str(message.author.id)] = {
                        "user": message.author.name,
                        "level": 1,
                        "word": 0,
                        "win": 0
                    }
                    await channel.send(user_card.get(str(message.author.id)))
                    with open('user_info.json', 'w', encoding='utf-8') as file:
                        file.write(json.dumps(user_card, ensure_ascii=False, indent=4))

                embed = discord.Embed(title=str(round) + "라운드를 시작합니다. 현재 " + str(win) + "승 " + str(lose) + "패",
                                      description="기권하시려면 `!exit`  또는 `!기권`을 입력해주시기 바랍니다.")
                await channel.send("", embed=embed)

                lastWord = ''
                alreadySet = set()
                firstTurn, resetRound, isPlaying = True, False, True
                who = 'CPU'

            if isPlaying and who == 'CPU':
                if firstTurn:
                    lastWord = random.choice(list(wordDict[random.choice(list(wordDict.keys()))]))
                    alreadySet.add(lastWord)
                    await channel.send(' CPU : ' + lastWord)
                    who = 'USER'
                    firstTurn = False

            if isPlaying and who == 'USER' and not message.author.bot and not firstTurn:
                yourWord = message.content
                if yourWord == '!exit' or yourWord == '!기권':
                    await channel.send('[결과] 당신은 기권했습니다. CPU의 승리입니다!')
                    resetRound = True
                    isPlaying = False
                    lose += 1
                    who = 'CPU'
                error = False

                firstLetter = yourWord[0]
                if (firstLetter != lastWord[-1]) and not checkDueum(lastWord[-1], firstLetter):
                    await channel.send(" [오류] '" + lastWord[-1] + "' (으)로 시작하는 단어를 입력하세요.")
                    who = 'USER'
                    error = True
                elif yourWord in hanbangSet:
                    await channel.send(' [오류] 한방단어는 사용할 수 없습니다.')
                    who = 'USER'
                    error = True
                elif yourWord in alreadySet:
                    await channel.send(' [오류] 이미 나온 단어입니다.')
                    who = 'USER'
                    error = True
                elif yourWord not in wordDict.get(firstLetter, set()):
                    await channel.send(' [오류] 사전에 없는 단어입니다.')
                    who = 'USER'
                    error = True

                if not error:
                    who = 'CPU'
                    alreadySet.add(yourWord)
                    lastWord = yourWord
                    user_card[str(message.author.id)]["word"] += 1
                    user_card[str(message.author.id)]["length"] += len(yourWord)
                    with open('user_info.json', 'w', encoding='utf-8') as file:
                        file.write(json.dumps(user_card, ensure_ascii=False, indent=4))
                    firstLetter = lastWord[-1]
                    if not list(filter(lambda x: x not in alreadySet, wordDict.get(firstLetter, set()))):
                        # 라운드 종료
                        await channel.send('[결과] CPU가 기권했습니다. 당신의 승리입니다!')
                        who = 'CPU'
                        isPlaying = False
                        win += 1
                        user_card[str(message.author.id)]["win"] += 1
                        with open('user_info.json', 'w', encoding='utf-8') as file:
                            file.write(json.dumps(user_card, ensure_ascii=False, indent=4))
                    else:
                        nextWords = sorted(filter(lambda x: x not in alreadySet, wordDict[firstLetter]),
                                           key=lambda x: -len(x))[
                                    :random.randint(20, 50)]
                        lastWord = nextWords[random.randint(0, random.randrange(0, len(nextWords)))]
                        alreadySet.add(lastWord)
                        await channel.send(' CPU : ' + lastWord)
                        who = 'USER'

            if resetRound and not firstTurn:
                firstTurn, resetRound = True, False
                who = 'CPU'

client.run('token')
