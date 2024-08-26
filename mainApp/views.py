from datetime import datetime

from django.http import JsonResponse
from django.db import connection, connections
from django.http import HttpResponse
<<<<<<< Updated upstream

=======
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.hashers import make_password, check_password

@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        if not (name and email and username and password):
            return JsonResponse({'error': 'All fields are required.'}, status=400)
>>>>>>> Stashed changes

        with connection.cursor() as cursor:
            # Check if email or username already exists
            cursor.execute("SELECT * FROM public.\"User\" WHERE email=%s OR username=%s", [email, username])
            if cursor.fetchone():
                return JsonResponse({'error': 'Email or username already exists.'}, status=400)

            # Insert new user into database
            hashed_password = make_password(password)
            cursor.execute(
                "INSERT INTO public.\"User\" (name, email, username, password) VALUES (%s, %s, %s, %s)",
                [name, email, username, hashed_password]
            )
            return JsonResponse({'message': 'User registered successfully.'}, status=201)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username_or_email = data.get('username') or data.get('email')
        password = data.get('password')

        if not (username_or_email and password):
            return JsonResponse({'error': 'Username/Email and password are required.'}, status=400)

        with connection.cursor() as cursor:
            # Check if user exists
            cursor.execute("SELECT * FROM public.\"User\" WHERE username=%s OR email=%s", [username_or_email, username_or_email])
            user = cursor.fetchone()

            if user and check_password(password, user[4]):  # assuming password is the 5th column in the table
                request.session['user_id'] = user[0]
                request.session['username'] = user[3]  # assuming username is the 4th column in the table
                request.session.set_expiry(0)  # Session expires on browser close
                return JsonResponse({'message': 'Logged in successfully.'}, status=200)
            else:
                return JsonResponse({'error': 'Invalid username/email or password.'}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def logout(request):
    if request.method == 'POST':
        request.session.flush()
        return JsonResponse({'message': 'Logged out successfully.'}, status=200)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

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
