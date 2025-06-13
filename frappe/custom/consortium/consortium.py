import frappe
import json
import requests

def before_save(doc, method):
    if doc.status != "Draft":
        return

    api_key = frappe.conf.get("docuseal_api_key")
    template_id = frappe.conf.get("docuseal_template_id")

    if not api_key or not template_id:
        frappe.throw("Docuseal API Key or Template ID is missing in site_config.json")

    for member in doc.members:
        if member.docuseal_submission_id:
            continue  # Already sent, skip

        payload = {
            "template_id": template_id,
            "merge_fields": {
                "projects": doc.projects,
                "user_id": member.user_id,
                "user_name": member.user_name
            },
            "submitters": [
                {
                    "email": member.user_id,
                    "name": member.user_name,
                    "role": "Signer"
                }
            ]
        }

        try:
            response = requests.post(
                url="https://api.docuseal.com/submissions",
                headers={
                    "X-Auth-Token": api_key,
                    "Content-Type": "application/json"
                },
                json=payload
            )
            response.raise_for_status()
            result = response.json()

            if isinstance(result, list) and result:
                submission_id = result[0].get("id")
                embed_url = result[0].get("embed_src")

                member.docuseal_submission_id = submission_id
                member.docuseal_document_url = embed_url  # ✅ store the actual usable URL

                frappe.msgprint(
                    f"Document sent to {member.user_name}<br>"
                    f"Submission ID: {submission_id}<br>"
                    f"URL: <a href='{embed_url}' target='_blank'>{embed_url or 'No URL available'}</a>"
                )
            else:
                frappe.msgprint(f"Document sent to {member.user_name}, but no valid submission returned: {result}")

        except Exception:
            frappe.log_error(frappe.get_traceback(), "Docuseal Integration Error")
            frappe.throw(f"Failed to send document to {member.user_name}. Check error logs.")
