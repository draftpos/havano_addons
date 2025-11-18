import frappe
import json
import random
import string
from frappe.utils import flt
from frappe import _  # For frappe.throw

# user_stock_report --------------------------------------------------------------
""" Return stock report for user based on the company that they belong to 
filter dates example 
{
  "from_date": "2025-01-01",
  "to_date": "2025-01-31",
  "company" : company
}


Exmaple

GET http://localhost:8000/api/method/havano_addons.www.api.user_stock_report?company=Showline

or 
http://localhost:8000/api/method/havano_addons.www.api.user_stock_report?company=Showline&from_date=2025-01-01&to_date=2025-12-31

with filters

Response

{
    "message": {
        "company": "Showline",
        "columns": [
            {
                "label": "Warehouse",
                "fieldname": "warehouse",
                "fieldtype": "Link",
                "options": "Warehouse",
                "width": 250
            },
            {
                "label": "Value At Selling",
                "fieldname": "selling_value",
                "fieldtype": "Currency",
                "width": 250
            },
            {
                "label": "Value At Cost",
                "fieldname": "cost_value",
                "fieldtype": "Currency",
                "width": 250
            },
            {
                "label": "Expected Profit",
                "fieldname": "expected_profit",
                "fieldtype": "Currency",
                "width": 250
            },
            {
                "label": "Company",
                "fieldname": "company",
                "fieldtype": "Link",
                "options": "Company",
                "width": 250
            }
        ],
        "data": [
            {
                "warehouse": "Stores - SHL",
                "selling_value": 30.0,
                "cost_value": 20.0,
                "expected_profit": 10.0,
                "company": "Showline"
            },
            {
                "warehouse": "Stores - SHL",
                "selling_value": 40.0,
                "cost_value": 30.0,
                "expected_profit": 10.0,
                "company": "Showline"
            },
            {
                "warehouse": "Stores - SHL",
                "selling_value": 30.0,
                "cost_value": 15.0,
                "expected_profit": 15.0,
                "company": "Showline"
            },
            {
                "warehouse": "Stores - SHL",
                "selling_value": 220.0,
                "cost_value": 200.0,
                "expected_profit": 20.0,
                "company": "Showline"
            },
            {
                "warehouse": "Stores - SHL",
                "selling_value": 30.0,
                "cost_value": 20.0,
                "expected_profit": 10.0,
                "company": "Showline"
            },
            {
                "warehouse": "Test - SHL",
                "selling_value": 60.0,
                "cost_value": 60.0,
                "expected_profit": 0.0,
                "company": "Showline"
            },
            {
                "warehouse": "Stores - SHL",
                "selling_value": 20.0,
                "cost_value": 10.0,
                "expected_profit": 10.0,
                "company": "Showline"
            },
            {
                "warehouse": "Total",
                "selling_value": 430.0,
                "cost_value": 355.0,
                "expected_profit": 75.0,
                "company": "",
                "bold": 1
            }
        ]
    }
}

"""


@frappe.whitelist(allow_guest=True)
def user_stock_report(company=None, from_date = None, to_date=None ):
    """
    Returns stock report for the given user - automatically determines company from user
    """
    if not company:
        frappe.throw("company is required")

    
    company = frappe.db.get_value("Company", company, "name")
    filters = {
    "from_date": from_date,
    "to_date": to_date,
    "company": company
    }


    

    # Get stock data for the company
    columns = get_columns()
    data = get_data(filters, company)
    
    if data:
        data = add_totals_row(data)

    return {
        "company": company,
        "columns": columns, 
        "data": data
    }

def find_employee_by_email(email):
    """
    Try multiple ways to find employee by email
    """
    # Method 1: Check user_id field (system user)
    employee = frappe.db.get_value("User", {"user_id": email}, ["name", "company", "user_id"], as_dict=True)
    if employee:
        return employee
    
    # Method 2: Check personal_email field
    employee = frappe.db.get_value("User", {"personal_email": email}, ["name", "company", "user_id"], as_dict=True)
    if employee:
        return employee
    
    # Method 3: Check company_email field
    employee = frappe.db.get_value("User", {"company_email": email}, ["name", "company", "user_id"], as_dict=True)
    if employee:
        return employee
    
    # Method 4: Check preferred_email field
    # employee = frappe.db.get_value("havano_employee", {"preferred_email": email}, ["name", "company", "user_id"], as_dict=True)
    # if employee:
    #     return employee
    
    return None

def get_columns():
    return [
        {"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 250},
        {"label": "Value At Selling", "fieldname": "selling_value", "fieldtype": "Currency", "width": 250},
        {"label": "Value At Cost", "fieldname": "cost_value", "fieldtype": "Currency", "width": 250},
        {"label": "Expected Profit", "fieldname": "expected_profit", "fieldtype": "Currency", "width": 250},
        {"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 250}
    ]


def get_data(filters, company):
    # Filter stock ledger entries by company via warehouse
    conditions = ""
    values = {"company": company}

    # Apply from_date only if provided
    if filters.get("from_date"):
        conditions += " AND sle.posting_date >= %(from_date)s"
        values["from_date"] = filters["from_date"]

    # Apply to_date only if provided
    if filters.get("to_date"):
        conditions += " AND sle.posting_date <= %(to_date)s"
        values["to_date"] = filters["to_date"]

    query = f"""
        SELECT
            sle.item_code,
            sle.warehouse,
            SUM(sle.actual_qty) AS qty
        FROM `tabStock Ledger Entry` sle
        WHERE sle.docstatus < 2
          AND sle.is_cancelled = 0
          AND sle.warehouse IN (
              SELECT name FROM `tabWarehouse` WHERE company = %(company)s
          )
          {conditions}
        GROUP BY sle.item_code, sle.warehouse
        HAVING SUM(sle.actual_qty) != 0
    """


    sle_entries = frappe.db.sql(query, values, as_dict=True)

    data = []

    for row in sle_entries:
        # Latest valuation rate
        val_rate = frappe.db.get_value(
            "Stock Ledger Entry",
            {"item_code": row.item_code, "warehouse": row.warehouse, "is_cancelled": 0},
            "valuation_rate",
            order_by="posting_date desc, posting_time desc, creation desc"
        ) or 0

        # Selling rate
        selling_rate = frappe.db.get_value(
            "Item Price",
            {
                "item_code": row.item_code,
                "selling": 1,
                "price_list": frappe.db.get_single_value("Selling Settings", "selling_price_list")
            },
            "price_list_rate"
        ) or frappe.db.get_value("Item", row.item_code, "standard_rate") or 0

        data.append({
            "warehouse": row.warehouse,
            "selling_value": flt(row.qty) * flt(selling_rate),
            "cost_value": flt(row.qty) * flt(val_rate),
            "expected_profit": flt(row.qty) * flt(selling_rate) - flt(row.qty) * flt(val_rate),
            "company": company
        })

    return data



def add_totals_row(data):
    total_selling_value = sum(flt(row.get("selling_value", 0)) for row in data)
    total_cost_value = sum(flt(row.get("cost_value", 0)) for row in data)

    totals_row = {
        "warehouse": _("Total"),
        "selling_value": total_selling_value,
        "cost_value": total_cost_value,
        "expected_profit": total_selling_value - total_cost_value,
        "company": "",
        "bold": 1
    }

    data.append(totals_row)
    return data