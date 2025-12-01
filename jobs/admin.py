from django.contrib import admin
from .models import (
    Company, JobCategory, Job, UserProfile, Application, SavedJob,
    Industry, JobType, Location, Skill
)

# --- Normalization Model Admin Classes ---

@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(JobType)
class JobTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


# --- Core Model Admin Classes ---

class JobInline(admin.TabularInline):
    """Allows viewing jobs linked to a company directly on the Company page."""
    model = Job
    extra = 0
    fields = ('title', 'location', 'job_type', 'is_active', 'date_posted')
    readonly_fields = ('date_posted',)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry', 'location', 'website')
    list_filter = ('industry', 'location')
    search_fields = ('name', 'description')
    inlines = [JobInline]


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'category', 'job_type', 'location', 'salary_min', 'is_active', 'date_posted')
    list_filter = ('is_active', 'job_type', 'category', 'location')
    search_fields = ('title', 'description', 'company__name')
    date_hierarchy = 'date_posted'
    raw_id_fields = ('company',) # Use a search box for the company FK, useful when you have many companies


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_title', 'phone_number', 'display_skills')
    search_fields = ('user__username', 'current_title', 'bio')
    filter_horizontal = ('skills',) # Better widget for ManyToMany field

    def display_skills(self, obj):
        return ", ".join([skill.name for skill in obj.skills.all()[:3]])
    display_skills.short_description = 'Skills (Top 3)'


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'applicant', 'status', 'date_applied')
    list_filter = ('status', 'date_applied')
    search_fields = ('job__title', 'applicant__username')
    date_hierarchy = 'date_applied'
    list_editable = ('status',) # Allows quick status changes


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'saved_at')
    list_filter = ('saved_at',)
    search_fields = ('user__username', 'job__title')