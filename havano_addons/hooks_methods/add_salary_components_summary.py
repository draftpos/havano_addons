from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, getdate, flt, cint, now_datetime
from frappe import _
import json

def add_salary_components_summary(doc, method):
    """
    Add salary components summary when Havano Payroll Entry is saved
    This accumulates totals across ALL employees for the same payroll period
    """
    try:
        # Only process if this is a Havano Payroll Entry
        if doc.doctype != "Havano Payroll Entry":
            return
            
        payroll_period = doc.get("payroll_period")
        if not payroll_period:
            frappe.msgprint(_("Payroll Period is required to generate summary"))
            return
        
        print("=== DEBUG: PROCESSING PAYROLL ENTRY ===")
        print(f"Payroll Period: {payroll_period}")
        print(f"Employee: {doc.first_name} {doc.surname}")
        print(f"Document Name: {doc.name}")
        print(f"Method: {method}")
        
        # Dictionary to store NEW amounts from this employee
        new_component_amounts = {}
        
        # Process earnings
        if doc.get("employee_earnings"):
            print(f"Found {len(doc.employee_earnings)} earnings records")
            for i, earning in enumerate(doc.employee_earnings):
                component_name = earning.get("components")
                amount_usd = flt(earning.get("amount_usd", 0))
                total_amount = amount_usd
                
                print(f"Earning {i}: {component_name} - USD: {amount_usd}, Total: {total_amount}")
                
                if component_name and total_amount > 0:
                    if component_name not in new_component_amounts:
                        new_component_amounts[component_name] = 0
                    new_component_amounts[component_name] += total_amount
        else:
            print("No earnings records found")
        
        # Process deductions
        if doc.get("employee_deductions"):
            print(f"Found {len(doc.employee_deductions)} deductions records")
            for i, deduction in enumerate(doc.employee_deductions):
                component_name = deduction.get("components")
                amount_usd = flt(deduction.get("amount_usd", 0))
                total_amount = amount_usd
                
                print(f"Deduction {i}: {component_name} - USD: {amount_usd}, Total: {total_amount}")
                
                if component_name and total_amount > 0:
                    if component_name not in new_component_amounts:
                        new_component_amounts[component_name] = 0
                    new_component_amounts[component_name] += total_amount
        else:
            print("No deductions records found")
        
        print("=== NEW AMOUNTS FROM THIS EMPLOYEE ===")
        if new_component_amounts:
            for comp, amount in new_component_amounts.items():
                print(f"  {comp}: {amount}")
        else:
            print("  No components with amounts > 0 found")
            frappe.msgprint(_("No salary components with amounts found to summarize"))
            return
        
        # Create or update records in Salary Summary On Payroll Run with CUMULATIVE totals
        records_created = 0
        records_updated = 0
        
        for component_name, new_amount in new_component_amounts.items():
            # Check if summary already exists for this period and component
            existing_summary = frappe.get_all(
                "Salary Summary On Payroll Run",
                filters={
                    "salary_component": component_name,
                    "period": payroll_period
                },
                fields=["name", "total"]
            )
            
            if existing_summary:
                # GET EXISTING TOTAL and ADD new amount
                existing_doc = frappe.get_doc("Salary Summary On Payroll Run", existing_summary[0].name)
                existing_total = flt(existing_doc.total) or 0
                
                # Update existing record with cumulative total
                existing_doc.total = new_amount
                existing_doc.save(ignore_permissions=True)
                records_updated += 1
                print(f"✓ Updated: {component_name} - Added {new_amount} to existing {existing_total} = {new_total}")
            else:
                # Create new record (first employee for this component in this period)
                summary_doc = frappe.new_doc("Salary Summary On Payroll Run")
                summary_doc.salary_component = component_name
                summary_doc.period = payroll_period
                summary_doc.total = new_amount
                summary_doc.insert(ignore_permissions=True)
                records_created += 1
                print(f"✓ Created: {component_name} - {new_amount}")
        
        # Final summary
        print(f"=== SUMMARY: {records_created} created, {records_updated} updated ===")
        
      
        
    except Exception as e:
        error_msg = f"Error in add_salary_components_summary: {str(e)}"
        print(f"!!! ERROR: {error_msg}")
        frappe.log_error(error_msg)
        frappe.throw(_("Failed to update salary components summary: {0}").format(str(e)))