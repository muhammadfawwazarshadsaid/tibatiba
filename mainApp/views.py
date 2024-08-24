import base64
from datetime import datetime

from django.http import JsonResponse
from django.db import connections
from django.http import HttpResponse


def testvercel(request):
    now = datetime.now()
    html = f'''
    <html>
        <body>
            <h1>Hello from Vercel!</h1>
            <p>The current time is { now }.</p>
        </body>
    </html>
    '''
    return HttpResponse(html)

def get_users(request):
    try:
        # Get the database connection
        with connections['default'].cursor() as cursor:
            # Execute the SQL query to fetch users
            cursor.execute('SELECT user_id, name, email, username FROM "User";')
            # Fetch all rows from the executed query
            rows = cursor.fetchall()

        # Convert rows to a list of dictionaries
        users = []
        for row in rows:
            user = {
                'user_id': row[0],
                'name': row[1],
                'email': row[2],
                'username': row[3]
            }
            users.append(user)

        # Return the JSON response
        return JsonResponse(users, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
import openai

def get_adjusted_query(user_query):
    openai.api_key = ''
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Given the user query '{user_query}', adjust it to match the data in the following format: place_description or post_caption."}
        ],
        max_tokens=50
    )
    adjusted_query = response.choices[0].message['content'].strip()
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


@csrf_exempt
def like_post(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        post_id = request.POST.get('post_id')
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO "SavedPost" (user_id, post_id, saved_date)
                VALUES (%s, %s, NOW())
                ON CONFLICT (user_id, post_id) DO NOTHING
                """, [user_id, post_id])
        return JsonResponse({'status': 'success'})

@csrf_exempt
def dislike_post(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        post_id = request.POST.get('post_id')
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO "DislikedPost" (user_id, post_id, disliked_date, expiry_date)
                VALUES (%s, %s, NOW(), NOW() + INTERVAL '1 DAY')
                ON CONFLICT (user_id, post_id) DO NOTHING
                """, [user_id, post_id])
        return JsonResponse({'status': 'success'})

def get_post_comments(request, post_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT c.comment_id, c.comment_text, c.comment_date, u.name AS user_name
            FROM "Comment" c
            JOIN "User" u ON c.user_id = u.user_id
            WHERE c.post_id = %s
            """, [post_id])
        comments = cursor.fetchall()
    comment_list = []
    for comment in comments:
        comment_list.append({
            'comment_id': comment[0],
            'comment_text': comment[1],
            'comment_date': comment[2],
            'user_name': comment[3]
        })
    return JsonResponse({'comments': comment_list})

