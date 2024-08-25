import base64
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

import google.generativeai as genai

genai.configure(api_key="AIzaSyDw8pJxo89LRpKy6UVJ_79hQVbSvY1fvHY")

model = genai.GenerativeModel('gemini-1.5-flash')


def get_adjusted_query(user_query):
    response = model.generate_content("Given the user query '{user_query}', adjust it to match the data in the following format: place_description or post_caption.")
    
    adjusted_query = response.text
    return adjusted_query

@csrf_exempt
def search_posts(request):
    if request.method == 'POST':
        query = request.POST.get('query', '')
        adjusted_query = get_adjusted_query(query)
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT p.post_id, p.place_photo, p.place_city, p.place_description, p.post_caption, p.post_date, u.name AS user_name
                FROM "Post" p
                JOIN "User" u ON p.user_id = u.user_id
                WHERE to_tsvector('indonesian', p.place_description || ' ' || p.post_caption) @@ to_tsquery('indonesian', %s)
                """, [adjusted_query])
            posts = cursor.fetchall()
        
        post_list = []
        for post in posts:
            place_photo = post[1]
            # Convert binary data to base64-encoded string
            if place_photo:
                place_photo = base64.b64encode(place_photo).decode('utf-8')
            post_list.append({
                'post_id': post[0],
                'place_photo': place_photo,
                'place_city': post[2],
                'place_description': post[3],
                'post_caption': post[4],
                'post_date': post[5],
                'user_name': post[6]
            })
        
        return JsonResponse({'posts': post_list})
