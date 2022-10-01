import aiohttp
import asyncio as aio
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')





class SearchRequest:
    API_ROOT = 'https://images-api.nasa.gov/'
    SEARCH_ENDPOINT = 'search'

    def __init__(self, session: aiohttp.ClientSession, q: str = None, center: str = None, description: str = None,
                 description_508: str = None, keywords: str = None, location: str = None, media_type: str = None,
                 nasa_id: str = None, page: int = None, photographer: str = None, secondary_creator: str = None,
                 title: str = None, year_start: int = None, year_end: str = None):
        self.__session = session
        self.__params = {key: val for key, val in locals().items() if val is not None
                         and key not in ('session', 'self')}
        if not self.__params:
            raise ValueError('At least one search parameter must be used.')

    async def execute_request(self):
        request_url = SearchRequest.API_ROOT + SearchRequest.SEARCH_ENDPOINT
        buffer = []
        async with self.__session.request(method='GET', url=request_url, params=self.__params) as response:
            api_response = await response.json()
            for item in api_response['collection']['items']:
                buffer.append(SearchItem(item))
                logging.debug(f'item {item} is added')
            render_tasks = [item.render(self.__session)
                            for item in buffer]
            response = await aio.gather(*render_tasks, return_exceptions=True)
            return response

class SearchItem:
    position = 1

    def __init__(self, item: dict):
        self.position = SearchItem.position
        SearchItem.position += 1
        self.id = item['data'][0]['nasa_id']
        self.title = item['data'][0]['title']
        self.description = item['data'][0].get('description', None)
        self.media_type = item['data'][0]['media_type']
        self.collection = item['href']
        self.preview = None
        self.captions = None
        if 'links' in item.keys():
            for link in item['links']:
                if link.get('rel', None) == 'preview':
                    self.preview = link.get('href', None)
                elif link.get('rel', None) == 'captions':
                    self.captions = link.get('href', None)

    async def render(self, session: aiohttp.ClientSession):
        logging.debug(f'start getting collection for {self.position}')
        async with session.get(self.collection) as collection:
            collection = await collection.json()
        logging.debug(f'finish getting collection for {self.position}, collection: {collection}')
        return {'id': self.id, 'type': self.media_type, 'title': self.title, 'description': self.description,
                'preview': self.preview, 'caption': self.captions, 'collection': collection}

    def __eq__(self, other):
        if isinstance(other, SearchItem):
            return self.id == other.id
        return False


async def search(query, media_type='image'):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0'}
    async with aiohttp.ClientSession(headers=headers) as session:
        logging.debug('create request')
        request = SearchRequest(session, q=query, media_type=media_type)
        logging.debug('send request')
        results = await request.execute_request()
        logging.debug('response is ready')
        return results


def main(query, media_type='image'):
    aio.set_event_loop_policy(aio.WindowsSelectorEventLoopPolicy())
    aio.run(search(query, media_type))


if __name__ == '__main__':
    main('mars', 'video')
