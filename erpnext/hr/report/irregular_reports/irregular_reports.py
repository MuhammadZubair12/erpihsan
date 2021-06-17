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
	data = get_data(conditions, filters)
	# data = []
	# pre_data = frappe.db.sql("select cast(time AS Date)  from `tabEmployee Checkin` at where docstatus =1 %s group by cast(time AS Date) order by cast(time AS Date)"%(conditions), filters, as_dict=1)
	# for d in pre_data:
	# 	conditions = get_conditions(filters,d.department)
	# 	post_data = get_data(conditions, filters)
	# 	if post_data:
	# 		data.append(["",d.Date,"","","","",""])
	# 		data.extend(post_data)
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
			"width": 150,
			"fieldtype": "data",
		},

		{
			"fieldname":"designation",
			"label": "Designation",
			"width": 150,
			"fieldtype": "data",
		},

		{
			"fieldname":"status",
			"label": "Status",
			"width": 150,
			"fieldtype": "data",
		},

		{
			"fieldname":"date",
			"label": "Date",
			"fieldtype": "Date",
			"width": 150,
		},

		{
			"fieldname":"time",
			"label": "Time",
			"fieldtype": "Time",
			"width": 150,
		},

		{
			"fieldname":"saluation",
			"label": "Total Time",
			"fieldtype": "Time",
			"width": 150,
		},

		{
			"fieldname":"shift",
			"label": "Shift",
			"fieldtype": "data",
			"width": 150,
		},
	]

def get_data(conditions, filters):

 	# data = frappe.db.sql(""" select distinct  c.employee ,  c.employee_name ,e.designation , e.status , c.time , c.shift 
 	# 	FROM `tabAttendance` at where at.docstatus =1 %s order by at.employee  """%(conditions), filters, as_list=1)
 	# return data
	data = frappe.db.sql(""" select distinct  e.employee_number ,  t.employee_name , e.designation , t.log_type , cast(time AS Date), cast(time AS Time),\
		IF(t.log_type ='IN', '',timediff(t.time,t.pretime)) as totaltime, t.shift FROM (select employee, employee_name,log_type,shift,time, LAG(time) OVER (ORDER BY employee,time ) as pretime from `tabEmployee Checkin` )as t\
			inner join `tabEmployee` e  on t.employee = e.name
 		where 1=1 %s order by t.employee, t.time"""%(conditions), filters, as_list=1)
	return data
	#  laste time report before modified by createch
 	# data = frappe.db.sql(""" select distinct  e.employee_number ,  c.employee_name , e.designation , c.log_type , cast(time AS Date), cast(time AS Time),\
	#  (CASE c.log_type WHEN 'IN' THEN '' WHEN 'OUT' THEN (time - coalesce(lag(time) over (order by c.employee))) END) AS totaltime, c.shift 
 	# 	FROM `tabEmployee Checkin` c  inner join `tabEmployee` e  on c.employee = e.name
 	# 	where 1=1 %s order by c.employee, time"""%(conditions), filters, as_list=1)
 	# return data

 	# data = frappe.db.sql(""" select distinct  c.employee ,  c.employee_name, c.employee_name,  c.log_type ,cast(time AS Time)  , c.shift 
 	# 	FROM `tabEmployee Checkin` c  left join `tabAttendance` at  on c.name = at.name 
 	# 	inner join `tabEmployee e on c.name  = at.name 
 	# 	where 1=1 %s order by c.employee """%(conditions), filters, as_list=1)
 	# return data


def get_conditions(filters, sales_order=None):
	conditions = ""
	if sales_order:
		conditions += " and department = '{}'".format(sales_order)

	if filters.get("department"):
		conditions += " and e.department =  %(department)s"

	if filters.get("employee"):
		conditions += " and t.employee =  %(employee)s"

	if filters.get("from_date") and filters.get("to_date"):
		conditions +=  "AND cast(time AS Date) BETWEEN (%(from_date)s) and (%(to_date)s)"

	return conditions