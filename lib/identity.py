import random


def read_file_as_list(filepath):
    with open(filepath) as f:
        return f.read().splitlines()


FIRST_NAMES = read_file_as_list("data/firstnames.txt")
LAST_NAMES = read_file_as_list("data/lastnames.txt")
EMAIL_PROVIDERS = read_file_as_list("data/email-providers.txt")


class Identity:
    def __init__(self, firstname=None, lastname=None, email=None) -> None:
        """Create a new identity. If no name or email is given, it is
        randomly generated."""
        self.firstname = firstname or random.choice(FIRST_NAMES)
        self.lastname = lastname or random.choice(LAST_NAMES)
        self.email = email or self.generate_fake_email(self.firstname, self.lastname)

    def generate_fake_email(self):
        name_separator = "." if random.random() > 0.6 else ""
        fn = (
            self.firstname[0]
            if name_separator and random.random() > 0.7
            else self.firstname
        )
        birth_year = random.randint(55, 99) if random.random() > 0.3 else ""
        mail = f"{fn.lower()}{name_separator}{self.lastname.lower()}{birth_year}@{random.choice(EMAIL_PROVIDERS)}"
        return mail.encode("ascii", "ignore").decode("ascii")

    def __str__(self) -> str:
        return f"{self.firstname} {self.lastname} <{self.email}>"
