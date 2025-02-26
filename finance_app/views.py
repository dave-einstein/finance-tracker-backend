from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

import boto3
from botocore.exceptions import ClientError

from decouple import config
import hmac
import hashlib
import base64
from datetime import datetime
from django.shortcuts import get_object_or_404
from .models import User,Transactions
from .serializers import UserSerializer,TransactionsSerializer


User = get_user_model()

region_name=config("region_name")
clientID = config("ClientID")
clientsecret = config("ClientSecret")
cognito = boto3.client("cognito-idp", region_name=region_name)

# Generate secret hash
def generate_secret_hash(username, client_id, client_secret):
    message = username + client_id
    dig = hmac.new(
        client_secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return base64.b64encode(dig).decode("utf-8")

class SignupView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        required_fields = ["first_name", "last_name", "username", "email", "password"]
        for field in required_fields:
            if not request.data.get(field):
                return JsonResponse({"error": f"{field} is required"}, status=400)

        name = f"{request.data['first_name']} {request.data['last_name']}"
        username = request.data["username"]
        email = request.data["email"]
        password = request.data["password"]

        try:
            secret_hash = generate_secret_hash(username, clientID, clientsecret)

            now = datetime.now()
            updated_at_timestamp = int(now.timestamp())

            cognito.sign_up(
                ClientId=clientID,
                SecretHash=secret_hash,
                Username=username,
                Password=password,
                UserAttributes=[
                    {"Name": "name", "Value": name},
                    {"Name": "email", "Value": email},
                    {"Name": "updated_at", "Value": str(updated_at_timestamp)},
                ],
            )

            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=201)
            return JsonResponse(serializer.errors, status=400)  # Return validation errors properly

        except cognito.exceptions.UsernameExistsException:
            return JsonResponse({"error": "User already exists"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)  # Only return 500 for unknown errors
        
class ConfirmEmail(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data["username"]
        code = request.data["token"]
        try:
            secret_hash = generate_secret_hash(
                username,clientID,clientsecret
            )
            cognito.confirm_sign_up(
                ClientId=clientID,
                SecretHash=secret_hash,
                Username=username,
                ConfirmationCode=code,
            )
            return JsonResponse(status=status.HTTP_202_ACCEPTED)
        except ClientError as e:
            return JsonResponse(data=e.response["Error"]["Message"],status=status.HTTP_400_BAD_REQUEST,safe=False)
        
class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            response = cognito.initiate_auth(
                ClientId="your_app_client_id",
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={"USERNAME": email, "PASSWORD": password},
            )

            user = User.objects.get(email = email)
            user_data = {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "email": user.email,
                "id": user.user_id,
                }

            # Get access token
            access_token = response["AuthenticationResult"]["AccessToken"]
            return JsonResponse({"access_token": access_token, "user": user_data}, status=status.HTTP_200_OK)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)        

class SignoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the Authorization header and extract the token
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        if not auth_header.startswith("Bearer "):
            return JsonResponse({"error": "Invalid token format"}, status=status.HTTP_400_BAD_REQUEST)

        access_token = auth_header.split("Bearer ")[1]  # Extract the token part

        try:
            cognito.global_sign_out(ClientId=clientID, AccessToken=access_token)
            return JsonResponse({"message": "User signed out"}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse(
                {"error": f"Failed to sign out"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

class TransactionView(APIView):
    """
    Retrieve or update a budget, and handle creation of income, savings, investments, and expenses.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve a budget and associated records."""
        transaction_id = request.query_params.get("transaction_id")
        try:
            transaction = Transactions.objects.get(transaction_id=transaction_id)
            serialized_transaction = TransactionsSerializer(transaction)
            return Response(serialized_transaction.data, status=status.HTTP_200_OK)
        except Transactions.DoesNotExist:
            return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """Create multiple transactions at once."""
        if not isinstance(request.data, list):
            return Response({"error": "Expected a list of transactions"}, status=status.HTTP_400_BAD_REQUEST)

        transaction_serializer = TransactionsSerializer(data=request.data, many=True)
        
        if not transaction_serializer.is_valid():
            return Response(transaction_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        transactions = transaction_serializer.save()
        return Response(TransactionsSerializer(transactions, many=True).data, status=status.HTTP_201_CREATED)

class DashboardView(APIView):
    """
    Retrieve a user's dashboard.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request):
        """Retrieve a user's dashboard."""
        try:

            user = request.user
            user_info = get_object_or_404(User, user_id=user.user_id)
            transactions = Transactions.objects.filter(user= user)
        
            return Response({
                "user" : user_info,
                "transactions" : TransactionsSerializer(transactions, many=True).data
                }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        