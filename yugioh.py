import discord, aiohttp
from tools import updateCounter, searchResultsTest

ygo_url = 'https://db.ygoprodeck.com/api/v7/cardinfo.php'
price_url = 'http://yugiohprices.com/api/get_card_prices'

async def ygo_search(query, fuzzy = False):
    queryKey = 'fname' if fuzzy else 'name'
    async with aiohttp.ClientSession() as session:
        async with session.get(ygo_url, params = {queryKey: query}) as r:
            if r.status != 200:
                raise RuntimeError(f'{r.status} - {r.reason}')
            
            return (await r.json())['data'][0]

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
                return -1
    searchTest = searchResultsTest(results['card_images'], n)
    if searchTest == 0:
        results['n_value'] = n
    elif searchTest == -2:
        results['n_value'] = 0
    else:
        results['n_value'] = searchTest
    return results

async def getEmbed(nthResult, colour):
    if nthResult == -1:
        return None
    name = nthResult['name']
    type = nthResult['type']
    description = nthResult['desc']
    n = nthResult['n_value']
    image_url = nthResult['card_images'][n]['image_url']
    price_min, price_mean = [None] * 2
    results = await prices_search(name)
    if results['status'] == 'success' and len(results['data']) != 0:
        priceResult = results['data']
        successFlag = 0
        for i in range(len(priceResult)):
            if priceResult[i]['price_data']['status'] == 'success':
                if priceResult[i]['print_tag'] == nthResult['card_sets'][n]['set_code']:
                    price_min = priceResult[i]['price_data']['data']['prices']['low']
                    price_mean = priceResult[i]['price_data']['data']['prices']['average']
                    break
    embed = discord.Embed(title = name, description = description, colour=colour)
    embed.set_image(url = image_url)

    if price_min is not None and price_mean is not None:
        embed.set_footer(text = f'Minimum: ${price_min}\nAverage: ${price_mean}')
    else:
        embed.set_footer(text = "No price available for this variant")

    return embed
