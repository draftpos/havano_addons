import frappe
from frappe.utils import nowdate, flt
from frappe import _

def add_lapf_data(doc, basic_amount, lapf_amount , employee, company):
    # If no LAPF or no Basic → skip
    payroll_period = doc.get("payroll_period")
    print("THIS IS LAPF FUNCTION DATA *******************")
    if not lapf_amount or not basic_amount:
        print(f"No LAPF or Basic amount found for employee {employee}")
        return

    # Calculate LAPF contributions
    amount_employee = round(basic_amount * 0.06, 2)
    amount_employer = round(basic_amount * 0.173, 2)
    total_amount = amount_employee + amount_employer

    # print(f"=== LAPF CALCULATIONS ===")
    # print(f"Basic Salary: {basic_amount}")
    # print(f"LAPF Amount: {lapf_amount}")
    # print(f"Employee Contribution (6%): {amount_employee}")
    # print(f"Employer Contribution (17.3%): {amount_employer}")
    # print(f"Total Contribution: {total_amount}")

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



# -------------------------------------------------

def add_zibawu_data(doc, basic_amount, zibawu_amount , employee, company):
    # If no LAPF or no Basic → skip
    print("THIS IS ZIBAWU FUNCTION DATA *******************")
    payroll_period = doc.get("payroll_period")
    if not zibawu_amount or not basic_amount:
        print(f"No zibawu or Basic amount found for employee {employee}")
        pass

    # Calculate LAPF contributions
    amount_employee = round(basic_amount * 0.02, 2)
    amount_employer =  0
    total_amount = amount_employee + amount_employer

    # print(f"=== LAPF CALCULATIONS ===")
    # print(f"Basic Salary: {basic_amount}")
    # print(f"Zibawu Amount: {zibawu_amount}")
    # print(f"Employee Contribution (2%): {amount_employee}")
    # print(f"Employer Contribution 0: {amount_employer}")
    # print(f"Total Contribution: {total_amount}")

    # Check if LAPF summary already exists for this period and employee
    existing_zibawu = frappe.get_all(
        "Zibawu",
        filters={
            "payroll_period": payroll_period,
            "employee_id": employee
        },
        fields=["name", "total_amount"],
        limit=1
    )

    if existing_zibawu:
        # Update existing record
        existing_doc = frappe.get_doc("Zibawu", existing_zibawu[0].name)
        existing_doc.amount_employee = amount_employee
        existing_doc.amount_employer = amount_employer
        existing_doc.total_amount = total_amount
        existing_doc.save(ignore_permissions=True)
        print(f"✓ Updated Zibawu for: {employee} - Total: {total_amount}")
    else:
        # Create new LAPF Pension document
        lapf_doc = frappe.new_doc("Zibawu")
        lapf_doc.employee_id = employee
        lapf_doc.employee_name = f"{doc.first_name} {doc.surname}"
        lapf_doc.payroll_period = payroll_period
        lapf_doc.date = nowdate()
        lapf_doc.salary_component = "zibawu"
        lapf_doc.currency = "USD"
        lapf_doc.amount_employee = amount_employee
        lapf_doc.amount_employer = amount_employer
        lapf_doc.total_amount = total_amount
        lapf_doc.company = company

        lapf_doc.insert(ignore_permissions=True)
        print(f"✓ Created Zibawu for: {employee} - Total: {total_amount}")



def add_ufawuz_data(doc, basic_amount, ufawuz_amount , employee, company):
    # If no LAPF or no Basic → skip
    print("THIS IS UFAWUZ FUNCTION DATA *******************")
    payroll_period = doc.get("payroll_period")
    if not ufawuz_amount or not basic_amount:
        print(f"No zibawu or Basic amount found for employee {employee}")
        pass

    # Calculate LAPF contributions
    amount_employee = round(basic_amount * 0.03, 2)
    amount_employer = 0
    total_amount = amount_employee + amount_employer

    # print(f"=== LAPF CALCULATIONS ===")
    # print(f"Basic Salary: {basic_amount}")
    # print(f"Zibawu Amount: {ufawuz_amount}")
    # print(f"Employee Contribution (6%): {amount_employee}")
    # print(f"Employer Contribution (17.3%): {amount_employer}")
    # print(f"Total Contribution: {total_amount}")

    # Check if LAPF summary already exists for this period and employee
    existing_ufawuz = frappe.get_all(
        "Ufawuz",
        filters={
            "payroll_period": payroll_period,
            "employee_id": employee
        },
        fields=["name", "total_amount"],
        limit=1
    )

    if existing_ufawuz:
        # Update existing record
        existing_doc = frappe.get_doc("Ufawuz", existing_ufawuz[0].name)
        existing_doc.amount_employee = amount_employee
        existing_doc.amount_employer = amount_employer
        existing_doc.total_amount = total_amount
        existing_doc.save(ignore_permissions=True)
        print(f"✓ Updated Ufawuz for: {employee} - Total: {total_amount}")
    else:
        # Create new LAPF Pension document
        lapf_doc = frappe.new_doc("Ufawuz")
        lapf_doc.employee_id = employee
        lapf_doc.employee_name = f"{doc.first_name} {doc.surname}"
        lapf_doc.payroll_period = payroll_period
        lapf_doc.date = nowdate()
        lapf_doc.salary_component = "ufawuz"
        lapf_doc.currency = "USD"
        lapf_doc.amount_employee = amount_employee
        lapf_doc.amount_employer = amount_employer
        lapf_doc.total_amount = total_amount
        lapf_doc.company = company

        lapf_doc.insert(ignore_permissions=True)
        print(f"✓ Created Ufawuz for: {employee} - Total: {total_amount}")


def add_cimas_data(doc, basic_amount, cimas_amount , employee, company):
    # If no LAPF or no Basic → skip
    print("THIS IS CIMAS FUNCTION DATA *******************")
    payroll_period = doc.get("payroll_period")
    if not cimas_amount or not basic_amount:
        print(f"No zibawu or Basic amount found for employee {employee}")
        pass

    # Calculate LAPF contributions
    amount_employee = round(cimas_amount * 0.25, 2)
    amount_employer = round(cimas_amount * 0.75, 2)
    total_amount = amount_employee + amount_employer

    # print(f"=== LAPF CALCULATIONS ===")
    # print(f"Basic Salary: {basic_amount}")
    # print(f"Zibawu Amount: {cimas_amount}")
    # print(f"Employee Contribution (6%): {amount_employee}")
    # print(f"Employer Contribution (17.3%): {amount_employer}")
    # print(f"Total Contribution: {total_amount}")

    # Check if LAPF summary already exists for this period and employee
    existing_cimas = frappe.get_all(
        "Cimas",
        filters={
            "payroll_period": payroll_period,
            "employee_id": employee
        },
        fields=["name", "total_amount"],
        limit=1
    )

    if existing_cimas:
        # Update existing record
        existing_doc = frappe.get_doc("Cimas", existing_cimas[0].name)
        existing_doc.amount_employee = amount_employee
        existing_doc.amount_employer = amount_employer
        existing_doc.total_amount = total_amount
        existing_doc.save(ignore_permissions=True)
        print(f"✓ Updated cimas for: {employee} - Total: {total_amount}")
    else:
        # Create new LAPF Pension document
        lapf_doc = frappe.new_doc("Cimas")
        lapf_doc.employee_id = employee
        lapf_doc.employee_name = f"{doc.first_name} {doc.surname}"
        lapf_doc.payroll_period = payroll_period
        lapf_doc.date = nowdate()
        lapf_doc.salary_component = "cimas"
        lapf_doc.currency = "USD"
        lapf_doc.amount_employee = amount_employee
        lapf_doc.amount_employer = amount_employer
        lapf_doc.total_amount = total_amount
        lapf_doc.company = company

        lapf_doc.insert(ignore_permissions=True)
        print(f"✓ Created cimas for: {employee} - Total: {total_amount}")


def add_funeral_policy_data(doc, basic_amount, comp_amount , employee, company):
        # If no LAPF or no Basic → skip
    print("THIS IS FUNERAL FUNCTION DATA *******************")
    payroll_period = doc.get("payroll_period")
    if not comp_amount or not basic_amount:
        print(f"No zibawu or Basic amount found for employee {employee}")
        pass

    # Calculate LAPF contributions
    amount_employee = round(comp_amount * 0.25, 2)
    amount_employer = round(comp_amount * 0.75, 2)
    total_amount = amount_employee + amount_employer

    # print(f"=== LAPF CALCULATIONS ===")
    # print(f"Basic Salary: {basic_amount}")
    # print(f"Policy Amount: {comp_amount}")
    # print(f"Employee Contribution (6%): {amount_employee}")
    # print(f"Employer Contribution (17.3%): {amount_employer}")
    # print(f"Total Contribution: {total_amount}")

    # Check if LAPF summary already exists for this period and employee
    existing_policy = frappe.get_all(
        "Funeral Policy",
        filters={
            "payroll_period": payroll_period,
            "employee_id": employee
        },
        fields=["name", "total_amount"],
        limit=1
    )

    if existing_policy:
        # Update existing record
        existing_doc = frappe.get_doc("Funeral Policy", existing_policy[0].name)
        existing_doc.amount_employee = amount_employee
        existing_doc.amount_employer = amount_employer
        existing_doc.total_amount = total_amount
        existing_doc.save(ignore_permissions=True)
        print(f"✓ Updated funeral policy for: {employee} - Total: {total_amount}")
    else:
        # Create new LAPF Pension document
        lapf_doc = frappe.new_doc("Funeral Policy")
        lapf_doc.employee_id = employee
        lapf_doc.employee_name = f"{doc.first_name} {doc.surname}"
        lapf_doc.payroll_period = payroll_period
        lapf_doc.date = nowdate()
        lapf_doc.salary_component = "funeral policy"
        lapf_doc.currency = "USD"
        lapf_doc.amount_employee = amount_employee
        lapf_doc.amount_employer = amount_employer
        lapf_doc.total_amount = total_amount
        lapf_doc.company = company

        lapf_doc.insert(ignore_permissions=True)
        print(f"✓ Created funeral policy for: {employee} - Total: {total_amount}")
