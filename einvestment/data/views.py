from rest_framework import generics, status, permissions, views, mixins, viewsets
from rest_framework.response import Response
from django.db.models import Q
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import (
    MainDataSerializer, InformativeDataSerializer, FinancialDataSerializer, ObjectPhotoSerializer,
    MainDataRetrieveSerializer, InformativeDataRetrieveSerializer, FinancialDataRetrieveSerializer,
    MainDataDraftSerializer, InformativeDataDraftSerializer, FinancialDataDraftSerializer,
    AllDataSerializer, ObjectIdAndCoordinatesSerializer, #InvestmentDraftSerializer,
    InvestorInfoSerializer, InvestorInfoGetSerializer, InvestorInfoGetMinimumSerializer,
    AllDataListSerializer, AllDataAllUsersListSerializer, CategorySerializer,
    LocationSerializer, ApproveRejectInvestorSerializer, InvestorInfoOwnSerializer,
    AllDataFilterSerializer, AreaSerializer
)
from .permissions import (
    IsLegal,
)
from .models import (
    Status, MainData, InformativeData, FinancialData, ObjectPhoto, AllData,
    InvestorInfo, Category, Area
)
from utils.logs import log


class MainDataView(generics.CreateAPIView):
    serializer_class = MainDataSerializer
    permission_classes = (IsLegal,)

    def perform_create(self, serializer):
        instance = MainData.objects.filter(
            Q(user=self.request.user) &
            Q(all_data__status=Status.DRAFT)
        ).first()
        instance.is_validated = True
        for key, value in serializer.validated_data.items():
            setattr(instance, key, value)
        instance.save()


class InformativeDataView(generics.CreateAPIView):
    serializer_class = InformativeDataSerializer
    permission_classes = (IsLegal,)
    
    def perform_create(self, serializer):
        instance = InformativeData.objects.filter(
            Q(user=self.request.user) &
            Q(all_data__status=Status.DRAFT)
        ).first()
        instance.is_validated = True
        for key, value in serializer.validated_data.items():
            setattr(instance, key, value)
        instance.save()


class ObjectPhotoView(generics.CreateAPIView):
    serializer_class = ObjectPhotoSerializer
    permission_classes = (IsLegal,)

    def perform_create(self, serializer):
        instance = InformativeData.objects.filter(
            Q(user=self.request.user) &
            Q(all_data__status=Status.DRAFT)
        ).first()
        ObjectPhoto.objects.create(
            image=serializer.validated_data['image'],
            informative_data=instance
        )


class FinancialDataView(generics.CreateAPIView):
    serializer_class = FinancialDataSerializer
    permission_classes = (IsLegal,)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        #log('StartLog')
        if serializer.is_valid():
            instance = FinancialData.objects.filter(
                Q(user=self.request.user) &
                Q(all_data__status=Status.DRAFT)
            ).first()
            instance.is_validated = True
            #setattr(instance, 'is_validated', True)
            for key, value in serializer.validated_data.items():
                setattr(instance, key, value)
            #log(f'is_validated: {instance.is_validated}')
            instance.save()

            all_data = AllData.objects.filter(
                Q(user=self.request.user) &
                Q(status=Status.DRAFT) &
                Q(main_data__is_validated=True) &
                Q(informative_data__is_validated=True)
                #Q(financial_data__is_validated=True)
            )
            #log(f'all_data: {all_data.id}')
            if all_data.exists():
                all_data = all_data.first()
                all_data.status = Status.CHECKING
                all_data.save()
                log(f'all_data2: {all_data.status}')

                main_data = MainData.objects.create(
                    user=self.request.user,
                )
                informative_data = InformativeData.objects.create(
                    user=self.request.user,
                )
                financial_data = FinancialData.objects.create(
                    user=self.request.user,
                )
                AllData.objects.create(
                    main_data=main_data,
                    informative_data=informative_data,
                    financial_data=financial_data,
                    user=self.request.user
                )
                return Response(serializer.validated_data)
            else:
                return Response({'error': 'Not all data validated'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MainDataDraftRetrieveView(generics.RetrieveAPIView):
    serializer_class = MainDataRetrieveSerializer
    permission_classes = (IsLegal,)

    def get_object(self):
        return MainData.objects.filter(Q(all_data__status=Status.DRAFT) & Q(user=self.request.user)).first()


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (permissions.AllowAny,)


class AreaListView(generics.ListAPIView):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    permission_classes = (permissions.AllowAny,)


class InformativeDataDraftRetrieveView(generics.RetrieveAPIView):
    serializer_class = InformativeDataRetrieveSerializer
    permission_classes = (IsLegal,)

    def get_object(self):
        return InformativeData.objects.filter(Q(all_data__status=Status.DRAFT) & Q(user=self.request.user)).first()


class FinancialDataDraftRetrieveView(generics.RetrieveAPIView):
    serializer_class = FinancialDataRetrieveSerializer
    permission_classes = (IsLegal,)

    def get_object(self):
        return FinancialData.objects.filter(Q(all_data__status=Status.DRAFT) & Q(user=self.request.user)).first()


class AllDataViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = AllData.objects.filter(status=Status.APPROVED)
    permission_classes = (permissions.AllowAny,)
    serializer_class = AllDataSerializer


class AllDataUserViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = AllData.objects.all()
    permission_classes = (IsLegal,)
    #serializer_class = AllDataListSerializer
    default_serializer_class = AllDataSerializer
    serializer_classes = {
        'list': AllDataListSerializer,
        'retrieve': AllDataSerializer
    }

    def get_queryset(self):
        return AllData.objects.filter(~Q(status=Status.DRAFT) & Q(user=self.request.user))
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)


class AllDataUserViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = AllData.objects.all()
    permission_classes = (IsLegal,)
    #serializer_class = AllDataListSerializer
    default_serializer_class = AllDataSerializer
    serializer_classes = {
        'list': AllDataListSerializer,
        'retrieve': AllDataSerializer
    }

    def get_queryset(self):
        return AllData.objects.filter(~Q(status=Status.DRAFT) & Q(user=self.request.user))
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)


class AllDataAllUsersViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = AllData.objects.all()
    permission_classes = (IsLegal,)
    #serializer_class = AllDataListSerializer
    default_serializer_class = AllDataSerializer
    serializer_classes = {
        'list': AllDataAllUsersListSerializer,
        'retrieve': AllDataSerializer
    }

    def get_queryset(self):
        return AllData.objects.filter(Q(status=Status.APPROVED))
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)


# class MainDataApprovedRetrieveView(generics.RetrieveAPIView):
#     serializer_class = MainDataRetrieveSerializer
#     permission_classes = (IsLegal,)

#     def get_object(self):
#         return MainData.objects.filter(user=self.request.user).first()


# class InformativeDataApprovedRetrieveView(generics.RetrieveAPIView):
#     serializer_class = InformativeDataRetrieveSerializer
#     permission_classes = (IsLegal,)

#     def get_object(self):
#         return InformativeData.objects.filter(user=self.request.user).first()


# class FinancialDataApprovedRetrieveView(generics.RetrieveAPIView):
#     serializer_class = FinancialDataRetrieveSerializer
#     permission_classes = (IsLegal,)

#     def get_object(self):
#         return FinancialData.objects.filter(user=self.request.user).first()


# class SetReadyStatusView(views.APIView):
#     permission_classes = (IsLegal,)

#     def post(self, request):
#         all_data = AllData.objects.filter(user=request.user).first()
#         all_data.status = Status.READY
#         all_data.save()
#         return Response()


class MainDataDraftView(generics.CreateAPIView):
    serializer_class = MainDataDraftSerializer
    permission_classes = (IsLegal,)

    def perform_create(self, serializer):
        hasnot_instance = False
        instance = MainData.objects.filter(
            Q(user=self.request.user) &
            Q(all_data__status=Status.DRAFT)
        ).first()
        if instance is None:
            hasnot_instance = True
            instance = MainData(user=self.request.user)
        for key, value in serializer.validated_data.items():
            setattr(instance, key, value)
        instance.save()
        if hasnot_instance:
            informdata = InformativeData(user=self.request.user)
            informdata.save()
            finandata = FinancialData(user=self.request.user)
            finandata.save()
            all_data = AllData(main_data=instance, informative_data=informdata, 
                               financial_data=finandata, user=self.request.user,
                               )
            all_data.save()



class InformativeDataDraftView(generics.CreateAPIView):
    serializer_class = InformativeDataDraftSerializer
    permission_classes = (IsLegal,)
    
    def perform_create(self, serializer):
        instance = InformativeData.objects.filter(
            Q(user=self.request.user) &
            Q(all_data__status=Status.DRAFT)
        ).first()
        for key, value in serializer.validated_data.items():
            setattr(instance, key, value)
        instance.save()


class FinancialDataDraftView(generics.CreateAPIView):
    serializer_class = FinancialDataDraftSerializer
    permission_classes = (IsLegal,)
    
    def perform_create(self, serializer):
        instance = FinancialData.objects.filter(
            Q(user=self.request.user) &
            Q(all_data__status=Status.DRAFT)
        ).first()
        for key, value in serializer.validated_data.items():
            setattr(instance, key, value)
        instance.save()


# class InvestmentDraftView(generics.CreateAPIView):
#     serializer_class = InvestmentDraftSerializer
#     permission_classes = (IsLegal,)
    
#     def perform_create(self, serializer):
#         all_data = AllData.objects.filter(
#             Q(all_data=serializer.validated_data['all_data']) &
#             Q(status=Status.APPROVED)
#         )

#         if all_data.exists():
#             instance = FinancialData.objects.filter(
#                 Q(investor=self.request.user) &
#                 Q(status=Status.DRAFT)
#             )

#             if not instance.exists():
#                 instance = Investment.objects.create(
#                     investor=self.request.user,
#                     status=Status.DRAFT
#                 )
#             else:
#                 instance = instance.first()

#             for key, value in serializer.validated_data.items():
#                 setattr(instance, key, value)
#             instance.save()


class InvestorInfoView(generics.CreateAPIView):
    serializer_class = InvestorInfoSerializer
    permission_classes = (IsLegal,)
    
    def perform_create(self, serializer):
        all_data = AllData.objects.filter(
            Q(id=serializer.validated_data['all_data'].id) &
            Q(status=Status.APPROVED)
        )

        if all_data.exists():
            instance = InvestorInfo.objects.create(
                investor=self.request.user,
                status=Status.APPROVED,
                all_data=all_data.first()
            )

            for key, value in serializer.validated_data.items():
                if not key == 'all_data':
                    setattr(instance, key, value)
            instance.save()


class InvestorInfoViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = InvestorInfo.objects.all()
    permission_classes = (IsLegal,)
    serializer_class = InvestorInfoGetSerializer

    def get_queryset(self):
        return InvestorInfo.objects.filter(
            Q(status=Status.APPROVED) &
            Q(all_data__user=self.request.user)
        )


user_id = openapi.Parameter(
    'user_id', openapi.IN_QUERY,
    description="If user_id exists, return investors for this user, else return investors for current user",
    type=openapi.TYPE_STRING
)
@method_decorator(name='list', decorator=swagger_auto_schema(manual_parameters=[
    user_id,
]))
class AllObjectInvestorsViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = InvestorInfo.objects.all()
    permission_classes = (IsLegal,)
    #serializer_class = InvestorInfoGetSerializer
    default_serializer_class = InvestorInfoGetSerializer
    serializer_classes = {
        'list': InvestorInfoGetMinimumSerializer,
        'retrieve': InvestorInfoGetSerializer
    }

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    def get_queryset(self):
        data = self.request.GET.dict()
        queryset = ~Q(status=Status.DRAFT)
        if 'user_id' in data:
            queryset &= Q(all_data__user__id=data['user_id'])
        else:
            queryset &= Q(all_data__user=self.request.user)
        return InvestorInfo.objects.filter(queryset)


class ObjectIdAndCoordinatesViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = AllData.objects.filter(status=Status.APPROVED)
    permission_classes = (permissions.AllowAny,)
    serializer_class = ObjectIdAndCoordinatesSerializer


from geopy.geocoders import Nominatim

class LocationView(generics.CreateAPIView):
    serializer_class = LocationSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            geolocator = Nominatim(user_agent="E-Investment")
            location = geolocator.reverse(f"{serializer.validated_data['lat']}, {serializer.validated_data['long']}")
            return Response(location.address)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApproveRejectView(generics.CreateAPIView):
    serializer_class = ApproveRejectInvestorSerializer
    permission_classes = (IsLegal,)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            investor = InvestorInfo.objects.filter(
                Q(id=serializer.validated_data['investor_id']) &
                Q(all_data__id=serializer.validated_data['all_data_id'])
            )
            if investor.exists():
                investor = investor.first()
                if serializer.validated_data['is_approve']:
                    investor.status = Status.APPROVED
                else:
                    investor.status = Status.REJECTED
                investor.save(force_update=True)
                return Response(serializer.validated_data)
            else:
                return Response({'error': 'Investor or object does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InvestorInfoOwnListView(generics.ListAPIView):
    queryset = InvestorInfo.objects.all()
    serializer_class = InvestorInfoOwnSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return InvestorInfo.objects.filter(investor=self.request.user)


categories = openapi.Parameter(
    'categories', openapi.IN_QUERY,
    description="Filter objects by array of categories id. Example: categories=1,2",
    type=openapi.TYPE_STRING
)
@method_decorator(name='get', decorator=swagger_auto_schema(manual_parameters=[
    categories,
]))
class AllDataFilterView(generics.ListAPIView):
    serializer_class = AllDataFilterSerializer
    permission_classes = (permissions.IsAuthenticated,)
    #pagination_class = TenPagesPagination

    def get_queryset(self):
        data = self.request.GET.dict()
        queryset = Q(status=Status.APPROVED)
        if 'categories' in data:
            category_list = []
            for category in data['categories'].split(','):
                category_list.append(int(category))
            queryset &= Q(main_data__category__pk__in=category_list)
        if 'locations' in data:
            location_list = []
            for location in data['locations'].split(','):
                location_list.append(int(location))
            queryset &= Q(main_data__location__pk__in=location_list)
        if 'startprice' in data and 'endprice' in data:                
            queryset &= Q(financial_data__authorized_capital__gte=int(data['startprice']), financial_data__authorized_capital__lte=int(data['endprice']))
        elif 'startprice' in data:                
            queryset &= Q(financial_data__authorized_capital__gte=int(data['startprice']))
        elif 'endprice' in data:                
            queryset &= Q(financial_data__authorized_capital__lte=int(data['endprice']))
        
        return AllData.objects.filter(queryset)


import math


lat_long = openapi.Parameter(
    'lat_long', openapi.IN_QUERY,
    description="Filter objects by latitude and longitude. Example: lat_long=21.1234,22.4321",
    type=openapi.TYPE_STRING
)
distance_km = openapi.Parameter(
    'distance', openapi.IN_QUERY,
    description="Filter objects by radius in km from latitude and longitude. Example: distance=10. Default distance 50 km",
    type=openapi.TYPE_STRING
)
@method_decorator(name='get', decorator=swagger_auto_schema(manual_parameters=[
    lat_long, distance_km
]))
class AllDataFilterByLatLongDistanceView(generics.ListAPIView):
    serializer_class = AllDataFilterSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        data = self.request.GET.dict()
        queryset = Q(status=Status.APPROVED)
        
        distance = 50.0
        earth_radius = 6371.0
        if 'distance' in data:
            distance = float(data['distance']) if distance <= earth_radius else earth_radius
        
        if 'lat_long' in data:
            lat_long_list = data['lat_long'].split(',')
            if len(lat_long_list) == 2:
                lat = float(lat_long_list[0])
                long = float(lat_long_list[1])
                max_lat = lat + math.degrees(distance / earth_radius)
                min_lat = lat - math.degrees(distance / earth_radius)
                max_long = long + math.degrees(math.asin(distance / earth_radius) / math.cos(math.radians(lat)))
                min_long = long - math.degrees(math.asin(distance / earth_radius) / math.cos(math.radians(lat)))
                #log(f'min_lat: {min_lat} max_lat: {max_lat} min_long: {min_long} max_long: {max_long}')
                queryset &= Q(main_data__lat__gte=min_lat)
                queryset &= Q(main_data__lat__lte=max_lat)
                queryset &= Q(main_data__long__gte=min_long)
                queryset &= Q(main_data__long__lte=max_long)
                return AllData.objects.filter(queryset)
            else:
                return []
        return []
