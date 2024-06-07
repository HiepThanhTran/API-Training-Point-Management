from core.base.admin import my_admin_site
from schools.models import EducationalSystem, Faculty, Major, AcademicYear, Class, Semester, Criterion, TrainingPoint, SemesterOfStudent

my_admin_site.register(EducationalSystem)
my_admin_site.register(Faculty)
my_admin_site.register(Major)
my_admin_site.register(AcademicYear)
my_admin_site.register(Class)
my_admin_site.register(Semester)
my_admin_site.register(SemesterOfStudent)
my_admin_site.register(Criterion)
my_admin_site.register(TrainingPoint)
