import frappe
import requests

def send_data_to_sales_invoice(doc, method):
    print("SEND DATA TO SALES INVOICE HOOK RUN")
#     pass
#     # Prepare data for the Sales Invoice
#     sales_invoice_data = {
#         "customer": doc.customer,
#         "items": []
#     }

#     # Populate items from Sales Order
#     for item in doc.items:
#         sales_invoice_data["items"].append({
#             "item_code": item.item_code,
#             "qty": item.qty,
#             "rate": item.rate,
#             "amount": item.amount
#         })

#     # Create the Sales Invoice
#     create_sales_invoice(sales_invoice_data)

# def create_sales_invoice(data):
#     # Create a new Sales Invoice record
#     sales_invoice = frappe.get_doc({
#         "doctype": "Sales Invoice",
#         "customer": data["customer"],
#         "items": data["items"],
#     })

#     # Insert the Sales Invoice record
#     sales_invoice.insert()
#     sales_invoice.submit()  # Submit the invoice
#     frappe.log("Sales Invoice created successfully: {}".format(sales_invoice.name))