// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Summary of Salary Register"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "100",
			"default": frappe.datetime.month_start(),
			"reqd":1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "100",
			"default": frappe.datetime.month_end(),
			"reqd":1
		},
		{
			"fieldname":"group_by",
			"label": __("Group by"),
			"fieldtype": "Select",
			"width": "100",
			"options": ["Branch", "Department", "Employee"],
      		"default": "Branch",
			"reqd":1
		},
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Employee"
		},
		{
			"fieldname":"department",
			"label": __("Department"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Department",
			get_query: function() {
				return {
					filters: [
						["Department", "is_group", "=", 0]
					]
				}
			},
		},
		{
			"fieldname":"branch",
			"label": __("Branch"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Branch"
		},
		{
			"fieldname":"status",
			"label": __("Status"),
			"fieldtype": "Select",
			"width": "100",
			"options": "\nDraft\nSubmitted"
		},
	]
};
