import frappe


@frappe.whitelist()
def get_qc_details(work_order):
    # এই Work Order-এর সমস্ত Stock Entry বের করা
    stock_entries = frappe.get_all(
        "Stock Entry",
        filters={"work_order": work_order, "docstatus": ["<", 2]},
        fields=["name", "docstatus"],
    )

    data = []
    for se in stock_entries:
        # Stock Entry-র সাথে লিংক থাকা Quality Inspection আনা
        qis = frappe.get_all(
            "Quality Inspection",
            filters={"reference_type": "Stock Entry", "reference_name": se.name},
            fields=[
                "name",
                "inspection_type",
                "quality_inspection_template",
                "docstatus",
                "status",
            ],
        )

        prod_qa = "-"
        app_qa = "-"
        se_status = "Submitted" if se.docstatus == 1 else "Draft"

        for qi in qis:
            ins_type = (qi.inspection_type or "").lower()
            ins_tmpl = (qi.quality_inspection_template or "").lower()

            # টাইপ অথবা টেমপ্লেটের নামে 'application' বা 'app' থাকলে সেটি Application Inspection
            if "application" in ins_type or "application" in ins_tmpl:
                app_qa = qi.name
            else:
                prod_qa = qi.name

        if prod_qa != "-" or app_qa != "-":
            data.append(
                {
                    "stock_entry": se.name,
                    "product_inspection": prod_qa,
                    "application_inspection": app_qa,
                    "status": se_status,
                }
            )

    return data