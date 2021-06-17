
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
			"label": " Employee Full Name ",
			"width": 200,
			"fieldtype": "Data",

		},

		{
			"fieldname":"sessi_no",
			"label": " Sessio No# ",
			"width": 200,
			"fieldtype": "Data",

		},

		{
			"fieldname":"Father_Name",
			"label": "Father Name",
			"width": 200,
			"fieldtype": "Data",
		},
		{
			"fieldname":"CNIC",
			"label": "CNIC No",
			"fieldtype": "",
			"width": 200,
		},

		{
			"fieldname":"Designation",
			"label": "Designation",
			"fieldtype": "",
			"width": 200,
		},
		{
			"fieldname":"Employement_Type",
			"label": "Employement Type",
			"fieldtype": "",
			"width": 200,
		},
		{
			"fieldname":"Skill_Level",
			"label": "Skill Level",
			"fieldtype": "",
			"width": 200,
		},
		{
			"fieldname":"salary",
			"label": "Employee_Salary (Daily/ Monthly)",
			"fieldtype": "Currency",
			"width": 200,
		},
		{
			"fieldname":"NO_OF_DAYS_WORKED",
			"label": "Working_Days",
			"fieldtype": "Int",
			"width": 200,
		},
		{
			"fieldname":"salary2",
			"label": "Salary to Pay Contribution",
			"fieldtype": "Currency",
			"width": 200,
		},
		{
			"fieldname":"Is_Employee_Separated",
			"label": "Is Employee Separated",
			"fieldtype": "",
			"width": 200,
		},
		{
			"fieldname":"Mobile_No",
			"label": "Mobile No",
			"fieldtype": "",
			"width": 200,
		},
		{
			"fieldname":"Employee_Gender",
			"label": "Employee Gender",
			"fieldtype": "",
			"width": 200,
		},
]

def get_data(conditions, filters):
	data = frappe.db.sql(""" select e.employee_name, e.sessi_no, e.father_name, e.passport_number, e.designation, e.employment_type,
		e.skill_level,
		pr.basic, pr.payment_days_custom, pr.basic, e.status, e.cell_number, e.gender
		from `tabSalary Slip` pr inner join `tabEmployee` e on e.name = pr.employee
		where pr.docstatus=1 and e.sessi_applicable = 'Yes' %s
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