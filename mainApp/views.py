from django.http import JsonResponse
from django.db import connections

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
