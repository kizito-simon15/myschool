import json
import logging
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.db.models import ProtectedError
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.db.models import Count
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .models import Student, Staff, AcademicYear, SchoolClass, StudentClassAssignment
from .forms import StudentForm, StaffForm, AcademicYearForm, SchoolClassForm
from collections import defaultdict







logger = logging.getLogger(__name__)

@login_required
@require_POST
def update_session(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        if 'sidebar_open' in data:
            request.session['sidebar_open'] = data['sidebar_open']
            logger.debug(f"Updated sidebar_open to {data['sidebar_open']}")
        if 'dark_mode' in data:
            request.session['dark_mode'] = data['dark_mode']
            logger.debug(f"Updated dark_mode to {data['dark_mode']}")
        request.session.modified = True
        logger.info("Session updated successfully")
        return JsonResponse({'status': 'success'})
    except json.JSONDecodeError:
        logger.error("Invalid JSON data received in update_session")
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'school/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['school_name'] = "St. Theresia-Avila"
        context['current_session'] = "2025/2026"
        context['current_term'] = "Term 1"
        context['notification_count'] = 0

        # Summary Cards
        current_year = AcademicYear.objects.filter(is_current=True).first()
        context['summary_cards'] = [
            {'label': 'Total Students', 'count': Student.objects.count(), 'icon': '👥'},
            {'label': 'Active Students', 'count': Student.objects.filter(is_active=True).count(), 'icon': '✅'},
            {'label': 'Total Staff', 'count': Staff.objects.count(), 'icon': '👩‍🏫'},
            {'label': 'Active Staff', 'count': Staff.objects.filter(is_active=True).count(), 'icon': '✔️'},
            {'label': 'Classes', 'count': SchoolClass.objects.filter(academic_year=current_year).count() if current_year else 0, 'icon': '🎓'},
            {'label': 'Academic Years', 'count': AcademicYear.objects.count(), 'icon': '📅'},
        ]

        # Bar Chart: Monthly Student Admissions (Last 6 Months)
        end_date = timezone.now()
        start_date = end_date - timezone.timedelta(days=180)
        monthly_admissions = Student.objects.filter(admission_date__range=(start_date, end_date)) \
            .extra({'month': "strftime('%%Y-%%m', admission_date)"}) \
            .values('month') \
            .annotate(count=Count('id')) \
            .order_by('month')
        context['bar_labels'] = [entry['month'] for entry in monthly_admissions]
        context['bar_vals_students'] = [entry['count'] for entry in monthly_admissions]
        if not context['bar_labels']:
            context['bar_labels'] = [f"{(start_date + timezone.timedelta(days=30*i)).strftime('%Y-%m')}" for i in range(6)]
            context['bar_vals_students'] = [0] * 6

        # Line Chart: Annual Student Growth (Last 5 Years)
        annual_growth = Student.objects.extra({'year': "strftime('%%Y', admission_date)"}) \
            .values('year') \
            .annotate(count=Count('id')) \
            .order_by('year')
        context['line_labels'] = [entry['year'] for entry in annual_growth]
        context['line_vals'] = [entry['count'] for entry in annual_growth]
        if not context['line_labels']:
            current_year_value = timezone.now().year
            context['line_labels'] = [str(current_year_value - i) for i in range(5, -1, -1)]
            context['line_vals'] = [0] * 6

        # Pie Chart: Gender Distribution
        gender_distribution = Student.objects.values('gender').annotate(count=Count('id'))
        context['pie_labels'] = [entry['gender'] or 'Unknown' for entry in gender_distribution]
        context['pie_vals'] = [entry['count'] for entry in gender_distribution]
        if not context['pie_labels']:
            context['pie_labels'] = ['Male', 'Female']
            context['pie_vals'] = [0, 0]

        # Class Distribution (for additional analysis)
        class_distribution = StudentClassAssignment.objects.filter(academic_year=current_year) \
            .values('school_class__name') \
            .annotate(count=Count('student')) \
            .order_by('school_class__name') if current_year else []
        context['class_labels'] = [entry['school_class__name'] or 'N/A' for entry in class_distribution]
        context['class_vals'] = [entry['count'] for entry in class_distribution]
        if not context['class_labels']:
            context['class_labels'] = ['N/A']
            context['class_vals'] = [0]

        context['school_classes'] = SchoolClass.objects.filter(academic_year__is_current=True)
        logger.debug("Home page context data prepared with real data analysis")
        return context
    


class StudentListView(LoginRequiredMixin, ListView):
    model         = Student
    paginate_by   = None                # handled client‑side
    template_name = "school/student_list.html"

    def get_queryset(self):
        # ListView still wants something – an empty QS is fine
        return Student.objects.none()

    def get_context_data(self, **kwargs):
        ctx          = super().get_context_data(**kwargs)
        current_year = AcademicYear.objects.filter(is_current=True).first()

        # classes for the current academic year ───────────────────────────────
        classes = (SchoolClass.objects
                   .filter(academic_year=current_year)
                   .order_by("name"))

        grouped = {}
        total   = active = 0
        for cls in classes:
            members = (Student.objects
                       .filter(class_assignments__academic_year=current_year,
                               class_assignments__school_class=cls)
                       .select_related()
                       .order_by("last_name", "first_name"))
            grouped[cls] = list(members)
            total   += len(members)
            active  += len([s for s in members if s.is_active])

        ctx.update({
            "groups":          grouped,       # {class_obj: [students]}
            "total_students":  total,
            "active_students": active,
        })
        return ctx


class StudentCreateView(LoginRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'school/student_form.html'
    success_url = reverse_lazy('student_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_session'] = "2025/2026"
        context['current_term'] = "Term 1"
        context['notification_count'] = 0
        logger.debug("Student create context data prepared")
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Student {self.object} created successfully.")
        logger.info(f"Student {self.object} created successfully")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error creating student. Please check the form.")
        logger.error(f"Error creating student: {form.errors}")
        return super().form_invalid(form)

class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'school/student_form.html'
    success_url = reverse_lazy('student_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_session'] = "2025/2026"
        context['current_term'] = "Term 1"
        context['notification_count'] = 0
        logger.debug(f"Student update context data prepared for student ID {self.kwargs['pk']}")
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Student {self.object} updated successfully.")
        logger.info(f"Student {self.object} updated successfully")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error updating student. Please check the form.")
        logger.error(f"Error updating student ID {self.kwargs['pk']}: {form.errors}")
        return super().form_invalid(form)

class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'school/student_detail.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_session'] = "2025/2026"
        context['current_term'] = "Term 1"
        context['notification_count'] = 0
        context['class_assignments'] = self.object.class_assignments.all()
        logger.debug(f"Student detail context data prepared for student ID {self.kwargs['pk']}")
        return context

class StudentDeleteView(LoginRequiredMixin, DeleteView):
    model = Student
    template_name = 'school/student_confirm_delete.html'
    success_url = reverse_lazy('student_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_session'] = "2025/2026"
        context['current_term'] = "Term 1"
        context['notification_count'] = 0
        logger.debug(f"Student delete context data prepared for student ID {self.kwargs['pk']}")
        return context

    def form_valid(self, form):
        messages.success(self.request, f"Student {self.object} deleted successfully.")
        logger.info(f"Student {self.object} deleted successfully")
        return super().form_valid(form)

class StudentPromotionView(LoginRequiredMixin, TemplateView):
    template_name = 'school/student_promotion.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_session'] = "2025/2026"
        context['current_term'] = "Term 1"
        context['notification_count'] = 0
        context['students'] = Student.objects.filter(is_active=True).prefetch_related('class_assignments')
        context['current_year'] = AcademicYear.objects.filter(is_current=True).first()
        context['classes'] = SchoolClass.objects.filter(academic_year=context['current_year']) if context['current_year'] else []
        logger.debug("Student promotion context data prepared")
        return context

    def post(self, request, *args, **kwargs):
        student_ids = request.POST.getlist('students')
        new_class_id = request.POST.get('new_class')
        current_year = AcademicYear.objects.filter(is_current=True).first()

        if not current_year:
            messages.error(request, "No current academic year defined. Please create and set a current year.")
            logger.warning("Promotion failed: No current academic year defined.")
            return redirect('student_promotion')
        if not new_class_id:
            messages.error(request, "Please select a class to promote to.")
            logger.warning("Promotion failed: No class selected.")
            return redirect('student_promotion')

        try:
            new_class = SchoolClass.objects.get(id=new_class_id, academic_year=current_year)
        except SchoolClass.DoesNotExist:
            messages.error(request, f"Selected class (ID: {new_class_id}) is not valid for the current year {current_year.year}.")
            logger.error(f"Promotion failed: Invalid class ID {new_class_id} for year {current_year.year}")
            return redirect('student_promotion')

        if not student_ids:
            messages.error(request, "Please select at least one student to promote.")
            logger.warning("Promotion failed: No students selected.")
            return redirect('student_promotion')

        promoted_count = 0
        for student_id in student_ids:
            try:
                student = Student.objects.get(id=student_id)
                # Update the existing assignment for the current year
                assignment, created = StudentClassAssignment.objects.update_or_create(
                    student=student,
                    academic_year=current_year,
                    defaults={'school_class': new_class}
                )
                promoted_count += 1
                logger.info(f"Promoted student ID {student_id} to {new_class.name} for year {current_year.year} (created: {created})")
            except Student.DoesNotExist:
                messages.error(request, f"Student with ID {student_id} not found.")
                logger.error(f"Promotion failed: Student ID {student_id} not found.")

        messages.success(request, f"Successfully promoted {promoted_count} student(s) to {new_class.name}.")
        logger.info(f"Promotion completed: {promoted_count} students promoted to {new_class.name} for {current_year.year}")
        return redirect('student_list')

class StaffListView(LoginRequiredMixin, ListView):
    model = Staff
    template_name = 'school/staff_list.html'
    context_object_name = 'staff'
    ordering = ['last_name', 'first_name']
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_session'] = "2025/2026"
        context['current_term'] = "Term 1"
        context['notification_count'] = 0
        context['total_staff'] = Staff.objects.count()
        context['active_staff'] = Staff.objects.filter(is_active=True).count()
        logger.debug("Staff list context data prepared")
        return context

class StaffCreateView(LoginRequiredMixin, CreateView):
    model = Staff
    form_class = StaffForm
    template_name = 'school/staff_form.html'
    success_url = reverse_lazy('staff_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_session'] = "2025/2026"
        context['current_term'] = "Term 1"
        context['notification_count'] = 0
        logger.debug("Staff create context data prepared")
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Staff {self.object} created successfully.")
        logger.info(f"Staff {self.object} created successfully")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error creating staff. Please check the form.")
        logger.error(f"Error creating staff: {form.errors}")
        return super().form_invalid(form)

class StaffUpdateView(LoginRequiredMixin, UpdateView):
    model = Staff
    form_class = StaffForm
    template_name = 'school/staff_form.html'
    success_url = reverse_lazy('staff_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_session'] = "2025/2026"
        context['current_term'] = "Term 1"
        context['notification_count'] = 0
        logger.debug(f"Staff update context data prepared for staff ID {self.kwargs['pk']}")
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Staff {self.object} updated successfully.")
        logger.info(f"Staff {self.object} updated successfully")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error updating staff. Please check the form.")
        logger.error(f"Error updating staff ID {self.kwargs['pk']}: {form.errors}")
        return super().form_invalid(form)

class StaffDetailView(LoginRequiredMixin, DetailView):
    model = Staff
    template_name = 'school/staff_detail.html'
    context_object_name = 'staff'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_session'] = "2025/2026"
        context['current_term'] = "Term 1"
        context['notification_count'] = 0
        logger.debug(f"Staff detail context data prepared for staff ID {self.kwargs['pk']}")
        return context

class StaffDeleteView(LoginRequiredMixin, DeleteView):
    model = Staff
    template_name = 'school/staff_confirm_delete.html'
    success_url = reverse_lazy('staff_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_session'] = "2025/2026"
        context['current_term'] = "Term 1"
        context['notification_count'] = 0
        logger.debug(f"Staff delete context data prepared for staff ID {self.kwargs['pk']}")
        return context

    def form_valid(self, form):
        messages.success(self.request, f"Staff {self.object} deleted successfully.")
        logger.info(f"Staff {self.object} deleted successfully")
        return super().form_valid(form)

class AcademicYearListView(LoginRequiredMixin, ListView):
    model = AcademicYear
    template_name = 'school/academicyear_list.html'
    context_object_name = 'academic_years'
    ordering = ['-year']
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_session'] = "2025/2026"
        context['current_term'] = "Term 1"
        context['notification_count'] = 0
        context['total_years'] = AcademicYear.objects.count()
        context['current_years'] = AcademicYear.objects.filter(is_current=True).count()
        logger.debug("Academic year list context data prepared")
        return context

class AcademicYearCreateView(LoginRequiredMixin, CreateView):
    model = AcademicYear
    form_class = AcademicYearForm
    template_name = 'school/academicyear_form.html'
    success_url = reverse_lazy('academicyear_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_session'] = "2025/2026"
        context['current_term'] = "Term 1"
        context['notification_count'] = 0
        logger.debug("Academic year create context data prepared")
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Academic Year {self.object.year} created successfully.")
        logger.info(f"Academic Year {self.object.year} created successfully")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error creating academic year. Please check the form.")
        logger.error(f"Error creating academic year: {form.errors}")
        return super().form_invalid(form)

class AcademicYearUpdateView(LoginRequiredMixin, UpdateView):
    model = AcademicYear
    form_class = AcademicYearForm
    template_name = 'school/academicyear_form.html'
    success_url = reverse_lazy('academicyear_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_session'] = "2025/2026"
        context['current_term'] = "Term 1"
        context['notification_count'] = 0
        logger.debug(f"Academic year update context data prepared for year {self.kwargs['pk']}")
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Academic Year {self.object.year} updated successfully.")
        logger.info(f"Academic Year {self.object.year} updated successfully")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error updating academic year. Please check the form.")
        logger.error(f"Error updating academic year ID {self.kwargs['pk']}: {form.errors}")
        return super().form_invalid(form)

class AcademicYearDeleteView(LoginRequiredMixin, DeleteView):
    model = AcademicYear
    template_name = 'school/academicyear_confirm_delete.html'
    success_url = reverse_lazy('academicyear_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_session'] = "2025/2026"
        context['current_term'] = "Term 1"
        context['notification_count'] = 0
        logger.debug(f"Academic year delete context data prepared for year {self.kwargs['pk']}")
        return context

    def form_valid(self, form):
        messages.success(self.request, f"Academic Year {self.object.year} deleted successfully.")
        logger.info(f"Academic Year {self.object.year} deleted successfully")
        return super().form_valid(form)

class SchoolClassListView(LoginRequiredMixin, ListView):
    model = SchoolClass
    template_name = 'school/schoolclass_list.html'
    context_object_name = 'school_classes'
    ordering = ['academic_year__year', 'name']
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(name__icontains=query)
        logger.debug(f"School class list queryset filtered with query: {query}")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_session'] = "2025/2026"
        context['current_term'] = "Term 1"
        context['notification_count'] = 0
        context['total_classes'] = SchoolClass.objects.count()
        context['current_classes'] = SchoolClass.objects.filter(academic_year__is_current=True).count()
        logger.debug("School class list context data prepared")
        return context

class SchoolClassCreateView(LoginRequiredMixin, CreateView):
    model = SchoolClass
    form_class = SchoolClassForm
    template_name = 'school/schoolclass_form.html'
    success_url = reverse_lazy('schoolclass_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_session'] = "2025/2026"
        context['current_term'] = "Term 1"
        context['notification_count'] = 0
        logger.debug("School class create context data prepared")
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Class {self.object.name} created successfully.")
        logger.info(f"Class {self.object.name} created successfully")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error creating class. Please check the form.")
        logger.error(f"Error creating class: {form.errors}")
        return super().form_invalid(form)

class SchoolClassUpdateView(LoginRequiredMixin, UpdateView):
    model = SchoolClass
    form_class = SchoolClassForm
    template_name = 'school/schoolclass_form.html'
    success_url = reverse_lazy('schoolclass_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_session'] = "2025/2026"
        context['current_term'] = "Term 1"
        context['notification_count'] = 0
        logger.debug(f"School class update context data prepared for class ID {self.kwargs['pk']}")
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Class {self.object.name} updated successfully.")
        logger.info(f"Class {self.object.name} updated successfully")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error updating class. Please check the form.")
        logger.error(f"Error updating class ID {self.kwargs['pk']}: {form.errors}")
        return super().form_invalid(form)

class SchoolClassDeleteView(LoginRequiredMixin, DeleteView):
    model = SchoolClass
    template_name = "school/schoolclass_confirm_delete.html"
    success_url = reverse_lazy("schoolclass_list")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            return super().post(request, *args, **kwargs)  # tries the delete
        except ProtectedError as exc:
            blockers  = list(exc.protected_objects)
            preview   = ", ".join(str(b.student) for b in blockers[:4])
            if len(blockers) > 4:
                preview += f" and {len(blockers)-4} others"
            messages.error(
                request,
                mark_safe(
                    f"❗ Cannot delete <strong>{self.object.name}</strong> because students are still assigned: "
                    f"{preview}.<br>Reassign or delete those students first."
                )
            )
            # ---> send back to the list view <---
            return redirect("schoolclass_list")



@login_required
@require_POST
def check_class_unique(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        name = data.get('name')
        academic_year = data.get('academic_year')
        if not name or not academic_year:
            logger.warning("check_class_unique failed: Name and academic year are required")
            return JsonResponse({'is_unique': False, 'message': 'Name and academic year are required'}, status=400)
        exists = SchoolClass.objects.filter(name=name, academic_year=academic_year).exists()
        logger.debug(f"check_class_unique: Class {name} for year {academic_year} is {'unique' if not exists else 'not unique'}")
        return JsonResponse({'is_unique': not exists})
    except json.JSONDecodeError:
        logger.error("check_class_unique failed: Invalid JSON data received")
        return JsonResponse({'is_unique': False, 'message': 'Invalid JSON data'}, status=400)
    

class AnalyticsView(LoginRequiredMixin, TemplateView):
    """
    A richer ‘overview’ page that piggy-backs on the same data
    but adds three more charts and extra KPI cards.
    """
    template_name = "school/analytics.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # ── keep the common header bits ──────────────────────────
        ctx["school_name"]       = "St. Theresia-Avila"
        ctx["current_session"]   = "2025/2026"
        ctx["current_term"]      = "Term 1"
        ctx["notification_count"] = 0

        # ── basic counts (reuse from HomeView) ──────────────────
        students_qs   = Student.objects.all()
        staff_qs      = Staff.objects.all()
        active_studs  = students_qs.filter(is_active=True)
        active_staff  = staff_qs.filter(is_active=True)

        ctx["kpi_cards"] = [
            ("Students",           students_qs.count(),                "",              "👥"),
            ("Active Students",    active_studs.count(),               "",              "✅"),
            ("New Students 30 d",  students_qs.filter(
                                         admission_date__gte=timezone.now()-timezone.timedelta(days=30)
                                   ).count(), "",                     "🆕"),
            ("Staff",              staff_qs.count(),                   "",              "👩‍🏫"),
            ("Active Staff",       active_staff.count(),               "",              "✔️"),
            ("New Staff 90 d",     staff_qs.filter(
                                         hire_date__gte=timezone.now()-timezone.timedelta(days=90)
                                   ).count() if hasattr(Staff,'hire_date') else 0, "", "🆕"),
        ]

        # ── student gender pie (same as HomeView) ───────────────
        gender = students_qs.values("gender").annotate(c=Count("id"))
        ctx["pie_labels"] = [g["gender"] or "Unknown" for g in gender] or ["Male","Female"]
        ctx["pie_vals"]   = [g["c"] for g in gender]                 or [0,0]

        # ── student vs staff donut (two-slice) ──────────────────
        ctx["pop_labels"] = ["Students","Staff"]
        ctx["pop_vals"]   = [students_qs.count(), staff_qs.count()]

        # ── staff hires per month (last 12 m) ───────────────────
        if hasattr(Staff, "hire_date"):
            end   = timezone.now()
            start = end - timezone.timedelta(days=365)
            hires = (staff_qs.filter(hire_date__range=(start,end))
                     .extra({'m':"strftime('%%Y-%%m', hire_date)"})
                     .values("m").annotate(c=Count("id")).order_by("m"))
            ctx["hire_labels"] = [h["m"] for h in hires]
            ctx["hire_vals"]   = [h["c"] for h in hires]
        else:
            ctx["hire_labels"] = []
            ctx["hire_vals"]   = []

        # ── age-band histogram (if DOB exists) ──────────────────
        bands = defaultdict(int)
        if hasattr(Student,"date_of_birth"):
            today = timezone.now().date()
            for dob in students_qs.values_list("date_of_birth", flat=True):
                if dob:
                    age = (today - dob).days // 365
                    band = f"{(age//5)*5}-{((age//5)*5)+4}"
                    bands[band] += 1
        if bands:
            ctx["age_labels"] = sorted(bands.keys(), key=lambda b:int(b.split("-")[0]))
            ctx["age_vals"]   = [bands[b] for b in ctx["age_labels"]]
        else:
            ctx["age_labels"] = ["N/A"]
            ctx["age_vals"]   = [0]

        # ── reuse everything HomeView already prepares ──────────
        base_ctx = HomeView().get_context_data()
        ctx.update({k:v for k,v in base_ctx.items()
                          if k not in ctx})   # don’t overwrite
        return ctx