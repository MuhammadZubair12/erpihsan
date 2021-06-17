import frappe

def update_it():
	count=0
	data = frappe.db.sql("select name from tabAttendance")
	for d in data:
		doc = frappe.get_doc("Attendance", d[0])
		doc.save()
		count+=1
		print(count)
