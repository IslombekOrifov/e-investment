from django.db import models
from django.utils.timezone import now
from phonenumber_field.modelfields import PhoneNumberField

from accounts.models import User


class Status(models.TextChoices):
    DRAFT = 'Draft', 'Draft'
    CHECKING = 'Checking', 'Checking'
    APPROVED = 'Approved', 'Approved'
    REJECTED = 'Rejected', 'Rejected'


class Category(models.Model):
    category = models.CharField(max_length=256)

    def __str__(self):
        return self.category


class MainData(models.Model):
    enterprise_name = models.CharField(max_length=30, default='')
    legal_form = models.CharField(max_length=30, default='')
    #legal_address = models.CharField(max_length=30, default='')
    lat = models.DecimalField(max_digits=12, decimal_places=8, default=0)
    long = models.DecimalField(max_digits=12, decimal_places=8, default=0)
    field_of_activity = models.CharField(max_length=30, default='')
    infrastructure = models.CharField(max_length=30, default='')
    project_staff = models.DecimalField(max_digits=4, decimal_places=0, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='main_data')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='main_data', blank=True, null=True, default=None)
    
    is_validated = models.BooleanField(default=False)

    def __str__(self):
        return self.enterprise_name + ' model'


class InformativeData(models.Model):
    product_info = models.CharField(max_length=256, default='')
    project_capacity = models.CharField(max_length=30, default='')
    formation_date = models.DateTimeField(blank=True, null=True)
    total_area = models.DecimalField(max_digits=6, decimal_places=0, default=0)
    building_area = models.DecimalField(max_digits=6, decimal_places=0, default=0)
    tech_equipment = models.CharField(max_length=30, default='')
    product_photo = models.ImageField(upload_to='files/product_photo/') #default='default.jpg'
    cadastral_info = models.ImageField(upload_to='files/cadastral_info/') #default='default.jpg'
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='informative_data')

    is_validated = models.BooleanField(default=False)

    def __str__(self):
        return self.product_info + ' model'


class ObjectPhoto(models.Model):
    image = models.ImageField(upload_to='files/object_photo/') # default='default.jpg'
    informative_data = models.ForeignKey(InformativeData, on_delete=models.CASCADE, related_name='object_photos')


class FinancialData(models.Model):
    export_share = models.DecimalField(max_digits=3, decimal_places=0, default=0)
    authorized_capital = models.DecimalField(max_digits=6, decimal_places=0, default=0)
    estimated_value = models.DecimalField(max_digits=6, decimal_places=0, default=0)
    investment_or_loan_amount = models.DecimalField(max_digits=6, decimal_places=0, default=0)
    investment_direction = models.CharField(max_length=30, default='')
    major_shareholders = models.CharField(max_length=30, default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_data')

    is_validated = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.investment_direction} {self.major_shareholders}' + ' model'


class AllData(models.Model):
    main_data = models.OneToOneField(MainData, on_delete=models.CASCADE, related_name='all_data')
    informative_data = models.OneToOneField(InformativeData, on_delete=models.CASCADE, related_name='all_data')
    financial_data = models.OneToOneField(FinancialData, on_delete=models.CASCADE, related_name='all_data')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='all_data')
    date_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    def __str__(self):
        return f'{self.main_data.enterprise_name} {self.date_created}'
    
    # def save(self, *args, **kwargs):
    #     self.date_created = now()
    #     return super(AllData, self).save(*args, **kwargs)


# class Investment(models.Model):
#     export_share_product = models.DecimalField(max_digits=6, decimal_places=0, default=0)
#     authorized_capital = models.DecimalField(max_digits=6, decimal_places=0, default=0)
#     company_value = models.DecimalField(max_digits=6, decimal_places=0, default=0)
#     investment_amount = models.DecimalField(max_digits=6, decimal_places=0, default=0)
#     investment_direction = models.CharField(max_length=30, default='')
#     principal_founders = models.TextField(default='')
#     investor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investor')
#     all_data = models.ForeignKey(AllData, on_delete=models.CASCADE, related_name='investment')
#     status = models.CharField(
#         max_length=10,
#         choices=Status.choices,
#         default=Status.DRAFT,
#     )


class InvestorInfo(models.Model):
    user_name = models.CharField(max_length=128, default='')
    email = models.EmailField(default='')
    user_phone = PhoneNumberField('Phone number', blank=True, null=True, default='')
    message = models.TextField(default='')
    file = models.FileField(upload_to='files/investment')
    investor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investor')
    all_data = models.ForeignKey(AllData, on_delete=models.CASCADE, related_name='investment')
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    #date_created = models.DateTimeField(auto_now_add=True)
    date_created = models.DateTimeField(blank=True, null=True, default=None)

    def __str__(self):
        return self.user_name

    def save(self, *args, **kwargs):
        self.date_created = now()
        return super(InvestorInfo, self).save(*args, **kwargs)



#If table not created
#python3 manage.py migrate --fake app_name zero
#Remove in the server all tables from models, views, serializers and cetera
#python3 manage.py makemigrations app_name
#python3 manage.py migrate app_name
