import random
import secrets


def order_id_generator():
    random_char = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    random_number = '0123456789'
    prefix = ''.join(secrets.choice(random_char) for i in range(2))
    order_id = ''.join(secrets.choice(random_number) for i in range(4))
    return f"{prefix}{order_id}"


def generate_number(count: int):
    random_number = '123456789'
    return ''.join(secrets.choice(random_number) for i in range(count))


def random_loop(start, end):
    return random.randint(start, end)


def generate_order_secure_code():
    random_number = '123456789'
    code = ''.join(secrets.choice(random_number) for i in range(4))
    return code




