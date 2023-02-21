# -*- coding: utf-8 -*-

from enum import unique, Enum


class Field(Enum):
    pass


@unique
class Valuation(Field):
    """
    估值指标
    tev: total enterprice value
    bv: book value
    tangbv: tangible book value
    fcf: free cashflow
    excl: exclued
    extra: extraordinary
    """
    tev_to_ltm_total_revenues = "tev_to_ltm_total_revenues"
    tev_to_ltm_ebitda = "tev_to_ltm_ebitda"
    tev_to_ltm_ebit = "tev_to_ltm_ebit"
    p_to_ltm_diluted_eps_before_extra = "p_to_ltm_diluted_eps_before_extra"
    p_to_bv = "p_to_bv"
    p_to_tangbv = "p_to_tangbv"
    market_cap_to_ltm_total_revenues = "market_cap_to_ltm_total_revenues"
    market_cap_to_ltm_ebt_excl_unusual_items = "market_cap_to_ltm_ebt_excl_unusual_items"
    tev_to_ltm_unlevered_fcf = "tev_to_ltm_unlevered_fcf"
    market_cap_to_ltm_levered_fcf = "market_cap_to_ltm_levered_fcf"
    total_enterprise_value = "total_enterprise_value"
    market_capitalization = "market_capitalization"
    shares_outstanding = "shares_outstanding"


@unique
class Income(Field):
    """
    利润表
    """
    # gross profit
    total_revenue = "total_revenue"
    revenues = "revenues"
    other_revenues_total = "other_revenues_total"
    finance_div_revenues = "finance_div_revenues"
    insurance_div_revenues = "insurance_div_revenues"
    gain_loss_on_sale_of_assets_rev = "gain_loss_on_sale_of_assets_rev"
    gain_loss_on_sale_of_invest_rev = "gain_loss_on_sale_of_invest_rev"
    interest_and_invest_income_rev = "interest_and_invest_income_rev"
    other_revenues = "other_revenues"
    cost_of_revenues = "cost_of_revenues"
    cost_of_goods_sold = "cost_of_goods_sold"
    finance_div_operating_exp = "finance_div_operating_exp"
    insurance_div_operating_exp = "insurance_div_operating_exp"
    interest_expensefinance_division = "interest_expensefinance_division"
    gross_profit = "gross_profit"

    # operating income
    sga_exp_total = "sga_exp_total"
    selling_general_admin_exp = "selling_general_admin_exp"
    explorationdrilling_costs = "explorationdrilling_costs"
    provision_for_bad_debts = "provision_for_bad_debts"
    stock_based_compensation = "stock_based_compensation"
    pre_opening_costs = "pre_opening_costs"
    rd_exp = "rd_exp"
    depreciation_amort_total = "depreciation_amort_total"
    depreciation_amort = "depreciation_amort"
    amort_of_goodwill_and_intangibles = "amort_of_goodwill_and_intangibles"
    impair_of_oil_gas_mineral_prop = "impair_of_oil_gas_mineral_prop"
    other_operating_expense_income = "other_operating_expense_income"
    other_operating_exp_total = "other_operating_exp_total"
    total_operating_expenses = "total_operating_expenses"
    operating_income = "operating_income"

    # net income
    interest_expense = "interest_expense"
    interest_and_invest_income = "interest_and_invest_income"
    interest_and_dividend_income = "interest_and_dividend_income"
    investment_income = "investment_income"
    net_interest_exp = "net_interest_exp"
    other_non_operating_exp_total = "other_non_operating_exp_total"
    income_loss_from_affiliates = "income_loss_from_affiliates"
    currency_exchange_gains_loss = "currency_exchange_gains_loss"
    other_non_operating_inc_exp = "other_non_operating_inc_exp"
    ebt_excl_unusual_items = "ebt_excl_unusual_items"
    merger_restruct_charges = "merger_restruct_charges"
    restructuring_charges = "restructuring_charges"
    merger_related_restruct_charges = "merger_related_restruct_charges"
    impairment_of_goodwill = "impairment_of_goodwill"
    gain_loss_on_sale_of_invest = "gain_loss_on_sale_of_invest"
    gain_loss_on_sale_of_assets = "gain_loss_on_sale_of_assets"
    other_unusual_items_total = "other_unusual_items_total"
    asset_writedown = "asset_writedown"
    in_process_rd_exp = "in_process_rd_exp"
    insurance_settlements = "insurance_settlements"
    legal_settlements = "legal_settlements"
    other_unusual_items = "other_unusual_items"
    total_unusual_items = "total_unusual_items"
    ebt_incl_unusual_items = "ebt_incl_unusual_items"
    income_tax_expense = "income_tax_expense"
    earnings_from_cont_ops = "earnings_from_cont_ops"
    earnings_of_discontinued_ops = "earnings_of_discontinued_ops"
    extraord_item_account_change = "extraord_item_account_change"
    other_expenses_including_taxes_private_only = "other_expenses_including_taxes_private_only"
    net_income_to_company = "net_income_to_company"
    minority_int_in_earnings = "minority_int_in_earnings"
    net_income = "net_income"
    pref_dividends_and_other_adj = "pref_dividends_and_other_adj"
    ni_to_common_incl_extra_items = "ni_to_common_incl_extra_items"
    ni_to_common_excl_extra_items = "ni_to_common_excl_extra_items"

    # per share items
    basic_eps = "basic_eps"
    basic_eps_excl_extra_items = "basic_eps_excl_extra_items"
    weighted_avg_shares_outstanding = "weighted_avg_shares_outstanding"
    diluted_eps_incl_extra_items = "diluted_eps_incl_extra_items"
    diluted_eps_excl_extra_items = "diluted_eps_excl_extra_items"
    weighted_avg_diluted_shares_out = "weighted_avg_diluted_shares_out"
    normalized_basic_eps = "normalized_basic_eps"
    normalized_diluted_eps = "normalized_diluted_eps"
    dividends_per_share = "dividends_per_share"
    gross_dividends_per_share = "gross_dividends_per_share"
    net_dividends_per_share = "net_dividends_per_share"
    special_gross_dividends_per_share = "special_gross_dividends_per_share"
    special_net_dividends_per_share = "special_net_dividends_per_share"

    # supplemental items
    corporate_tax_rate = "corporate_tax_rate"
    imputed_dividend_amount = "imputed_dividend_amount"
    imputation_percentage = "imputation_percentage"
    imputation_credit_amount = "imputation_credit_amount"
    special_dividend_imputed_dividend_amount = "special_dividend_imputed_dividend_amount"
    special_dividend_imputation_percentage = "special_dividend_imputation_percentage"
    special_dividend_imputation_credit_amount = "special_dividend_imputation_credit_amount"
    payout_ratio = "payout_ratio"
    ebitda = "ebitda"
    ebita = "ebita"
    ebit = "ebit"
    ebitdar = "ebitdar"
    ebitda_incl_equity_inc_from_affiliates = "ebitda_incl_equity_inc_from_affiliates"
    ebita_incl_equity_inc_from_affiliates = "ebita_incl_equity_inc_from_affiliates"
    ebit_incl_equity_inc_from_affiliates = "ebit_incl_equity_inc_from_affiliates"
    ebitdar_incl_equity_inc_from_affiliates = "ebitdar_incl_equity_inc_from_affiliates"
    ebitda_excl_sbc_and_incl_equity_inc_from_affiliates = "ebitda_excl_sbc_and_incl_equity_inc_from_affiliates"
    ebita_excl_sbc_and_incl_equity_inc_from_affiliates = "ebita_excl_sbc_and_incl_equity_inc_from_affiliates"
    ebit_excl_sbc_and_incl_equity_inc_from_affiliates = "ebit_excl_sbc_and_incl_equity_inc_from_affiliates"
    ebitdar_excl_sbc_and_incl_equity_inc_from_affiliates = "ebitdar_excl_sbc_and_incl_equity_inc_from_affiliates"
    ebitda_excl_sbc = "ebitda_excl_sbc"
    ebita_excl_sbc = "ebita_excl_sbc"
    ebit_excl_sbc = "ebit_excl_sbc"
    ebitdar_excl_sbc = "ebitdar_excl_sbc"
    ebitdacapex = "ebitdacapex"
    effective_tax_rate = "effective_tax_rate"
    normalized_net_income = "normalized_net_income"
    owned_operated_same_store_sales_growth = "owned_operated_same_store_sales_growth"
    as_reported_total_revenue = "as_reported_total_revenue"
    provision_for_doubtful_accountspatient_service_revenue = "provision_for_doubtful_accountspatient_service_revenue"
    ni_per_sfas_123_after_options = "ni_per_sfas_123_after_options"
    advertising_expense = "advertising_expense"
    marketing_expense = "marketing_expense"
    selling_and_marketing_expense = "selling_and_marketing_expense"
    general_and_administrative_expense = "general_and_administrative_expense"
    rd_expense = "rd_expense"
    net_rental_expense_total = "net_rental_expense_total"
    minimum_rental_expense = "minimum_rental_expense"
    depreciation_of_rental_assets = "depreciation_of_rental_assets"
    revenues_per_share = "revenues_per_share"
    total_revenues_employee = "total_revenues_employee"
    diluted_net_income = "diluted_net_income"
    imputed_oper_lease_interest_exp = "imputed_oper_lease_interest_exp"
    imputed_oper_lease_depreciation = "imputed_oper_lease_depreciation"
    stock_based_comp_cogs = "stock_based_comp_cogs"
    stock_based_comp_rd_exp = "stock_based_comp_rd_exp"
    stock_based_comp_sm_exp = "stock_based_comp_sm_exp"
    stock_based_comp_ga_exp = "stock_based_comp_ga_exp"
    stock_based_comp_sga_exp = "stock_based_comp_sga_exp"
    stock_based_comp_unallocated = "stock_based_comp_unallocated"
    stock_based_comp_after_tax = "stock_based_comp_after_tax"
    stock_based_comp_total = "stock_based_comp_total"
    non_cash_pension_expense = "non_cash_pension_expense"
    distributable_cash = "distributable_cash"
    standardized_distributable_cash = "standardized_distributable_cash"
    distributable_cash_per_share = "distributable_cash_per_share"
    annualized_distributions_per_unit = "annualized_distributions_per_unit"
    distributable_cash_payout_ratio_income_trusts = "distributable_cash_payout_ratio_income_trusts"
    debt_issuance_costs = "debt_issuance_costs"
    period_date_income_statement = "period_date_income_statement"
    filing_date_income_statement = "filing_date_income_statement"
    financial_accounting_standard = "financial_accounting_standard"
    filing_currency = "filing_currency"


@unique
class Balance(Field):
    """
    资产负债表
    """
    # assets
    cash_and_equivalents = "cash_and_equivalents"
    short_term_investments = "short_term_investments"
    trading_asset_securities = "trading_asset_securities"
    total_cash_st_investments = "total_cash_st_investments"
    accounts_receivable = "accounts_receivable"
    other_receivables = "other_receivables"
    notes_receivable = "notes_receivable"
    total_receivables = "total_receivables"
    inventory = "inventory"
    prepaid_exp = "prepaid_exp"
    finance_div_loans_and_leases_st = "finance_div_loans_and_leases_st"
    finance_div_other_curr_assets = "finance_div_other_curr_assets"
    other_current_assets_total = "other_current_assets_total"
    loans_held_for_sale = "loans_held_for_sale"
    deferred_tax_assets_curr = "deferred_tax_assets_curr"
    restricted_cash = "restricted_cash"
    other_current_assets = "other_current_assets"
    total_current_assets = "total_current_assets"
    gross_property_plant_equipment = "gross_property_plant_equipment"
    accumulated_depreciation = "accumulated_depreciation"
    net_property_plant_equipment = "net_property_plant_equipment"
    longterm_investments = "longterm_investments"
    goodwill = "goodwill"
    other_intangibles = "other_intangibles"
    finance_div_loans_and_leases_lt = "finance_div_loans_and_leases_lt"
    finance_div_other_lt_assets = "finance_div_other_lt_assets"
    other_assets_total = "other_assets_total"
    capitalizedpurchased_software = "capitalizedpurchased_software"
    accounts_receivable_longterm = "accounts_receivable_longterm"
    loans_receivable_longterm = "loans_receivable_longterm"
    deferred_tax_assets_lt = "deferred_tax_assets_lt"
    deferred_charges_lt = "deferred_charges_lt"
    other_longterm_assets = "other_longterm_assets"
    total_assets = "total_assets"

    # liabilities
    accounts_payable = "accounts_payable"
    accrued_exp = "accrued_exp"
    total_shortterm_borrowings = "total_shortterm_borrowings"
    curr_port_of_lt_debtcap_leases = "curr_port_of_lt_debtcap_leases"
    curr_port_of_long_term_debt = "curr_port_of_long_term_debt"
    curr_port_of_cap_leases = "curr_port_of_cap_leases"
    finance_div_debt_current = "finance_div_debt_current"
    finance_div_other_curr_liab = "finance_div_other_curr_liab"
    other_current_liabilities_total = "other_current_liabilities_total"
    curr_income_taxes_payable = "curr_income_taxes_payable"
    unearned_revenue_current = "unearned_revenue_current"
    def_tax_liability_curr = "def_tax_liability_curr"
    other_current_liabilities = "other_current_liabilities"
    total_current_liabilities = "total_current_liabilities"
    longterm_debt = "longterm_debt"
    capital_leases = "capital_leases"
    finance_div_debt_noncurr = "finance_div_debt_noncurr"
    finance_div_other_noncurr_liab = "finance_div_other_noncurr_liab"
    other_liabilities_total = "other_liabilities_total"
    unearned_revenue_noncurrent = "unearned_revenue_noncurrent"
    pension_other_postretire_benefits = "pension_other_postretire_benefits"
    def_tax_liability_noncurr = "def_tax_liability_noncurr"
    other_noncurrent_liabilities = "other_noncurrent_liabilities"
    total_liabilities = "total_liabilities"

    # equity
    pref_stock_redeemable = "pref_stock_redeemable"
    pref_stock_nonredeem = "pref_stock_nonredeem"
    pref_stock_convertible = "pref_stock_convertible"
    pref_stock_other = "pref_stock_other"
    common_stock = "common_stock"
    total_pref_equity = "total_pref_equity"
    common_stock_apic = "common_stock_apic"
    additional_paid_in_capital = "additional_paid_in_capital"
    retained_earnings = "retained_earnings"
    treasury_stock_other = "treasury_stock_other"
    treasury_stock = "treasury_stock"
    comprehensive_inc_and_other = "comprehensive_inc_and_other"
    total_common_equity = "total_common_equity"
    minority_interest = "minority_interest"
    total_equity = "total_equity"
    total_liabilities_and_equity = "total_liabilities_and_equity"

    # supplemental
    number_of_equity_capital_structure_share_classes = "number_of_equity_capital_structure_share_classes"
    total_shares_out_on_filing_date = "total_shares_out_on_filing_date"
    total_shares_out_on_balance_sheet_date = "total_shares_out_on_balance_sheet_date"
    book_valueshare = "book_valueshare"
    book_valueshare_reported = "book_valueshare_reported"
    tangible_book_value = "tangible_book_value"
    tangible_book_valueshare = "tangible_book_valueshare"
    tangible_book_valueshare_reported = "tangible_book_valueshare_reported"
    total_intangibles = "total_intangibles"
    total_debt = "total_debt"
    total_current_debt = "total_current_debt"
    total_noncurrent_debt = "total_noncurrent_debt"
    net_debt = "net_debt"
    total_redeemable_minority_interest = "total_redeemable_minority_interest"
    total_minority_interest = "total_minority_interest"
    cash_per_share = "cash_per_share"
    total_capital = "total_capital"
    working_capital = "working_capital"
    net_working_capital = "net_working_capital"
    liquidation_value_of_preferred_stock_convertible = "liquidation_value_of_preferred_stock_convertible"
    liquidation_value_of_preferred_stock_nonredeemable = "liquidation_value_of_preferred_stock_nonredeemable"
    liquidation_value_of_preferred_stock_redeemable = "liquidation_value_of_preferred_stock_redeemable"
    buildings = "buildings"
    land = "land"
    lifo_reserve = "lifo_reserve"
    machinery = "machinery"
    employees_under_union_contracts = "employees_under_union_contracts"
    parttime_employees = "parttime_employees"
    total_employees = "total_employees"
    equity_method_investments = "equity_method_investments"
    finished_goods_inventory = "finished_goods_inventory"
    full_time_employees = "full_time_employees"
    raw_materials_inventory = "raw_materials_inventory"
    work_in_progress_inventory = "work_in_progress_inventory"
    construction_in_progress = "construction_in_progress"
    debt_equivalent_oper_leases = "debt_equivalent_oper_leases"
    debt_equivalent_of_unfunded_pbo = "debt_equivalent_of_unfunded_pbo"
    cost_of_borrowing = "cost_of_borrowing"
    accounts_receivables_unbilled = "accounts_receivables_unbilled"
    period_date_balance_sheet = "period_date_balance_sheet"
    filing_date_balance_sheet = "filing_date_balance_sheet"


@unique
class CashFlow(Field):
    """
    现金流量表
    """
    # operating cashflow
    net_income_cf = "net_income_cf"
    depreciation_amort_cf = "depreciation_amort_cf"
    amort_of_goodwill_and_intangibles_cf = "amort_of_goodwill_and_intangibles_cf"
    impair_of_oil_gas_mineral_prop_cf = "impair_of_oil_gas_mineral_prop_cf"
    depreciation_amort_total_cf = "depreciation_amort_total_cf"
    other_amortization = "other_amortization"
    other_noncash_items_total = "other_noncash_items_total"
    minority_int_in_earnings_cf = "minority_int_in_earnings_cf"
    gain_loss_from_sale_of_asset = "gain_loss_from_sale_of_asset"
    gain_loss_on_sale_of_invest_cf = "gain_loss_on_sale_of_invest_cf"
    asset_writedown_restructuring_costs = "asset_writedown_restructuring_costs"
    net_increase_decrease_in_loans_origsold = "net_increase_decrease_in_loans_origsold"
    provision_for_credit_losses = "provision_for_credit_losses"
    income_loss_on_equity_invest = "income_loss_on_equity_invest"
    stockbased_compensation = "stockbased_compensation"
    tax_benefit_from_stock_options = "tax_benefit_from_stock_options"
    provision_writeoff_of_bad_debts = "provision_writeoff_of_bad_debts"
    net_cash_from_discontinued_ops = "net_cash_from_discontinued_ops"
    other_operating_activities = "other_operating_activities"
    change_in_net_operating_assets = "change_in_net_operating_assets"
    change_in_trad_asset_securities = "change_in_trad_asset_securities"
    change_in_accounts_receivable = "change_in_accounts_receivable"
    change_in_inventories = "change_in_inventories"
    change_in_acc_payable = "change_in_acc_payable"
    change_in_unearned_rev = "change_in_unearned_rev"
    change_in_inc_taxes = "change_in_inc_taxes"
    change_in_def_taxes = "change_in_def_taxes"
    change_in_other_net_operating_assets = "change_in_other_net_operating_assets"
    cash_from_ops = "cash_from_ops"

    # investing cashflow
    capital_expenditure = "capital_expenditure"
    sale_of_property_plant_and_equipment = "sale_of_property_plant_and_equipment"
    cash_acquisitions = "cash_acquisitions"
    divestitures = "divestitures"
    other_investing_activities_total = "other_investing_activities_total"
    sale_purchase_of_real_estate_properties = "sale_purchase_of_real_estate_properties"
    sale_purchase_of_intangible_assets = "sale_purchase_of_intangible_assets"
    invest_in_marketable_equity_securt = "invest_in_marketable_equity_securt"
    net_inc_dec_in_loans_originatedsold = "net_inc_dec_in_loans_originatedsold"
    other_investing_activities = "other_investing_activities"
    cash_from_investing = "cash_from_investing"

    # financing cashflow
    short_term_debt_issued = "short_term_debt_issued"
    longterm_debt_issued = "longterm_debt_issued"
    total_debt_issued = "total_debt_issued"
    short_term_debt_repaid = "short_term_debt_repaid"
    longterm_debt_repaid = "longterm_debt_repaid"
    total_debt_repaid = "total_debt_repaid"
    issuance_of_common_stock = "issuance_of_common_stock"
    repurchase_of_common_stock = "repurchase_of_common_stock"
    issuance_of_preferred_stock = "issuance_of_preferred_stock"
    repurchase_of_preferred_stock = "repurchase_of_preferred_stock"
    common_dividends_paid = "common_dividends_paid"
    pref_dividends_paid = "pref_dividends_paid"
    common_andor_pref_dividends_paid = "common_andor_pref_dividends_paid"
    total_dividends_paid = "total_dividends_paid"
    other_financing_activities_total = "other_financing_activities_total"
    special_dividend_paid = "special_dividend_paid"
    other_financing_activities = "other_financing_activities"
    cash_from_financing = "cash_from_financing"

    # summary
    foreign_exchange_rate_adj = "foreign_exchange_rate_adj"
    misc_cash_flow_adj = "misc_cash_flow_adj"
    net_change_in_cash = "net_change_in_cash"

    # supplementals
    cash_interest_paid = "cash_interest_paid"
    cash_taxes_paid = "cash_taxes_paid"
    levered_free_cash_flow = "levered_free_cash_flow"
    unlevered_free_cash_flow = "unlevered_free_cash_flow"
    cash_flow_per_share = "cash_flow_per_share"
    change_in_net_working_capital = "change_in_net_working_capital"
    net_debt_issued = "net_debt_issued"
    maintenance_capex = "maintenance_capex"
    depreciation_of_rental_assets_cf = "depreciation_of_rental_assets_cf"
    sale_proceeds_from_rental_assets = "sale_proceeds_from_rental_assets"
    period_date_cash_flow = "period_date_cash_flow"
    filing_date_cash_flow = "filing_date_cash_flow"


@unique
class BalanceSheetRatio(Field):
    """
    资产负债表相关比率
    """
    total_asset_turnover = "total_asset_turnover"
    fixed_asset_turnover = "fixed_asset_turnover"
    accounts_receivable_turnover = "accounts_receivable_turnover"
    inventory_turnover = "inventory_turnover"
    current_ratio = "current_ratio"
    quick_ratio = "quick_ratio"
    avg_days_sales_out = "avg_days_sales_out"
    avg_days_inventory_out = "avg_days_inventory_out"
    avg_days_payable_out = "avg_days_payable_out"
    avg_cash_conversion_cycle = "avg_cash_conversion_cycle"


@unique
class Growth(Field):
    """
    成长能力
    """
    total_revenues_1_yr_growth = "total_revenues_1_yr_growth"
    gross_profit_1_yr_growth = "gross_profit_1_yr_growth"
    ebitda_1_yr_growth = "ebitda_1_yr_growth"
    ebita_1_yr_growth = "ebita_1_yr_growth"
    ebit_1_yr_growth = "ebit_1_yr_growth"
    earnings_from_cont_ops_1_yr_growth = "earnings_from_cont_ops_1_yr_growth"
    net_income_1_yr_growth = "net_income_1_yr_growth"
    normalized_net_income_1_yr_growth = "normalized_net_income_1_yr_growth"
    diluted_eps_before_extra_1_yr_growth = "diluted_eps_before_extra_1_yr_growth"
    accounts_receivable_1_yr_growth = "accounts_receivable_1_yr_growth"
    inventory_1_yr_growth = "inventory_1_yr_growth"
    net_ppe_1_yr_growth = "net_ppe_1_yr_growth"
    common_equity_1_yr_growth = "common_equity_1_yr_growth"
    total_assets_1_yr_growth = "total_assets_1_yr_growth"
    tangible_book_value_1_yr_growth = "tangible_book_value_1_yr_growth"
    cash_from_operations_1_yr_growth = "cash_from_operations_1_yr_growth"
    capital_expenditures_1_yr_growth = "capital_expenditures_1_yr_growth"
    levered_free_cash_flow_1_yr_growth = "levered_free_cash_flow_1_yr_growth"
    unlevered_free_cash_flow_1_yr_growth = "unlevered_free_cash_flow_1_yr_growth"
    dividend_per_share_1_yr_growth = "dividend_per_share_1_yr_growth"
    total_revenues_2_yr_cagr = "total_revenues_2_yr_cagr"
    gross_profit_2_yr_cagr = "gross_profit_2_yr_cagr"
    ebitda_2_yr_cagr = "ebitda_2_yr_cagr"
    ebita_2_yr_cagr = "ebita_2_yr_cagr"
    ebit_2_yr_cagr = "ebit_2_yr_cagr"
    earnings_from_cont_ops_2_yr_cagr = "earnings_from_cont_ops_2_yr_cagr"
    net_income_2_yr_cagr = "net_income_2_yr_cagr"
    normalized_net_income_2_yr_cagr = "normalized_net_income_2_yr_cagr"
    diluted_eps_before_extra_2_yr_cagr = "diluted_eps_before_extra_2_yr_cagr"
    accounts_receivable_2_yr_cagr = "accounts_receivable_2_yr_cagr"
    inventory_2_yr_cagr = "inventory_2_yr_cagr"
    net_ppe_2_yr_cagr = "net_ppe_2_yr_cagr"
    common_equity_2_yr_cagr = "common_equity_2_yr_cagr"
    total_assets_2_yr_cagr = "total_assets_2_yr_cagr"
    tangible_book_value_2_yr_cagr = "tangible_book_value_2_yr_cagr"
    cash_from_ops_2_yr_cagr = "cash_from_ops_2_yr_cagr"
    capital_expenditures_2_yr_cagr = "capital_expenditures_2_yr_cagr"
    levered_free_cash_flow_2_yr_cagr = "levered_free_cash_flow_2_yr_cagr"
    unlevered_free_cash_flow_2_yr_cagr = "unlevered_free_cash_flow_2_yr_cagr"
    dividend_per_share_2_yr_cagr = "dividend_per_share_2_yr_cagr"
    total_revenues_3_yr_cagr = "total_revenues_3_yr_cagr"
    gross_profit_3_yr_cagr = "gross_profit_3_yr_cagr"
    ebitda_3_yr_cagr = "ebitda_3_yr_cagr"
    ebita_3_yr_cagr = "ebita_3_yr_cagr"
    ebit_3_yr_cagr = "ebit_3_yr_cagr"
    earnings_from_cont_ops_3_yr_cagr = "earnings_from_cont_ops_3_yr_cagr"
    net_income_3_yr_cagr = "net_income_3_yr_cagr"
    normalized_net_income_3_yr_cagr = "normalized_net_income_3_yr_cagr"
    diluted_eps_before_extra_3_yr_cagr = "diluted_eps_before_extra_3_yr_cagr"
    accounts_receivable_3_yr_cagr = "accounts_receivable_3_yr_cagr"
    inventory_3_yr_cagr = "inventory_3_yr_cagr"
    net_ppe_3_yr_cagr = "net_ppe_3_yr_cagr"
    common_equity_3_yr_cagr = "common_equity_3_yr_cagr"
    total_assets_3_yr_cagr = "total_assets_3_yr_cagr"
    tangible_book_value_3_yr_cagr = "tangible_book_value_3_yr_cagr"
    cash_from_ops_3_yr_cagr = "cash_from_ops_3_yr_cagr"
    capital_expenditures_3_yr_cagr = "capital_expenditures_3_yr_cagr"
    levered_free_cash_flow_3_yr_cagr = "levered_free_cash_flow_3_yr_cagr"
    unlevered_free_cash_flow_3_yr_cagr = "unlevered_free_cash_flow_3_yr_cagr"
    dividend_per_share_3_yr_cagr = "dividend_per_share_3_yr_cagr"
    total_revenues_5_yr_cagr = "total_revenues_5_yr_cagr"
    gross_profit_5_yr_cagr = "gross_profit_5_yr_cagr"
    ebitda_5_yr_cagr = "ebitda_5_yr_cagr"
    ebita_5_yr_cagr = "ebita_5_yr_cagr"
    ebit_5_yr_cagr = "ebit_5_yr_cagr"
    earnings_from_cont_ops_5_yr_cagr = "earnings_from_cont_ops_5_yr_cagr"
    net_income_5_yr_cagr = "net_income_5_yr_cagr"
    normalized_net_income_5_yr_cagr = "normalized_net_income_5_yr_cagr"
    diluted_eps_before_extra_5_yr_cagr = "diluted_eps_before_extra_5_yr_cagr"
    accounts_receivable_5_yr_cagr = "accounts_receivable_5_yr_cagr"
    inventory_5_yr_cagr = "inventory_5_yr_cagr"
    net_ppe_5_yr_cagr = "net_ppe_5_yr_cagr"
    common_equity_5_yr_cagr = "common_equity_5_yr_cagr"
    total_assets_5_yr_cagr = "total_assets_5_yr_cagr"
    tangible_book_value_5_yr_cagr = "tangible_book_value_5_yr_cagr"
    cash_from_ops_5_yr_cagr = "cash_from_ops_5_yr_cagr"
    capital_expenditures_5_yr_cagr = "capital_expenditures_5_yr_cagr"
    levered_free_cash_flow_5_yr_cagr = "levered_free_cash_flow_5_yr_cagr"
    unlevered_free_cash_flow_5_yr_cagr = "unlevered_free_cash_flow_5_yr_cagr"
    dividend_per_share_5_yr_cagr = "dividend_per_share_5_yr_cagr"
    total_revenues_7_yr_cagr = "total_revenues_7_yr_cagr"
    gross_profit_7_yr_cagr = "gross_profit_7_yr_cagr"
    ebitda_7_yr_cagr = "ebitda_7_yr_cagr"
    ebita_7_yr_cagr = "ebita_7_yr_cagr"
    ebit_7_yr_cagr = "ebit_7_yr_cagr"
    earnings_from_cont_ops_7_yr_cagr = "earnings_from_cont_ops_7_yr_cagr"
    net_income_7_yr_cagr = "net_income_7_yr_cagr"
    normalized_net_income_7_yr_cagr = "normalized_net_income_7_yr_cagr"
    diluted_eps_before_extra_7_yr_cagr = "diluted_eps_before_extra_7_yr_cagr"
    accounts_receivable_7_yr_cagr = "accounts_receivable_7_yr_cagr"
    inventory_7_yr_cagr = "inventory_7_yr_cagr"
    net_ppe_7_yr_cagr = "net_ppe_7_yr_cagr"
    common_equity_7_yr_cagr = "common_equity_7_yr_cagr"
    total_assets_7_yr_cagr = "total_assets_7_yr_cagr"
    tangible_book_value_7_yr_cagr = "tangible_book_value_7_yr_cagr"
    cash_from_ops_7_yr_cagr = "cash_from_ops_7_yr_cagr"
    capital_expenditures_7_yr_cagr = "capital_expenditures_7_yr_cagr"
    levered_free_cash_flow_7_yr_cagr = "levered_free_cash_flow_7_yr_cagr"
    unlevered_free_cash_flow_7_yr_cagr = "unlevered_free_cash_flow_7_yr_cagr"
    dividend_per_share_7_yr_cagr = "dividend_per_share_7_yr_cagr"
    total_revenues_10_yr_cagr = "total_revenues_10_yr_cagr"
    gross_profit_10_yr_cagr = "gross_profit_10_yr_cagr"
    ebitda_10_yr_cagr = "ebitda_10_yr_cagr"
    ebita_10_yr_cagr = "ebita_10_yr_cagr"
    ebit_10_yr_cagr = "ebit_10_yr_cagr"
    earnings_from_cont_ops_10_yr_cagr = "earnings_from_cont_ops_10_yr_cagr"
    net_income_10_yr_cagr = "net_income_10_yr_cagr"
    normalized_net_income_10_yr_cagr = "normalized_net_income_10_yr_cagr"
    diluted_eps_before_extra_10_yr_cagr = "diluted_eps_before_extra_10_yr_cagr"
    accounts_receivable_10_yr_cagr = "accounts_receivable_10_yr_cagr"
    inventory_10_yr_cagr = "inventory_10_yr_cagr"
    net_ppe_10_yr_cagr = "net_ppe_10_yr_cagr"
    common_equity_10_yr_cagr = "common_equity_10_yr_cagr"
    total_assets_10_yr_cagr = "total_assets_10_yr_cagr"
    tangible_book_value_10_yr_cagr = "tangible_book_value_10_yr_cagr"
    cash_from_ops_10_yr_cagr = "cash_from_ops_10_yr_cagr"
    capital_expenditures_10_yr_cagr = "capital_expenditures_10_yr_cagr"
    levered_free_cash_flow_10_yr_cagr = "levered_free_cash_flow_10_yr_cagr"
    unlevered_free_cash_flow_10_yr_cagr = "unlevered_free_cash_flow_10_yr_cagr"
    dividend_per_share_10_yr_cagr = "dividend_per_share_10_yr_cagr"


@unique
class Leverage(Field):
    """
    财务杠杆
    """
    cash_from_ops_to_curr_liab = "cash_from_ops_to_curr_liab"
    total_debt_to_equity = "total_debt_to_equity"
    total_debt_to_capital = "total_debt_to_capital"
    lt_debt_to_equity = "lt_debt_to_equity"
    lt_debt_to_capital = "lt_debt_to_capital"
    total_liabilities_to_total_assets = "total_liabilities_to_total_assets"
    ebit_to_interest_exp = "ebit_to_interest_exp"
    ebitda_to_interest_exp = "ebitda_to_interest_exp"
    ebitda_capex_to_interest_exp = "ebitda_capex_to_interest_exp"
    total_debt_to_ebitda = "total_debt_to_ebitda"
    net_debt_to_ebitda = "net_debt_to_ebitda"
    total_debt_to_ebitda_capex = "total_debt_to_ebitda_capex"
    net_debt_to_ebitda_capex = "net_debt_to_ebitda_capex"
    capex_as_of_revenues = "capex_as_of_revenues"
    altman_z_score = "altman_z_score"


@unique
class Profitability(Field):
    """
    盈利能力
    """
    return_on_assets = "return_on_assets"
    return_on_capital = "return_on_capital"
    return_on_equity = "return_on_equity"
    return_on_common_equity = "return_on_common_equity"
    gross_margin = "gross_margin"
    ebitda_margin = "ebitda_margin"
    ebita_margin = "ebita_margin"
    ebit_margin = "ebit_margin"
    sga_margin = "sga_margin"
    earnings_from_cont_ops_margin = "earnings_from_cont_ops_margin"
    net_income_margin = "net_income_margin"
    net_inc_avail_for_common_margin = "net_inc_avail_for_common_margin"
    levered_free_cash_flow_margin = "levered_free_cash_flow_margin"
    unlevered_free_cash_flow_margin = "unlevered_free_cash_flow_margin"
    normalized_net_income_margin = "normalized_net_income_margin"
