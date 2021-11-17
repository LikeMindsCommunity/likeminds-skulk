from django.urls import path
from .kyc_view_impl import *

app_name = "kyc"

urlpatterns = [
    path('create', CreateKycView.as_view(), name="create-kyc"),
    path('upload', UploadKycView.as_view(), name="upload-kyc"),
    path('fetch', FetchKycView.as_view(), name='fetch-kyc'),
    path('fetch_all', FetchAllKycView.as_view(), name='fetch-all-kyc'),
    path('edit', EditKycView.as_view(), name='edit-kyc')
]
