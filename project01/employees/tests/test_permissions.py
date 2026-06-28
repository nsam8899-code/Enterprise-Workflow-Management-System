from django.test import TestCase
from employees.models import MenuPermission

class MenuPermissionModelTestCase(TestCase):
    def test_menu_permission_allowed_roles(self):
        perm = MenuPermission.objects.create(
            menu_name="employees",
            display_name="Employee Directory",
            allow_superuser=True,
            allow_admin=True,
            allow_manager=False,
            allow_employee=False
        )
        self.assertTrue(perm.is_allowed("Super User"))
        self.assertTrue(perm.is_allowed("Admin"))
        self.assertFalse(perm.is_allowed("Manager"))
        self.assertFalse(perm.is_allowed("Employee"))
