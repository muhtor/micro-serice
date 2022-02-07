import secrets
import binascii
import os


def random_string_generator():
    allowed_char = "0123456789abcdefghijklmnopqrstuvwxyz"
    return ''.join(secrets.choice(allowed_char) for i in range(12))


def random_activation_code():
    random_number = '123456789'
    generated = ''.join(secrets.choice(random_number) for i in range(6))
    return generated


def generate_activation_sms(instance):
    code = random_activation_code()
    # Klass = instance.__class__
    # qs_code = Klass.objects.filter(code=str(code), activated=False)
    # if qs_code.exists():
    #     return random_string_generator()
    return code


def random_token_generator():
    allowed_char = "0123456789abcdefghijklmnopqrstuvwxyz"
    return ''.join(secrets.choice(allowed_char) for i in range(15))


def otp_generator(instance):
    """One Time Password Generate :)"""
    token = random_string_generator()
    Klass = instance.__class__
    qs_exists = Klass.objects.filter(one_time_pwd=token)
    if qs_exists.exists():
        return random_string_generator()
    return token


def generate_auth_key():
    return binascii.hexlify(os.urandom(20)).decode()





