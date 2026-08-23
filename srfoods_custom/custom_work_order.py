import frappe

@frappe.whitelist()
def get_latest_completed_qc(work_order):
    qc = frappe.db.get_value(
        "Quality Inspection",
        {
            "reference_type": "Work Order",
            "reference_name": work_order,
            "status": "Accepted",
            "docstatus": 1
        },
        ["name", "status"],
        as_dict=True,
        order_by="creation desc"
    )
    return qc
