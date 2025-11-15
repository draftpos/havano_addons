import frappe
from frappe.utils import nowdate, flt
from frappe import _

def lapf_add(doc, method):
    """
    Auto-create LAPF Pension summary from Havano Payroll Entry.
    Triggered using on_update(doc, method) hook.
    This accumulates LAPF totals across ALL employees for the same payroll period
    """
    try:
        # Ensure correct doctype
        if doc.doctype != "Havano Payroll Entry":
            return

        payroll_period = doc.get("payroll_period")
        if not payroll_period:
            frappe.msgprint(_("Payroll Period is required to generate LAPF summary"))
            return

        print("=================== DEBUG: PROCESSING LAPF PAYROLL ENTRY ===============")
        print(f"Payroll Period: {payroll_period}")
        print(f"Employee: {doc.first_name} {doc.surname}")
        print(f"Document Name: {doc.name}")
        print("ALL FIELDS ================================")
        print(doc.as_dict())

        # --- Get employee details ---
        employee = frappe.db.get_value(
            "havano_employee",
            {
                "first_name": doc.first_name,
                # "surname": doc.surname
            },
            "name"
        )
        if not employee:
            frappe.throw("Employee is missing on Havano Payroll Entry")

        # --- Get company from EMPLOYEE (Havano Payroll Entry has no company field) ---
        company = frappe.db.get_value("havano_employee", {"first_name" : doc.first_name,} , "company")
        if not company:
            frappe.throw(f"Employee {employee} has no company assigned")

        # Extract Basic Salary & LAPF component from earnings
        basic_amount = 0
        lapf_amount = 0

        if doc.get("employee_earnings"):
            for row in doc.employee_earnings:
                component = row.get("components")
                amount = flt(row.get("amount_usd", 0))

                if component == "Basic Salary":
                    basic_amount = amount

                if component == "LAPF":
                    lapf_amount = amount

        # If no LAPF or no Basic → skip
        if not lapf_amount or not basic_amount:
            print(f"No LAPF or Basic amount found for employee {employee}")
            pass

        # Calculate LAPF contributions
        amount_employee = round(basic_amount * 0.06, 2)
        amount_employer = round(basic_amount * 0.173, 2)
        total_amount = amount_employee + amount_employer

        print(f"=== LAPF CALCULATIONS ===")
        print(f"Basic Salary: {basic_amount}")
        print(f"LAPF Amount: {lapf_amount}")
        print(f"Employee Contribution (6%): {amount_employee}")
        print(f"Employer Contribution (17.3%): {amount_employer}")
        print(f"Total Contribution: {total_amount}")

        # Check if LAPF summary already exists for this period and employee
        existing_lapf = frappe.get_all(
            "LAPF Pension",
            filters={
                "payroll_period": payroll_period,
                "employee_id": employee
            },
            fields=["name", "total_amount"],
            limit=1
        )

        if existing_lapf:
            # Update existing record
            existing_doc = frappe.get_doc("LAPF Pension", existing_lapf[0].name)
            existing_doc.amount_employee = amount_employee
            existing_doc.amount_employer = amount_employer
            existing_doc.total_amount = total_amount
            existing_doc.save(ignore_permissions=True)
            print(f"✓ Updated LAPF for: {employee} - Total: {total_amount}")
        else:
            # Create new LAPF Pension document
            lapf_doc = frappe.new_doc("LAPF Pension")
            lapf_doc.employee_id = employee
            lapf_doc.employee_name = f"{doc.first_name} {doc.surname}"
            lapf_doc.payroll_period = payroll_period
            lapf_doc.date = nowdate()
            lapf_doc.salary_component = "LAPF"
            lapf_doc.currency = "USD"
            lapf_doc.amount_employee = amount_employee
            lapf_doc.amount_employer = amount_employer
            lapf_doc.total_amount = total_amount
            lapf_doc.company = company

            lapf_doc.insert(ignore_permissions=True)
            print(f"✓ Created LAPF for: {employee} - Total: {total_amount}")


        return f"LAPF processed for {employee}"

    except Exception as e:
        error_msg = f"Error in lapf_add: {str(e)}"
        print(f"!!! ERROR: {error_msg}")
        frappe.log_error(frappe.get_traceback(), "lapf_add")
        frappe.throw(_("Failed to update LAPF summary: {0}").format(str(e)))

