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

#	data = get_data(conditions, filters)
# 	pre_data = frappe.db.sql(""" select at.employee , SEC_TO_TIME(SUM(TIME_TO_SEC(late_entry_time))) AS TotalTime , SEC_TO_TIME(SUM(TIME_TO_SEC(early_exit_time))) AS TotalEarlyExitTime , SEC_TO_TIME(SUM(TIME_TO_SEC(at.over_time))) AS TotalOverTime  FROM `tabAttendance` at  where at.docstatus =1 %s  order by at.attendance_date """%(conditions), filters, as_dict=1)
# 	for d in pre_data:
# 		conditions = get_conditions(filters,d.employee)
# 		post_data = get_data(conditions, filters)
# 		if post_data:
# 			data.extend(post_data)
# 			data.append(["<b> ","Total", " " , " " , " " ," " ," " , d.TotalTime , d.TotalEarlyExitTime , d.TotalOverTime , "  </b>"])

#	data = get_data(conditions, filters)

	data_sum = frappe.db.sql(""" select at.employee, SEC_TO_TIME(SUM(TIME_TO_SEC(at.total_time))) AS TotalWorkingHour , 
		SEC_TO_TIME(SUM(TIME_TO_SEC(late_entry_time))) AS TotalTime , SEC_TO_TIME(SUM(TIME_TO_SEC(early_exit_time))) 
		AS TotalEarlyExitTime , SEC_TO_TIME(SUM(TIME_TO_SEC(at.overtime_time))) AS TotalOverTime, at.employee_number,
		SEC_TO_TIME(SUM(TIME_TO_SEC(ot.total_time))) AS AddOvertime, at.employee_name
		  FROM 
		`tabAttendance` at inner join `tabEmployee` emp on emp.name = at.employee
		left join `tabOvertime` ot on at.employee = ot.employee and at.attendance_date = ot.date and ot.docstatus =1
		  where at.docstatus =1 %s group by 1 order by at.attendance_date"""%(conditions), filters)

	if data_sum:
		for d in data_sum:
			conditions = get_conditions(filters,d[0])
			post_data = get_data(conditions, filters)
			if post_data:
				data.append(["-","<b>"+str(d[0])+" | "+str(d[5])+"</b>", "<b>"+str(d[7])+"</b>"])
				data.extend(post_data)
				total_time = str(d[1])
				if " " in total_time:
					days = int(total_time.split(" ")[0])
					time = total_time.split(" ")[2].split(":")
					hh = time[0]
					mm = time[1]
					ss = time[2]
					new_hh = (int(days)*24)+int(hh)
					total_time = str(new_hh).zfill(2)+":"+str(mm).zfill(2)+":"+str(ss).zfill(2)

				late_entry_time = str(d[2])
				if " " in late_entry_time:
					days = int(late_entry_time.split(" ")[0])
					time = late_entry_time.split(" ")[2].split(":")
					hh = time[0]
					mm = time[1]
					ss = time[2]
					new_hh = (int(days)*24)+int(hh)
					late_entry_time = str(new_hh).zfill(2)+":"+str(mm).zfill(2)+":"+str(ss).zfill(2)

				early_exit_time = str(d[3])
				if " " in early_exit_time:
					days = int(early_exit_time.split(" ")[0])
					time = early_exit_time.split(" ")[2].split(":")
					hh = time[0]
					mm = time[1]
					ss = time[2]
					new_hh = (int(days)*24)+int(hh)
					early_exit_time = str(new_hh).zfill(2)+":"+str(mm).zfill(2)+":"+str(ss).zfill(2)

				overtime_time = str(d[4])
				if " " in overtime_time:
					days = int(overtime_time.split(" ")[0])
					time = overtime_time.split(" ")[2].split(":")
					hh = time[0]
					mm = time[1]
					ss = time[2]
					new_hh = (int(days)*24)+int(hh)
					overtime_time = str(new_hh).zfill(2)+":"+str(mm).zfill(2)+":"+str(ss).zfill(2)

				add_overtime_time = str(d[6])
				if " " in add_overtime_time:
					days = int(add_overtime_time.split(" ")[0])
					time = add_overtime_time.split(" ")[2].split(":")
					hh = time[0]
					mm = time[1]
					ss = time[2]
					new_hh = (int(days)*24)+int(hh)
					add_overtime_time = str(new_hh).zfill(2)+":"+str(mm).zfill(2)+":"+str(ss).zfill(2)

				data.append(["-","<b class='row-total'> Total </b> ","", " " , " " , " " ," ", total_time , late_entry_time ,early_exit_time, overtime_time , add_overtime_time,""])
				data.append([""])
	return columns, data

def get_column():
	return [
		{
			"fieldname":"attendance_date",
			"label": "Attendance Date",
			"width": 200,
			"fieldtype": "Date",
		},
		# {
		# 	"fieldname":"employee",
		# 	"label": "Employee",
		# 	"width": 120,
		# 	"fieldtype": "Link",
		# 	"options": "Employee"
		# },
		# {
		# 	"fieldname":"employee_number",
		# 	"label": "Employee No",
		# 	"width": 120,
		# 	"fieldtype": "Data",
		# },
		{
			"fieldname":"shift",
			"label": "Shift",
			"width": 300,
			"fieldtype": "data",
		},
		{
			"fieldname":"Remarks",
			"label": "Remarks",
			"fieldtype": "Data",
			"width": 100,
		},	


		{
			"fieldname":"date_in",
			"label": "Date In",
			"width": 120,
			"fieldtype": "Date",

		},




		{



			"fieldname":"time_in",
			"label": "Time In",
			"fieldtype": "Time",
			"width": 110,
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
			"fieldtype": "Time",
			"width": 100,
		},
		{
			"fieldname":"working_hours",
			"label": "Work Hours",
			"fieldtype": "Data",
			"width": 100,
		},		

		{
			"fieldname":"late_arrived",
			"label": "Late Arr.",
			"fieldtype": "Data",
			"width": 100,
		},		

		{
			"fieldname":"early_hour",
			"label": "Early Hour",
			"fieldtype": "Data",
			"width": 100,
		},		

		{
			"fieldname":"hover_time",
			"label": "Over Time",
			"fieldtype": "Data",
			"width": 100,
		},	

		{
			"fieldname":"additional_ot",
			"label": "Add. Over Time",
			"fieldtype": "Data",
			"width": 150,
		},		
		{
			"fieldname":"type",
			"label": "Type",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"fieldname":"reason_for_manual",
			"label": "Reason for Manual",
			"fieldtype": "Data",
			"width": 150,
		},		



	]

def get_data(conditions, filters):

 	# data = frappe.db.sql(""" select  at.attendance_date,  at.shift, at.attendance_date, at.time_in ,
 	# 	IF(TIME(at.time_out) >= TIME('00:00:01') , 
 	# 									IF(TIME(at.time_out) <= TIME('09:00:00'), 
 	# 									DATE_ADD(at.attendance_date, INTERVAL 1 DAY), at.attendance_date), 
 	# 									at.attendance_date) , at.time_out, at.working_hours , at.late_entry_time, at.early_exit_time,  at.over_time ,
 	# 	IF(at.status = 'Present', IF(at.late_entry = 1 , 'Late Entry', IF(at.early_exit_time = 1 , 'Early Exit', 'On Time')), at.status), CONVERT(at.late_entry_time, TIME),
 	# 	tSEC_TO_TIME(SUM(TIME_TO_SEC(at.late_entry_time))) AS ToalLateTime 
		# FROM `tabAttendance` at  where at.docstatus =1  %s order by at.attendance_date  """%(conditions), filters, as_list=1)
 	

 	data = frappe.db.sql(""" select  at.attendance_date,  at.shift, 
 		IF(at.status = 'Present', IF(at.late_entry = 1 , 'Late Entry', IF(at.early_exit_time = 1 , 'Early Exit', 'On Time')), at.status),
 	 at.attendance_date, at.time_in,
 		IF(TIME(at.time_out) >= TIME('00:00:01') , 
 										IF(TIME(at.time_out) <= TIME('09:00:00'), 
 										DATE_ADD(at.attendance_date, INTERVAL 1 DAY), at.attendance_date), 
 										at.attendance_date) , at.time_out, at.total_time , at.late_entry_time, at.early_exit_time,  at.overtime_time, ot.total_time, at.input_status,
 		at.reason_for_manual
		FROM `tabAttendance` at  inner join `tabEmployee` emp on emp.name = at.employee
		left join `tabOvertime` ot on at.employee = ot.employee and at.attendance_date = ot.date and ot.docstatus =1
		where at.docstatus =1  %s order by at.attendance_date  """%(conditions), filters, as_list=1)
 	return data


def get_sum_late_entry():

 	late = frappe.db.sql(""" SELECT SEC_TO_TIME(SUM(TIME_TO_SEC(late_entry_time))) AS TotalTime  from `tabAttendance`   """ ,  as_list=1)
 	return late


def get_conditions(filters, sales_order=None):

	conditions = ""

	if sales_order:
		conditions += " and at.employee = '{}'".format(sales_order)

	if filters.get("branch"):
		conditions += " and emp.branch =  %(branch)s"

	if filters.get("department"):
		conditions += " and emp.department =  %(department)s"

	if filters.get("employee"):
		conditions += " and at.employee =  %(employee)s"

	if filters.get("from_date") and filters.get("to_date"):
		conditions +=  "AND at.attendance_date BETWEEN (%(from_date)s) and (%(to_date)s)"
	return conditions