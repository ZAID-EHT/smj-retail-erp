"""Controlled collaboration adapters for allowlisted generated documents."""

from __future__ import annotations

import json
from urllib.parse import quote

import frappe
from frappe import _
from frappe.utils import cint, getdate, validate_email_address
from frappe.utils.html_utils import sanitize_html

from my_store_ui.universal.api import _get_permitted_doc, _require_login, _readable_fields
from my_store_ui.universal.registry import get_generated_feature


MAX_COMMENT_LENGTH = 10000
MAX_EMAIL_RECIPIENTS = 20
MAX_TAGS = 20


def _context(feature: str, name: str, permission: str = "read"):
	record = get_generated_feature(feature)
	doc = _get_permitted_doc(record["doctype"], name, permission)
	return record, doc


def _can(doc, permission: str) -> bool:
	return bool(frappe.has_permission(doc.doctype, permission, doc=doc))


def _version_summaries(doc) -> list[dict]:
	if not doc.meta.track_changes:
		return []
	from frappe.desk.form.load import get_versions
	readable = {field.fieldname for field in _readable_fields(doc.meta)}
	result = []
	for row in get_versions(doc):
		changed = []
		try:
			data = json.loads(row.get("data") or "{}")
			for change in data.get("changed", []):
				if change and change[0] in readable:
					changed.append(change[0])
		except (TypeError, ValueError):
			pass
		result.append({"name": row.name, "owner": row.owner, "creation": row.creation, "changed_fields": changed})
	return result


@frappe.whitelist(methods=["GET"])
def get_collaboration_state(feature: str, name: str):
	_require_login()
	_record, doc = _context(feature, name)
	from frappe.desk.form.load import get_assignments, get_attachments, get_comments, get_tags
	attachments = [
		{"name": row.name, "file_name": row.file_name, "file_url": row.file_url, "is_private": bool(row.is_private), "download_url": row.file_url}
		for row in get_attachments(doc.doctype, doc.name)
	]
	comments = [
		{"name": row.name, "content": row.content, "owner": row.owner, "creation": row.creation}
		for row in get_comments(doc.doctype, doc.name)
	]
	can_share = _can(doc, "share")
	shares = []
	if can_share:
		from frappe.share import get_users
		shares = [{key: row.get(key) for key in ("name", "user", "read", "write", "submit", "share", "everyone")} for row in get_users(doc.doctype, doc.name)]
	permissions = {
		"can_comment": _can(doc, "read"), "can_attach": _can(doc, "write"),
		"can_remove_attachment": _can(doc, "write"), "can_assign": _can(doc, "write"),
		"can_share": can_share, "can_tag": _can(doc, "write"), "can_email": _can(doc, "email"),
		"can_print": _can(doc, "print"),
	}
	return {
		"attachments": attachments, "comments": comments,
		"assignments": get_assignments(doc.doctype, doc.name), "shares": shares,
		"tags": [tag for tag in (get_tags(doc.doctype, doc.name) or "").split(",") if tag],
		"versions": _version_summaries(doc), "permissions": permissions,
		"upload": {"endpoint": "/api/method/upload_file", "doctype": doc.doctype, "docname": doc.name, "is_private": 1},
	}


@frappe.whitelist(methods=["POST"])
def add_comment(feature: str, name: str, content: str):
	_require_login()
	_record, doc = _context(feature, name)
	content = sanitize_html(str(content or "").strip(), always_sanitize=True)
	if not content or len(content) > MAX_COMMENT_LENGTH:
		frappe.throw(_("Comment is empty or too long."), frappe.ValidationError)
	comment = doc.add_comment("Comment", text=content)
	return {"name": comment.name, "content": comment.content, "owner": comment.owner, "creation": comment.creation}


@frappe.whitelist(methods=["POST"])
def remove_attachment(feature: str, name: str, file_name: str):
	_require_login()
	_record, doc = _context(feature, name, "write")
	files = frappe.get_list("File", filters={"name": file_name, "attached_to_doctype": doc.doctype, "attached_to_name": doc.name}, pluck="name", limit_page_length=1)
	if not files:
		frappe.throw(_("Attachment was not found or is unavailable."), frappe.DoesNotExistError)
	frappe.delete_doc("File", files[0])
	return {"removed": True}


@frappe.whitelist(methods=["GET"])
def search_assignment_users(feature: str, name: str, search: str = ""):
	_require_login()
	_context(feature, name, "write")
	search = (search or "").strip()[:140]
	rows = frappe.get_list("User", filters={"enabled": 1, "user_type": "System User"}, or_filters=[["name", "like", f"%{search}%"], ["full_name", "like", f"%{search}%"]] if search else None, fields=["name", "full_name", "user_image"], limit_page_length=20)
	return {"results": [{"value": row.name, "label": row.full_name or row.name, "image": row.user_image} for row in rows]}


@frappe.whitelist(methods=["POST"])
def add_assignment(feature: str, name: str, user: str, due_date: str | None = None, description: str | None = None):
	_require_login()
	_record, doc = _context(feature, name, "write")
	if not frappe.get_list("User", filters={"name": user, "enabled": 1, "user_type": "System User"}, pluck="name", limit_page_length=1):
		frappe.throw(_("Assignee is not available."), frappe.PermissionError)
	from frappe.desk.form.assign_to import add
	args = {"assign_to": json.dumps([user]), "doctype": doc.doctype, "name": doc.name, "description": str(description or "")[:1000]}
	if due_date:
		args["date"] = str(getdate(due_date))
	return add(args)


@frappe.whitelist(methods=["POST"])
def remove_assignment(feature: str, name: str, user: str):
	_require_login()
	_record, doc = _context(feature, name, "write")
	from frappe.desk.form.assign_to import remove
	return remove(doc.doctype, doc.name, user)


@frappe.whitelist(methods=["POST"])
def add_share(feature: str, name: str, user: str, write: int = 0, submit: int = 0, share: int = 0):
	_require_login()
	_record, doc = _context(feature, name)
	if not _can(doc, "share"):
		frappe.throw(_("Sharing is not available."), frappe.PermissionError)
	if not frappe.get_list("User", filters={"name": user, "enabled": 1}, pluck="name", limit_page_length=1):
		frappe.throw(_("User is not available."), frappe.PermissionError)
	from frappe.share import add
	row = add(doc.doctype, doc.name, user=user, read=1, write=cint(write), submit=cint(submit), share=cint(share), notify=0)
	return {"name": row.name, "user": row.user, "read": row.read, "write": row.write, "submit": row.submit, "share": row.share}


@frappe.whitelist(methods=["POST"])
def remove_share(feature: str, name: str, user: str):
	_require_login()
	_record, doc = _context(feature, name)
	if not _can(doc, "share"):
		frappe.throw(_("Sharing is not available."), frappe.PermissionError)
	from frappe.share import remove
	remove(doc.doctype, doc.name, user)
	return {"removed": True}


@frappe.whitelist(methods=["POST"])
def set_tags(feature: str, name: str, tags):
	_require_login()
	_record, doc = _context(feature, name, "write")
	if isinstance(tags, str):
		try:
			tags = json.loads(tags)
		except ValueError:
			tags = [value.strip() for value in tags.split(",") if value.strip()]
	if not isinstance(tags, list) or len(tags) > MAX_TAGS:
		frappe.throw(_("Tags have an invalid format."), frappe.ValidationError)
	clean = []
	for tag in tags:
		tag = str(tag).strip()[:100]
		if tag and tag not in clean:
			clean.append(tag)
	from frappe.desk.doctype.tag.tag import DocTags
	DocTags(doc.doctype).remove_all(doc.name)
	for tag in clean:
		doc.add_tag(tag)
	return {"tags": clean}


@frappe.whitelist(methods=["POST"])
def email_document(feature: str, name: str, recipients, subject: str, message: str, attach_pdf: int = 0, print_format: str = "Standard", letterhead: str | None = None, language: str | None = None):
	_require_login()
	_record, doc = _context(feature, name)
	if not _can(doc, "email"):
		frappe.throw(_("Email is not available."), frappe.PermissionError)
	if isinstance(recipients, str):
		try:
			recipients = json.loads(recipients)
		except ValueError:
			recipients = [value.strip() for value in recipients.replace(";", ",").split(",") if value.strip()]
	if not isinstance(recipients, list) or not recipients or len(recipients) > MAX_EMAIL_RECIPIENTS:
		frappe.throw(_("Recipients are required."), frappe.ValidationError)
	clean_recipients = [validate_email_address(str(value), throw=True) for value in recipients]
	attachments = []
	if cint(attach_pdf):
		if not _can(doc, "print"):
			frappe.throw(_("You cannot attach a PDF for this document."), frappe.PermissionError)
		try:
			attachments.append(frappe.attach_print(doc.doctype, doc.name, print_format=print_format, letterhead=letterhead, lang=language))
		except OSError:
			frappe.throw(_("PDF generation is unavailable because the configured PDF executable is missing."), frappe.ValidationError)
	frappe.sendmail(recipients=clean_recipients, subject=str(subject or doc.name)[:500], message=sanitize_html(str(message or ""), always_sanitize=True), attachments=attachments, reference_doctype=doc.doctype, reference_name=doc.name)
	return {"queued": True, "recipients": len(clean_recipients)}
