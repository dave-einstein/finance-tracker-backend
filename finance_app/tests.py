from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from .models import *
from .serializers import *
class MyModelSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            email='testuser@example.com',
            password='password'
            )
    
    def test_userserializer_valid_data(self):
        data = {
            'user_id': 'hhegw78478266bd',
            'first_name': 'David',
            'last_name': 'Kipkoech',
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password',
            'password2': 'password',
            'currency': 'USD',
        }

        serializer = UserSerializer(data=data)

        if not serializer.is_valid():
            print("Serializer Errors:", serializer.errors)  # ✅ Debug output

        self.assertTrue(serializer.is_valid(), msg=f"Serializer errors: {serializer.errors}")


    def test_budgetserializer_valid_data(self):
        data = {
            'id': 'hhegw78478266bd',
            'user': self.user.user_id,
            'description': 'Test Budget',
            'year' : '2024', 
            'month' : 'January',
            }
        serializer = BudgetSerializer(data=data)
        self.assertTrue(serializer.is_valid())
class UserCreationTestCase(APITestCase):
    def test_user_creation(self):
        url = reverse('signup')  # Ensure 'signup' is the correct name of your URL pattern
        data = {
            'user_id' : 'hhegw78478266bd',
            'first_name': 'David',
            'last_name': 'Kipkoech',
            'username': 'testuser2',
            'email': 'testuser@example.com',
            'password': 'Password@123',
            'password2': 'Password@123',
            'currency': 'USD',
        }
        
        response = self.client.post(url, data, format='json')
        print("Response Status Code:", response.status_code)
        print("Response Data:", response.json())  # ✅ Debugging output
        self.assertEqual(response.status_code, 201)  # Adjust expected status code based on your API response