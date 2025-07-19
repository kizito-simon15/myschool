from django.urls import path
from .views import (
    HomeView,
    StudentListView, StudentCreateView, StudentUpdateView, StudentDeleteView, StudentDetailView, StudentPromotionView,
    StaffListView, StaffCreateView, StaffUpdateView, StaffDeleteView, StaffDetailView,
    AcademicYearListView, AcademicYearCreateView, AcademicYearUpdateView, AcademicYearDeleteView,
    SchoolClassListView, SchoolClassCreateView, SchoolClassUpdateView, SchoolClassDeleteView,
    update_session, check_class_unique, AnalyticsView ,
)

urlpatterns = [
    path('check-class-unique/', check_class_unique, name='check_class_unique'),
    path('', HomeView.as_view(), name='home'),
    path('students/', StudentListView.as_view(), name='student_list'),
    path('students/add/', StudentCreateView.as_view(), name='student_create'),
    path('students/<int:pk>/', StudentDetailView.as_view(), name='student_detail'),
    path('students/<int:pk>/edit/', StudentUpdateView.as_view(), name='student_update'),
    path('students/<int:pk>/delete/', StudentDeleteView.as_view(), name='student_delete'),
    path('students/promote/', StudentPromotionView.as_view(), name='student_promotion'),
    path('staff/', StaffListView.as_view(), name='staff_list'),
    path('staff/add/', StaffCreateView.as_view(), name='staff_create'),
    path('staff/<int:pk>/', StaffDetailView.as_view(), name='staff_detail'),
    path('staff/<int:pk>/edit/', StaffUpdateView.as_view(), name='staff_update'),
    path('staff/<int:pk>/delete/', StaffDeleteView.as_view(), name='staff_delete'),
    path('academic-years/', AcademicYearListView.as_view(), name='academicyear_list'),
    path('academic-years/add/', AcademicYearCreateView.as_view(), name='academicyear_create'),
    path('academic-years/<int:pk>/edit/', AcademicYearUpdateView.as_view(), name='academicyear_update'),
    path('academic-years/<int:pk>/delete/', AcademicYearDeleteView.as_view(), name='academicyear_delete'),
    path('classes/', SchoolClassListView.as_view(), name='schoolclass_list'),
    path('classes/add/', SchoolClassCreateView.as_view(), name='schoolclass_create'),
    path('classes/<int:pk>/edit/', SchoolClassUpdateView.as_view(), name='schoolclass_update'),
    path('classes/<int:pk>/delete/', SchoolClassDeleteView.as_view(), name='schoolclass_delete'),
    
    path('update-session/', update_session, name='update_session'),
    path("analytics/",  AnalyticsView.as_view(), name="analytics"), 
]