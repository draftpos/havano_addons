frappe.query_reports["Cimas Custom Report"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company")
        },
        {
            "fieldname": "employee_id",
            "label": __("Employee"),
            "fieldtype": "Link",
            "options": "Employee"
        },
        {
            "fieldname": "department",
            "label": __("Department"),
            "fieldtype": "Link",
            "options": "Department"
        },
        {
            "fieldname": "payroll_period",
            "label": __("Payroll Period"),
            "fieldtype": "Data"
        },
        {
            "fieldname": "salary_component",
            "label": __("Salary Component"),
            "fieldtype": "Data"
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date"
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date"
        },
        {
            "fieldname": "employment_type",
            "label": __("Employment Type"),
            "fieldtype": "Select",
            "options": "\nFull-time\nPart-time\nContract\nIntern"
        }
    ],

    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        // Make totals row bold
        if (data && data.bold) {
            value = value.replace('>', ' style="font-weight: bold;">');
        }
        
        return value;
    }
};