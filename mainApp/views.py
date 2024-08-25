import base64
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
import google.generativeai as genai

genai.configure(api_key="AIzaSyDw8pJxo89LRpKy6UVJ_79hQVbSvY1fvHY")

model = genai.GenerativeModel('gemini-1.5-flash')

def extract_key_terms(user_query):
    response = model.generate_content(f"Identify key location or relevant terms from the following query in one word: '{user_query}'")
    key_terms = response.text.strip().lower()
    return key_terms

@csrf_exempt
def search_posts(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        query = body.get('query', '')
        
        key_terms = extract_key_terms(query)
        
        print(f"Extracted Key Terms: '{key_terms}'")
        
        if not key_terms:
            return JsonResponse({'error': 'Could not extract meaningful terms from the query.'}, status=400)
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT p.post_id, p.place_photo, p.place_city, p.place_description, p.post_caption, p.post_date, u.name AS user_name
                FROM "Post" p
                JOIN "User" u ON p.user_id = u.user_id
                WHERE to_tsvector('indonesian', p.place_description || ' ' || p.post_caption || ' ' || p.place_city) @@ plainto_tsquery('indonesian', %s)
                """, [key_terms])
            posts = cursor.fetchall()
        
        post_list = []
        for post in posts:
            place_photo = post[1]
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
