from core.base.admin import my_admin_site
from users.models import Account, Student, Administrator, Specialist, Assistant

my_admin_site.register(Account)
my_admin_site.register(Administrator)
my_admin_site.register(Specialist)
my_admin_site.register(Assistant)
my_admin_site.register(Student)
