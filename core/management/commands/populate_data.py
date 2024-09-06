from faker import Faker
import random
from datetime import datetime, timedelta


from core.models import *
from client.models import *
from freelancer.models import *
fake = Faker()

def create_custom_users(num=10):
    for _ in range(num):
        CustomUser.objects.create(
            username=fake.user_name(),
            email=fake.email(),
            password=fake.password(),
            is_superuser=random.choice([True, False]),
            is_staff=random.choice([True, False]),
            status=random.choice(['active', 'inactive']),
            role=random.choice(['admin', 'client', 'freelancer']),
            welcome_email_sent=fake.boolean(),
            permission=fake.boolean(),
            email_verified=fake.boolean(),
            google=fake.boolean(),
        )

def create_registers(num=10):
    for _ in range(num):
        user = CustomUser.objects.order_by('?').first()  # Pick a random user
        Register.objects.create(
            user=user,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone_number=fake.phone_number(),
            profile_picture=fake.image_url(),
            bio_description=fake.text(max_nb_chars=200),
            location=fake.city(),
            linkedin=fake.url(),
            instagram=fake.url(),
            twitter=fake.url(),
            status=random.choice(['active', 'inactive']),
        )

def create_freelancer_profiles(num=10):
    for _ in range(num):
        user = CustomUser.objects.filter(role='freelancer').order_by('?').first()  # Pick a random freelancer
        FreelancerProfile.objects.create(
            user=user,
            professional_title=fake.job(),
            skills=', '.join(fake.words(nb=5)),
            experience_level=fake.word(),
            portfolio_link=fake.url(),
            education=fake.text(max_nb_chars=200),
            resume=fake.file_name(),
            aadhaar_document=fake.file_name(),
            status=random.choice(['active', 'inactive']),
            work_type=random.choice(['full_time', 'part_time']),
        )

def create_todos(num=10):
    for _ in range(num):
        user = CustomUser.objects.order_by('?').first()  # Pick a random user
        Todo.objects.create(
            user=user,
            title=fake.sentence(nb_words=3),
            is_completed=fake.boolean(),
        )

def create_proposals(num=10):
    for _ in range(num):
        project = Project.objects.order_by('?').first()  # Pick a random project
        freelancer = CustomUser.objects.filter(role='freelancer').order_by('?').first()  # Pick a random freelancer
        Proposal.objects.create(
            project=project,
            freelancer=freelancer,
            date_issued=fake.date_this_year(),
            proposal_details=fake.text(),
            budget=fake.random_number(digits=5),
            deadline=fake.date_this_year(),
            status=random.choice(['Pending', 'Accepted', 'Rejected']),
            fancy_num=fake.random_number(digits=5),
            proposal_file=fake.file_name(),
            locked=fake.boolean(),
        )

def create_proposal_files(num=10):
    for _ in range(num):
        proposal = Proposal.objects.order_by('?').first()  # Pick a random proposal
        ProposalFile.objects.create(
            proposal=proposal,
            file=fake.file_name(),
            uploaded_at=fake.date_time_this_year(),
        )

def create_client_profiles(num=10):
    for _ in range(num):
        user = CustomUser.objects.filter(role='client').order_by('?').first()  # Pick a random client
        ClientProfile.objects.create(
            user=user,
            client_type=random.choice(['Individual', 'Company']),
            company_name=fake.company(),
            website=fake.url(),
            license_number=fake.random_number(digits=10),
            aadhaar_document=fake.file_name(),
            status=random.choice(['active', 'inactive']),
        )

def create_projects(num=10):
    for _ in range(num):
        user = CustomUser.objects.filter(role='client').order_by('?').first()  # Pick a random client
        Project.objects.create(
            title=fake.sentence(nb_words=6),
            description=fake.text(),
            budget=fake.random_number(digits=5),
            category=fake.word(),
            allow_bid=fake.boolean(),
            end_date=fake.date_this_year(),
            file_upload=fake.file_name(),
            created_at=fake.date_time_this_year(),
            user=user,
            status=random.choice(['open', 'closed']),
            start_date=fake.date_this_year(),
            project_end_date=fake.date_this_year(),
            project_status=random.choice(['Not Started', 'In Progress', 'Completed']),
            freelancer=CustomUser.objects.filter(role='freelancer').order_by('?').first(),  # Pick a random freelancer
            git_repo_link=fake.url(),
            gst_rate=fake.random_number(digits=2),
        )

def create_repositories(num=10):
    for _ in range(num):
        project = Project.objects.order_by('?').first()  # Pick a random project
        Repository.objects.create(
            project=project,
            name=fake.word(),
            created_by=CustomUser.objects.order_by('?').first(),  # Pick a random user
        )

def create_shared_files(num=10):
    for _ in range(num):
        repository = Repository.objects.order_by('?').first()  # Pick a random repository
        SharedFile.objects.create(
            repository=repository,
            file=fake.file_name(),
            description=fake.text(max_nb_chars=100),
            uploaded_by=CustomUser.objects.order_by('?').first(),  # Pick a random user
        )

def create_shared_urls(num=10):
    for _ in range(num):
        repository = Repository.objects.order_by('?').first()  # Pick a random repository
        SharedURL.objects.create(
            repository=repository,
            url=fake.url(),
            description=fake.text(max_nb_chars=100),
            shared_by=CustomUser.objects.order_by('?').first(),  # Pick a random user
        )

def create_shared_notes(num=10):
    for _ in range(num):
        repository = Repository.objects.order_by('?').first()  # Pick a random repository
        SharedNote.objects.create(
            repository=repository,
            note=fake.text(),
            added_by=CustomUser.objects.order_by('?').first(),  # Pick a random user
        )

def create_tasks(num=10):
    for _ in range(num):
        project = Project.objects.order_by('?').first()  # Pick a random project
        Task.objects.create(
            project=project,
            title=fake.sentence(nb_words=4),
            description=fake.text(),
            start_date=fake.date_this_year(),
            due_date=fake.date_this_year() + timedelta(days=random.randint(1, 30)),
            status=random.choice(['Pending', 'In Progress', 'Completed', 'On Hold']),
            created_at=fake.date_time_this_year(),
            updated_at=fake.date_time_this_year(),
            progress_percentage=random.uniform(0.0, 100.0),
        )

def create_freelance_contracts(num=10):
    for _ in range(num):
        client = CustomUser.objects.filter(role='client').order_by('?').first()  # Pick a random client
        freelancer = CustomUser.objects.filter(role='freelancer').order_by('?').first()  # Pick a random freelancer
        project = Project.objects.order_by('?').first()  # Pick a random project
        FreelanceContract.objects.create(
            client=client,
            freelancer=freelancer,
            project=project,
            client_signature=fake.file_name(),
            freelancer_signature=fake.file_name(),
            contract_date=fake.date_this_year(),
            pdf_version=fake.file_name(),
        )

def create_payment_installments(num=10):
    for _ in range(num):
        contract = FreelanceContract.objects.order_by('?').first()  # Pick a random contract
        PaymentInstallment.objects.create(
            contract=contract,
            amount=fake.random_number(digits=5),
            due_date=fake.date_this_year(),
            status=random.choice(['pending', 'paid']),
            razorpay_order_id=fake.uuid4(),
            razorpay_payment_id=fake.uuid4(),
            paid_at=fake.date_this_year(),
        )

def create_reviews(num=10):
    for _ in range(num):
        project = Project.objects.order_by('?').first()  # Pick a random project
        reviewer = CustomUser.objects.order_by('?').first()  # Pick a random reviewer
        reviewee = CustomUser.objects.order_by('?').first()  # Pick a random reviewee
        Review.objects.create(
            project=project,
            reviewer=reviewer,
            reviewee=reviewee,
            review_text=fake.text(),
            overall_rating=random.uniform(0, 5),
            quality_of_work=random.uniform(0, 5),
            communication=random.uniform(0, 5),
            adherence_to_deadlines=random.uniform(0, 5),
            professionalism=random.uniform(0, 5),
            problem_solving_ability=random.uniform(0, 5),
            review_date=fake.date_time_this_year(),
        )

# Call functions to populate the database
create_custom_users(10)
create_registers(10)
create_freelancer_profiles(10)
create_todos(10)
create_proposals(10)
create_proposal_files(10)
create_client_profiles(10)
create_projects(10)
create_repositories(10)
create_shared_files(10)
create_shared_urls(10)
create_shared_notes(10)
create_tasks(10)
create_freelance_contracts(10)
create_payment_installments(10)
create_reviews(10)
