import random
import time


def log(line):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {line}", flush=True)


def get_lines_as_list(filepath):
    with open(filepath) as f:
        return f.read().splitlines()


def generate_fake_email(fn, ln):
    name_separator = "." if random.random() > 0.6 else ""
    fn = fn[0] if name_separator and random.random() > 0.7 else fn
    birth_year = random.randint(55, 99) if random.random() > 0.3 else ""
    mail = f"{fn.lower()}{name_separator}{ln.lower()}{birth_year}@{random.choice(_email_providers)}"
    return mail.encode("ascii", "ignore").decode("ascii")


_email_providers = get_lines_as_list("email-providers.txt")
