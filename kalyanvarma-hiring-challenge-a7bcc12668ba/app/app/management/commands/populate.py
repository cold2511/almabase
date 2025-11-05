import random
from django.core.management.base import BaseCommand
from faker import Faker
from app.models.contact import Contact
from app.models.scam import ScamRecord
from app.models.user import User

fake = Faker()

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        self.populate_database()

    def create_sample_user(self):
        first_name = fake.first_name()
        last_name = fake.last_name()
        phone_number = fake.phone_number()[:10]
        password = fake.password()
        email = fake.email() if random.choice([True, False]) else None
        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            password=password,
            email=email
        )
        return user

    def create_sample_contact(self, user):
        first_name = fake.first_name()
        last_name = fake.last_name()
        phone_number = fake.phone_number()[:10]
        contact = Contact.objects.create(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            created_by=user,
            updated_by=user
        )
        return contact

    def create_sample_spam(self, phone_number, user):
        spam = ScamRecord.objects.create(
            phone_number=phone_number,
            reported_by=user,
            created_by=user,
            updated_by=user,
        )
        return spam

    def populate_database(self, num_users=100, max_contacts_per_user=10, max_spam_per_user=10):
        users = []

        for _ in range(num_users):
            user = self.create_sample_user()
            users.append(user)

        for user in users:
            num_contacts = random.randint(0, max_contacts_per_user)
            for _ in range(num_contacts):
                self.create_sample_contact(user)

        for user in users:
            num_spam = random.randint(0, max_spam_per_user)
            for _ in range(num_spam):
                phone_number = fake.phone_number()[:10]
                self.create_sample_spam(phone_number, user)

        print('Database populated with sample data')

