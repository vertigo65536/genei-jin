import os, requests, json, discord
from tools import updateCounter, searchResultsTest
from dotenv import load_dotenv

load_dotenv()
lego_url = "https://brickset.com/api/v3.asmx/getSets"
apiKey = os.getenv('BRICKSET_KEY')

def lego_search(query, fuzzy = False):
    queryKey = 'fname' if fuzzy else 'name'
    r = requests.get(lego_url,
        params={
            'apiKey': apiKey,
            'userHash': "",
            'params':"{query: '" + query + "'}"
        }
    )
    parsed = json.loads(r.text)
    if parsed['status'] == 'success':
        return parsed['sets']
    else:
        return -1


# Searches youtube, taking a query and a result number as parameters
# and returning a url

async def search(query, n, prefix=None, modifier=None):
    result = lego_search(query)
    if isinstance(result, int) and result == -1:
        return -1
    if len(result) == 0:
        return -1
    return result[n]

async def getEmbed(results, colour):
    if results == -1:
         return None
    e = discord.Embed(title=results['name'],
        url=results['bricksetURL'],
        colour = colour
    )
    e.set_image(url=results['image']['imageURL'])
    e.add_field(name='Rating',
        value=results['rating'],
        inline=False
    )
    try:
        e.add_field(name='Price',
            value="£" + results['LEGOCom']['UK']['retailPrice'],
            inline=False
        )
    except:
        pass
    return e
