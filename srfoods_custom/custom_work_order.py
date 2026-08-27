import frappe
from frappe import _
from frappe.utils import flt
import erpnext.manufacturing.doctype.work_order.work_order as original_wo


@frappe.whitelist()
def make_material_consumption_entry(work_order_id, qty=None):
    wo = frappe.get_doc("Work Order", work_order_id)

    if flt(wo.material_transferred_for_manufacturing) <= 0:
        frappe.throw(_("প্রথমে কাঁচামাল ট্রান্সফার (Material Transfer) করতে হবে।"))

    pending_jobs = frappe.get_all(
        "Job Card",
        filters={
            "work_order": work_order_id,
            "docstatus": 1,
            "status": ["!=", "Completed"],
        },
        fields=["name", "operation"],
    )

    if pending_jobs:
        pending_names = ", ".join([f"{d.name} ({d.operation})" for d in pending_jobs])
        frappe.throw(_(f"সব Job Card এখনও কমপ্লিট হয়নি: {pending_names}"))

    ste = original_wo.make_stock_entry(
        work_order_id=work_order_id,
        purpose="Material Consumption for Manufacture",
        qty=flt(qty) or flt(wo.qty),
    )

    if not ste:
        frappe.throw(_("Stock Entry তৈরি করা সম্ভব হয়নি।"))

    if isinstance(ste, dict):
        return ste
    return ste.as_dict()


@frappe.whitelist()
def custom_make_stock_entry(work_order_id, purpose, qty=None):
    # স্ট্যান্ডার্ড মেথড কল করা
    ste = original_wo.make_stock_entry(
        work_order_id=work_order_id, purpose=purpose, qty=qty
    )

    # Manufacture এন্ট্রির ক্ষেত্রে মেমরিতেই টিক সেট করে দেওয়া
    if purpose == "Manufacture":
        if hasattr(ste, "custom_application_inspection_required"):
            ste.custom_application_inspection_required = 1
        if hasattr(ste, "application_inspection_required"):
            ste.application_inspection_required = 1

        if hasattr(ste, "custom_production_inspection_required"):
            ste.custom_production_inspection_required = 1
        if hasattr(ste, "production_inspection_required"):
            ste.production_inspection_required = 1

    return ste


def validate_stock_entry_qc_submission(doc, method):
    # শুধুমাত্র Manufacture Stock Entry সাবমিট করার সময় ভ্যালিডেশন চেক হবে
    if doc.stock_entry_type == "Manufacture" or doc.purpose == "Manufacture":
        req_app = getattr(
            doc,
            "custom_application_inspection_required",
            getattr(doc, "application_inspection_required", 0),
        )
        req_prod = getattr(
            doc,
            "custom_production_inspection_required",
            getattr(doc, "production_inspection_required", 0),
        )

        # যদি কোনো ইন্সপেকশন রিকোয়ারমেন্ট না থাকে
        if not (req_app or req_prod):
            return

        # বর্তমান Stock Entry-র সাথে লিংক থাকা সমস্ত Quality Inspection আনা
        all_qi = frappe.get_all(
            "Quality Inspection",
            filters={
                "reference_type": "Stock Entry",
                "reference_name": doc.name,
                "docstatus": ["<", 2],  # Draft (0) এবং Submitted (1) উভয় রেকর্ড চেক
            },
            fields=["name", "docstatus", "status", "quality_inspection_template", "inspection_type"],
        )

        # ১. যদি কোনো ইন্সপেকশন তৈরি না থাকে
        if not all_qi:
            frappe.throw(
                _("এই Stock Entry-র জন্য Quality Inspection তৈরি করা হয়নি। দয়া করে আগে Quality Inspection তৈরি ও Submit করুন।"),
                title=_("Quality Inspection Required"),
            )

        # ২. কোনো ইন্সপেকশন Draft থাকলে সাবমিট করতে দেবে না
        draft_qi = [d.name for d in all_qi if d.docstatus == 0]
        if draft_qi:
            frappe.throw(
                _(f"নিচের Quality Inspection-গুলো এখনও Draft অবস্থায় আছে, আগে এগুলো Submit করুন: <b>{', '.join(draft_qi)}</b>"),
                title=_("Draft Inspection Found"),
            )

        # ৩. কোনো ইন্সপেকশন Rejected থাকলে সাবমিট আটকে দেবে
        rejected_qi = [d.name for d in all_qi if d.status == "Rejected"]
        if rejected_qi:
            frappe.throw(
                _(f"নিচের Quality Inspection-গুলো Rejected হয়েছে, তাই Stock Entry সাবমিট করা যাবে না: <b>{', '.join(rejected_qi)}</b>"),
                title=_("Inspection Rejected"),
            )

        # ৪. উভয় চেকবক্স টিক থাকলে অন্তত ২টি সাবমিটেড ইন্সপেকশন নিশ্চিত করা
        if req_app and req_prod and len(all_qi) < 2:
            frappe.throw(
                _(f"Application এবং Production উভয় ইন্সপেকশনই সম্পন্ন করতে হবে (কমপক্ষে ২টি সাবমিটেড রেকর্ড আবশ্যক)। বর্তমানে সাবমিট আছে: {len(all_qi)}"),
                title=_("Missing Inspection"),
            )