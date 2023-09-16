from django.contrib import admin

from . models import (
    MainData, InformativeData, FinancialData, ObjectPhoto, Status, AllData,
    InvestorInfo, Category, Area, SmartNote, Currency, CurrencyPrice
)


# class PostAdmin(admin.ModelAdmin):
#     list_display = ('title', 'pubdate','user')

# class MyPost(Post):
#     class Meta:
#         proxy = True

# class MyPostAdmin(PostAdmin):
#     def get_queryset(self, request):
#         return self.model.objects.filter(user = request.user)


# admin.site.register(Post, PostAdmin)
# admin.site.register(MyPost, MyPostAdmin)

class AllDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_created', 'status')
    ordering = ('-date_created',)


class AllDataReady(AllData):
    class Meta:
        proxy = True


class AllDataReadyAdmin(AllDataAdmin):
    def get_queryset(self, request):
        return self.model.objects.filter(status=Status.CHECKING)


admin.site.register(AllData, AllDataAdmin)
admin.site.register(AllDataReady, AllDataReadyAdmin)

admin.site.register(MainData)
admin.site.register(InformativeData)
admin.site.register(FinancialData)
admin.site.register(ObjectPhoto)
admin.site.register(InvestorInfo)
admin.site.register(Category)
admin.site.register(Area)

admin.site.register(SmartNote)

admin.site.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')


admin.site.register(CurrencyPrice)
class CurrencyPriceAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'cb_price')
    ordering = ('-date',)
