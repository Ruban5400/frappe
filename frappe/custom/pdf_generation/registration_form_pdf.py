import frappe
from frappe.utils.pdf import get_pdf
from frappe.www.printview import get_rendered_template

@frappe.whitelist()
def generate_pdf(docname):
    doc = frappe.get_doc("Registration Form", docname)

    # Render your custom HTML with dynamic values
    template = frappe.render_template("frappe/custom/pdf_templates/registration_template.html", {
        "organisation": doc.name_of_the_organisation,
        "registration_no": doc.registration_no,
        "valid_upto": "28 January 2026"
    })

    pdf_content = get_pdf(template)
    
    file_name = f"{docname}-Membership-Certificate.pdf"
    file_path = frappe.get_site_path("public", "files", file_name)

    with open(file_path, "wb") as f:
        f.write(pdf_content)

    return {
        "pdf_url": f"/files/{file_name}"
    }
