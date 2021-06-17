# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime, date, timedelta

class Overtime(Document):
	pass

	def validate(self):
		diff = 0
		durr = 0
		total_seconds = 0
		total_mins = 0
		total_mins_for_half_day = 0
		diff = datetime.strptime(str(self.end_time), "%H:%M:%S") - datetime.strptime(str(self.start_time), "%H:%M:%S")
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
		time = str(self.total_time).split(":")
		delta = timedelta(hours=int(time[0]), minutes=int(time[1]), seconds=int(time[2]))
		self.total_secs = delta.total_seconds()