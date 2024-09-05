"""
Copyright (c) 2024, TI Sin Problemas and contributors
For license information, please see license.txt
"""

from erpnext.setup.doctype.employee.employee import Employee as ERPNextEmployee


class Employee(ERPNextEmployee):

    def set_employee_name(self):
        names = [
            self.first_name,
            self.middle_name,
            self.last_name,
            self.mx_second_last_name,
        ]
        filtered_names = filter(lambda x: x, names)
        self.employee_name = " ".join(filtered_names)
