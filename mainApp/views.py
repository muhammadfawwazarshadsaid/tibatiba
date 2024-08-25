from datetime import datetime

from django.http import JsonResponse
from django.db import connections
from django.http import HttpResponse
# from rest_framework import generics, status
# from rest_framework.response import Response
# from .serializers import UserRegistrationSerializer

# class RegisterUserView(generics.CreateAPIView):
#     serializer_class = UserRegistrationSerializer

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             self.perform_create(serializer)
#             return Response({"message": "Registration successful!"}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
