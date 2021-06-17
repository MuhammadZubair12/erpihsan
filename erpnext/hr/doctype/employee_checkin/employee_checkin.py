# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import now, cint, get_datetime
from frappe.model.document import Document
from frappe import _
from datetime import datetime, date, timedelta

from erpnext.hr.doctype.shift_assignment.shift_assignment import get_actual_start_end_datetime_of_shift

class EmployeeCheckin(Document):
	def validate(self):
		self.validate_duplicate_log()
		self.fetch_shift()
		self.add_attendance()

	def add_attendance(self):
		comp_date = str(self.time).split(" ")[0]
		emp_default = frappe.db.sql(""" select default_shift from `tabEmployee` where name = %s """, (self.employee))
		emp = frappe.db.sql(""" select shift, start_date, end_date from `tabEmployee Shift` where parent = %s """, (self.employee))
		if emp:
			flag = False
			for a in emp:
				s_date = str(a[1])
				e_date = str(a[2])
				if comp_date >= s_date and comp_date <= e_date:
					# frappe.msgprint('shift', a[0])
					if a[0]:
						flag = True
						next_day = frappe.db.sql(""" select next from `tabShift Type` where name = %s """, (a[0]))
						if next_day[0][0]:
							# frappe.msgprint("Evening Time With Table and Date Found")
							self.next_day_out()
						else:
							# frappe.msgprint("Morning Time With Table and Date Found")
							self.current_day_out()
					break
			if not flag:
				# frappe.msgprint('Default will be call')
				confirm_shift = frappe.db.sql(""" select next from `tabShift Type` where name = %s """, (emp_default[0][0]))
				if confirm_shift[0][0]:
					# frappe.msgprint('Evening Time With Table But Not Date Exists')
					self.next_day_out()
				else:
					# frappe.msgprint('Morining Time With Table But Not Date Exists')
					self.current_day_out()
		else:
			# frappe.msgprint('Default will call')
			confirm_shift_default = frappe.db.sql(""" select next from `tabShift Type` where name = %s """, (emp_default[0][0]))
			if confirm_shift_default[0][0]:
				# frappe.msgprint('Evening time')
				self.next_day_out()
			else:
				# frappe.msgprint('morning')
				self.current_day_out()

	def next_day_out(self):
		time1 = str(self.time).split(" ")[1]
		date_n32 = str(self.time).split(" ")[0]
		days = timedelta(1)
		date_time_obj = datetime.strptime(date_n32, '%Y-%m-%d')
		ab = date_time_obj - days
		a_time = '00:00:00'
		e_time = '00:59:59'
		start_time = '01:00:00'
		end_time = '09:00:00'
		# frappe.throw(frappe.as_json(ab))
		# if time1 >= start_time and time1 <= end_time:
		if time1 >=a_time and time1 <= e_time or time1 >= start_time and time1 <= end_time:
			new_date = str(ab).split(" ")[0]
			# frappe.throw(frappe.as_json(new_date))
			attend = frappe.db.get_value("Attendance", {"employee": self.employee, "attendance_date": new_date, "docstatus": ("!=", 2)}, "name")
			if not attend:
				n_att = frappe.new_doc("Attendance")
				n_att.employee = self.employee
				n_att.attendance_date = new_date
				if self.log_type == "OUT":
					n_att.time_in = "00:00:00"
					n_att.time_out = time1
				else:
					n_att.time_in = time1
					n_att.time_out = "00:00:00"
				n_att.insert(ignore_permissions=True)
				n_att.submit()
			else:
				attendance_doc = frappe.get_doc("Attendance", attend)
				if attendance_doc.time_in == "00:00:00" or attendance_doc.time_in == "0:00:00":
					attendance_doc.time_in = None
				if attendance_doc.time_out == "00:00:00" or attendance_doc.time_out == "0:00:00":
					attendance_doc.time_out = None
				if self.log_type == "OUT":
					if attendance_doc.time_out:
						diff = datetime.strptime(str(attendance_doc.time_out),"%H:%M:%S") - datetime.strptime(str(time1), "%H:%M:%S")
						diff = diff.total_seconds()
						if diff > 0:
							attendance_doc.time_out = time1
							attendance_doc.save(ignore_permissions=True)
					else:
						attendance_doc.time_out = time1
						attendance_doc.save(ignore_permissions=True)
				else:
					if attendance_doc.time_in:
						diff = datetime.strptime(str(attendance_doc.time_in),"%H:%M:%S") - datetime.strptime(str(time1), "%H:%M:%S")
						diff = diff.total_seconds()
						if diff > 0:
							# attendance_doc.time_in = time1
							attendance_doc.save(ignore_permissions=True)
					else:
						# attendance_doc.time_in = time1
						attendance_doc.save(ignore_permissions=True)
		s_time = '18:00:00'
		e_time = '24:00:00'
		date = str(self.time).split(" ")[0]
		if time1 >= s_time and time1 <= e_time:
			attend = frappe.db.get_value("Attendance", {"employee": self.employee, "attendance_date": date, "docstatus": ("!=", 2)}, "name")
			if not attend:
				n_att = frappe.new_doc("Attendance")
				n_att.employee = self.employee
				n_att.attendance_date = date
				if self.log_type == "OUT":
					n_att.time_in = "00:00:00"
					n_att.time_out = time1
				else:
					n_att.time_in = time1
					n_att.time_out = "00:00:00"
				n_att.insert(ignore_permissions=True)
				n_att.submit()
			else:
				attendance_doc = frappe.get_doc("Attendance", attend)
				if attendance_doc.time_in == "00:00:00" or attendance_doc.time_in == "0:00:00":
					attendance_doc.time_in = None
				if attendance_doc.time_out == "00:00:00" or attendance_doc.time_out == "0:00:00":
					attendance_doc.time_out = None
				if self.log_type == "OUT":
					if attendance_doc.time_out:
						diff = datetime.strptime(str(attendance_doc.time_out),"%H:%M:%S") - datetime.strptime(str(time1), "%H:%M:%S")
						diff = diff.total_seconds()
						if diff < 0 or diff > 0:
							attendance_doc.time_out = time1
							attendance_doc.save(ignore_permissions=True)
					else:
						attendance_doc.time_out = time1
						attendance_doc.save(ignore_permissions=True)
				else:
					if attendance_doc.time_in:
						diff = datetime.strptime(str(attendance_doc.time_in),"%H:%M:%S") - datetime.strptime(str(time1), "%H:%M:%S")
						diff = diff.total_seconds()
						if diff > 0:
							# attendance_doc.time_in = time1
							attendance_doc.save(ignore_permissions=True)
					else:
						# attendance_doc.time_in = time1
						attendance_doc.save(ignore_permissions=True)
	def current_day_out(self):
		self.date_only = str(self.time).split(" ")[0]
		self.time_only = str(self.time).split(" ")[1]
		date = str(self.time).split(" ")[0]
		time = str(self.time).split(" ")[1]
		# frappe.msgprint(frappe.as_json(time))
		att = frappe.db.get_value("Attendance", {"employee": self.employee, "attendance_date": date, "docstatus": ("!=", 2)}, "name")
		# frappe.msgprint(frappe.as_json(att))
		if not att:
			# frappe.msgprint(frappe.as_json(att))
			new_att = frappe.new_doc("Attendance")
			new_att.employee = self.employee
			new_att.attendance_date = date
			if self.log_type == "OUT":
				new_att.time_in = "00:00:00"
				new_att.time_out = time
			else:
				new_att.time_in = time
				new_att.time_out = "00:00:00"
			new_att.insert(ignore_permissions=True)
			new_att.submit()
		else:
			attendance_doc = frappe.get_doc("Attendance", att)
			if attendance_doc.time_in == "00:00:00" or attendance_doc.time_in == "0:00:00":
				attendance_doc.time_in = None
			if attendance_doc.time_out == "00:00:00" or attendance_doc.time_out == "0:00:00":
				attendance_doc.time_out = None
			if self.log_type == "OUT":
				if attendance_doc.time_out:
					diff = datetime.strptime(str(attendance_doc.time_out), "%H:%M:%S") - datetime.strptime(str(time), "%H:%M:%S")
					diff = diff.total_seconds()
		
					if diff < 0:
						attendance_doc.time_out = time
						attendance_doc.save(ignore_permissions=True)
				else:
					attendance_doc.time_out = time
					attendance_doc.save(ignore_permissions=True)
			else:
				if attendance_doc.time_in:
					diff = datetime.strptime(str(attendance_doc.time_in), "%H:%M:%S") - datetime.strptime(str(time), "%H:%M:%S")
					diff = diff.total_seconds()
		
					if diff > 0:
						attendance_doc.time_in = time
						attendance_doc.save(ignore_permissions=True)
				else:
					attendance_doc.time_in = time
					attendance_doc.save(ignore_permissions=True)

	def validate_duplicate_log(self):
		doc = frappe.db.exists('Employee Checkin', {
			'employee': self.employee,
			'time': self.time,
			'name': ['!=', self.name]})
		if doc:
			doc_link = frappe.get_desk_link('Employee Checkin', doc)
			frappe.throw(_('This employee already has a log with the same timestamp.{0}')
				.format("<Br>" + doc_link))

	def fetch_shift(self):
		shift_actual_timings = get_actual_start_end_datetime_of_shift(self.employee, get_datetime(self.time), True)
		if shift_actual_timings[0] and shift_actual_timings[1]:
			if shift_actual_timings[2].shift_type.determine_check_in_and_check_out == 'Strictly based on Log Type in Employee Checkin' and not self.log_type and not self.skip_auto_attendance:
				frappe.throw(_('Log Type is required for check-ins falling in the shift: {0}.').format(shift_actual_timings[2].shift_type.name))
			if not self.attendance:
				self.shift = shift_actual_timings[2].shift_type.name
				self.shift_actual_start = shift_actual_timings[0]
				self.shift_actual_end = shift_actual_timings[1]
				self.shift_start = shift_actual_timings[2].start_datetime
				self.shift_end = shift_actual_timings[2].end_datetime
		else:
			self.shift = None

@frappe.whitelist()
def add_log_based_on_employee_field(employee_field_value, timestamp, device_id=None, log_type=None, skip_auto_attendance=0, employee_fieldname='attendance_device_id'):
	"""Finds the relevant Employee using the employee field value and creates a Employee Checkin.

	:param employee_field_value: The value to look for in employee field.
	:param timestamp: The timestamp of the Log. Currently expected in the following format as string: '2019-05-08 10:48:08.000000'
	:param device_id: (optional)Location / Device ID. A short string is expected.
	:param log_type: (optional)Direction of the Punch if available (IN/OUT).
	:param skip_auto_attendance: (optional)Skip auto attendance field will be set for this log(0/1).
	:param employee_fieldname: (Default: attendance_device_id)Name of the field in Employee DocType based on which employee lookup will happen.
	"""

	if not employee_field_value or not timestamp:
		frappe.throw(_("'employee_field_value' and 'timestamp' are required."))

	employee = frappe.db.get_values("Employee", {employee_fieldname: employee_field_value}, ["name", "employee_name", employee_fieldname], as_dict=True)
	if employee:
		employee = employee[0]
	else:
		frappe.throw(_("No Employee found for the given employee field value. '{}': {}").format(employee_fieldname,employee_field_value))

	doc = frappe.new_doc("Employee Checkin")
	doc.employee = employee.name
	doc.employee_name = employee.employee_name
	doc.time = timestamp
	doc.device_id = device_id
	doc.log_type = log_type
	if cint(skip_auto_attendance) == 1: doc.skip_auto_attendance = '1'
	doc.insert()

	return doc


def mark_attendance_and_link_log(logs, attendance_status, attendance_date, working_hours=None, late_entry=False, early_exit=False, shift=None):
	"""Creates an attendance and links the attendance to the Employee Checkin.
	Note: If attendance is already present for the given date, the logs are marked as skipped and no exception is thrown.

	:param logs: The List of 'Employee Checkin'.
	:param attendance_status: Attendance status to be marked. One of: (Present, Absent, Half Day, Skip). Note: 'On Leave' is not supported by this function.
	:param attendance_date: Date of the attendance to be created.
	:param working_hours: (optional)Number of working hours for the given date.
	"""
	log_names = [x.name for x in logs]
	employee = logs[0].employee
	if attendance_status == 'Skip':
		frappe.db.sql("""update `tabEmployee Checkin`
			set skip_auto_attendance = %s
			where name in %s""", ('1', log_names))
		return None
	elif attendance_status in ('Present', 'Absent', 'Half Day'):
		employee_doc = frappe.get_doc('Employee', employee)
		if not frappe.db.exists('Attendance', {'employee':employee, 'attendance_date':attendance_date, 'docstatus':('!=', '2')}):
			doc_dict = {
				'doctype': 'Attendance',
				'employee': employee,
				'attendance_date': attendance_date,
				'status': attendance_status,
				'working_hours': working_hours,
				'company': employee_doc.company,
				'shift': shift,
				'late_entry': late_entry,
				'early_exit': early_exit
			}
			attendance = frappe.get_doc(doc_dict).insert()
			attendance.submit()
			frappe.db.sql("""update `tabEmployee Checkin`
				set attendance = %s
				where name in %s""", (attendance.name, log_names))
			return attendance
		else:
			frappe.db.sql("""update `tabEmployee Checkin`
				set skip_auto_attendance = %s
				where name in %s""", ('1', log_names))
			return None
	else:
		frappe.throw(_('{} is an invalid Attendance Status.').format(attendance_status))


def calculate_working_hours(logs, check_in_out_type, working_hours_calc_type):
	"""Given a set of logs in chronological order calculates the total working hours based on the parameters.
	Zero is returned for all invalid cases.
	
	:param logs: The List of 'Employee Checkin'.
	:param check_in_out_type: One of: 'Alternating entries as IN and OUT during the same shift', 'Strictly based on Log Type in Employee Checkin'
	:param working_hours_calc_type: One of: 'First Check-in and Last Check-out', 'Every Valid Check-in and Check-out'
	"""
	total_hours = 0
	in_time = out_time = None
	if check_in_out_type == 'Alternating entries as IN and OUT during the same shift':
		in_time = logs[0].time
		if len(logs) >= 2:
			out_time = logs[-1].time
		if working_hours_calc_type == 'First Check-in and Last Check-out':
			# assumption in this case: First log always taken as IN, Last log always taken as OUT
			total_hours = time_diff_in_hours(in_time, logs[-1].time)
		elif working_hours_calc_type == 'Every Valid Check-in and Check-out':
			logs = logs[:]
			while len(logs) >= 2:
				total_hours += time_diff_in_hours(logs[0].time, logs[1].time)
				del logs[:2]

	elif check_in_out_type == 'Strictly based on Log Type in Employee Checkin':
		if working_hours_calc_type == 'First Check-in and Last Check-out':
			first_in_log_index = find_index_in_dict(logs, 'log_type', 'IN')
			first_in_log = logs[first_in_log_index] if first_in_log_index or first_in_log_index == 0 else None
			last_out_log_index = find_index_in_dict(reversed(logs), 'log_type', 'OUT')
			last_out_log = logs[len(logs)-1-last_out_log_index] if last_out_log_index or last_out_log_index == 0 else None
			if first_in_log and last_out_log:
				in_time, out_time = first_in_log.time, last_out_log.time
				total_hours = time_diff_in_hours(in_time, out_time)
		elif working_hours_calc_type == 'Every Valid Check-in and Check-out':
			in_log = out_log = None
			for log in logs:
				if in_log and out_log:
					if not in_time:
						in_time = in_log.time
					out_time = out_log.time
					total_hours += time_diff_in_hours(in_log.time, out_log.time)
					in_log = out_log = None
				if not in_log:
					in_log = log if log.log_type == 'IN'  else None
				elif not out_log:
					out_log = log if log.log_type == 'OUT'  else None
			if in_log and out_log:
				out_time = out_log.time
				total_hours += time_diff_in_hours(in_log.time, out_log.time)
	return total_hours, in_time, out_time

def time_diff_in_hours(start, end):
	return round((end-start).total_seconds() / 3600, 1)

def find_index_in_dict(dict_list, key, value):
	return next((index for (index, d) in enumerate(dict_list) if d[key] == value), None)
