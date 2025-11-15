import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    
    # Add totals row
    if data:
        data = add_totals_row(data)
    
    return columns, data

def get_columns():
    return [
        {"label": "Employee ID", "fieldname": "employee_id", "fieldtype": "Link", "options": "Employee", "width": 120},
        {"label": "Full Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
        {"label": "Payroll Period", "fieldname": "payroll_period", "fieldtype": "Data", "width": 120},
        {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 100},
        {"label": "Salary Component", "fieldname": "salary_component", "fieldtype": "Data", "width": 140},
        {"label": "Currency", "fieldname": "currency", "fieldtype": "Link", "options": "Currency", "width": 80},
        {"label": "Amount Employee", "fieldname": "amount_employee", "fieldtype": "Currency", "width": 130},
        {"label": "Total Amount", "fieldname": "total_amount", "fieldtype": "Currency", "width": 120},
        {"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 120},
        {"label": "Department", "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 120},
        {"label": "Designation", "fieldname": "designation", "fieldtype": "Link", "options": "Designation", "width": 120},
        {"label": "Employment Type", "fieldname": "employment_type", "fieldtype": "Data", "width": 120},
        {"label": "Remarks", "fieldname": "remarks", "fieldtype": "Small Text", "width": 200}
    ]

def get_data(filters):
    conditions = get_conditions(filters)
    
    # Query to get Zibawu records with all fields
    zibawu_entries = frappe.db.sql(
        """
        SELECT 
            employee_id,
            employee_name,
            payroll_period,
            date,
            salary_component,
            currency,
            amount_employee,
            total_amount,
            company,
            department,
            designation,
            employment_type,
            remarks
        FROM `tabZibawu`
        WHERE docstatus = 0 {conditions}
        ORDER BY date DESC, employee_id
        """.format(conditions=conditions),
        filters,
        as_dict=True
    )
    
    return zibawu_entries

def get_conditions(filters):
    conditions = ""
    
    if filters.get("company"):
        conditions += " AND company = %(company)s"
    if filters.get("employee_id"):
        conditions += " AND employee_id = %(employee_id)s"
    if filters.get("department"):
        conditions += " AND department = %(department)s"
    if filters.get("payroll_period"):
        conditions += " AND payroll_period = %(payroll_period)s"
    if filters.get("salary_component"):
        conditions += " AND salary_component = %(salary_component)s"
    if filters.get("from_date"):
        conditions += " AND date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " AND date <= %(to_date)s"
    if filters.get("employment_type"):
        conditions += " AND employment_type = %(employment_type)s"
    
    return conditions

def add_totals_row(data):
    """Add a totals row at the bottom with sums of amount fields"""
    total_amount_employee = 0
    total_total_amount = 0
    
    for row in data:
        total_amount_employee += flt(row.get('amount_employee', 0))
        total_total_amount += flt(row.get('total_amount', 0))
    
    # Add totals row
    totals_row = {
        "employee_id": "",
        "employee_name": "TOTAL",
        "payroll_period": "",
        "date": "",
        "salary_component": "",
        "currency": "",
        "amount_employee": total_amount_employee,
        "total_amount": total_total_amount,
        "company": "",
        "department": "",
        "designation": "",
        "employment_type": "",
        "remarks": "",
        "bold": 1
    }
    
    data.append(totals_row)
    return data