# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.desk.reportview import build_match_conditions
import collections
import itertools

def execute(filters=None):
	if not filters:
		filters = {}
	columns = get_column(filters)
	conditions = get_conditions(filters)
	ss = get_data(conditions, filters)
	group_by = str(filters.get("group_by")).lower()
	data = []
	grouped = collections.defaultdict(list)
	for (item) in ss:
		qty_dict = ss[(item)]
		row=[qty_dict.get(group_by)]
		for i,d in qty_dict.items():
			if i not in ["employee", "branch", "status"]:
				row.append(d)
		# row = [qty_dict.get(report_type),qty_dict.opening,qty_dict.receipt,qty_dict.transfer,qty_dict.adjustment,qty_dict.sale,qty_dict.closing]
		data.append(row)
	new_lst = []
	for k,g in itertools.groupby(sorted(data,key=lambda x:x[0]) , lambda x:x[0]):
		l = list(g)
		overtime = sum([float(x[23]) for x in l])//60
		total_hr = 0
		total_min = overtime
		while total_min >= 60:
			total_hr+=1
			total_min-=60
		res = str(total_hr).zfill(2)+":"+str(int(total_min)).zfill(2)
		new_lst.append([k,l[0][1],l[0][2],l[0][3],l[0][4],sum([float(x[5]) for x in l]), sum([float(x[6]) for x in l]), sum([float(x[7]) for x in l]), sum([float(x[8]) for x in l]), sum([float(x[9]) for x in l]),
			sum([float(x[10]) for x in l]),sum([float(x[11]) for x in l]),sum([float(x[12]) for x in l]),sum([float(x[13]) for x in l]),
			sum([float(x[14]) for x in l]),sum([float(x[15]) for x in l]),sum([float(x[16]) for x in l]), sum([float(x[17]) for x in l]),
			sum([float(x[18]) for x in l]),
			sum([float(x[19]) for x in l]), sum([float(x[20]) for x in l]),
			sum([float(x[21]) for x in l]),sum([float(x[22]) for x in l]),res,
			sum([float(x[24]) for x in l]),sum([float(x[25]) for x in l]),sum([float(x[26]) for x in l]),
			sum([float(x[27]) for x in l])
			 ])
	return columns, new_lst

def get_column(filters):
	group_by = str(filters.get("group_by"))
	columns = [
		{"fieldname": group_by.lower(), "label": _(group_by), "fieldtype":"Link", "options": group_by, "width": 150},

		{"fieldname": "employee_number", "label": _("Employee No"), "fieldtype":"Data", "width": 150},
		{"fieldname": "employee_name", "label": _("Employee Name"), "fieldtype":"Data", "width": 150},
		{"fieldname": "department", "label": _("Department"), "fieldtype":"Data", "width": 150},
		{"fieldname": "designation", "label": _("Designation"), "fieldtype":"Data", "width": 150},

		{"fieldname": "No_of_Staff", "label": _("No of Staff"), "fieldtype":"Int", "width": 100},
		{"fieldname": "Gross_Pay", "label": _("Gross Pay"), "fieldtype":"Currency", "width": 120},
		{"fieldname": "Earned_Salary", "label": _("Earned Salary"), "fieldtype":"Currency", "width": 120},
		{"fieldname": "Medical_Allowance", "label": _("Medical Allowance"), "fieldtype":"Currency", "width": 150},
		{"fieldname": "Conveyance_Allowance", "label": _("Conveyance Allowance"), "fieldtype":"Currency", "width": 170},
		{"fieldname": "Additional_Earning", "label": _("Additional Earning"), "fieldtype":"Currency", "width": 170},
		{"fieldname": "Total_Earned_Pay", "label": _("Total Earned Pay"), "fieldtype":"Currency", "width": 120},

		{"fieldname": "Absent_Deduction", "label": _("Absent Deduction"), "fieldtype":"Currency", "width": 140},
		{"fieldname": "Late_Arrival_Deduction", "label": _("Late Arrival Deduction"), "fieldtype":"Currency", "width": 170},
		{"fieldname": "Early_Leave_Deduction", "label": _("Early Leave Deduction"), "fieldtype":"Currency", "width": 170},
		{"fieldname": "Other_Deduction", "label": _("Other Deduction"), "fieldtype":"Currency", "width": 120},
		{"fieldname": "EOBI", "label": _("EOBI"), "fieldtype":"Currency", "width": 80},

		{"fieldname": "Income_Tax", "label": _("Income Tax"), "fieldtype":"Currency", "width": 100},
		{"fieldname": "Lunch", "label": _("Lunch"), "fieldtype":"Currency", "width": 90},
		{"fieldname": "Loan_Repayment", "label": _("Loan Repayment"), "fieldtype":"Currency", "width": 120},
		{"fieldname": "Advance_Deduction", "label": _("Advance Deduction"), "fieldtype":"Currency", "width": 150},
		{"fieldname": "Total_Deduction", "label": _("Total Deduction"), "fieldtype":"Currency", "width": 120},

		{"fieldname": "Net_Total", "label": _("Net Total"), "fieldtype":"Currency", "width": 120},
		{"fieldname": "Overtime_Hrs", "label": _("Overtime Hrs"), "fieldtype":"Data", "width": 110},
		{"fieldname": "Overtime_Amount", "label": _("Overtime Amount"), "fieldtype":"Currency", "width": 130},
		{"fieldname": "Add_Overtime", "label": _("Add. Overtime"), "fieldtype":"Currency", "width": 120},
		{"fieldname": "OT_Total", "label": _("OT Total"), "fieldtype":"Currency", "width": 120},
		{"fieldname": "Net_Pay", "label": _("Net Pay"), "fieldtype":"Currency", "width": 120},
	]
	# if group_by in ["Branch", "Department"]:
	# 	columns.insert(1,{"fieldname": "No_of_Staff", "label": _("No of Staff"), "fieldtype":"Int", "width": 80})
	return columns

def get_data(conditions, filters):
	iwb_map = {}
	loan_name = []
	overtime_name = []
	employee = []
	data = frappe.db.sql("""Select p.name as name,p.employee as employee, p.department as department, p.branch as branch,p.status as status, 
		p.designation as designation, p.employee_name as employee_name, p.employee_number as employee_number,
		1 as No_of_Staff, c.salary_component as salary_component, c.amount as amount, 
		p.total_loan_repayment as total_loan_repayment, p.overtime_mins as approved_overtime
		from `tabSalary Slip` p inner join `tabSalary Detail` c on c.parent = p.name where p.name != 'abc' {conditions}
		order by employee,name""".format(conditions= conditions), as_dict=1)
	for d in data:
		key = (d.get("employee") or "None")
		if key not in iwb_map:
			iwb_map[key] = frappe._dict({
				"employee": d.employee, "employee_number": d.employee_number,
				"employee_name": d.employee_name, "department": d.department or "None",
				"designation": d.designation, "branch": d.branch or "None",
				"status":d.status or "None",
				"No_of_Staff": 1,
				"Gross_Pay": 0.0, "Earned_Salary": 0.0,
				"Medical_Allowance": 0.0, "Conveyance_Allowance": 0.0, "Additional_Earning": 0.0,
				"Total_Earned_Pay": 0.0, "Absent_Deduction": 0.0,
				"Late_Arrival_Deduction": 0.0, "Early_Leave_Deduction": 0.0,
				"Other_Deduction": 0.0, "EOBI": 0.0,
				"Income_Tax": 0.0, "Lunch": 0.0,
				"Loan_Repayment": 0.0, "Advance_Deduction": 0.0, "Total_Deduction": 0.0,"Net_Total": 0.0,
				"Overtime_Hrs": 0.0, "Overtime_Amount": 0.0,
				"Add_Overtime": 0.0, "OT_Total": 0.0, "Net_Pay": 0.0,
			})
		qty_dict = iwb_map[(d.get("employee") or "None")]
		amount = d.amount

		if d.total_loan_repayment > 0 and d.name not in loan_name:
			qty_dict.Loan_Repayment += d.total_loan_repayment
			qty_dict.Total_Deduction += d.total_loan_repayment
			qty_dict.Net_Pay -= d.total_loan_repayment
			qty_dict.Net_Total -= d.total_loan_repayment
			loan_name.append(d.name)

		if d.approved_overtime > 0 and d.name not in overtime_name:
			qty_dict.Overtime_Hrs += d.approved_overtime
			overtime_name.append(d.name)

		if d.salary_component == "Basic":
			qty_dict.Total_Earned_Pay += amount
			qty_dict.Gross_Pay += amount
			qty_dict.Earned_Salary += amount
			qty_dict.Net_Pay += amount
			qty_dict.Net_Total += amount

		elif d.salary_component == "Medical Allowance":
			qty_dict.Total_Earned_Pay += amount
			qty_dict.Gross_Pay += amount
			qty_dict.Medical_Allowance += amount
			qty_dict.Net_Pay += amount
			qty_dict.Net_Total += amount

		elif d.salary_component == "Conveyance Allowance":
			qty_dict.Total_Earned_Pay += amount
			qty_dict.Conveyance_Allowance += amount
			qty_dict.Net_Pay += amount
			qty_dict.Net_Total += amount

		elif d.salary_component == "Additional Earning":
			qty_dict.Total_Earned_Pay += amount
			qty_dict.Additional_Earning += amount
			qty_dict.Net_Pay += amount
			qty_dict.Net_Total += amount

		elif d.salary_component == "Absent Deduction":
			qty_dict.Absent_Deduction += amount
			qty_dict.Total_Deduction += amount
			qty_dict.Net_Pay -= amount
			qty_dict.Net_Total -= amount

		elif d.salary_component == "Late Arrival Deduction":
			qty_dict.Late_Arrival_Deduction += amount
			qty_dict.Total_Deduction += amount
			qty_dict.Net_Pay -= amount
			qty_dict.Net_Total -= amount

		elif d.salary_component == "Early Leave Deduction":
			qty_dict.Early_Leave_Deduction += amount
			qty_dict.Total_Deduction += amount
			qty_dict.Net_Pay -= amount
			qty_dict.Net_Total -= amount

		elif d.salary_component == "Additional Days Deduction" or d.salary_component == "Additional Deduction":
			qty_dict.Other_Deduction += amount
			qty_dict.Total_Deduction += amount
			qty_dict.Net_Pay -= amount
			qty_dict.Net_Total -= amount

		elif d.salary_component == "EOBI":
			qty_dict.EOBI += amount
			qty_dict.Total_Deduction += amount
			qty_dict.Net_Pay -= amount
			qty_dict.Net_Total -= amount

		elif d.salary_component == "Income Tax":
			qty_dict.Income_Tax += amount
			qty_dict.Total_Deduction += amount
			qty_dict.Net_Pay -= amount
			qty_dict.Net_Total -= amount

		elif d.salary_component == "Lunch":
			qty_dict.Lunch += amount
			qty_dict.Total_Deduction += amount
			qty_dict.Net_Pay -= amount
			qty_dict.Net_Total -= amount

		elif d.salary_component == "Advance Deduction":
			qty_dict.Advance_Deduction += amount
			qty_dict.Total_Deduction += amount
			qty_dict.Net_Pay -= amount
			qty_dict.Net_Total -= amount

		elif d.salary_component == "Approved Overtime":
			qty_dict.Overtime_Amount += amount
			qty_dict.Net_Pay += amount
			qty_dict.OT_Total += amount

		elif d.salary_component == "Overtime":
			qty_dict.Add_Overtime += amount
			qty_dict.Net_Pay += amount
			qty_dict.OT_Total += amount

	return iwb_map

def get_conditions(filters):
	conditions = ""
	if filters.get("from_date"):
		conditions += " and p.start_date >= '{}'".format(filters.get("from_date"))
	if filters.get("to_date"):
		conditions += " and p.end_date <= '{}'".format(filters.get("to_date"))
	if filters.get("employee"):
		conditions += " and p.employee = '{}'".format(filters.get("employee"))
	if filters.get("department"):
		conditions += " and p.department = '{}'".format(filters.get("department"))
	if filters.get("branch"):
		conditions += " and p.branch = '{}'".format(filters.get("branch"))
	if filters.get("status"):
		conditions += " and p.status = '{}'".format(filters.get("status"))

	return conditions