from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class AccountManager(BaseUserManager):
	def create_account(self, email=None, password=None, **extra_fields):
		from core.utils import factory
		if not email:
			raise ValueError(_("Email must be set"))

		if not password:
			raise ValueError(_("Password must be set"))

		account = self.create(email=self.normalize_email(email), password=make_password(password), **extra_fields)
		factory.set_permissions_for_account(account)

		return account

	def create_superuser(self, email=None, password=None, **extra_fields):
		from core.utils import factory
		extra_fields.setdefault("is_staff", True)
		extra_fields.setdefault("is_superuser", True)
		extra_fields.setdefault("role", self.model.Role.ADMINISTRATOR)
		extra_fields.setdefault("avatar", factory.get_or_upload_image(ftype="avatar"))

		from users.models import Administrator
		account = self.create_account(email=email, password=password, **extra_fields)
		administrator = Administrator.objects.create(account=account, first_name=f"Administrator {account.id}", date_of_birth=timezone.now(), )
		factory.set_role_for_account(user=administrator, account=account)

		return account
