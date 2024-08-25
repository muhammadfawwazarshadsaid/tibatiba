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
        
        if not key_terms:
            return JsonResponse({'error': 'Could not extract meaningful terms from the query.'}, status=400)
        
        with connection.cursor() as cursor:
            # Fetching posts with related comments and trip information
            cursor.execute("""
                SELECT p.post_id, p.place_photo, p.place_city, p.place_description, p.post_caption, p.post_date, u.name AS user_name,
                       jsonb_agg(DISTINCT jsonb_build_object(
                           'comment_id', c.comment_id,
                           'comment_text', c.comment_text,
                           'comment_date', c.comment_date,
                           'user_name', u2.name,
                           'likes', COALESCE(lc.count, 0)
                       )) AS comments,
                       jsonb_build_object(
                           'trip_id', t.trip_id,
                           'trip_type', t.trip_type,
                           'trip_name', t.trip_name,
                           'trip_description', t.trip_description,
                           'trip_start_date', t.trip_start_date,
                           'trip_end_date', t.trip_end_date
                       ) AS trip
                FROM "Post" p
                JOIN "User" u ON p.user_id = u.user_id
                LEFT JOIN "Comment" c ON c.post_id = p.post_id
                LEFT JOIN "User" u2 ON c.user_id = u2.user_id
                LEFT JOIN (
                    SELECT comment_id, COUNT(*) AS count
                    FROM "LikeComment"
                    GROUP BY comment_id
                ) lc ON lc.comment_id = c.comment_id
                LEFT JOIN "Trip" t ON t.post_id = p.post_id
                WHERE to_tsvector('indonesian', p.place_description || ' ' || p.post_caption || ' ' || p.place_city) @@ plainto_tsquery('indonesian', %s)
                GROUP BY p.post_id, u.name, p.place_photo, p.place_city, p.place_description, p.post_caption, p.post_date, t.trip_id, t.trip_type, t.trip_name, t.trip_description, t.trip_start_date, t.trip_end_date
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
                'user_name': post[6],
                'comments': json.loads(post[7]),  # Convert JSON string to Python dictionary
                'trip': json.loads(post[8]) if post[8] else None  # Convert JSON string to Python dictionary, handle None
            })
        
        return JsonResponse({'posts': post_list})
