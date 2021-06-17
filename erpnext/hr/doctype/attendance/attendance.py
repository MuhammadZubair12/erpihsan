# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from frappe.utils import getdate, nowdate
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr
from datetime import datetime, date, timedelta

class Attendance(Document):
	def validate_duplicate_record(self):
		res = frappe.db.sql("""select name from `tabAttendance` where employee = %s and attendance_date = %s
			and name != %s and docstatus != 2""",
			(self.employee, getdate(self.attendance_date), self.name))
		if res:
			frappe.throw(_("Attendance for employee {0} is already marked").format(self.employee))

	def check_leave_record(self):
		leave_record = frappe.db.sql("""select leave_type, half_day, half_day_date from `tabLeave Application`
			where employee = %s and %s between from_date and to_date and status = 'Approved'
			and docstatus = 1""", (self.employee, self.attendance_date), as_dict=True)
		if leave_record:
			for d in leave_record:
				if d.half_day_date == getdate(self.attendance_date):
					self.status = 'Half Day'
					frappe.msgprint(_("Employee {0} on Half day on {1}").format(self.employee, self.attendance_date))
				else:
					self.status = 'On Leave'
					self.leave_type = d.leave_type
					frappe.msgprint(_("Employee {0} is on Leave on {1}").format(self.employee, self.attendance_date))

		if self.status == "On Leave" and not leave_record:
			frappe.throw(_("No leave record found for employee {0} for {1}").format(self.employee, self.attendance_date))

	def validate_attendance_date(self):
		date_of_joining = frappe.db.get_value("Employee", self.employee, "date_of_joining")

		# leaves can be marked for future dates
		if self.status != 'On Leave' and not self.leave_application and getdate(self.attendance_date) > getdate(nowdate()):
			frappe.throw(_("Attendance can not be marked for future dates"))
		elif date_of_joining and getdate(self.attendance_date) < getdate(date_of_joining):
			frappe.throw(_("Attendance date can not be less than employee's joining date"))

	def validate_employee(self):
		emp = frappe.db.sql("select name from `tabEmployee` where name = %s and status = 'Active'",
		 	self.employee)
		if not emp:
			frappe.throw(_("Employee {0} is not active or does not exist").format(self.employee))

	def validate(self):
		from erpnext.controllers.status_updater import validate_status
		validate_status(self.status, ["Present", "Absent", "On Leave", "Half Day", "Holiday"])
		self.validate_attendance_date()
		self.validate_duplicate_record()
		self.check_leave_record()
		self.calculate_time()

	def before_update_after_submit(self):
		self.calculate_time()

	def calculate_time(self):
		self.late_entry = 0
		self.early_exit = 0
		self.over_time = 0
		self.early_exit_time = None
		self.late_entry_time = None
		self.overtime_time = None
		self.early_exit_mins = 0
		self.late_entry_mins = 0
		self.overtime_mins = 0
		self.total_time = "00:00:00"
		if self.status == "Present": self.status = "Absent"
		shift = None
		if not self.override_shift:
			get_shift = frappe.db.sql("select shift from `tabEmployee Shift` where parent = %s and %s between start_date and end_date order by idx",(self.employee, self.attendance_date))
			if get_shift:
				shift = get_shift[0][0]
			else:
				shift = frappe.db.get_value("Employee", self.employee, "default_shift")
			self.shift = shift
		if not self.shift: frappe.throw("Please select shift in employee master of employee {}".format(str(self.employee)))
		s = frappe.get_doc("Shift Type", self.shift)
		holiday_list = frappe.db.get_value("Employee", self.employee, "holiday_list")
		if not holiday_list:
			holiday_list = s.holiday_list
		self.holiday_list = holiday_list
		if self.get_holiday() and not self.override_holiday:
			self.status = "Holiday"
		start_time = s.start_time
		end_time = s.end_time
		actual_start_time = s.actual_start_time
		over_time_allowed = s.pre_approved_overtime
		if self.time_in and self.time_out and self.time_out != "00:00:00" and self.time_in != "00:00:00" and self.time_in != "0:00:00" and self.time_out != "0:00:00":
			if self.status == "Absent": self.status = "Present"
			diff = 0
			durr = 0
			total_seconds = 0
			total_mins = 0
			total_mins_for_half_day = 0
			# time_in = frappe.utils.data.get_datetime(self.time_in)
			# time_out = frappe.utils.data.get_datetime(self.time_out)
			if "." in str(self.time_in): self.time_in = str(self.time_in).split(".")[0]
			if "." in str(self.time_out): self.time_out = str(self.time_out).split(".")[0]
			diff = datetime.strptime(str(self.time_out), "%H:%M:%S") - datetime.strptime(str(self.time_in), "%H:%M:%S")
			if diff.days < 0:
				diff = timedelta(days=0, seconds=diff.seconds, microseconds=diff.microseconds)
			durr += diff.total_seconds()
			totals = durr / 60
			total_mins = int(totals)
			total_mins_for_half_day = total_mins
			mins_secs = total_mins * 60
			total_secs = int(durr - mins_secs)
			total_hours = 0
			while total_mins >= 60:
				total_hours += 1
				total_mins -= 60
			self.total_time = str(total_hours).zfill(2)+":"+str(total_mins).zfill(2)+":"+str(total_secs).zfill(2)
			if self.status != "Holiday":
				if datetime.strptime(str(self.time_out), "%H:%M:%S") < datetime.strptime(str(end_time), "%H:%M:%S"):
					self.early_exit = 1
					p = datetime.strptime(str(end_time), "%H:%M:%S").time()
					m = datetime.strptime(str(self.time_out), "%H:%M:%S").time()
					self.early_exit_time = datetime.combine(date.today(), p) - datetime.combine(date.today(), m)
					self.early_exit_mins = get_mins(self.early_exit_time)
					if self.status == "Absent": self.status = "Present"
				elif datetime.strptime(str(self.time_out), "%H:%M:%S") > datetime.strptime(str(end_time), "%H:%M:%S"):
					timeout = self.time_out
					if datetime.strptime(str(self.time_out), "%H:%M:%S") > datetime.strptime(str(over_time_allowed), "%H:%M:%S"):
						timeout = over_time_allowed
					p = datetime.strptime(str(end_time), "%H:%M:%S").time()
					m = datetime.strptime(str(timeout), "%H:%M:%S").time()
					self.overtime_time = datetime.combine(date.today(), m) - datetime.combine(date.today(), p)
					converted_ot = datetime.strptime(str(self.overtime_time), "%H:%M:%S")
					if converted_ot >= datetime.strptime("04:00:00", "%H:%M:%S"):
						self.overtime_time = "04:00:00"
					elif converted_ot >= datetime.strptime("03:00:00", "%H:%M:%S") and converted_ot <= datetime.strptime("03:59:59", "%H:%M:%S"):
						self.overtime_time = "03:00:00"
					elif converted_ot >= datetime.strptime("02:00:00", "%H:%M:%S") and converted_ot <= datetime.strptime("02:59:59", "%H:%M:%S"):
						self.overtime_time = "02:00:00"
					elif converted_ot >= datetime.strptime("01:00:00", "%H:%M:%S") and converted_ot <= datetime.strptime("01:59:59", "%H:%M:%S"):
						self.overtime_time = "01:00:00"
					elif converted_ot >= datetime.strptime("00:00:00", "%H:%M:%S") and converted_ot <= datetime.strptime("00:59:59", "%H:%M:%S"):
						self.overtime_time = None
					if self.overtime_time:
						self.over_time = 1
						self.overtime_mins = get_mins(self.overtime_time)
						if self.status == "Absent": self.status = "Present"
					else:
						self.over_time = 0
						self.overtime_mins = 0
				if datetime.strptime(str(self.time_in), "%H:%M:%S") > datetime.strptime(str(actual_start_time), "%H:%M:%S"):
					self.late_entry = 1
					p = datetime.strptime(str(self.time_in), "%H:%M:%S").time()
					m = datetime.strptime(str(start_time), "%H:%M:%S").time()
					self.late_entry_time = datetime.combine(date.today(), p) - datetime.combine(date.today(), m)
					self.late_entry_mins = get_mins(self.late_entry_time)
					# frappe.throw(str(self.late_entry_mins))
					if self.status == "Absent": self.status = "Present"
		else:
			self.total_time = "00:00:00"

	def get_holiday(self):
		if self.holiday_list:
			holiday_list = frappe.get_doc("Holiday List", self.holiday_list)
			holiday_dates = dict((str(h.holiday_date), h) for h in holiday_list.get("holidays"))
			if str(self.attendance_date) in holiday_dates.keys():
				return 1
			else:
				return 0

@frappe.whitelist()
def check():
	diff = datetime.strptime(str("10:05:00"), "%H:%M:%S") - datetime.strptime(str("05:05:00"), "%H:%M:%S")
	durr = diff.total_seconds()
	# p = datetime.strptime(str("23:01:00"), "%H:%M:%S").time()
	# m = datetime.strptime(str("00:01:00"), "%H:%M:%S").time()
	# res = datetime.combine(date.today(), p) - datetime.combine(date.today(), m)
	# print(res)
	import math
	total_hours = math.floor(durr / 1000 / 60 / 60)
	durr -= total_hours*1000*60*60
	total_mins = math.floor(durr / 1000 / 60)
	durr -= total_mins*1000*60
	total_secs = math.floor(durr / 1000)
	print(str(total_hours)+":"+str(total_mins)+":"+str(total_secs))

@frappe.whitelist()
def get_events(start, end, filters=None):
	events = []

	employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user})

	if not employee:
		return events

	from frappe.desk.reportview import get_filters_cond
	conditions = get_filters_cond("Attendance", filters, [])
	add_attendance(events, start, end, conditions=conditions)
	return events

def add_attendance(events, start, end, conditions=None):
	query = """select name, attendance_date, status
		from `tabAttendance` where
		attendance_date between %(from_date)s and %(to_date)s
		and docstatus < 2"""
	if conditions:
		query += conditions

	for d in frappe.db.sql(query, {"from_date":start, "to_date":end}, as_dict=True):
		e = {
			"name": d.name,
			"doctype": "Attendance",
			"date": d.attendance_date,
			"title": cstr(d.status),
			"docstatus": d.docstatus
		}
		if e not in events:
			events.append(e)

def mark_absent(employee, attendance_date, shift=None):
	employee_doc = frappe.get_doc('Employee', employee)
	if not frappe.db.exists('Attendance', {'employee':employee, 'attendance_date':attendance_date, 'docstatus':('!=', '2')}):
		doc_dict = {
			'doctype': 'Attendance',
			'employee': employee,
			'attendance_date': attendance_date,
			'status': 'Absent',
			'company': employee_doc.company,
			'shift': shift
		}
		attendance = frappe.get_doc(doc_dict).insert()
		attendance.submit()
		return attendance.name

def get_mins(time):
	time = str(time).split(":")
	delta = timedelta(hours=int(time[0]), minutes=int(time[1]), seconds=int(time[2]))
	total_seconds = delta.total_seconds()
	# minutes = int(total_seconds // 60)
	# seconds = int(total_seconds % 60)
	return total_seconds

def update_it():
	data = frappe.db.sql("select name from `tabAttendance`")
	count=0
	for d in data:
		doc = frappe.get_doc("Attendance", d[0])
		doc.save()
		count+=1
		print(count)