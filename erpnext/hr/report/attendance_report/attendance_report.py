# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.desk.reportview import build_match_conditions

def execute(filters=None):
	if not filters:
		filters = {}
	columns = get_column()
	conditions = get_conditions(filters)
	data = get_data(conditions, filters)

	return columns, data

def get_column():
	return [_("Attendance") + ":Link/Attendance:150",_("Employee") + ":Link/Employee:150",_("Employee No#") + "::150",
	_("Employee Name") + "::150",_("Date") + ":Date:120",_("Status") + "::100", 
	_("Department") + ":Link/Department:100",_("Shift") + ":Link/Shift Type:100",_("Time In") + "::100",_("Time Out") + "::100", 
	_("Total Time") + "::100", _("Late Mins") + ":Float:100",_("Early Mins") + ":Float:100",_("Overtime Mins") + ":Float:100",]

def get_data(conditions, filters):
 	data = frappe.db.sql("""Select name, employee,employee_number,employee_name, attendance_date, status, department,shift,
 		time_in, time_out, total_time, ROUND(late_entry_mins/60), ROUND(early_exit_mins/60), ROUND(overtime_mins/60)
 		from `tabAttendance` where docstatus=1 %s
		"""%(conditions), filters, as_list=1)
 	return data

def get_conditions(filters):
	conditions = ""
	if filters.get("employee"):
		conditions += " and employee =  %(supplier)s"
	if filters.get("from_date"):
		conditions += " and attendance_date >=  %(from_date)s"
	if filters.get("to_date"):
		conditions += " and attendance_date <=  %(to_date)s"
	return conditions