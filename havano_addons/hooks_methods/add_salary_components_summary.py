from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, getdate, flt, cint, now_datetime
from frappe import _
import json
from .add_salary_component_data import add_salary_component_data_for_report

date_for_purchase_invoice=""
def add_salary_components_summary(doc, method):
    print(f"=================== add_salary_components_summary REACHED nowwww ========={doc}==========")
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
        
        # Check if payroll period is already completed
        completed_summary = frappe.get_all(
            "Salary Summary On Payroll Run",
            filters={
                "period": payroll_period,
                "completed": "yes"
            },
            limit=1
        )
        
        if completed_summary:
            frappe.throw(_("Payroll period {0} is already completed. Cannot process more entries.").format(payroll_period))
            return

        
        havano_employee = frappe.get_value(
                "havano_employee",
                {
                    "first_name": doc.first_name,
                    "last_name": doc.surname
                },
                "name"
            )
        total_net_salary=0
        if havano_employee:
            emp_doc = frappe.get_doc("havano_employee", havano_employee)
            # Now you have the full document
            print("EMPLOYEE FROM HAVANO EMPLOYEE------------------------------")
            print(emp_doc)
            print(havano_employee)
            print(f"Payee: {emp_doc.payee}")
            print(f"aids_levy : {emp_doc.aids_levy}")
            # print(emp_doc.as_dict())


        completed_summary = frappe.get_all(
            "Salary Summary On Payroll Run",
            filters={
                "period": payroll_period,
                "completed": "yes"
            },
            limit=1
        )
        date_for_purchase_invoice=payroll_period
        print(f"Date for purchase invoice set to: {date_for_purchase_invoice}")
        
        if completed_summary:
            frappe.throw(_("Payroll period {0} is already completed. Cannot process more entries.").format(payroll_period))
            return
        
        # Dictionary to store NEW amounts from this employee
        new_component_amounts = {}
        
        # Process earnings
        # if doc.get("employee_earnings"):
        #     for i, earning in enumerate(doc.employee_earnings):
        #         component_name = earning.get("components")
        #         amount_usd = flt(earning.get("amount_usd", 0))
        #         total_amount = amount_usd
        #         if component_name and total_amount > 0:
        #             if component_name not in new_component_amounts:
        #                 new_component_amounts[component_name] = 0
        #             new_component_amounts[component_name] += total_amount
        # else:
        #     print("No earnings records found")
        
        # Process deductions
        if doc.get("employee_deductions"):
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

        # MODIFY COMPONENTS TO HAVE CALCULATED DETAILS

        new_component_amounts['PAYEE'] = emp_doc.payee
        new_component_amounts['Aids Levy'] = emp_doc.aids_levy
        
        try:
            add_salary_component_data_for_report(doc, new_component_amounts)
        except Exception as e:
            print(e)

        if new_component_amounts:
            # for comp, amount in new_component_amounts.items():
            #     print(f"  {comp}: {amount}")
                pass
        else:
            frappe.msgprint(_("No salary components with amounts found to summarize"))
            return
        
        # Create or update records in Salary Summary On Payroll Run with CUMULATIVE totals
        records_created = 0
        records_updated = 0
        def get_reporting_components():
            settings = frappe.get_single("Havano Payroll Settings")

            # Make sure the table exists and has rows
            if not settings.components_for_reporting:
                frappe.throw("No components found in Components for Reporting.")

            components = []
            for row in settings.components_for_reporting:
                components.append({
                    "component": row.component,
                    "code": row.code
                })

            return components
        allowed_components_for_reporting = get_reporting_components()
        # frappe.log_error(f"allowed components {allowed_components_for_reporting}")
        
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
                existing_doc.total = new_amount + existing_total
                existing_doc.save(ignore_permissions=True)
                records_updated += 1
            else:
                exists = any(c["component"] == component_name for c in allowed_components_for_reporting)
                if exists:  
                    frappe.log_error(f"component exists {exists}")
                    # Create new record (first employee for this component in this period)
                    summary_doc = frappe.new_doc("Salary Summary On Payroll Run")
                    summary_doc.salary_component = component_name
                    summary_doc.period = payroll_period
                    summary_doc.total = new_amount
                    summary_doc.completed = "no"  # Default to not completed
                    summary_doc.insert(ignore_permissions=True)
                    records_created += 1
                else:
                    frappe.log_error(f"component dont exists {exists}")
        # Check if this is the last employee
       
        is_last_employee = check_if_last_employee(doc, payroll_period)
        
        if is_last_employee:
            # Mark all salary summaries for this period as completed
            mark_period_completed(payroll_period)
            frappe.msgprint(_("All employees processed for period {0}. Payroll run completed.").format(payroll_period))
        
        # Final summary
        # print(f"=== SUMMARY: {records_created} created, {records_updated} updated ===")
        # print(f"=== IS LAST EMPLOYEE: {is_last_employee} ===")
        
    except Exception as e:
        error_msg = f"Error in add_salary_components_summary: {str(e)}"
        print(f"!!! ERROR: {error_msg}")
        frappe.log_error(frappe.get_traceback(), "add_salary_components_summary")
        frappe.throw(_("Failed to update salary components summary: {0}").format(str(e)))

def check_if_last_employee(current_doc, payroll_period):
    """
    Check if all employees for this company have been processed for this payroll period
    """
    try:
        # Get company from current document

        
        # Get all ACTIVE employees for this specific company
        all_employees = frappe.get_all("havano_employee", 
                                     filters={"status": "Active"},
                                     fields=["name"])
        
        # Get count of payroll entries for this period and company
        payroll_count = frappe.db.count("Havano Payroll Entry", {
            "payroll_period": payroll_period,
            "docstatus": ["!=", 2]  # Exclude cancelled
        })
        
        employee_count = len(all_employees)
        
        # print(f"=== EMPLOYEE CHECK ===")
        # print(f"Total active employees: {employee_count}")
        # print(f"Payroll entries count: {payroll_count}")
        
        # Simple check: if payroll entries count >= employee count, we're done
        # This assumes one payroll entry per employee
        is_last = payroll_count >= employee_count
        
        # print(f"All employees processed: {is_last}")
        
        return is_last
        
    except Exception as e:
        print(f"Error in check_if_last_employee: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "check_if_last_employee")
        return False

def mark_period_completed(payroll_period):
    """
    Mark all Salary Summary records for a period as completed
    """
    try:
        # Get all salary summaries for this period
        salary_summaries = frappe.get_all("Salary Summary On Payroll Run",
                                        filters={"period": payroll_period},
                                        fields=["name"])
        
        for summary in salary_summaries:
            summary_doc = frappe.get_doc("Salary Summary On Payroll Run", summary.name)
            summary_doc.completed = "yes"
            summary_doc.save(ignore_permissions=True)
            
            # Trigger purchase invoice creation for each completed salary summary
            create_purchase_invoice_on_salary_run(summary_doc,payroll_period)
        print(f"✓ Marked {len(salary_summaries)} records as completed for period: {payroll_period}")
        
    except Exception as e:
        print(f"Error in mark_period_completed: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "mark_period_completed")
        frappe.throw(_("Failed to mark period as completed: {0}").format(str(e)))

def create_purchase_invoice_on_salary_run(doc,payroll_period, method=None):
    
    """
    Create Purchase Invoices from Salary Summary On Payroll Run
    This function is called when completed turns to "yes"
    Creates one purchase invoice per salary component using configuration from havano_salary_component
    """
    try:
        # Only process if the document is completed
        if doc.get("completed") != "yes":
            return
            
        # Check if this is a Salary Summary On Payroll Run document
        if doc.doctype != "Salary Summary On Payroll Run":
            return

        # Get the salary component details
        salary_component_name = doc.salary_component
        salary_component = frappe.get_doc("havano_salary_component", salary_component_name)
        
        # Check if purchase invoice already exists for this salary summary
        existing_invoice = frappe.db.exists("Purchase Invoice", {
            "bill_no": f"Salary-Run-{doc.period}-{doc.salary_component}"
        })
        
        if existing_invoice:
            frappe.msgprint(_("Purchase Invoice already exists for this salary summary: {0}").format(existing_invoice))
            return
        
        # Get company from document or use default
        company = getattr(doc, 'company', None)
        if not company:
            company = frappe.defaults.get_user_default("company")
            if not company:
                frappe.throw(_("Company is not set in Salary Summary and no default company found"))
        
        # Find the salary account configuration for this company
        salary_account = None
        for account in salary_component.accounts:
            if account.company == company:
                salary_account = account
                break

        if not salary_account:
            frappe.msgprint(_("No salary accounts configuration found for company: {0} in salary component {1}").format(company, salary_component_name))
            return
        
        # Validate required fields
        if not salary_account.supplier:
            frappe.throw(_("Supplier is not configured in salary accounts for company: {0}").format(company))
        
        if not salary_account.item:
            frappe.throw(_("Item is not configured in salary accounts for company: {0}").format(company))
        
        if not salary_account.account:
            frappe.throw(_("Account is not configured in salary accounts for company: {0}").format(company))
        
        # Validate that the account is not a group account and get a valid leaf account
        expense_account = get_valid_expense_account(salary_account.account, company)
        if not expense_account:
            frappe.throw(_("No valid expense account found. Please configure a non-group account in salary accounts."))
        if  salary_account.supplier == "Employees":
            return
        else: 
            # Create Purchase Invoice
            purchase_invoice = frappe.new_doc("Purchase Invoice")
            if salary_account.supplier == "Employees":
                return
            purchase_invoice.update({
                "supplier": salary_account.supplier,
                "company": salary_account.company,
                "currency": salary_account.currency or frappe.get_cached_value('Company', company, 'default_currency'),
                "cost_center": salary_account.cost_center,
                "bill_no": f"Salary-Run-{doc.period}-{doc.salary_component}",
                "bill_date": nowdate(),
                "due_date": nowdate(),
                "items": [],
            })
            purchase_invoice.custom_from_payroll = 1
            purchase_invoice.custom_payroll_period = payroll_period

            
            # Add the salary component as an item
            item = {
                "item_code": salary_account.item,
                "item_name": doc.salary_component,
                "description": f"{doc.salary_component} - {doc.period}",
                "qty": 1,
                "rate": doc.total,
                "amount": doc.total,
                "cost_center": salary_account.cost_center,
                "expense_account": expense_account
            }
            purchase_invoice.append("items", item)
            
            # Calculate taxes and totals
            purchase_invoice.run_method("set_missing_values")
            purchase_invoice.run_method("calculate_taxes_and_totals")
            
            # Save the purchase invoice
            purchase_invoice.insert(ignore_permissions=True)
            purchase_invoice.submit()
            frappe.log_error(f"Purchase Invoice {purchase_invoice.name} created for Salary Summary", "Purchase Invoice Created")
            
        # Add comment to salary summary
        doc.add_comment("Comment", f"Purchase Invoice <a href='/app/purchase-invoice/{purchase_invoice.name}'>{purchase_invoice.name}</a> created automatically")
        
        frappe.msgprint(_("Purchase Invoice {0} created successfully for {1}").format(purchase_invoice.name, doc.salary_component))
        
        return purchase_invoice.name
        
    except Exception as e:
        # Truncate error message to 140 characters for log title
        error_msg = str(e)
        log_title = error_msg[:140] if len(error_msg) > 140 else error_msg
        frappe.log_error(frappe.get_traceback(), log_title)
        frappe.throw(_("Failed to create purchase invoice: {0}").format(error_msg))

def get_valid_expense_account(account, company):
    """
    Get a valid leaf account for expense posting
    """
    try:
        # Check if the account exists and is not a group account
        account_doc = frappe.get_doc("Account", account)
        
        if not account_doc.is_group:
            return account  # It's already a leaf account
        
        # If it's a group account, find the first leaf account under it
        leaf_accounts = frappe.get_all("Account",
            filters={
                "parent_account": account,
                "is_group": 0,
                "company": company,
                "disabled": 0
            },
            fields=["name"],
            order_by="name",
            limit=1
        )
        
        if leaf_accounts:
            return leaf_accounts[0].name
        
        # If no leaf accounts found directly, try to find a default expense account for the company
        default_expense_account = frappe.get_cached_value('Company', company, 'default_expense_account')
        if default_expense_account:
            default_account_doc = frappe.get_doc("Account", default_expense_account)
            if not default_account_doc.is_group:
                return default_expense_account
        
        return None
        
    except Exception:
        return None