import frappe
from frappe.utils import nowdate, flt
from frappe import _
from .add_data_to_report_doctypes import add_lapf_data, add_zibawu_data, add_ufawuz_data, add_cimas_data, add_funeral_policy_data

doc = {'name': 58, 'owner': 'Administrator', 'creation': '2025-11-15 04:18:45.168537', 'modified': '2025-11-15 04:18:45.168537', 'modified_by': 'Administrator', 'docstatus': 0, 'idx': 0, 'payroll_period': 'July 2025', 'first_name': 'sss', 'surname': 'f', 'doctype': 'Havano Payroll Entry', 'employee_deductions': [{'name': 'nhlkeb5p8g', 'owner': 'Administrator', 'creation': '2025-11-15 04:18:45.168537', 'modified': '2025-11-15 04:18:45.168537', 'modified_by': 'Administrator', 'docstatus': 0, 'idx': 1, 'components': 'zibawu', 'item_code': None, 'amount_usd': 10.0, 'amount_zwg': 0.0, 'exchange_rate': None, 'is_tax_applicable': 0, 'parent': 58, 'parentfield': 'employee_deductions', 'parenttype': 'Havano Payroll Entry', 'doctype': 'havano_payroll_earnings', '__unsaved': 1}], 'employee_earnings': [{'name': 'nhlg3dk56b', 'owner': 'Administrator', 'creation': '2025-11-15 04:18:45.168537', 'modified': '2025-11-15 04:18:45.168537', 'modified_by': 'Administrator', 'docstatus': 0, 'idx': 1, 'components': 'Basic Salary', 'item_code': 'BS', 'amount_usd': 300.0, 'amount_zwg': 0.0, 'exchange_rate': None, 'is_tax_applicable': 0, 'parent': 58, 'parentfield': 'employee_earnings', 'parenttype': 'Havano Payroll Entry', 'doctype': 'havano_payroll_earnings', '__unsaved': 1}], '__unsaved': 1}

def convert_dict_to_doc(doc_dict):
    """
    Convert a raw Python dict (e.g. from console or API) 
    into a real Frappe DocType instance with normal methods.
    """

    # Ensure frappe can create it
    if "doctype" not in doc_dict:
        frappe.throw("Dictionary must contain a 'doctype' key")

    # Use frappe.get_doc to hydrate the dict
    doc = frappe.get_doc(doc_dict)

    return doc



def add_salary_component_data_for_report(doc, new_component_amounts):
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

        # print("=================== DEBUG: PROCESSING LAPF PAYROLL ENTRY ===============")
        # print(f"Payroll Period: {payroll_period}")
        # print(f"Employee: {doc.first_name} {doc.surname}")
        # print(f"Document Name: {doc.name}")
        # print("ALL FIELDS ================================")
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

        if doc.get("employee_earnings"):
            for row in doc.employee_earnings:
                component = row.get("components")
                amount = flt(row.get("amount_usd", 0))

                if component == "Basic Salary":
                    basic_amount = amount
                    

                

        print("DETAILD WHEN ADD_DATA FUNCTIONS ARE ABOUT TO RUN")
        print(new_component_amounts)

        if new_component_amounts:
            for comp, comp_amount in new_component_amounts.items():
                print(f"  {comp}: {comp_amount}")

                if comp.lower() == "zibawu":
                    add_zibawu_data(doc, basic_amount, comp_amount , employee, company)
                elif comp.lower() == "lapf":
                    add_lapf_data(doc, basic_amount, comp_amount , employee, company)

                elif comp.lower() == "ufawuz":
                    add_ufawuz_data(doc, basic_amount, comp_amount , employee, company)
                
                elif comp.lower() == "cimas":
                    add_cimas_data(doc, basic_amount, comp_amount , employee, company)

                elif comp.lower() == "funeral policy":
                    add_funeral_policy_data(doc, basic_amount, comp_amount , employee, company)

                elif comp.lower() == "nec":
                    pass

                elif comp.lower() == "nssa":
                    pass

                elif comp.lower() == "basic salary":
                    pass

                elif comp.lower() == "aids levy":
                    pass

                elif comp.lower() == "payee":
                    pass

                elif comp.lower() == "payee":
                    pass
                    
                    



        


        return f"LAPF processed for {employee}. MAIN FUNCTION"

    except Exception as e:
        error_msg = f"Error in lapf_add: {str(e)}"
        print(f"!!! ERROR: {error_msg}")
        frappe.log_error(frappe.get_traceback(), "lapf_add")
        frappe.throw(_("Failed to update LAPF summary: {0}").format(str(e)))

