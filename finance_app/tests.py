from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from .models import User, Budget, Income, Savings, Investment, Expense
from .serializers import (
    UserSerializer,BudgetSerializer, IncomeSerializer, SavingsSerializer, 
    InvestmentSerializer, ExpensesSerializer
)
import random
from unittest.mock import patch
from rest_framework.authtoken.models import Token
from rest_framework import status
from decouple import config

class MyModelSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            email='testuser@example.com',
            password='password'
            )
        self.budget = Budget.objects.create(
            user=self.user,
            description='Test Budget',
            year="2024",
            month="Jan",
        )
    
    def test_userserializer_valid_data(self):
        data = {
            'user_id': 'hhegw78478266bd',
            'first_name': 'David',
            'last_name': 'Kipkoech',
            'username': 'testuser1',
            'email': 'testuser1@example.com',
            'password': 'Password@123',
            'password2': 'Password@123',
            'currency': 'USD',
        }

        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())

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

    def test_incomeserializer_valid_data(self):
        data = {
            'id': 'hhegw78478266bd',
            'description': 'Test Income',
            'budget' : self.budget.id,
            'income_type' : 'freelancing',
            'amount': '1000',
            }
        serializer = IncomeSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_savingsserializer_valid_data(self):
        data = {
            'id': 'hhegw78478266bd',
            'description': 'Test Savings',
            'budget' : self.budget.id,
            'amount': '1000',
            }
        serializer = SavingsSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_investmentserializer(self):
        data = {
            'id': 'hhegw78478266bd',
            'description': 'Test Investment',
            'budget' : self.budget.id,
            'amount': '1000',
            }
        serializer = InvestmentSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_expenseserializer_valid_data(self):
        data = {
            'id': 'hhegw78478266bd',
            'description': 'Test Expense',
            'budget' : self.budget.id,
            'amount': '1000',
            }
        serializer = ExpensesSerializer(data=data)
        self.assertTrue(serializer.is_valid())

class UserCreationTestCase(APITestCase):
    # def test_user_creation(self):
    #     url = reverse('signup')
    #     value1 = random.randint(1, 9999)
    #     data = {
    #         'user_id' : 'hhegw78478266bd123',
    #         'first_name': 'David',
    #         'last_name': 'Kipkoech',
    #         'username': f'testuser{value1}',
    #         'email': f'testuser{value1}@example.com',
    #         'password': 'Password@123',
    #         'password2': 'Password@123',
    #         'currency': 'USD',
    #     }
        
    #     response = self.client.post(url, data, format='json')
    #     self.assertEqual(response.status_code, 201)

    def test_confirm_email(self):
        value2 = random.randint(10000,999999)
        self.user = User.objects.create_user(
            username=f'testuser{value2}',
            email=f'testuser{value2}@example.com',
            password='Password@123',
            first_name='David',
            last_name='Kipkoech',
            currency='USD'
        )

        data = {
            'username' : self.user.username,
            'token': 'testtoken',
        }
        url = reverse('confirm-email')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
    
    # def test_login(self):
    #     value3 = random.randint(1000000,99999999)
    #     self.user = User.objects.create_user(
    #         username=f'testuser{value3}',
    #         email=f'testuser{value3}@example.com',
    #         password='Password@123',
    #         first_name='David',
    #         last_name='Kipkoech',
    #         currency='USD'
    #         )
    #     self.user.is_active = True
    #     self.user.save()
    #     data = {
    #         'username' : 'testuser640526',
    #         'password' : 'Password@123',
    #         }
    #     url = reverse('login')
    #     response = self.client.post(url, data, format='json')
    #     self.assertEqual(response.status_code, 200)

class SignoutViewTestCase(APITestCase):
    
    def setUp(self):
        self.signout_url = reverse("logout")
        self.access_token = "valid_test_token"
        self.clientID = config("ClientID")

        # Create a test user and authenticate
        self.user = User.objects.create_user(username="testuser", password="Password@123")
        self.client.force_authenticate(user=self.user)

    @patch("finance_app.views.cognito.global_sign_out")
    def test_successful_signout(self, mock_global_signout):
        """Test signing out a user successfully."""
        mock_global_signout.return_value = {"Success":True}  # Mock successful response

        response = self.client.post(
            self.signout_url,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"  # Ensure format matches API expectations
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "User signed out"})
        mock_global_signout.assert_called_once_with(
            ClientId=self.clientID, AccessToken=self.access_token
        )

    @patch("finance_app.views.cognito.global_sign_out")
    def test_failed_signout(self, mock_global_signout):
        """Test signing out failure."""
        mock_global_signout.side_effect = Exception("Signout failed")  # Simulate failure

        response = self.client.post(
            self.signout_url,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}" 
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"error": "Failed to sign out"})
        mock_global_signout.assert_called_once()

class BudgetViewTestCase(APITestCase):
    def setUp(self):
        """Set up test data, including a test user and a budget."""
        # Create user and authentication token
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        # Create a budget
        self.budget = Budget.objects.create(
            user=self.user, description="Test Budget", year=2025, month=2
        )

        # Create related objects
        self.income = Income.objects.create(
            budget=self.budget, description="Salary", income_type="Job", amount=5000
        )
        self.savings = Savings.objects.create(
            budget=self.budget, description="Emergency Fund", amount=1000
        )
        self.investment = Investment.objects.create(
            budget=self.budget, description="Stocks", amount=1500
        )
        self.expense = Expense.objects.create(
            budget=self.budget, description="Rent", amount=2000
        )

    def test_get_budget_details(self):
        """Test retrieving a budget along with associated records."""
        url = reverse("budget")
        response = self.client.get(url,data={"budget_id" : self.budget.id},format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["budget"]["description"], "Test Budget")
        self.assertEqual(len(response.data["income"]), 1)
        self.assertEqual(len(response.data["savings"]), 1)
        self.assertEqual(len(response.data["investments"]), 1)
        self.assertEqual(len(response.data["expenses"]), 1)

    def test_get_budget_not_found(self):
        """Test retrieving a non-existent budget."""
        url = reverse("budget")
        response = self.client.get(url,data={"budget_id" : "99999"},format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_budget_with_related_entries(self):
        """Test creating a budget along with income, savings, investments, and expenses."""
        url = reverse("budget")
        data = {
            "id": "hhegw78478266bd",
            "user": self.user.user_id, 
            "description": "New Budget",
            "year": 2025,
            "month": 3,
            "income": [{"description": "Freelance", "income_type": "Side Job", "amount": 2000}],
            "savings": [{"description": "Vacation Fund", "amount": 500}],
            "investments": [{"description": "Crypto", "amount": 300}],
            "expenses": [{"description": "Groceries", "amount": 400}],
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Budget.objects.filter(description="New Budget").count(), 1)
        new_budget = Budget.objects.get(description="New Budget")
        self.assertEqual(Income.objects.filter(budget=new_budget).count(), 1)
        self.assertEqual(Savings.objects.filter(budget=new_budget).count(), 1)
        self.assertEqual(Investment.objects.filter(budget=new_budget).count(), 1)
        self.assertEqual(Expense.objects.filter(budget=new_budget).count(), 1)

    def test_create_budget_invalid_data(self):
        """Test creating a budget with missing required fields."""
        url = reverse("budget")
        data = {"year": 2025}  # Missing description and month
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
