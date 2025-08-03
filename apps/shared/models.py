from django.db import models
from datetime import datetime

class AccountType(models.Model):
    account_type_id = models.AutoField(primary_key=True)
    admin = models.BooleanField()
    peso = models.BooleanField()
    user = models.BooleanField()
    coordinator = models.BooleanField()
    ojt = models.BooleanField(default=False)  # Added for OJT account type with default



class Aacup(models.Model):
    aacup_id = models.AutoField(primary_key=True)
    standard = models.ForeignKey('Standard', on_delete=models.CASCADE, related_name='aacups')

class Ched(models.Model):
    ched_id = models.AutoField(primary_key=True)
    standard = models.ForeignKey('Standard', on_delete=models.CASCADE, related_name='cheds')
    job_alignment_count = models.IntegerField(default=0)

class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    comment_content = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField()

class CompTechJob(models.Model):
    comp_tech_jobs_id = models.AutoField(primary_key=True)
    suc = models.ForeignKey('Suc', on_delete=models.CASCADE, related_name='comptechjob_sucs')
    info_system_jobs = models.ForeignKey('InfoSystemJob', on_delete=models.CASCADE, related_name='comptechjob_infosystemjobs')
    info_tech_jobs = models.ForeignKey('InfoTechJob', on_delete=models.CASCADE, related_name='comptechjob_infotechjobs')
    job_title = models.CharField(max_length=255)

class ExportedFile(models.Model):
    exported_file_id = models.AutoField(primary_key=True)
    standard = models.ForeignKey('Standard', on_delete=models.CASCADE, related_name='exported_files')
    file_name = models.CharField(max_length=255)
    exported_date = models.DateTimeField()

class Feed(models.Model):
    feed_id = models.AutoField(primary_key=True)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='feeds')
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='feeds')

class Forum(models.Model):
    forum_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='forums')
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='forums')
    comment = models.ForeignKey('Comment', on_delete=models.SET_NULL, null=True, related_name='forums')
    like = models.ForeignKey('Like', on_delete=models.SET_NULL, null=True, related_name='forums')

class HighPosition(models.Model):
    high_position_id = models.AutoField(primary_key=True)
    aacup = models.ForeignKey('Aacup', on_delete=models.CASCADE, related_name='high_positions')
    tracker_form = models.ForeignKey('TrackerForm', on_delete=models.CASCADE, related_name='high_positions')

class Import(models.Model):
    import_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='imports')
    import_year = models.IntegerField()
    import_by = models.CharField(max_length=255)

class InfoTechJob(models.Model):
    info_tech_jobs_id = models.AutoField(primary_key=True)
    suc = models.ForeignKey('Suc', on_delete=models.CASCADE, related_name='infotechjob_sucs')
    info_systems_jobs = models.ForeignKey('InfoSystemJob', on_delete=models.CASCADE, related_name='infotechjob_infosystemjobs')
    comp_tech_jobs = models.ForeignKey('CompTechJob', on_delete=models.CASCADE, related_name='infotechjob_comptechjobs')
    job_title = models.CharField(max_length=255)

class InfoSystemJob(models.Model):
    info_system_jobs_id = models.AutoField(primary_key=True)
    suc = models.ForeignKey('Suc', on_delete=models.CASCADE, related_name='infosystemjob_sucs')
    info_tech_jobs = models.ForeignKey('InfoTechJob', on_delete=models.CASCADE, related_name='infosystemjob_infotechjobs')
    comp_tech_jobs = models.ForeignKey('CompTechJob', on_delete=models.CASCADE, related_name='infosystemjob_comptechjobs')
    job_title = models.CharField(max_length=255)

class Like(models.Model):
    like_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='likes')

class Message(models.Model):
    message_id = models.AutoField(primary_key=True)
    sender_id = models.IntegerField()
    receiver_id = models.IntegerField()
    message_content = models.TextField()
    date_send = models.DateTimeField()

class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='notifications')
    notif_type = models.CharField(max_length=100)
    subject = models.CharField(max_length=255, blank=True, null=True)  # Added subject field
    notifi_content = models.TextField()
    notif_date = models.DateTimeField()

class PostCategory(models.Model):
    post_cat_id = models.AutoField(primary_key=True)
    events = models.BooleanField()
    announcements = models.BooleanField()
    donation = models.BooleanField()
    personal = models.BooleanField()

class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='posts')
    post_cat = models.ForeignKey('PostCategory', on_delete=models.CASCADE, related_name='posts')
    post_title = models.CharField(max_length=255)
    post_image = models.ImageField(upload_to='post_images/', null=True, blank=True)
    post_content = models.TextField()
    type = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Qpro(models.Model):
    qpro_id = models.AutoField(primary_key=True)
    standard = models.ForeignKey('Standard', on_delete=models.CASCADE, related_name='qpros')

class Repost(models.Model):
    repost_id = models.AutoField(primary_key=True)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='reposts')
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='reposts')
    repost_date = models.DateTimeField()

class Standard(models.Model):
    standard_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, default="CTU Standard")
    description = models.TextField(blank=True)
    qpro = models.ForeignKey('Qpro', on_delete=models.CASCADE, related_name='standards', null=True, blank=True)
    suc = models.ForeignKey('Suc', on_delete=models.CASCADE, related_name='standards', null=True, blank=True)
    aacup = models.ForeignKey('Aacup', on_delete=models.CASCADE, related_name='standards', null=True, blank=True)
    ched = models.ForeignKey('Ched', on_delete=models.CASCADE, related_name='standards', null=True, blank=True)

class Suc(models.Model):
    suc_id = models.AutoField(primary_key=True)
    standard = models.ForeignKey('Standard', on_delete=models.CASCADE, related_name='suc_sucs')
    info_tech_jobs = models.ForeignKey('InfoTechJob', on_delete=models.CASCADE, related_name='suc_infotechjobs')
    info_system_jobs = models.ForeignKey('InfoSystemJob', on_delete=models.CASCADE, related_name='suc_infosystemjobs')
    comp_tech_jobs = models.ForeignKey('CompTechJob', on_delete=models.CASCADE, related_name='suc_comptechjobs')

class TrackerForm(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, default="CTU Alumni Tracker Form")
    description = models.TextField(blank=True)
    accepting_responses = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # Ensure only one tracker form exists
        constraints = [
            models.CheckConstraint(
                check=models.Q(id=1),
                name='single_tracker_form'
            )
        ]

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    import_id = models.ForeignKey('Import', on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    account_type = models.ForeignKey('AccountType', on_delete=models.CASCADE, related_name='users')
    acc_username = models.CharField(max_length=100, unique=True)
    acc_password = models.DateField()
    user_status = models.CharField(max_length=50)
    f_name = models.CharField(max_length=100)
    m_name = models.CharField(max_length=100, null=True, blank=True)
    l_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    phone_num = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    profile_bio = models.TextField(null=True, blank=True)
    profile_resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    year_graduated = models.IntegerField(null=True, blank=True)
    course = models.CharField(max_length=100, null=True, blank=True)
    section = models.CharField(max_length=50, null=True, blank=True)
    civil_status = models.CharField(max_length=50, null=True, blank=True)
    social_media = models.CharField(max_length=255, null=True, blank=True)
    # Additional fields for full alumni info
    birthdate = models.DateField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    program = models.CharField(max_length=100, null=True, blank=True)
    company_name_current = models.CharField(max_length=255, null=True, blank=True)
    position_current = models.CharField(max_length=255, null=True, blank=True)
    sector_current = models.CharField(max_length=255, null=True, blank=True)
    employment_duration_current = models.CharField(max_length=100, null=True, blank=True)
    salary_current = models.CharField(max_length=100, null=True, blank=True)
    supporting_document_current = models.CharField(max_length=255, null=True, blank=True)
    awards_recognition_current = models.CharField(max_length=255, null=True, blank=True)
    supporting_document_awards_recognition = models.CharField(max_length=255, null=True, blank=True)
    unemployment_reason = models.CharField(max_length=255, null=True, blank=True)
    pursue_further_study = models.CharField(max_length=10, null=True, blank=True)
    date_started = models.DateField(null=True, blank=True)
    school_name = models.CharField(max_length=255, null=True, blank=True)
    job_code = models.CharField(max_length=20, null=True, blank=True)
    ojtstatus = models.CharField(max_length=50, null=True, blank=True)
    
    # NEW: Direct tracker question fields (replacing TrackerResponse JSON)
    # Note: Basic info (name, age, birthdate, phone, address, civil_status, social_media) 
    # already exists in User model from import, so we only add employment/study fields
    
    # Employment Information
    q_employment_status = models.CharField(max_length=50, null=True, blank=True)  # Q21: "Are you employed?"
    q_employment_type = models.CharField(max_length=100, null=True, blank=True)   # Q22: "Employed by company/self-employed"
    q_employment_permanent = models.CharField(max_length=20, null=True, blank=True)  # Q23: "Permanent/Temporary"
    q_company_name = models.CharField(max_length=255, null=True, blank=True)      # Q24: "Current Company Name"
    q_current_position = models.CharField(max_length=255, null=True, blank=True)  # Q25: "Current Position"
    q_job_sector = models.CharField(max_length=50, null=True, blank=True)        # Q26: "Private/Government"
    q_employment_duration = models.CharField(max_length=100, null=True, blank=True)  # Q27: "How long employed"
    q_salary_range = models.CharField(max_length=100, null=True, blank=True)     # Q28: "Salary range"
    q_awards_received = models.CharField(max_length=10, null=True, blank=True)   # Q29: "Yes/No"
    q_awards_document = models.FileField(upload_to='awards/', null=True, blank=True)  # Q30: File upload
    q_employment_document = models.FileField(upload_to='employment/', null=True, blank=True)  # Q31: File upload
    
    # Unemployment
    q_unemployment_reason = models.JSONField(null=True, blank=True)  # Q32: Checkbox options
    
    # Further Study
    q_pursue_study = models.CharField(max_length=10, null=True, blank=True)  # Q33: "Yes/No"
    q_study_start_date = models.DateField(null=True, blank=True)     # Q34: "Date Started"
    q_post_graduate_degree = models.CharField(max_length=255, null=True, blank=True)  # Q35: "Specify degree"
    q_institution_name = models.CharField(max_length=255, null=True, blank=True)  # Q36: "Institution name"
    q_units_obtained = models.CharField(max_length=50, null=True, blank=True)  # Q37: "Units obtained"
    
    # Additional fields for distinct questions
    home_address = models.TextField(null=True, blank=True)  # Q12: "Complete Home Address"
    company_address = models.TextField(null=True, blank=True)  # Q18: "Company Address (1st employer)"
    
    # Metadata
    tracker_submitted_at = models.DateTimeField(null=True, blank=True)
    tracker_last_updated = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'acc_username'
    REQUIRED_FIELDS = []
    
    class Meta:
        indexes = [
            models.Index(fields=['user_status', 'year_graduated']),
            models.Index(fields=['company_name_current', 'position_current']),
            models.Index(fields=['pursue_further_study', 'year_graduated']),
            models.Index(fields=['tracker_submitted_at']),
            models.Index(fields=['q_employment_status', 'year_graduated']),
            models.Index(fields=['q_company_name', 'q_current_position']),
            models.Index(fields=['q_pursue_study', 'year_graduated']),
        ]

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

class QuestionCategory(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)  # Added for ordering

class Question(models.Model):
    category = models.ForeignKey(QuestionCategory, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    type = models.CharField(max_length=50)
    options = models.JSONField(blank=True, null=True)  # For radio/multiple/checkbox

class TrackerResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answers = models.JSONField()  # {question_id: answer} - for temporary storage during form submission
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Ensure only one response per user
        unique_together = ['user']
    
    def save(self, *args, **kwargs):
        # When saving, also update the User model fields
        super().save(*args, **kwargs)
        self.update_user_fields()
    
    def update_user_fields(self):
        """Update User model fields from JSON answers"""
        if not self.answers:
            return
            
        user = self.user
        answers = self.answers
        
        # Question ID to field mapping (ALL fields including Part 1)
        question_field_mapping = {
            # Part 1: Personal Information (update existing fields)
            1: 'year_graduated',            # "Year Graduated"
            2: 'course',                    # "Course Graduated"
            3: 'email',                     # "Email"
            4: 'l_name',                    # "Last Name"
            5: 'f_name',                    # "First Name"
            6: 'm_name',                    # "Middle Name (If none write N/A)"
            7: 'age',                       # "Age"
            8: 'birthdate',                 # "Birthdate"
            9: 'phone_num',                 # "Landline or Mobile Number"
            10: 'social_media',             # "Social Media Account Link"
            11: 'address',                  # "Complete Current Address"
            12: 'home_address',             # "Complete Home Address" (NEW FIELD)
            13: 'civil_status',             # "Civil Status"
            
            # Part 2: First Employment (update existing fields)
            14: 'company_name_current',     # "Name of your organization/employer (1st employer)"
            15: 'date_started',             # "Date Hired (1st employer)"
            16: 'position_current',         # "Position (1st employer)"
            17: 'user_status',              # "Status of your employment (1st employer)"
            18: 'company_address',          # "Company Address (1st employer)" (NEW FIELD)
            19: 'sector_current',           # "Sector (1st employer)"
            20: 'supporting_document_current', # "First Employment Supporting Document"
            
            # Part 3: Current Employment (new tracker fields)
            21: 'q_employment_status',      # "Are you PRESENTLY employed?"
            22: 'q_pursue_study',           # "Did you pursue further study?"
            23: 'q_employment_type',        # "Are you employed by company/organization or self-employed?"
            24: 'q_employment_permanent',   # "Status of your current employment"
            25: 'q_company_name',           # "Current Company Name"
            26: 'q_current_position',       # "Current Position"
            27: 'q_job_sector',             # "Current Sector of your Job"
            28: 'q_employment_duration',    # "How long have you been employed?"
            29: 'q_salary_range',           # "Current Salary range"
            30: 'q_awards_received',        # "Have you received any awards or recognition?"
            31: 'q_awards_document',        # "Supporting Documents for awards/recognition"
            32: 'q_employment_document',    # "Employment Supporting Document(Current)"
            
            # Part 4: Unemployment & Further Study
            33: 'q_unemployment_reason',    # "Reason for unemployment"
            34: 'q_study_start_date',       # "Date Started"
            35: 'q_post_graduate_degree',   # "Please specify post graduate/degree"
            36: 'q_institution_name',       # "Name of Institution/University"
            37: 'q_units_obtained',         # "Total number of units obtain"
        }
        
        # Update User fields from answers
        for question_id_str, answer in answers.items():
            try:
                # Skip non-numeric question IDs (like "Job Code")
                if not question_id_str.isdigit():
                    continue
                    
                question_id = int(question_id_str)
                if question_id in question_field_mapping:
                    field_name = question_field_mapping[question_id]
                    
                    # Skip file upload fields (handled separately)
                    if isinstance(answer, dict) and answer.get('type') == 'file':
                        continue
                    
                    # Handle different field types
                    if field_name in ['birthdate', 'date_started', 'q_study_start_date'] and answer:
                        try:
                            if '/' in str(answer):
                                date_obj = datetime.strptime(str(answer), '%m/%d/%Y').date()
                            else:
                                date_obj = datetime.strptime(str(answer), '%Y-%m-%d').date()
                            setattr(user, field_name, date_obj)
                        except (ValueError, TypeError):
                            pass
                    elif field_name == 'age' and answer:
                        try:
                            setattr(user, field_name, int(answer))
                        except (ValueError, TypeError):
                            pass
                    elif field_name == 'q_unemployment_reason':
                        if isinstance(answer, list):
                            setattr(user, field_name, answer)
                        else:
                            setattr(user, field_name, [answer] if answer else [])
                    else:
                        # Handle regular string fields
                        setattr(user, field_name, str(answer) if answer else None)
            except (ValueError, TypeError):
                continue
        
        # Update metadata
        user.tracker_submitted_at = self.submitted_at
        user.save()

# OJT-specific models
class OJTImport(models.Model):
    import_id = models.AutoField(primary_key=True)
    coordinator = models.CharField(max_length=100)  # Coordinator who imported
    batch_year = models.IntegerField()
    course = models.CharField(max_length=100)
    import_date = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=255)
    records_imported = models.IntegerField(default=0)
    status = models.CharField(max_length=50, default='Completed')  # Completed, Failed, Partial
class TrackerFileUpload(models.Model):
    response = models.ForeignKey(TrackerResponse, on_delete=models.CASCADE, related_name='files')
    question_id = models.IntegerField()  # ID of the question this file answers
    file = models.FileField(upload_to='tracker_uploads/')
    original_filename = models.CharField(max_length=255)
    file_size = models.IntegerField()  # File size in bytes
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.original_filename} - {self.response.user.f_name} {self.response.user.l_name}"
