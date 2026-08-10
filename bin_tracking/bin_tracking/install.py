import frappe


def after_install():
	"""Run after app installation"""
	frappe.msgprint("Bin Tracking app installed successfully!")
	# You can add initialization code here


def before_uninstall():
	"""Run before app uninstallation"""
	pass
