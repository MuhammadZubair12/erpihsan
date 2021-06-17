// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Irregular Reports"] = {
	"filters": [
			{
				"fieldname": "department",
				"label": __("Department"),
				"fieldtype": "Link",
				"options": "Department",
			},

			{
				"fieldname": "employee",
				"label": __("Employee"),
				"fieldtype": "Link",
				"options": "Employee",
			},


			{
				"fieldname": "from_date",
				"label": __("From Date"),
				"fieldtype": "Date",
				"default": frappe.datetime.month_start()
			},

			{
				"fieldname": "to_date",
				"fieldtype": "Date",
				"label": __("To Date"),
				"default": frappe.datetime.month_end()
			},
	]
};
