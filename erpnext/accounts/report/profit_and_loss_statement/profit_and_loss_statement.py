# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt
from erpnext.accounts.report.financial_statements import (get_period_list, get_columns, get_data)

def execute(filters=None):
	period_list = get_period_list(filters.fiscal_year, filters.periodicity)

	income = get_data(filters.company, "Income", "Credit", period_list, filters.accumulated_value, ignore_closing_entries=True)
	expense = get_data(filters.company, "Expense", "Debit", period_list, filters.accumulated_value, ignore_closing_entries=True)
	net_profit_loss = get_net_profit_loss(income, expense, period_list)

	data = []
	data.extend(income or [])
	data.extend(expense or [])
	if net_profit_loss:
		data.append(net_profit_loss)

	columns = get_columns(filters.periodicity,period_list,filters.accumulated_value)

	return columns, data

def get_net_profit_loss(income, expense, period_list):
	if income and expense:
		total_column=0
		net_profit_loss = {
			"account_name": "'" + _("Net Profit / Loss") + "'",
			"account": None,
			"warn_if_negative": True
		}
		has_value = False

		for period in period_list:
			net_profit_loss[period.key] = flt(income[-2][period.key] - expense[-2][period.key], 3)
			
			if net_profit_loss[period.key]:
				has_value=True
			
			total_column=total_column+net_profit_loss[period.key]
			net_profit_loss["total"]=total_column
		
		if has_value:

			return net_profit_loss
