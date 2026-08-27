import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 250},
        {"label": "Stock Unit", "fieldname": "stock_uom", "fieldtype": "Data", "width": 100},
        {"label": "In Qty", "fieldname": "in_qty", "fieldtype": "Float", "width": 120},
        {"label": "Out Qty", "fieldname": "out_qty", "fieldtype": "Float", "width": 120},
        {"label": "Balance", "fieldname": "balance", "fieldtype": "Float", "width": 120},
        {"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 150},
        {"label": "Item Group", "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 130},
    ]

def get_data(filters):
    query = """
    SELECT 
        sle.posting_date,
        item.item_name,
        sle.stock_uom,
        CASE WHEN sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END AS in_qty,
        CASE WHEN sle.actual_qty < 0 THEN ABS(sle.actual_qty) ELSE 0 END AS out_qty,
        sle.qty_after_transaction AS balance,
        sle.warehouse,
        item.item_group
    FROM `tabStock Ledger Entry` sle
    LEFT JOIN `tabItem` item ON sle.item_code = item.name
    WHERE sle.is_cancelled = 0 
    AND sle.warehouse IN ('Stores - SP', 'PM Warehouse', 'WIP Warehouse')
    """
    
    if filters.get("from_date"):
        query += f" AND sle.posting_date >= '{filters.get('from_date')}'"
    
    if filters.get("to_date"):
        query += f" AND sle.posting_date <= '{filters.get('to_date')}'"
    
    if filters.get("item_name"):
        query += f" AND item.item_name LIKE '%{filters.get('item_name')}%'"
    
    if filters.get("batch_no"):
        query += f" AND sle.batch_no = '{filters.get('batch_no')}'"
    
    query += " ORDER BY sle.posting_date DESC, sle.creation DESC"
    
    return frappe.db.sql(query, as_dict=True)