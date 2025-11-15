import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}

    conditions = []
    values = {}

    if filters.get("salary_component"):
        conditions.append("salary_component LIKE %(salary_component)s")
        values["salary_component"] = f"%{filters['salary_component']}%"

    if filters.get("period"):
        conditions.append("period LIKE %(period)s")
        values["period"] = f"%{filters['period']}%"

    if filters.get("completed"):
        conditions.append("completed = %(completed)s")
        values["completed"] = filters["completed"]

    condition_sql = " AND ".join(conditions)
    if condition_sql:
        condition_sql = "WHERE " + condition_sql

    data = frappe.db.sql(f"""
        SELECT
            salary_component,
            period,
            total,
            completed
        FROM `tabSalary Summary On Payroll Run`
        {condition_sql}
        ORDER BY modified DESC
    """, values, as_dict=True)

    # Get company currency
    company_currency = frappe.db.get_single_value('Global Defaults', 'default_currency') or 'USD'

    # Calculate totals based on FILTERED data
    total_amount = 0
    formatted_data = []
    
    for row in data:
        # Calculate total from filtered data
        try:
            total_value = float(row.get('total') or 0)
            total_amount += total_value
        except (ValueError, TypeError):
            total_value = 0
        
        # Format the total with currency, commas and 2 decimal places
        row['total'] = f"{company_currency} {total_value:,.2f}"
        
        # Format completed status with better visual indicators
        
        formatted_data.append(row)

    # Add totals row that reflects FILTERED data
    if formatted_data:
        formatted_data.append({
            "salary_component": "━━━━━━━━━━━━━━━━",
            "period": "",
            "total": f"<b>{company_currency} {total_amount:,.2f}</b>",
            "completed": "",
            "indent": 0,
            "is_total_row": True
        })

    columns = [
        {
            "label": _("Salary Component"), 
            "fieldname": "salary_component", 
            "fieldtype": "Data", 
            "width": 320,
            "align": "left"
        },
        {
            "label": _("Payroll Period"), 
            "fieldname": "period", 
            "fieldtype": "Data", 
            "width": 280,
            "align": "center"
        },
        {
            "label": _("Total Amount"), 
            "fieldname": "total", 
            "fieldtype": "Data", 
            "width": 220,
            "align": "right"
        }
    ]

    return columns, formatted_data