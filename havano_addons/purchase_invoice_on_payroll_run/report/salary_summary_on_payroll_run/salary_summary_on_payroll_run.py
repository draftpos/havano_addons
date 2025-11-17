import frappe
from frappe import _
from frappe.utils import flt, nowdate

def execute(filters=None):
    try:
        if filters is None:
            filters = {}
            
        columns = get_columns()
        data = get_data(filters)
        chart = get_chart(data)
        report_summary = get_report_summary(data)
        
        return columns, data, None, chart, report_summary
    except Exception as e:
        frappe.log_error(f"Salary Summary Report Error: {str(e)}")
        return [], [], None, None, []

def get_columns():
    return [
        {
            "fieldname": "name",
            "label": _("ID"),
            "fieldtype": "Link",
            "options": "Salary Summary On Payroll Run",
            "width": 120
        },
        {
            "fieldname": "salary_component",
            "label": _("Salary Component"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "period",
            "label": _("Period"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "total",
            "label": _("Total Amount"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "completed",
            "label": _("Completed"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "creation",
            "label": _("Created On"),
            "fieldtype": "Date",
            "width": 120
        }
    ]

def get_data(filters):
    try:
        conditions = []
        params = {}
        
        if filters.get("salary_component"):
            conditions.append("salary_component LIKE %(salary_component)s")
            params["salary_component"] = f"%{filters['salary_component']}%"
        
        if filters.get("period"):
            conditions.append("period LIKE %(period)s")
            params["period"] = f"%{filters['period']}%"
        
        if filters.get("completed"):
            conditions.append("completed = %(completed)s")
            params["completed"] = filters["completed"]
        
        if filters.get("from_date"):
            conditions.append("DATE(creation) >= %(from_date)s")
            params["from_date"] = filters["from_date"]
        
        if filters.get("to_date"):
            conditions.append("DATE(creation) <= %(to_date)s")
            params["to_date"] = filters["to_date"]
        
        where_condition = ""
        if conditions:
            where_condition = " WHERE " + " AND ".join(conditions)
        
        query = f"""
            SELECT 
                name,
                salary_component,
                period,
                total,
                completed,
                DATE(creation) as creation
            FROM `tabSalary Summary On Payroll Run`
            {where_condition}
            ORDER BY creation DESC, salary_component
        """
        
        data = frappe.db.sql(query, params, as_dict=1)
        return data
        
    except Exception as e:
        frappe.log_error(f"Error in get_data: {str(e)}")
        return []

def get_chart(data):
    try:
        if not data:
            return None
            
        # Prepare data for chart - limit to top 10 components by total amount
        chart_data = sorted(data, key=lambda x: flt(x.get('total') or 0), reverse=True)[:10]
        
        components = [row.get('salary_component') or 'Unknown' for row in chart_data]
        totals = [flt(row.get('total') or 0) for row in chart_data]
        
        chart = {
            "data": {
                "labels": components,
                "datasets": [
                    {
                        "name": _("Total Amount"),
                        "values": totals
                    }
                ]
            },
            "type": "bar",
            "colors": ["#7CD6FD"],
            "height": 250,
            "axisOptions": {
                "xIsSeries": 0
            }
        }
        
        return chart
    except Exception as e:
        frappe.log_error(f"Error in get_chart: {str(e)}")
        return None

def get_report_summary(data):
    try:
        if not data:
            return []
        
        total_amount = sum(flt(row.get('total') or 0) for row in data)
        completed_count = sum(1 for row in data if row.get('completed') == 'yes')
        pending_count = sum(1 for row in data if row.get('completed') == 'no')
        total_records = len(data)
        
        return [
            {
                "value": total_records,
                "indicator": "Blue",
                "label": _("Total Records"),
                "datatype": "Int"
            },
            {
                "value": total_amount,
                "indicator": "Green",
                "label": _("Total Amount"),
                "datatype": "Currency"
            },
            {
                "value": completed_count,
                "indicator": "Green",
                "label": _("Completed"),
                "datatype": "Int"
            },
            {
                "value": pending_count,
                "indicator": "Red",
                "label": _("Pending"),
                "datatype": "Int"
            }
        ]
    except Exception as e:
        frappe.log_error(f"Error in get_report_summary: {str(e)}")
        return []