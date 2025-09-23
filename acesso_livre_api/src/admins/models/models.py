from ..auth.models import Auth, ResetTokenMixin

class Admin(Auth, ResetTokenMixin):
    __tablename__ = "admins"