"""
Integration tests for the Alpha Trader User model.

These tests require a live connection to the Alpha Trader API.
See conftest.py for required environment variables.

Usage:
    pytest tests/user/test_user.py -v
"""

import os
import pytest


class TestUserModel:
    """Tests for User model initialization and properties."""

    def test_user_has_valid_id(self, user):
        """Test that user has a valid ID."""
        assert user.id is not None
        assert isinstance(user.id, str)
        assert len(user.id) > 0

    def test_user_has_username(self, user, api_credentials):
        """Test that user has the expected username."""
        assert user.username is not None
        assert user.username == api_credentials["username"]

    def test_user_has_email(self, user):
        """Test that own user has email address."""
        assert user.email is not None
        assert "@" in user.email

    def test_user_has_jwt_token(self, user):
        """Test that own user has JWT token."""
        assert user.jwt_token is not None
        assert isinstance(user.jwt_token, str)

    def test_user_is_my_user(self, user):
        """Test that user is marked as own user."""
        assert user.my_user is True

    def test_user_has_capabilities(self, user):
        """Test that user has capabilities object."""
        assert user.capabilities is not None
        assert hasattr(user.capabilities, "locale")
        assert hasattr(user.capabilities, "premium")


class TestUserAchievements:
    """Tests for User achievements functionality."""

    def test_achievements_is_list(self, user):
        """Test that achievements returns a list."""
        achievements = user.achievements

        assert achievements is not None
        assert isinstance(achievements, list)

    def test_achievements_have_expected_attributes(self, user):
        """Test that achievements have expected attributes."""
        achievements = user.achievements

        if len(achievements) > 0:
            achievement = achievements[0]
            assert hasattr(achievement, "description")
            assert hasattr(achievement, "type")
            assert hasattr(achievement, "claimed")
            assert hasattr(achievement, "id")


class TestUserSecuritiesAccount:
    """Tests for User securities account functionality."""

    def test_securities_account_exists(self, user):
        """Test that user has a securities account."""
        securities_account = user.securities_account

        assert securities_account is not None

    def test_securities_account_is_private(self, user):
        """Test that user's securities account is private."""
        securities_account = user.securities_account

        assert securities_account.private_account is True

    def test_securities_account_has_id(self, user):
        """Test that securities account has an ID."""
        securities_account = user.securities_account

        assert securities_account.id is not None
        assert isinstance(securities_account.id, str)

    def test_securities_account_has_clearing_account(self, user):
        """Test that securities account has a clearing account ID."""
        securities_account = user.securities_account

        assert securities_account.clearing_account_id is not None


class TestUserBankAccount:
    """Tests for User bank account functionality."""

    def test_bank_account_exists(self, user):
        """Test that user has a bank account."""
        bank_account = user.bank_account

        assert bank_account is not None

    def test_bank_account_has_id(self, user):
        """Test that bank account has an ID."""
        bank_account = user.bank_account

        assert bank_account.id is not None

    def test_bank_account_has_cash(self, user):
        """Test that bank account has cash attribute."""
        bank_account = user.bank_account

        assert hasattr(bank_account, "cash")
        assert isinstance(bank_account.cash, (int, float))


class TestUserCompanies:
    """Tests for User companies functionality."""

    def test_companies_is_list(self, user):
        """Test that companies returns a list."""
        companies = user.companies

        assert companies is not None
        assert isinstance(companies, list)


class TestUserSalary:
    """Tests for User salary functionality."""

    def test_salary_is_numeric(self, user):
        """Test that salary returns a numeric value."""
        salary = user.salary

        assert salary is not None
        assert isinstance(salary, (int, float))
        assert salary >= 0
