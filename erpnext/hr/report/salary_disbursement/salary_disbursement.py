
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
		{
			"fieldname":"amount",
			"label": "Amount",
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname":"bank_name",
			"label": "BankName",
			"width": 150,
			"fieldtype": "Data",
		},
		{
			"fieldname":"bank_ac_no",
			"label": "BeneficiaryAccountNumber",
			"width": 150,
			"fieldtype": "Data",
		},
		{
			"fieldname":"employee_name",
			"label": " BeneficiaryName ",
			"width": 150,
			"fieldtype": "Data",

		},
		{
			"fieldname":"employee_code",
			"label": "BeneficiaryCode",
			"width": 120,
			"fieldtype": "Data",
		},
		{
			"fieldname":"employee_number",
			"label": "ReferenceField1",
			"width": 120,
			"fieldtype": "Data",
		},
		{
			"fieldname":"ref2",
			"label": "ReferenceField2",
			"width": 100,
			"fieldtype": "Data",
		},
		{
			"fieldname":"personal_email",
			"label": "BeneficiaryEmail",
			"width": 120,
			"fieldtype": "Data",
		},
		{
			"fieldname":"cell_number",
			"label": "BeneficiaryNumber",
			"width": 120,
			"fieldtype": "Data",
		},
		
]

def get_data(conditions, filters):
	data = frappe.db.sql(""" select pr.employee_number, pr.employee_name, e.bank_ac_no, ROUND(pr.net_pay,0) as amount,
		e.bank_name, e.personal_email, e.cell_number, CONCAT(MONTHNAME(pr.start_date)," ",YEAR(pr.start_date)) as ref2
		from `tabSalary Slip` pr inner join `tabEmployee` e on e.name = pr.employee
		where pr.docstatus=1 %s
		 """%(conditions), filters, as_dict=1)
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