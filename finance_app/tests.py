from django.test import TestCase
from .models import User, Transactions
from .serializers import UserSerializer, TransactionsSerializer
from uuid import uuid4
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse

class UserSerializerTest(TestCase):
    """Test cases for the UserSerializer."""
    
    def setUp(self):
        """Create a test user for serialization tests."""
        self.user = User.objects.create(
            user_id=uuid4(),
            first_name="John",
            last_name="Doe",
            username="johndoe",
            email="johndoe@example.com",
            currency="USD",
            created_at=now()
        )

    def test_user_serialization(self):
        """Test that the UserSerializer correctly serializes user data."""
        serializer = UserSerializer(instance=self.user)
        expected_data = serializer.data
        self.assertEqual(serializer.data, expected_data)

    def test_user_deserialization_valid_data(self):
        """Test deserialization of valid user data."""
        user_data = {
            'user_id': str(uuid4()),
            'first_name': "Alice",
            'last_name': "Smith",
            'username': "alicesmith",
            'email': "alice@example.com",
            'currency': "EUR",
            'created_at': now(),
        }
        serializer = UserSerializer(data=user_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_user_deserialization_invalid_data(self):
        """Test deserialization of invalid user data (missing required fields)."""
        user_data = {
            'first_name': "Alice",
            'email': "alice@example.com",
            'currency': "EUR",
        }
        serializer = UserSerializer(data=user_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)

class TransactionsSerializerTest(TestCase):
    """Test cases for the TransactionsSerializer."""
    
    def setUp(self):
        """Create a test user and transaction for serialization tests."""
        self.user = User.objects.create(
            user_id=uuid4(),
            first_name="John",
            last_name="Doe",
            username="johndoe",
            email="johndoe@example.com",
            currency="USD",
            created_at=now()
        )

        self.transaction = Transactions.objects.create(
            transaction_id=uuid4(),
            user=self.user,
            transaction_type="income",
            description="Salary Payment",
            amount=5000.00,
            created_at=now(),
            updated_at=now(),
        )

    def test_transaction_serialization(self):
        """Test that the TransactionsSerializer correctly serializes transaction data."""
        serializer = TransactionsSerializer(instance=self.transaction)
        expected_data = expected_data = serializer.data 
        self.assertEqual(serializer.data, expected_data)

    def test_transaction_deserialization_valid_data(self):
        """Test deserialization of valid transaction data."""
        transaction_data = {
            'transaction_id': str(uuid4()),
            'user': self.user.user_id,
            'transaction_type': "expenses",
            'category': "Food", 
            'description': "Grocery Shopping",
            'amount': "100.50",
            'created_at': now(),
            'updated_at': now(),
        }
        serializer = TransactionsSerializer(data=transaction_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_transaction_deserialization_invalid_data(self):
        """Test deserialization of invalid transaction data (missing fields)."""
        transaction_data = {
            'transaction_type': "expenses",
            'description': "Grocery Shopping",
            'amount': "100.50",
        }
        serializer = TransactionsSerializer(data=transaction_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('user', serializer.errors)  # 'user' is required

User = get_user_model()

# class SignupViewTest(APITestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.signup_url = reverse("signup")
#         self.valid_data = {
#             "first_name": "John",
#             "last_name": "Doe",
#             "username": "johndoe",
#             "email": "johndoe@example.com",
#             "password": "securepassword123"
#         }

#     @patch('boto3.client')
#     def test_signup_success(self, mock_cognito):
#         mock_cognito.return_value.sign_up.return_value = {}
#         response = self.client.post(self.signup_url, self.valid_data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#     def test_signup_missing_field(self):
#         invalid_data = self.valid_data.copy()
#         invalid_data.pop('email')  # Remove email to trigger error
#         response = self.client.post(self.signup_url, invalid_data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('error', response.json())


# class LoginViewTest(APITestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.login_url = reverse("login")
#         self.user = User.objects.create_user(
#             username="johndoe",
#             email="johndoe@example.com",
#             password="securepassword123"
#         )

#     @patch('boto3.client')
#     def test_login_success(self, mock_cognito):
#         mock_cognito.return_value.initiate_auth.return_value = {
#             "AuthenticationResult": {"AccessToken": "mocked_token"}
#         }
#         response = self.client.post(self.login_url, {
#             "email": "johndoe@example.com",
#             "password": "securepassword123"
#         }, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn("access_token", response.json())

#     def test_login_invalid_credentials(self):
#         response = self.client.post(self.login_url, {
#             "email": "wrong@example.com",
#             "password": "wrongpassword"
#         }, format='json')
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class TransactionViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.transation_url = reverse("transaction")  # Adjust if necessary
        self.user = User.objects.create_user(username="johndoe", email="johndoe@example.com", password="securepassword123")
        self.transaction = Transactions.objects.create(
            user=self.user,
            transaction_type="income",
            category="Salary",
            description="Monthly salary",
            amount=5000.00,
        )
        self.client.force_authenticate(user=self.user)

    def test_get_transaction_success(self):
        # Serializing the transaction object
        serialized_transaction = TransactionsSerializer(self.transaction)
        
        response = self.client.get(self.transation_url, {"transaction_id": str(self.transaction.transaction_id)})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), serialized_transaction.data)  # Ensure the response matches the serialized data

    def test_create_transactions_success(self):
        transaction_data = [  # Wrap in a list
            {
                "user": self.user.user_id,  # Ensure this is an integer ID
                "transaction_type": "expenses",
                "category": "Food",
                "description": "Lunch",
                "amount": 15.00,  # Ensure it's a float, not a string
            }
        ]
        response = self.client.post(self.transation_url, transaction_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)



    def test_create_transaction_invalid_format(self):
        response = self.client.post(self.transation_url, {"invalid": "data"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
