from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, getdate, flt, cint, now_datetime
from frappe import _
import json
from ....hooks_methods.get_customers_with_groups import get_all_customers_from_groups_and_sub_groups

class HaGroupInvoice(Document):
    def validate(self):
        # Update total customers count when group customer is selected
        if self.group_customer:
            self.update_total_customers()
        
        # Calculate grand total from items
        self.calculate_grand_total()
    
    def on_submit(self):
        self.create_sales_invoices()







    def before_submit(self):
        # Store the original group for reference
        self.original_group_customer = self.group_customer
    
    def on_update_after_submit(self):
        # Allow group customer changes after submission only through promote functionality
        if hasattr(self, '_is_promoting') and self._is_promoting:
            return
        # Otherwise, prevent changes
        if self.group_customer != self.original_group_customer:
            frappe.throw(_("Not allowed to change Group Customer after submission"))




        
    @frappe.whitelist()
    def update_total_customers(self):
        """Update the total number of customers in the selected group"""
        customers = get_all_customers_from_groups_and_sub_groups(self)
        customers_count = len(customers) if customers else 0
        self.total_customers = customers_count
    
    def calculate_grand_total(self):
        """Calculate grand total from all items"""
        total = 0
        for item in self.items:
            # Calculate amount for each item if not already calculated
            if not item.amount:
                item.amount = flt(item.qty) * flt(item.rate)
            total += flt(item.amount)
        
        self.grand_total = total
    
    def create_sales_invoices(self):
        """Create Sales Invoices for all customers in the group"""
        customers = get_all_customers_from_groups_and_sub_groups(self)
        
        if not customers:
            frappe.throw(_("No active customers found in the selected group"))
        
        created_invoices = []
        failed_customers = []
        
        for customer in customers:
            try:
                sales_invoice = self.create_sales_invoice_for_customer(customer)
                created_invoices.append({
                    'customer': customer.name,
                    'invoice': sales_invoice.name,
                    'status': 'Submitted'
                })
                
                # Add a small delay to avoid overwhelming the system
                frappe.db.commit()
                
            except Exception as e:
                failed_customers.append({
                    'customer': customer.name,
                    'error': str(e)
                })
                frappe.log_error(f"Failed to create invoice for {customer.name}", str(e))
        
        # Update the parent document with creation results
        self.update_creation_results(created_invoices, failed_customers)
    
    def create_sales_invoice_for_customer(self, customer):
        """Create a Sales Invoice for a specific customer"""
        sales_invoice = frappe.new_doc('Sales Invoice')
        
        # Set basic information
        sales_invoice.update({
            'customer': customer.name,
            'company': self.company,
            'posting_date': self.posting_date,
            'posting_time': self.posting_time,
            'due_date': self.payment_due_date,
            'currency': self.currency,
            'price_list': self.price_list,
            'update_stock': self.update_stock,
            'cost_center': self.cost_center,
            'project': self.project
        })
        
        # Add items from the group invoice
        for item in self.items:
            sales_invoice.append('items', {
                'item_code': item.item_code,
                'qty': item.qty,
                'rate': item.rate,
                'cost_center': item.cost_center or self.cost_center,
                'project': item.project or self.project,
                'income_account': item.income_account,
                'expense_account': item.expense_account,
                'warehouse': self.source_warehouse if self.update_stock else None
            })
        
        # Calculate taxes and totals
        sales_invoice.set_missing_values()
        sales_invoice.calculate_taxes_and_totals()
        
        # Save and submit the invoice
        sales_invoice.insert(ignore_permissions=True)
        sales_invoice.submit()
        
        return sales_invoice
    
    def update_creation_results(self, created_invoices, failed_customers):
        """Update the document with creation results"""
        self.db_set('creation_status', json.dumps({
            'created_invoices': created_invoices,
            'failed_customers': failed_customers,
            'total_created': len(created_invoices),
            'total_failed': len(failed_customers),
            'completion_time': now_datetime().strftime('%Y-%m-%d %H:%M:%S')
        }))
        
        # Also add a comment to the document
        comment_text = f"""
        <p><b>Invoice Creation Results:</b></p>
        <p>Successfully created: {len(created_invoices)} invoices</p>
        <p>Failed: {len(failed_customers)} customers</p>
        """
        
        if failed_customers:
            comment_text += "<p><b>Failed Customers:</b></p>"
            for fc in failed_customers:
                comment_text += f"<p>{fc['customer']}: {fc['error']}</p>"
        
        frappe.get_doc({
            'doctype': 'Comment',
            'comment_type': 'Info',
            'reference_doctype': self.doctype,
            'reference_name': self.name,
            'content': comment_text
        }).insert(ignore_permissions=True)



@frappe.whitelist()
def create_invoices_now(docname):
    """Manual method to create invoices without submitting"""
    doc = frappe.get_doc('Ha Group Invoice', docname)
    doc.create_sales_invoices()
    return True







@frappe.whitelist()
def get_customer_count(from_group, to_group):
    """Get count of customers in the from_group"""
    count = frappe.db.count('Customer', {'customer_group': from_group})
    return {'count': count}

@frappe.whitelist()
def bulk_promote_customers(from_group, to_group):
    """Move all customers from one group to another"""
    try:
        # Get all customers in the from_group
        customers = frappe.get_all('Customer',
            filters={'customer_group': from_group},
            pluck='name'
        )
        
        promoted_count = 0
        for customer_name in customers:
            frappe.db.set_value('Customer', customer_name, 'customer_group', to_group)
            promoted_count += 1
        
        frappe.db.commit()
        
        return {
            "success": True,
            "promoted_count": promoted_count
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Bulk Customer Promotion Error")
        frappe.throw(_("Error promoting customers: {0}").format(str(e)))