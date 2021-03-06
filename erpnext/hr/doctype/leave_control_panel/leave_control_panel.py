# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from frappe.utils import cint, cstr, flt, nowdate, comma_and, date_diff
from frappe import msgprint, _
from frappe.model.document import Document

class LeaveControlPanel(Document):
	def get_employees(self):
		lst1 = [[self.employee_type,"employment_type"],[self.branch,"branch"],[self.designation,"designation"],[self.department, "department"]]
		condition = "and "
		flag = 0
		for l in lst1:
			if(l[0]):
				if flag == 0:
					condition += l[1] + "= '" + l[0] +"'"
				else:
					condition += " and " + l[1]+ "= '" +l[0] +"'"
				flag = 1
		emp_query = "select name from `tabEmployee` where status = 'Active'"
		if flag == 1:
			emp_query += condition
		e = frappe.db.sql(emp_query)
		return e

	def validate_values(self):
		for f in ["from_date", "to_date", "leave_type", "no_of_days"]:
			if not self.get(f):
				frappe.throw(_("{0} is required").format(self.meta.get_label(f)))
	
	def to_date_validation(self):
		if date_diff(self.to_date, self.from_date) <= 0:
			return "Invalid period"

	def allocate_leave(self):
		self.validate_values()
		leave_allocated_for = []
		employees = self.get_employees()
		if not employees:
			frappe.throw(_("No employee found"))

		for d in self.get_employees():
			try:
				la = frappe.new_doc('Leave Allocation')
				la.set("__islocal", 1)
				la.employee = cstr(d[0])
				la.employee_name = frappe.db.get_value('Employee',cstr(d[0]),'employee_name')
				la.leave_type = self.leave_type
				la.from_date = self.from_date
				la.to_date = self.to_date
				la.carry_forward = cint(self.carry_forward)
				la.new_leaves_allocated = flt(self.no_of_days)
				la.docstatus = 1
				la.save()
				leave_allocated_for.append(d[0])
			except:
				pass
		if leave_allocated_for:
			msgprint(_("Leaves Allocated Successfully for {0}").format(comma_and(leave_allocated_for)))
