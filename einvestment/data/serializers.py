from rest_framework import serializers

from django.core.files.base import ContentFile
import base64
import six
import uuid

from .models import (
    MainData, InformativeData, FinancialData, ObjectPhoto, AllData,
    InvestorInfo, Category, Area, SmartNote, Currency
)

class MainDataSerializer(serializers.Serializer):
    enterprise_name = serializers.CharField(max_length=30)
    legal_form = serializers.CharField(max_length=30)
    location = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Area.objects.all())
    lat = serializers.DecimalField(max_digits=22, decimal_places=18)
    long = serializers.DecimalField(max_digits=22, decimal_places=18)
    field_of_activity = serializers.CharField(max_length=30)
    infrastructure = serializers.CharField(max_length=30)
    project_staff = serializers.DecimalField(max_digits=4, decimal_places=0)
    category = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Category.objects.all())


class Base64ImageField(serializers.ImageField):
    """
    A Django REST framework field for handling image-uploads through raw post data.
    It uses base64 for encoding and decoding the contents of the file.

    Heavily based on
    https://github.com/tomchristie/django-rest-framework/pull/1268

    Updated for Django REST framework 3.
    """

    def to_internal_value(self, data):

        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data = data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            # Generate file name:
            file_name = str(uuid.uuid4())[:12] # 12 characters are more than enough.
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension, )

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


class ObjectPhotoSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    class Meta:
        model = ObjectPhoto
        fields = ('image',)


class InformativeDataSerializer(serializers.Serializer):
    product_info = serializers.CharField(max_length=30)
    project_capacity = serializers.CharField(max_length=30)
    formation_date = serializers.DateTimeField()
    total_area = serializers.DecimalField(max_digits=6, decimal_places=0)
    building_area = serializers.DecimalField(max_digits=6, decimal_places=0)
    tech_equipment = serializers.CharField(max_length=30)
    product_photo = Base64ImageField(max_length=None, use_url=True)
    cadastral_info = Base64ImageField(max_length=None, use_url=True)


class FinancialDataSerializer(serializers.Serializer):
    export_share = serializers.DecimalField(max_digits=18, decimal_places=4)
    authorized_capital = serializers.DecimalField(max_digits=18, decimal_places=4)
    estimated_value = serializers.DecimalField(max_digits=18, decimal_places=4)
    investment_or_loan_amount = serializers.DecimalField(max_digits=18, decimal_places=4)
    investment_direction = serializers.CharField(max_length=30)
    major_shareholders = serializers.CharField(max_length=30)
    currency = serializers.PrimaryKeyRelatedField(queryset=Currency.objects.all())


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class MainDataRetrieveSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    class Meta:
        model = MainData
        fields = '__all__'
    
    def get_category(self, object):
        return object.category.category
    
    def get_location(self, object):
        return object.location.location


class InformativeDataRetrieveSerializer(serializers.ModelSerializer):
    object_photos = ObjectPhotoSerializer(many=True)
    class Meta:
        model = InformativeData
        fields = (
            'id', 
            'product_info',
            'project_capacity',
            'formation_date',
            'total_area',
            'building_area',
            'tech_equipment',
            'product_photo',
            'cadastral_info',
            'user',
            'object_photos'
        )


class FinancialDataRetrieveCustomSerializer(serializers.ModelSerializer):
    currency = serializers.SerializerMethodField()
    class Meta:
        model = FinancialData
        fields = '__all__'
    
    def get_currency(self, object):
        return object.currency.code
    

class FinancialDataRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialData
        fields = '__all__'


class AllDataSerializer(serializers.ModelSerializer):
    main_data = MainDataRetrieveSerializer()
    informative_data = InformativeDataRetrieveSerializer()
    financial_data = FinancialDataRetrieveCustomSerializer()
    class Meta:
        model = AllData
        fields = (
            'id', 
            'user',
            'main_data',
            'informative_data',
            'financial_data',
            'status',
            'date_created',
        )


class AllDataFilterSerializer(serializers.ModelSerializer):
    lat = serializers.SerializerMethodField()
    long = serializers.SerializerMethodField()
    class Meta:
        model = AllData
        fields = ('id', 'lat', 'long')
    
    def get_lat(self, object):
        return object.main_data.lat
    
    def get_long(self, object):
        return object.main_data.long
    
# class CategoryDraftSerializer(serializers.Serializer):
#     id = serializers.IntegerField(default=0)


# class MainDataDraftSerializer(serializers.ModelSerializer):
#     category = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Category.objects.all())
#     #category = CategoryDataDraftSerializer(allow_null=True)
#     class Meta:
#         model = MainData
#         fields = (
#             'enterprise_name',
#             'legal_form',
#             'lat',
#             'long',
#             'field_of_activity',
#             'infrastructure',
#             'project_staff',
#             'category',
#         )
#         extra_kwargs = {
#             'enterprise_name': {'allow_null': True},
#             'legal_form':  {'allow_null': True},
#             'lat':  {'allow_null': True},
#             'long':  {'allow_null': True},
#             'field_of_activity':  {'allow_null': True},
#             'infrastructure':  {'allow_null': True},
#             'project_staff':  {'allow_null': True},
#             #'category':  {'allow_null': True},
#         }


class MainDataDraftSerializer(serializers.Serializer):
    enterprise_name = serializers.CharField(max_length=256, allow_null=True, allow_blank=True, default='')
    legal_form = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, default='')
    location = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Area.objects.all())
    lat = serializers.DecimalField(max_digits=22, decimal_places=18, default=0)
    long = serializers.DecimalField(max_digits=22, decimal_places=18, default=0)
    field_of_activity = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, default='')
    infrastructure = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, default='')
    project_staff = serializers.DecimalField(max_digits=4, decimal_places=0, default=0)
    category = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Category.objects.all())


class InformativeDataDraftSerializer(serializers.Serializer):
    product_info = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, default='')
    project_capacity = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, default='')
    formation_date = serializers.DateTimeField(allow_null=True, default=None)
    total_area = serializers.DecimalField(max_digits=6, decimal_places=0, default=0)
    building_area = serializers.DecimalField(max_digits=6, decimal_places=0, default=0)
    tech_equipment = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, default='')
    #product_photo = serializers.ImageField(allow_null=True, default=None)
    #cadastral_info = serializers.FileField(allow_null=True, default=None)
    product_photo = Base64ImageField(max_length=None, use_url=True, allow_null=True, default=None)
    cadastral_info = Base64ImageField(max_length=None, use_url=True, allow_null=True, default=None)


class FinancialDataDraftSerializer(serializers.Serializer):
    export_share = serializers.DecimalField(max_digits=18, decimal_places=4, default=0)
    authorized_capital = serializers.DecimalField(max_digits=18, decimal_places=4, default=0)
    estimated_value = serializers.DecimalField(max_digits=18, decimal_places=4, default=0)
    investment_or_loan_amount = serializers.DecimalField(max_digits=18, decimal_places=4, default=0)
    investment_direction = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, default='')
    major_shareholders = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, default='')
    currency = serializers.PrimaryKeyRelatedField(queryset=Currency.objects.all())


# class InvestmentDraftSerializer(serializers.Serializer):
#     export_share_product = serializers.DecimalField(max_digits=6, decimal_places=0, default=0)
#     authorized_capital = serializers.DecimalField(max_digits=6, decimal_places=0, default=0)
#     company_value = serializers.DecimalField(max_digits=6, decimal_places=0, default=0)
#     investment_amount = serializers.DecimalField(max_digits=6, decimal_places=0, default=0)
#     investment_direction = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, default='')
#     principal_founders = serializers.CharField(max_length=1024, allow_null=True, allow_blank=True, default='')
#     all_data = serializers.IntegerField()


class InvestorInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestorInfo
        fields = ('user_name', 'email', 'user_phone', 'message', 'file', 'all_data')


class InvestorInfoOwnSerializer(serializers.ModelSerializer):
    enterprise_name = serializers.SerializerMethodField()
    id_object = serializers.SerializerMethodField()
    
    class Meta:
        model = InvestorInfo
        fields = ('enterprise_name', 'id_object', 'message', 'date_created', 'status')
    
    def get_enterprise_name(self, object):
        return object.all_data.main_data.enterprise_name
    
    def get_id_object(self, object):
        return object.all_data.id


class ApproveRejectInvestorSerializer(serializers.Serializer):
    investor_id = serializers.IntegerField()
    all_data_id = serializers.IntegerField()
    is_approve = serializers.BooleanField()


class InvestorInfoGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestorInfo
        fields = '__all__'


class InvestorInfoGetMinimumSerializer(serializers.ModelSerializer):
    message = serializers.SerializerMethodField()
    class Meta:
        model = InvestorInfo
        fields = ('user_name', 'id', 'date_created', 'message')
    
    def get_message(self, object):
        return object.message[:87] + '...'


class CoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainData
        fields = ('lat', 'long',)


class ObjectIdAndCoordinatesSerializer(serializers.ModelSerializer):
    main_data = CoordinatesSerializer()
    class Meta:
        model = AllData
        fields = (
            'id', 
            'main_data',
        )


class AllDataListSerializer(serializers.ModelSerializer):
    enterprise_name = serializers.SerializerMethodField()
    class Meta:
        model = AllData
        fields = (
            'id', 
            'enterprise_name',
            'status',
            'date_created',
        )
    
    def get_enterprise_name(self, object):
        return object.main_data.enterprise_name


class AllDataAllUsersListSerializer(serializers.ModelSerializer):
    enterprise_name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    product_info = serializers.SerializerMethodField()
    class Meta:
        model = AllData
        fields = (
            'id', 
            'enterprise_name',
            'image',
            'product_info',
        )
    
    def get_enterprise_name(self, object):
        return object.main_data.enterprise_name
    
    def get_image(self, object):
        image = object.informative_data.object_photos.all().first()
        return_image = ''
        if image is not None:
            return_image = image.image.url
        return return_image
    
    def get_product_info(self, object):
        return object.informative_data.product_info


class LocationSerializer(serializers.Serializer):
    lat = serializers.DecimalField(max_digits=22, decimal_places=18)
    long = serializers.DecimalField(max_digits=22, decimal_places=18)


class SmartNoteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmartNote
        fields = ('id', 'main_data', 'text', 'name', 'custom_id')


class SmartNoteMainDataSerializer(serializers.ModelSerializer):
    enterprise_name = serializers.CharField(source='main_data.enterprise_name', read_only=True)
    class Meta:
        model = MainData
        fields = ('id', 'enterprise_name')


class SmartNoteListRetrieveSerializer(serializers.ModelSerializer):
    main_data = SmartNoteMainDataSerializer()
    enterprise_name = serializers.SerializerMethodField()

    class Meta:
        model = SmartNote
        fields = ('id', 'enterprise_name', 'main_data', 'text', 'name', 'custom_id')

    def get_enterprise_name(self, object):
        main_data = object.main_data
        if main_data and main_data.enterprise_name:
            return main_data.enterprise_name
        else:
            return None


class SmartNoteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmartNote
        fields = ('text', 'name', 'custom_id')


class CustomIdSerializer(serializers.Serializer):
    custom_id = serializers.CharField(max_length=30, allow_null=True, allow_blank=True)