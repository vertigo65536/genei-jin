import discord, aiohttp
from tools import updateCounter

ygo_url = 'https://db.ygoprodeck.com/api/v4/cardinfo.php'
price_url = 'http://yugiohprices.com/api/get_card_prices'

async def ygo_search(query, fuzzy = False):
    queryKey = 'fname' if fuzzy else 'name'
    async with aiohttp.ClientSession() as session:
        async with session.get(ygo_url, params = {queryKey: query}) as r:
            if r.status != 200:
                raise RuntimeError(f'{r.status} - {r.reason}')

            return (await r.json())[0]

async def prices_search(query):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{price_url}/{query}') as r:
            if r.status != 200:
                raise RuntimeError(f'{r.status} - {r.reason}')

            return await r.json()

async def search(query, n, prefix=None):
    try:
        results = await ygo_search(query)
    except RuntimeError:
        try:
            results = await ygo_search(query, True)
        except RuntimeError:
            queryWords = query.split()
            for i in range(len(queryWords) - 1):
                try:
                    results = await ygo_search(' '.join(queryWords[:i+1]) + ', ' + ' '.join(queryWords[i+1:]), True)
                except RuntimeError:
                    try:
                        results = await ygo_search(' '.join(queryWords[:i+1]) + '-' + ' '.join(queryWords[i+1:]), True)
                    except RuntimeError:
                        continue

                break
            else:
                await bot.say('No results')
                return

    if len(results) == 0:
        await bot.say('No results')
        return
    if n > len(results) - 1:
        return -2
    nthResult = results[n]
    
    return nthResult
    print(nthResult)
    return nthResult


async def getEmbed(nthResult):
    name = nthResult['name']
    type = nthResult['type']
    description = nthResult['desc']
    image_url = nthResult['image_url']

    price_min, price_mean = [None] * 2
    results = await prices_search(name)
    if results['status'] == 'success' and len(results['data']) != 0:
        nthResult = results['data'][0]
        if nthResult['price_data']['status'] == 'success':
            price_min = nthResult['price_data']['data']['prices']['low']
            price_mean = nthResult['price_data']['data']['prices']['average']
 
    embed = discord.Embed(title = name, description = description)
    embed.set_image(url = image_url)
 
    if price_min is not None and price_mean is not None:
        embed.set_footer(text = f'Minimum: ${price_min}\nAverage: ${price_mean}')
    return embed


async def increment(yuMessage, message, operation, db):
    if operation == "+":
        newCounter = int(yuMessage[3])+1
    elif operation =="-":
        newCounter = int(yuMessage[3])-1
        if newCounter < 0:
            newCounter = 0 
    else:
        newCounter = 0
    results = await search(yuMessage[2], newCounter)
    if results == -1:
        return
    elif results == -2:
        newCounter = 0
        results = await search(yuMessage[2], newCounter)
    e = await getEmbed(results)
    await message.edit(embed = e)
    updateCounter(message.id, db, newCounter)
    return
