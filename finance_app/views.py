from django.http import HttpResponse,JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework import status

import boto3
from botocore.exceptions import ClientError

from decouple import config
import hmac
import hashlib
import base64
from datetime import datetime

from .models import *
from .serializers import *

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
        name = request.data.get("first_name") + "" + request.data.get("last_name")
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            secret_hash = generate_secret_hash(
                username,clientID,clientsecret
            )

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

            # Save user in Django database
            data = JSONParser().parse(request)
            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
            return JsonResponse(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ConfirmEmail(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        code = request.data.get("code")
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
            return JsonResponse(data=e.response["Error"]["Message"],status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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

            # Get access token
            access_token = response["AuthenticationResult"]["AccessToken"]
            return JsonResponse({"access_token": access_token}, status=status.HTTP_200_OK)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        
    def get(request):
        """
        Get a user credentials.
        """
        try:
            users = User.objects.get(user_id = request.POST['user_id'])
            #get existing user
            serializer = UserSerializer(users)
            return JsonResponse(serializer.data,status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)


class SignoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get access token from request headers
        access_token = request.META.get("HTTP_AUTHORIZATION")
        try:
            cognito.global_signout(ClientId="your_app_client_id", AccessToken=access_token)
            return JsonResponse({"message": "User signed out"}, status=status.HTTP_200_OK)
        except:
            return JsonResponse({"error": "Failed to sign out"}, status=status.HTTP_400_BAD_REQUEST)

class BudgetView(APIView):
    """
    Retrieve or update a budget, and handle creation of income, savings, investments, and expenses.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request):
        # Retrieve budget and associated records
        try:
            budget = Budget.objects.get(id=request.GET.get('budget_id'))
            savings = Savings.objects.filter(budget=budget)
            income = Income.objects.filter(budget=budget)
            investment = Investment.objects.filter(budget=budget)
            expenses = Expense.objects.filter(budget=budget)
        except Budget.DoesNotExist:
            return JsonResponse(status=status.HTTP_404_NOT_FOUND)

        # Serialize and return JSON response
        return JsonResponse({
            'budget': BudgetSerializer(budget).data,
            'savings': SavingsSerializer(savings, many=True).data,
            'income': IncomeSerializer(income, many=True).data,
            'investment': InvestmentSerializer(investment, many=True).data,
            'expenses': ExpensesSerializer(expenses, many=True).data,
        }, safe=False,status=status.HTTP_201_CREATED)

    def put(self,request):
        # Update budget
        try:
            data = JSONParser().parse(request)
            budget = Budget.objects.get(id=data.get('budget_id'))
            budget_serializer = BudgetSerializer(budget, data=data)
            if budget_serializer.is_valid():
                budget_serializer.save()
                return JsonResponse(budget_serializer.data, status=status.HTTP_201_CREATED)
            return JsonResponse(budget_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Budget.DoesNotExist:
            return JsonResponse(status=status.HTTP_404_NOT_FOUND)

    def post(self,request):
        # Create new income, savings, investment, or expense entry
        data = JSONParser().parse(request)
        budget_id = data.get('budget_id')

        try:
            budget = Budget.objects.get(id=budget_id)
        except Budget.DoesNotExist:
            return JsonResponse({'error': 'Budget not found'}, status=404)

        record_type = data.get('type')  # Should be 'income', 'savings', 'investment', or 'expense'
        if record_type == 'income':
            serializer = IncomeSerializer(data={**data, 'budget': budget.id})
        elif record_type == 'savings':
            serializer = SavingsSerializer(data={**data, 'budget': budget.id})
        elif record_type == 'investment':
            serializer = InvestmentSerializer(data={**data, 'budget': budget.id})
        elif record_type == 'expense':
            serializer = ExpensesSerializer(data={**data, 'budget': budget.id})
        else:
            return JsonResponse({'error': 'Invalid type'}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)