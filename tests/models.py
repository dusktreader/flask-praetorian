from tortoise.models import Model
from tortoise import fields
from tortoise.exceptions import DoesNotExist

from sanic_praetorian import TortoiseUserMixin


class User(Model):
    """
    Provides a basic user model for use in the tests
    """

    class Meta:
        table = "User"

    id = fields.IntField(pk=True)
    username = fields.CharField(unique=True, max_length=255)
    password = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255, unique=True, required=False)
    roles = fields.CharField(max_length=255, default='')
    is_active = fields.BooleanField(default=True)

    def __str__(self):
        return f"User {self.id}: {self.username}"

    @property
    def rolenames(self):
        try:
            return self.roles.split(",")
        except Exception:
            return []

    @classmethod
    async def lookup(cls, username=None, email=None):
        try:
            if username:
                return await cls.filter(username=username).get()
            elif email:
                return await cls.filter(email=email).get()
            else:
                return None
        except DoesNotExist:
            return None

    @classmethod
    async def identify(cls, id):
        try:
            return await cls.filter(id=id).get()
        except DoesNotExist:
            return None

    @property
    def identity(self):
        return self.id

    def is_valid(self):
        return self.is_active


class MixinUser(Model, TortoiseUserMixin):

    class Meta:
        table = "MixinUser"

    id = fields.IntField(pk=True)
    username = fields.CharField(unique=True, max_length=255)
    password = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255, unique=True, required=False)
    roles = fields.CharField(max_length=255, default='')


class ValidatingUser(User):

    class Meta:
        table = "ValidatingUser"

    id = fields.IntField(pk=True)
    username = fields.CharField(unique=True, max_length=255)
    password = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255, unique=True, required=False)
    roles = fields.CharField(max_length=255, default='')
    is_active = fields.BooleanField(default=True)

    def is_valid(self):
        return self.is_active


class TotpUser(User, Model, TortoiseUserMixin):

    class Meta:
        table = "TotpUser"

    totp = fields.CharField(max_length=255, default=None, null=True)
    totp_last_counter = fields.IntField(default=None, null=True)

    async def cache_verify(self, counter=None, seconds=None):
        self.totp_last_counter = counter
        await self.save(update_fields=["totp_last_counter"])

    async def get_cache_verify(self):
        return self.totp_last_counter
