# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.hr.doctype.attendance_machine.attendance_machine import mark_absent2
from frappe.utils.background_jobs import enqueue
import pandas as pd
from datetime import date, datetime, timedelta

class MarkAbsent(Document):
	pass

	def on_submit(self):
		today = self.start_date
		end = pd.to_datetime(self.end_date) + pd.DateOffset(days=1)
		end = end.strftime('%Y-%m-%d')
		while str(today) != str(end):
			enqueue("erpnext.hr.doctype.attendance_machine.attendance_machine.mark_absent2", date=today, queue='long', timeout=1500)
			# enqueue("erpnext.hr.doctype.mark_absent.mark_absent.convert_holidays_to_absent", start_date=self.start_date, end_date=self.end_date, queue='long', timeout=1500)
			frappe.msgprint("Queued for marking attendance. It may take a few minutes to an hour.")
			print(today)
			today = pd.to_datetime(today) + pd.DateOffset(days=1)
			today = today.strftime('%Y-%m-%d')


def convert_holidays_to_absent(start_date,end_date):
	data = frappe.db.sql("select name,attendance_date,employee from `tabAttendance` where status = 'Holiday' and attendance_date between %s and %s",(start_date,end_date), as_dict=1)
	for d in data:
		date = frappe.utils.getdate(d.attendance_date)
		yesterday = date - timedelta(days=1)
		tomorrow = date + timedelta(days=1)
		check_yesterday = frappe.db.sql("""select status from `tabAttendance` where employee = %s and attendance_date = %s
				and status = 'Absent'
			""",(d.employee, yesterday))
		check_tomorrow = frappe.db.sql("""select status from `tabAttendance` where employee = %s and attendance_date = %s
				and status = 'Absent'
			""",(d.employee, tomorrow))
		if check_yesterday or check_tomorrow:
			doc = frappe.get_doc("Attendance", d.name)
			doc.override_holiday = 1
			doc.status = 'Absent'
			doc.save()