import frappe

no_cache = 1


def get_context(context):
	# Guest access is gated in the template (Jinja checks frappe.session.user),
	# not here — every whitelisted API this page calls also independently
	# rejects Guest sessions, so this is defense in depth, not the only gate.
	context.title = "Bin Lookup"
	context.show_sidebar = False
	context.no_cache = 1
