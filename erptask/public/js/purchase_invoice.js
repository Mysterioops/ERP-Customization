//####################
// Customization
//####################

frappe.ui.form.on('Purchase Invoice', {
    refresh: update_indicator,
    supplier: update_indicator,
    grand_total: update_indicator
});

frappe.ui.form.on('Purchase Invoice Item', {
    item_code: (frm) => update_indicator(frm),
    qty: (frm) => update_indicator(frm),
    rate: (frm) => update_indicator(frm),
    amount: (frm) => update_indicator(frm),
    items_add: (frm) => update_indicator(frm),
    items_remove: (frm) => update_indicator(frm)
});

function update_indicator(frm) {
    const field = frm.fields_dict.custom_purchase_limit_indicator;
    if (!field) return;

    if (!frm.doc.supplier) {
        field.$wrapper.html("");
        return;
    }

    frappe.db.get_value("Supplier", frm.doc.supplier, "custom_max_purchase").then(r => {
        let max = (r && r.message && r.message.custom_max_purchase) || 0;
        let total = frm.doc.grand_total || 0;

        let color = "grey";
        let message = "No purchase limit configured for this supplier";

        if (max) {
            let is_within = total <= max;

            color = is_within ? "green" : "red";
            message = is_within
                ? "Within supplier purchase limit"
                : "Supplier maximum purchase limit reached";
        }

        field.$wrapper.html(`
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="
                    width:12px;
                    height:12px;
                    border-radius:50%;
                    background:${color};
                "></span>
                <span style="font-weight:500;">${message}</span>
            </div>
        `);
    });
}
