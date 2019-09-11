## 단어추가에 대하여
kkutu.txt 파일은 끝말잇기에 사용될 단어에 대한 데이터베이스입니다.
따라서 끝말잇기 도중 누락된 단어를 찾으시게 된다면 kkutu.txt에 단어를 추가해주시기 바랍니다.
```python
...
with open('kkutu.txt', 'rt', encoding='utf-8') as f:
    s = f.read()
...
```
## 한방단어에 대하여
한방단어에 대한 데이터베이스는 봇 실행시 kkutu.txt에 나열된 단어들에 한정하여 사용시 끝말잇기가 종료되는 단어들을 따로 선별하여 구성됩니다.

```python
for i in wordDict:
    for j in wordDict[i]:
        if j[-1] not in wordDict:
            delList.append(j)
```

## 게임채널에 대하여
봇이 서버내 모든 채널에서 플레이하는 것을 방지하기 위하여, 다음과 같이 설정을 하였습니다.
아래의 경우, 채널의 이름이 `끝말잇기` 인 경우에만 끝말잇기를 즐길 수 있습니다.
```python
...
if message.channel.name == "끝말잇기":
    if ('!start' == message.content or '!시작' == message.content) and (not isPlaying):
        round += 1
        if not (str(message.author.id) in user_card):
            user_card[str(message.author.id)] = {
                "user": message.author.name,
...
```

## 원본 소스 (Python CLI)

https://m.blog.naver.com/njw1204/221364710539
