def default_mapping():
    return {"Leads":["Leads","Zoho_Leads","Total_Leads"],
            "Revenue":["Revenue","Invoice_Amount","Total_Revenue"]}

def resolve_kpi_for_column(col: str, mapping: dict[str, list[str]]):
    for kpi, cols in mapping.items():
        if col in cols: return kpi
    return None
