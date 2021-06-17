
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
	
	return [
		# {
		# 	"fieldname":"employee_number",
		# 	"label": "Employee No",
		# 	"width": 250,
		# 	"fieldtype": "Data",
		# },

		{
			"fieldname":"employee_name",
			"label": " Name ",
			"width": 200,
			"fieldtype": "Data",

		},

		{
			"fieldname":"eobi_no",
			"label": "EOBI_NO",
			"width": 200,
			"fieldtype": "Data",
		},
		{
			"fieldname":"CNIC",
			"label": "CNIC",
			"fieldtype": "",
			"width": 200,
		},

		{
			"fieldname":"NIC",
			"label": "NIC",
			"fieldtype": "",
			"width": 200,
		},
		{
			"fieldname":"DOB",
			"label": "DOB",
			"fieldtype": "Date",
			"width": 200,
		},
		{
			"fieldname":"DOJ",
			"label": "DOJ",
			"fieldtype": "Date",
			"width": 200,
		},
		{
			"fieldname":"DOE",
			"label": "DOE",
			"fieldtype": "Date",
			"width": 200,
		},
		{
			"fieldname":"NO_OF_DAYS_WORKED",
			"label": "NO_OF_DAYS_WORKED",
			"fieldtype": "Int",
			"width": 200,
		},
]

def get_data(conditions, filters):
	data = frappe.db.sql(""" select e.employee_name, e.eobi_no, e.passport_number, e.nic, e.date_of_birth,
		e.date_of_joining, e.relieving_date, pr.payment_days_custom
		from `tabSalary Slip` pr inner join `tabEmployee` e on e.name = pr.employee
		where pr.docstatus=1 and e.employment_type = 'Permanent - Registered' %s
		 """%(conditions), filters, as_list=1)
	return data

def get_conditions(filters):
	conditions = ""

	if filters.get("from_date"):
		conditions += " and pr.start_date >= '{}'".format(filters.get("from_date"))
	if filters.get("to_date"):
		conditions += " and pr.end_date <= '{}'".format(filters.get("to_date"))
	if filters.get("employee"):
		conditions += " and pr.employee = '{}'".format(filters.get("employee"))
	if filters.get("department"):
		conditions += " and pr.department = '{}'".format(filters.get("department"))
	if filters.get("branch"):
		conditions += " and pr.branch = '{}'".format(filters.get("branch"))
	if filters.get("salary_mode"):
		conditions += " and e.salary_mode = '{}'".format(filters.get("salary_mode"))

	return conditions