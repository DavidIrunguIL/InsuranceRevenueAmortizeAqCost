from src.insurance_revenue_class import InsuranceRevenueGenerator
from input_data import  get_data
import pandas as pd
import numpy as np
from datetime import datetime as dt
import warnings
warnings.filterwarnings('ignore')


current_year = dt.now().year
month = dt.now().month
prev_year = current_year - 1

# if 
start_period = f"{prev_year}01"
end_period = dt.now().strftime("%Y%m")  # current year and month

#the *last completed* month instead:
today = dt.now()
last_month = today.replace(day=1) - pd.DateOffset(days=1)
end_period = last_month.strftime("%Y%m")


GetData = get_data.GetData
current_prem_reg = GetData.get_prem_reg(current_year, month-1)
prev_prem_reg = GetData.get_prem_reg(prev_year, 12)


prem_reg = pd.concat([current_prem_reg,prev_prem_reg], axis=0)

prem_reg.to_excel(f"output_data/prem_reg.xlsx", index=False)
current_upr_reg = GetData.get_upr_reg(current_year, month-1)
prev_upr_reg = GetData.get_upr_reg(prev_year, 12)



prem_reg['NetAfterXOL'] = prem_reg['netamount'] - prem_reg['XolTotal']


prem_register_list = [
    "basicprem",  "brkcomm", "tlevy", "pcf", "duty", "wtax", "eareamt", "surp1amt", "surp2amt", 
    "Loggross","Facprop", "QsAmt","NetAfterXOL", "netamount", "Xol1", "Xol2", 
    "Xol3", "Xol4", "Xol5", "XolTotal",  "NetComm", "QsComm", "facpropcomm", "surpcomm", 
    "surp2comm", "fobcomm", "NewBusiness", "RenewalPremium", "OtherPremium"
] #missing: ["netamountAfterNonProportionalTreaty", "NetAfterXOL"]


upr_list = [
    'Basic Premium', 'FacPremium', 'Surp1Prem', 'Surp2Prem', 'QSPrem', 'FOBPrem', 'Net Premium',
    'GrossCommission', 'FACComm', 'Surp1Comm', 'Surp2Comm', 'QSComm', 'FOBComm', 'NetComm',
    'GrossUPR', 'EareUPR', 'FacPropUPR', 'QSUPR', 'Surp1UPR', 'Surp2UPR', 'NetUPR',
    'BrokerDAC', 'FACDAC', 'FOBDAC', 'Surp1DAC', 'Surp2DAC', 'QuotaDAC', 'NETDAC'
]


prem_reg['period'] = pd.to_numeric(prem_reg['period'])
current_period = dt.now().strftime('%Y%m')
current_start_period = int(dt(dt.now().year, 1, 1).strftime('%Y%m'))

prev_year_prem_ = prem_reg[prem_reg['period'] < current_start_period]
current_year_prem_ = prem_reg[prem_reg['period'] >= current_start_period]

current_prem_piv_table = InsuranceRevenueGenerator.get_prem_rev_calculation(current_year_prem_,prem_register_list)
prev_prem_piv_table = InsuranceRevenueGenerator.get_prem_rev_calculation(prev_year_prem_,prem_register_list)

current_prem_piv_table.to_excel(f"output_data/current_prem_piv_table.xlsx", index=False)
prev_prem_piv_table.to_excel(f"output_data/prev_prem_piv_table.xlsx", index=False)

grp_col = 'departmentname'
current_upr_pivot_table = InsuranceRevenueGenerator.get_upr_rev_calculation(current_upr_reg,upr_list,grp_col)
prev_upr_pivot_table = InsuranceRevenueGenerator.get_upr_rev_calculation(prev_upr_reg,upr_list,grp_col)




insurance_rev = InsuranceRevenueGenerator.get_insurance_revenue(current_upr_pivot_table, current_prem_piv_table,
                               prev_upr_pivot_table, prev_prem_piv_table,
                               current_year, prev_year)

numeric_cols = insurance_rev.columns.difference(['Department'])
insurance_rev[numeric_cols] = insurance_rev[numeric_cols].apply(pd.to_numeric, errors='coerce')
insurance_rev = insurance_rev[insurance_rev['Department'] != 'Total']
period = prem_reg['period'].max()
# insurance_rev['period'] = period
# existing_insurance_revenue = domo.read_dataframe('Insurance_revenue', query='SELECT * FROM table')


# if existing_insurance_revenue['period'].max() == period:
#     existing_insurance_revenue = existing_insurance_revenue[existing_insurance_revenue['period'] != period]

# insurance_rev = pd.concat([insurance_rev,existing_insurance_revenue])
#period_type
# cond = [(insurance_rev['period'] == period), 
#        (insurance_rev['period'] < period)]
# vals = ['current_period', 'previous_period']
# insurance_rev['period_type'] = np.select(cond, vals)
insurance_rev.to_excel(f"insurance_revenue_amortize_aq_cost_{period}.xlsx", index=False)