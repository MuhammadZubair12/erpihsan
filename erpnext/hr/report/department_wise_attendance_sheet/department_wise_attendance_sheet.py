# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.desk.reportview import build_match_conditions

from frappe.utils import flt, getdate, formatdate, cstr

from frappe.utils import getdate, now, nowdate
from datetime import date, datetime, timedelta

import dateutil.relativedelta
import calendar
import json



def execute(filters=None):
	if not filters:
		filters = {}
	columns = get_column()
	conditions = get_conditions(filters)
	data = []
	#department = pre_data
	#attendance = post_data : 

	pre_data = frappe.db.sql("select emp.department,COUNT(emp.name) as strength from `tabAttendance` at inner join `tabEmployee` emp on at.employee = emp.name where emp.department IS NOT NULL and at.docstatus =1 %s group by 1 order by 1"%(conditions), filters, as_dict=1)
	for d in pre_data:
		conditions = get_conditions(filters,d.department)
		post_data = get_data(conditions, filters)
		if post_data:
			data.append(["","<b>"+str(d.department)+" - "+str(d.strength)+"</b>","","","","",""])
			data.extend(post_data)
	return columns, data


def get_column():
	return [

		{
			"fieldname":"emp_no",
			"label": "Emp. No",
			"width": 120,
			"fieldtype": "Data",
			"options": ""
		},
		{
			"fieldname":"emp_name",
			"label": "Employee Name",
			"width": 250,
			"fieldtype": "Data",
		},

		{
			"fieldname":"date_in",
			"label": "Date In",
			"fieldtype": "Date",
			"width": 150,
		},
		{
			"fieldname":"Time_in",
			"label": "Time In",
			"fieldtype": "Data",
			"width": 150,
		},

		{
			"fieldname":"date_out",
			"label": "Date Out",
			"fieldtype": "Date",
			"width": 150,
		},

		{
			"fieldname":"Time_Out",
			"label": "Time Out",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"fieldname":"over_time",
			"label": "Overtime",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"fieldname":"type",
			"label": "Type",
			"fieldtype": "Data",
			"width": 150,
		},

		{
			"fieldname":"status",
			"label": "Remarks",
			"fieldtype": "Data",
			"width": 150,
		},
	]
# tabEmployee = emp, tabAttendance = at, tabOvertime = ot
def get_data(conditions, filters):
	# overtimedata = frappe.db.sql(""" select total_time from `tabOvertime` where name =  """)
 	data = frappe.db.sql(""" select distinct  at.employee_number,  at.employee_name , at.attendance_date , at.time_in , 
 		IF(TIME(at.time_out) >= TIME('00:00:01') , IF(TIME(at.time_out) <= TIME('09:00:00'), DATE_ADD(at.attendance_date, INTERVAL 1 DAY), at.attendance_date), at.attendance_date)  , 
 		at.time_out , ot.total_time, at.input_status,
 		IF(at.status = 'Present',
			IF(at.late_entry = 1 and at.early_exit = 1 , 'Late Entry + Early Exit', 
			IF(at.late_entry = 1, 'Late Entry ', IF(at.early_exit = 1, 'Early Exist', 'On Time') )), at.status) AS Remarks FROM `tabAttendance` at 
			inner join `tabEmployee` emp on emp.name = at.employee
			LEFT JOIN `tabOvertime` ot ON at.employee = ot.employee and at.attendance_date = ot.date
			where emp.status !=  "Left" and at.docstatus =1 %s order by at.attendance_date  """%(conditions), filters, as_list=1)
 	return data



def get_conditions(filters, sales_order=None):
	conditions = ""
	if sales_order:
		conditions += " and emp.department = '{}'".format(sales_order)

	if filters.get("department"):
		conditions += " and emp.department =  %(department)s"

	if filters.get("employee"):
		conditions += " and at.employee =  %(employee)s"

	if filters.get("from_date") and filters.get("to_date"):
		conditions +=  "AND at.attendance_date BETWEEN (%(from_date)s) and (%(to_date)s)"

	return conditions