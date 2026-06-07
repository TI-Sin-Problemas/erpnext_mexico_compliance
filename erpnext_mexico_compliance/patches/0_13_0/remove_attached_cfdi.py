import frappe


def execute():
	"""Remove attached CFDI files"""
	File = frappe.qb.DocType("File")
	query = frappe.qb.get_query(
		File,
		fields=["name"],
		filters=[
			["file_name", "like", "%CFDI%"],
			"and",
			[["file_name", "like", "%.pdf"], "or", ["file_name", "like", "%.xml"]],
			"and",
			["attached_to_doctype", "in", ["Sales Invoice", "Payment Entry"]],
		],
	)

	for file_name in query.run(pluck="name"):
		frappe.delete_doc("File", file_name)
