import frappe
from frappe import _


def get_job_card_permission_query_conditions(user):
    if not user:
        user = frappe.session.user

    roles = frappe.get_roles(user)
    if "System Manager" in roles or "Manufacturing Manager" in roles or user == "Administrator":
        return ""

    escaped_user = frappe.db.escape(user)
    emp = frappe.db.get_value("Employee", {"user_id": user}, "name")
    
    emp_cond = ""
    if emp:
        emp_cond = f"OR `tabJob Card`.name IN (SELECT parent FROM `tabJob Card Time Log` WHERE employee = {frappe.db.escape(emp)})"

    return f"""(
        `tabJob Card`.name IN (
            SELECT reference_name FROM `tabToDo` 
            WHERE reference_type = 'Job Card' 
            AND (allocated_to = {escaped_user} OR owner = {escaped_user})
            AND status != 'Cancelled'
        )
        {emp_cond}
    )"""



def auto_assign_employee_to_job_card(doc, method):
    if doc.reference_type == "Job Card" and doc.reference_name and doc.allocated_to:
        emp = frappe.db.get_value("Employee", {"user_id": doc.allocated_to}, "name")
        if emp:
            
            exists = frappe.db.exists("Job Card Time Log", {
                "parent": doc.reference_name,
                "employee": emp
            })
            
            if not exists:
                import uuid
                row_name = frappe.generate_hash(length=10)
                
                
                frappe.db.sql("""
                    INSERT INTO `tabJob Card Time Log` 
                    (name, parent, parenttype, parentfield, employee, idx, docstatus)
                    VALUES (%s, %s, 'Job Card', 'employee', %s, 1, 0)
                """, (row_name, doc.reference_name, emp))



def validate_job_card(doc, method):
    user = frappe.session.user
    roles = frappe.get_roles(user)

    if "System Manager" in roles or "Manufacturing Manager" in roles or user == "Administrator":
        return

    emp = frappe.db.get_value("Employee", {"user_id": user}, "name")
    assigned = [d.employee for d in doc.get("employee", [])]
    
    is_todo = frappe.db.sql("""
        SELECT name FROM `tabToDo` 
        WHERE reference_type = 'Job Card' 
        AND reference_name = %s 
        AND (allocated_to = %s OR owner = %s)
        AND status != 'Cancelled'
    """, (doc.name, user, user))

    if not is_todo and (not emp or emp not in assigned):
        frappe.throw(_("এই Job Card টি আপনার জন্য বরাদ্দ করা নয়।"))