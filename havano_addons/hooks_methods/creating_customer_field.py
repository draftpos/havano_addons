import frappe

def update_customer_doctype(doc=None, method=None):
    # Add custom field programmatically if it doesn't exist
    if doc:
        if not frappe.get_meta("Customer").has_field("default_cost_center"):
            custom_field = frappe.get_doc({
                "doctype": "Custom Field",
                "dt": "Customer",
                "fieldname": "default_cost_center",
                "label": "Default Cost Center",
                "fieldtype": "Link",
                "options": "Cost Center",
                "insert_after": "customer_primary_contact"
            })
            custom_field.insert()
            print("----------------------CUSTOM HOOK RUN--------------------")
            frappe.msgprint("Added Default Cost Center field to Customer doctype")
    else:
        "DOC HAS BEEN NOT PROVIDED"