# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe.utils import add_days, getdate, cint, cstr

from frappe import throw, _
from erpnext.utilities.transaction_base import TransactionBase, delete_events
from erpnext.stock.utils import get_valid_serial_nos
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
from datetime import datetime, date, timedelta
from frappe.utils.background_jobs import enqueue
from frappe.model.document import Document
from frappe import utils
import sys
import time
#from zk import ZK, const
import pandas as pd


class AttendanceMachine(Document):
	pass

@frappe.whitelist()
def first_task():
	get_data(job_time="1st")

@frappe.whitelist()
def second_task():
	get_data(job_time="2nd")

@frappe.whitelist()
def get_data(att_date = None, end_date = None, ip = None, att_type="IN", port = 0, job_time= None,employee=None):
	today = frappe.utils.getdate(frappe.utils.nowdate())
	end = frappe.utils.getdate(frappe.utils.nowdate())
	day = end.strftime("%A")
	if day == "Monday":
		today = today - timedelta(days=2)
	else:
		today = today - timedelta(days=1)

	if not att_date:
		today = datetime.today().strftime('%Y-%m-%d')
	else:
		today = att_date

	if not end_date:
		end = datetime.today().strftime('%Y-%m-%d')
	else:
		end = end_date

	end = pd.to_datetime(end) + pd.DateOffset(days=1)
	end = end.strftime('%Y-%m-%d')

	while str(today) != str(end):
		if employee:
			doc = frappe.get_doc("Attendance Machine")
			if doc.machines:
				for d in doc.get("machines"):
					enqueue("erpnext.hr.doctype.attendance_machine.attendance_machine.generate_attendance", today=today, ip=d.ip.strip(), port=d.port, att_type=d.att_type, employee=employee, queue='long', timeout=1500)
					frappe.msgprint(_("Queued for biometric attendance. It may take a few minutes to an hour."))
					print("Queued for biometric attendance. It may take a few minutes to an hour.")
		elif ip:
			enqueue("erpnext.hr.doctype.attendance_machine.attendance_machine.generate_attendance", today=today, ip=ip.strip(), port=int(port), att_type=att_type, employee=employee, queue='long', timeout=1500)
			frappe.msgprint(_("Queued for biometric attendance. It may take a few minutes to an hour, You'll get notification if something went wrong."))
			print("Queued for biometric attendance. It may take a few minutes to an hour.")
		else:
			doc = frappe.get_doc("Attendance Machine")
			if doc.machines:
				for d in doc.get("machines"):
					enqueue("erpnext.hr.doctype.attendance_machine.attendance_machine.generate_attendance", today=today, ip=d.ip.strip(), port=d.port, att_type=d.att_type, queue='long', timeout=1500)
					frappe.msgprint(_("Queued for biometric attendance. It may take a few minutes to an hour."))
					print("Queued for biometric attendance. It may take a few minutes to an hour.")
		print(today)
		today = pd.to_datetime(today) + pd.DateOffset(days=1)
		today = today.strftime('%Y-%m-%d')

def generate_attendance(today,ip,port,att_type = "IN",employee=None):
	conn = None
	#zk = ZK(ip, port=port, timeout=5, password=0, force_udp=False, ommit_ping=False)
	try:
		#conn = zk.connect()
		conn.disable_device()
		attendance = conn.get_attendance()
		for a in attendance:
			a = str(a).split()
			biometric = str(a[1])
			date = a[3]
			time = a[4]
			date_time = date+" "+time
			if date == today:
				emp = frappe.db.get_value("Employee", {"status": "Active", "attendance_device_id": biometric}, "name")
				if emp:
					if employee:
						if emp == employee:
							# if datetime.strptime(str(time), "%H:%M:%S") >= datetime.strptime("00:00:01", "%H:%M:%S") and datetime.strptime(str(time), "%H:%M:%S") <= datetime.strptime("09:00:00", "%H:%M:%S"):
							# 	date = datetime.strptime(date, '%Y-%m-%d')
							# 	# date = date - timedelta(days=1)
							# 	shift = None
							# 	get_shift = frappe.db.sql("select shift from `tabEmployee Shift` where parent = %s and %s between start_date and end_date order by idx",(emp, date))
							# 	if get_shift:
							# 		shift = get_shift[0][0]
							# 	else:
							# 		shift = frappe.db.get_value("Employee", emp, "default_shift")
							# 	if shift:
							# 		if frappe.db.get_value("Shift Type", shift, "next"):
							# 			date_time = str(date).split(" ")[0]+" "+str(time)
							att = frappe.db.get_value("Employee Checkin", {"employee": emp, "time": date_time}, "name")
							if not att:
								new_att = frappe.new_doc("Employee Checkin")
								new_att.employee = emp
								new_att.time = date_time
								new_att.log_type = att_type
								new_att.insert(ignore_permissions=True)
					else:
						# if datetime.strptime(str(time), "%H:%M:%S") >= datetime.strptime("00:00:01", "%H:%M:%S") and datetime.strptime(str(time), "%H:%M:%S") <= datetime.strptime("09:00:00", "%H:%M:%S"):
						# 	date = datetime.strptime(date, '%Y-%m-%d')
						# 	# date = date - timedelta(days=1)
						# 	shift = None
						# 	get_shift = frappe.db.sql("select shift from `tabEmployee Shift` where parent = %s and %s between start_date and end_date order by idx",(emp, date))
						# 	if get_shift:
						# 		shift = get_shift[0][0]
						# 	else:
						# 		shift = frappe.db.get_value("Employee", emp, "default_shift")
						# 	if shift:
						# 		if frappe.db.get_value("Shift Type", shift, "next"):
						# 			date_time = str(date).split(" ")[0]+" "+str(time)
						att = frappe.db.get_value("Employee Checkin", {"employee": emp, "time": date_time}, "name")
						if not att:
							new_att = frappe.new_doc("Employee Checkin")
							new_att.employee = emp
							new_att.time = date_time
							new_att.log_type = att_type
							new_att.insert(ignore_permissions=True)
		conn.enable_device()
	except Exception as e:
	    print ("Process terminate : {}".format(e))
	    error_message = frappe.get_traceback()+"\n\n Machine Data (IP: {0}, Port : {1}): \n{2}".format(ip,port,str(e))
	    frappe.log_error(error_message, "Machine Error")
	finally:
	    if conn:
	        conn.disconnect()
def mark_absent_long():
	enqueue("erpnext.hr.doctype.attendance_machine.attendance_machine.mark_absent", queue='long', timeout=1500)

def mark_absent():
	emp = frappe.db.sql('select name from `tabEmployee` where status = "Active"')
	if emp:
		for d in emp:
			check = frappe.db.get_value("Attendance", {"employee": d[0], "attendance_date": frappe.utils.nowdate(), "docstatus": 1}, "name")
			if not check:
				try:
					doc = frappe.new_doc("Attendance")
					doc.employee = d[0]
					doc.attendance_date = frappe.utils.nowdate()
					doc.time_in = "00:00:00"
					doc.time_out = "00:00:00"
					doc.status = "Absent"
					doc.save()
					doc.submit()
				except Exception as e:
					frappe.log_error(str(e), "Mark Absent")

def mark_absent2(date=None):
	emp = frappe.db.sql('select name from `tabEmployee` where status = "Active"')
	if emp:
		for d in emp:
			check = frappe.db.get_value("Attendance", {"employee": d[0], "attendance_date": date, "docstatus": 1}, "name")
			if not check:
				try:
					doc = frappe.new_doc("Attendance")
					doc.employee = d[0]
					doc.attendance_date = date
					doc.time_in = "00:00:00"
					doc.time_out = "00:00:00"
					doc.status = "Absent"
					doc.save()
					doc.submit()
				except Exception as e:
					frappe.log_error(str(e), "Mark Absent")
