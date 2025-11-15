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
        {"label": "Item", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 180},
        {"label": "Item Group", "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 120},
        {"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 160},
        {"label": "Stock UOM", "fieldname": "stock_uom", "fieldtype": "Data", "width": 90},
        {"label": "Balance Qty", "fieldname": "qty", "fieldtype": "Float", "width": 110},
        {"label": "Standard Selling Rate", "fieldname": "selling_rate", "fieldtype": "Currency", "width": 130},
        {"label": "Selling Value", "fieldname": "selling_value", "fieldtype": "Currency", "width": 120},
        {"label": "Valuation Rate", "fieldname": "valuation_rate", "fieldtype": "Currency", "width": 120},
        {"label": "Cost Value", "fieldname": "cost_value", "fieldtype": "Currency", "width": 120},
        {"label": "Expected Profit", "fieldname": "expected_profit", "fieldtype": "Currency", "width": 120},
        {"label": "Simple Code", "fieldname": "simple_code", "fieldtype": "Data", "width": 100},
        {"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 120}
    ]


def get_data(filters):
    conditions = ""
    if filters.get("company"):
        conditions += " AND sle.company = %(company)s"
    if filters.get("item_code"):
        conditions += " AND sle.item_code = %(item_code)s"
    if filters.get("warehouse"):
        conditions += " AND sle.warehouse = %(warehouse)s"
    if filters.get("item_group"):
        conditions += " AND it.item_group = %(item_group)s"

    # Aggregate the stock ledger with proper joins
    sle_entries = frappe.db.sql(
        """
        SELECT
            sle.item_code,
            sle.warehouse,
            sle.company,
            sle.stock_uom,
            SUM(sle.actual_qty) AS qty,
            SUM(sle.stock_value_difference) AS value_diff
        FROM `tabStock Ledger Entry` sle
        LEFT JOIN `tabItem` it ON sle.item_code = it.name
        WHERE sle.docstatus < 2 AND sle.is_cancelled = 0 {conditions}
        GROUP BY sle.item_code, sle.warehouse, sle.company
        HAVING SUM(sle.actual_qty) != 0
        """.format(conditions=conditions),
        filters,
        as_dict=True
    )
    
    data = []
    
    for row in sle_entries:
        # Get item details
        item_details = frappe.db.get_value(
            "Item", 
            row.item_code, 
            ["item_name", "item_group", "stock_uom", "custom_simple_code", "standard_rate"], 
            as_dict=True
        )
        
        if not item_details:
            continue
            
        # Get valuation rate from last SLE
        val_rate = frappe.db.get_value(
            "Stock Ledger Entry",
            {
                "item_code": row.item_code, 
                "warehouse": row.warehouse,
                "is_cancelled": 0
            },
            "valuation_rate",
            order_by="posting_date desc, posting_time desc, creation desc"
        ) or 0
        
        # Get standard selling rate from Item Price or fallback to item standard_rate
        selling_rate = frappe.db.get_value(
            "Item Price",
            {
                "item_code": row.item_code, 
                "selling": 1,
                "price_list": frappe.db.get_single_value("Selling Settings", "selling_price_list")
            },
            "price_list_rate"
        ) or item_details.standard_rate or 0
        
        # Calculate values
        cost_value = flt(row.qty) * flt(val_rate)
        selling_value = flt(row.qty) * flt(selling_rate)
        expected_profit = selling_value - cost_value        

        data.append({
            "item_code": row.item_code,
            "item_name": item_details.item_name,
            "item_group": item_details.item_group,
            "warehouse": row.warehouse,
            "stock_uom": row.stock_uom or item_details.stock_uom,
            "qty": row.qty,
            "selling_rate": selling_rate,
            "selling_value": selling_value,
            "valuation_rate": val_rate,
            "cost_value": cost_value,
            "expected_profit": expected_profit,
            "simple_code": item_details.custom_simple_code or "",
            "company": row.company
        })

    return data


def add_totals_row(data):
    """Add a totals row at the bottom with sums of quantity and values"""
    total_qty = 0
    total_selling_value = 0
    total_cost_value = 0
    
    for row in data:
        total_qty += flt(row.get('qty', 0))
        total_selling_value += flt(row.get('selling_value', 0))
        total_cost_value += flt(row.get('cost_value', 0))
    
    # Add totals row
    totals_row = {
        "item_code": "",
        "item_name": "TOTAL",
        "item_group": "",
        "warehouse": "",
        "stock_uom": "",
        "qty": total_qty,
        "selling_rate": "",
        "selling_value": total_selling_value,
        "valuation_rate": "",
        "cost_value": total_cost_value,
        "simple_code": "",
        "company": "",
        "bold": 1
    }
    
    data.append(totals_row)
    return data