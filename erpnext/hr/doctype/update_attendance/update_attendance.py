# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue

class UpdateAttendance(Document):
	pass

	def on_submit(self):
		enqueue("erpnext.hr.doctype.update_attendance.update_attendance.update_attendance_que", start_date=self.start_date, end_date=self.end_date, employee=self.employee, queue='long', timeout=1500)

@frappe.whitelist()
def update_attendance_long(start_date,end_date,employee):
	enqueue("erpnext.hr.doctype.update_attendance.update_attendance.update_attendance_que", start_date=start_date, end_date=end_date, employee=employee, queue='long', timeout=1500)

def update_attendance_que(start_date,end_date,employee):
	data = frappe.db.sql("select name from `tabAttendance` where attendance_date between %s and %s and employee = %s",(start_date,end_date, employee), as_dict=1)
	for d in data:
		doc = frappe.get_doc("Attendance", d.name)
		doc.save()