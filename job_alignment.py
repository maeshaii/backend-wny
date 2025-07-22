import pandas as pd

ALIGNMENT_FILE = 'job_alignment_mapping.xlsx'

# Load the mapping table once (for performance)
def load_alignment_mapping():
    df = pd.read_excel(ALIGNMENT_FILE)
    # Normalize columns
    df['Course'] = df['Course'].str.upper().str.strip()
    df['Job Code'] = df['Job Code'].astype(str).str.strip()
    return df

alignment_df = load_alignment_mapping()

def is_job_aligned_excel(course, job_code):
    """
    Returns True if the job_code is aligned with the course, False otherwise.
    """
    if not course or not job_code:
        return False
    course = str(course).upper().strip()
    job_code = str(job_code).strip()
    match = alignment_df[(alignment_df['Course'] == course) & (alignment_df['Job Code'] == job_code)]
    return not match.empty

# Example usage:
# print(is_job_aligned_excel('BSIT', '15-1132'))  # True
# print(is_job_aligned_excel('BSIS', '15-1132'))  # False 