import bcrypt


class PasswordService:

    @staticmethod
    def hash_password(password: str) -> bytes:
        salt: bytes = bcrypt.gensalt()
        pwd_bytes: bytes = password.encode()
        return bcrypt.hashpw(pwd_bytes, salt)

    @staticmethod
    def check_password(
            password: str,
            hashed_password: bytes) -> bool:
        return bcrypt.checkpw(password=password.encode(), hashed_password=hashed_password)


password_service = PasswordService()

