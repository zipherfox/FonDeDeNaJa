import random
import string

def generate_cookie(length=32):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

if __name__ == "__main__":
    print(generate_cookie())