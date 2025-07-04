import os
import django
from datetime import datetime, date
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from apps.shared.models import User, AccountType

def create_sample_alumni_data():
    # Get alumni account type
    try:
        alumni_account_type = AccountType.objects.get(user=True, admin=False, peso=False, coordinator=False)
    except AccountType.DoesNotExist:
        print("Error: Alumni account type not found")
        return
    
    # Sample data for realistic alumni
    sample_alumni = [
        {
            'ctu_id': '1337566',
            'f_name': 'Maria',
            'm_name': 'Santos',
            'l_name': 'Garcia',
            'gender': 'F',
            'birthdate': '2002-03-15',
            'course': 'BSIT',
            'year_graduated': 2023,
            'user_status': 'Employed',
            'phone_num': '09123456789',
            'address': 'Cebu City, Philippines'
        },
        {
            'ctu_id': '1337567',
            'f_name': 'John',
            'm_name': 'Michael',
            'l_name': 'Rodriguez',
            'gender': 'M',
            'birthdate': '2001-07-22',
            'course': 'BSIT',
            'year_graduated': 2023,
            'user_status': 'Employed',
            'phone_num': '09187654321',
            'address': 'Mandaue City, Philippines'
        },
        {
            'ctu_id': '1337568',
            'f_name': 'Ana',
            'm_name': 'Clara',
            'l_name': 'Martinez',
            'gender': 'F',
            'birthdate': '2002-11-08',
            'course': 'BSIS',
            'year_graduated': 2023,
            'user_status': 'Unemployed',
            'phone_num': '09234567890',
            'address': 'Lapu-Lapu City, Philippines'
        },
        {
            'ctu_id': '1337569',
            'f_name': 'Carlos',
            'm_name': 'Jose',
            'l_name': 'Lopez',
            'gender': 'M',
            'birthdate': '2001-12-03',
            'course': 'BSIT',
            'year_graduated': 2023,
            'user_status': 'High Position',
            'phone_num': '09345678901',
            'address': 'Talisay City, Philippines'
        },
        {
            'ctu_id': '1337570',
            'f_name': 'Isabella',
            'm_name': 'Rose',
            'l_name': 'Fernandez',
            'gender': 'F',
            'birthdate': '2002-05-18',
            'course': 'BSIS',
            'year_graduated': 2023,
            'user_status': 'Absorb',
            'phone_num': '09456789012',
            'address': 'Cebu City, Philippines'
        },
        {
            'ctu_id': '1337571',
            'f_name': 'Miguel',
            'm_name': 'Angel',
            'l_name': 'Gonzalez',
            'gender': 'M',
            'birthdate': '2001-09-30',
            'course': 'BIT-CT',
            'year_graduated': 2023,
            'user_status': 'Employed',
            'phone_num': '09567890123',
            'address': 'Mandaue City, Philippines'
        },
        {
            'ctu_id': '1337572',
            'f_name': 'Sofia',
            'm_name': 'Elena',
            'l_name': 'Perez',
            'gender': 'F',
            'birthdate': '2002-01-14',
            'course': 'BSIT',
            'year_graduated': 2023,
            'user_status': 'High Position',
            'phone_num': '09678901234',
            'address': 'Lapu-Lapu City, Philippines'
        },
        {
            'ctu_id': '1337573',
            'f_name': 'Diego',
            'm_name': 'Rafael',
            'l_name': 'Torres',
            'gender': 'M',
            'birthdate': '2001-04-25',
            'course': 'BSIS',
            'year_graduated': 2023,
            'user_status': 'Unemployed',
            'phone_num': '09789012345',
            'address': 'Talisay City, Philippines'
        },
        {
            'ctu_id': '1337574',
            'f_name': 'Valentina',
            'm_name': 'Isabel',
            'l_name': 'Ramirez',
            'gender': 'F',
            'birthdate': '2002-08-12',
            'course': 'BIT-CT',
            'year_graduated': 2023,
            'user_status': 'Absorb',
            'phone_num': '09890123456',
            'address': 'Cebu City, Philippines'
        },
        {
            'ctu_id': '1337575',
            'f_name': 'Alejandro',
            'm_name': 'Luis',
            'l_name': 'Cruz',
            'gender': 'M',
            'birthdate': '2001-06-07',
            'course': 'BSIT',
            'year_graduated': 2023,
            'user_status': 'Employed',
            'phone_num': '09901234567',
            'address': 'Mandaue City, Philippines'
        },
        # 2022 batch
        {
            'ctu_id': '1337576',
            'f_name': 'Camila',
            'm_name': 'Victoria',
            'l_name': 'Reyes',
            'gender': 'F',
            'birthdate': '2001-02-28',
            'course': 'BSIT',
            'year_graduated': 2022,
            'user_status': 'High Position',
            'phone_num': '09912345678',
            'address': 'Lapu-Lapu City, Philippines'
        },
        {
            'ctu_id': '1337577',
            'f_name': 'Gabriel',
            'm_name': 'Antonio',
            'l_name': 'Morales',
            'gender': 'M',
            'birthdate': '2000-10-15',
            'course': 'BSIS',
            'year_graduated': 2022,
            'user_status': 'Employed',
            'phone_num': '09923456789',
            'address': 'Talisay City, Philippines'
        },
        {
            'ctu_id': '1337578',
            'f_name': 'Lucia',
            'm_name': 'Carmen',
            'l_name': 'Ortiz',
            'gender': 'F',
            'birthdate': '2001-12-20',
            'course': 'BIT-CT',
            'year_graduated': 2022,
            'user_status': 'Absorb',
            'phone_num': '09934567890',
            'address': 'Cebu City, Philippines'
        },
        {
            'ctu_id': '1337579',
            'f_name': 'Adrian',
            'm_name': 'Javier',
            'l_name': 'Silva',
            'gender': 'M',
            'birthdate': '2000-07-04',
            'course': 'BSIT',
            'year_graduated': 2022,
            'user_status': 'Unemployed',
            'phone_num': '09945678901',
            'address': 'Mandaue City, Philippines'
        },
        {
            'ctu_id': '1337580',
            'f_name': 'Elena',
            'm_name': 'Patricia',
            'l_name': 'Vargas',
            'gender': 'F',
            'birthdate': '2001-03-11',
            'course': 'BSIS',
            'year_graduated': 2022,
            'user_status': 'Employed',
            'phone_num': '09956789012',
            'address': 'Lapu-Lapu City, Philippines'
        }
    ]
    
    created_count = 0
    skipped_count = 0
    
    for alumni_data in sample_alumni:
        # Check if user already exists
        if User.objects.filter(acc_username=alumni_data['ctu_id']).exists():
            print(f"Skipped: CTU ID {alumni_data['ctu_id']} already exists")
            skipped_count += 1
            continue
        
        # Parse birthdate
        birthdate = datetime.strptime(alumni_data['birthdate'], "%Y-%m-%d").date()
        
        # Create the alumni user
        user = User.objects.create(
            acc_username=alumni_data['ctu_id'],
            acc_password=birthdate,
            user_status=alumni_data['user_status'],
            f_name=alumni_data['f_name'],
            m_name=alumni_data['m_name'],
            l_name=alumni_data['l_name'],
            gender=alumni_data['gender'],
            phone_num=alumni_data['phone_num'],
            address=alumni_data['address'],
            year_graduated=alumni_data['year_graduated'],
            course=alumni_data['course'],
            account_type=alumni_account_type
        )
        
        print(f"Created: {user.f_name} {user.l_name} ({user.acc_username}) - {user.user_status}")
        created_count += 1
    
    print(f"\nSummary:")
    print(f"Created: {created_count} alumni accounts")
    print(f"Skipped: {skipped_count} duplicates")

if __name__ == "__main__":
    create_sample_alumni_data() 