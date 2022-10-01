from django.shortcuts import render
from django.views import View
from django.http.response import JsonResponse
from .services.search_engine import search
from .forms import SearchForm
import asyncio as aio

aio.set_event_loop_policy(aio.WindowsSelectorEventLoopPolicy())


class SearchPage(View):
    async def get(self, request, *args, **kwargs):
        form = SearchForm()
        return render(request, 'search_page.html', {'form': form})

    async def post(self, request, *args, **kwargs):
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data.get('search_query', '')
            media_type = form.cleaned_data.get('media_type')
            results = []
            if 'image' in media_type:
                result_images = await search(query=query, media_type='image')
                results = [*result_images]
            if 'video' in media_type:
                result_videos = await search(query=query, media_type=media_type)
                results.extend(result_videos)
        return render(request, 'search_page.html', {'form': form, 'results': results})
