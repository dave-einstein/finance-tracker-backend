from rest_framework import serializers
from .models import User,Budget,Income,Savings,Investment,Expense

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'username', 'email', 'currency', 'created_at']

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ['id', 'user', 'description', 'year', 'month', 'created_at']

class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = ['id', 'description', 'budget', 'income_type','amount', 'created_at']

class SavingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Savings
        fields = ['id', 'description', 'budget','amount', 'created_at']

class InvestmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investment
        fields = ['id', 'description', 'budget','amount', 'created_at']

class ExpensesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['id', 'description', 'budget','amount', 'created_at']