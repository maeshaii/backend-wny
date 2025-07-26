import os
import django
import pandas as pd
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

def simple_job_populate():
    print("=== SIMPLE JOB POPULATION ===")
    
    try:
        # Read the Excel file
        df = pd.read_excel('job_alignment_mapping.xlsx')
        print(f"Loaded Excel file with {len(df)} rows")
        
        # Clear existing data using raw SQL
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM shared_infosystemjob")
            cursor.execute("DELETE FROM shared_infotechjob")
            cursor.execute("DELETE FROM shared_comptechjob")
        print("Cleared existing job mapping data")
        
        # Process each row
        for index, row in df.iterrows():
            try:
                job_title = str(row.get('Job Title', '')).strip()
                course = str(row.get('Course', '')).strip().upper()
                
                if not job_title or job_title == 'nan':
                    continue
                
                # Use raw SQL to insert without foreign key constraints
                with connection.cursor() as cursor:
                    if 'BSIS' in course or 'INFORMATION SYSTEMS' in course:
                        cursor.execute(
                            "INSERT INTO shared_infosystemjob (job_title) VALUES (%s)",
                            [job_title]
                        )
                        print(f"Added BSIS: {job_title}")
                    elif 'BSIT' in course or 'INFORMATION TECHNOLOGY' in course:
                        cursor.execute(
                            "INSERT INTO shared_infotechjob (job_title) VALUES (%s)",
                            [job_title]
                        )
                        print(f"Added BSIT: {job_title}")
                    elif 'BIT-CT' in course or 'COMPUTER TECHNOLOGY' in course:
                        cursor.execute(
                            "INSERT INTO shared_comptechjob (job_title) VALUES (%s)",
                            [job_title]
                        )
                        print(f"Added BIT-CT: {job_title}")
                    else:
                        # Add to all three
                        cursor.execute(
                            "INSERT INTO shared_infosystemjob (job_title) VALUES (%s)",
                            [job_title]
                        )
                        cursor.execute(
                            "INSERT INTO shared_infotechjob (job_title) VALUES (%s)",
                            [job_title]
                        )
                        cursor.execute(
                            "INSERT INTO shared_comptechjob (job_title) VALUES (%s)",
                            [job_title]
                        )
                        print(f"Added to all courses: {job_title}")
                        
            except Exception as e:
                print(f"Error processing row {index}: {e}")
                continue
        
        # Print summary
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM shared_infosystemjob")
            bsis_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM shared_infotechjob")
            bsit_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM shared_comptechjob")
            bit_ct_count = cursor.fetchone()[0]
        
        print(f"\n=== SUMMARY ===")
        print(f"InfoSystemJob (BSIS): {bsis_count} jobs")
        print(f"InfoTechJob (BSIT): {bsit_count} jobs")
        print(f"CompTechJob (BIT-CT): {bit_ct_count} jobs")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    simple_job_populate() 