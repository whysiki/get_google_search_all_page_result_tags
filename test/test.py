# 得到所有字段集合
datafields = {
    i.strip()
    for i in "fnd17_oxlcxspebq, fnd17_shsoutbs,fnd17_oxlcxspebq, fnd28_value_05191q, fnd17_oxlcxspebq, fnd28_value_05192q,fnd17_oxlcxspebq, fnd28_value_05301q,fnd17_oxlcxspebq, fnd28_value_05302,fnd17_pehigh, fnd17_pelow,fnd17_priceavg150day, fnd17_priceavg200day,fnd17_priceavg150day, fnd17_priceavg50day,fnd17_priceavg200day, fnd17_priceavg50day,fnd17_pxedra, fnd17_tbea,fnd17_pxedra, fnd28_newa3_value_18191a,fnd17_pxedra, fnd28_newa3_value_18198a,fnd17_pxedra, fnd28_value_02300a,fnd17_pxedra, fnd28_value_05302,fnd17_pxedra, mdl175_ebitda,fnd17_pxedra, mdl175_pain".split(
        ","
    )
    if i.strip()
}
datafields = list(datafields)  # 去重
print(f"Total datafields: {len(datafields)}")  # 18
all_combinations_list = []  # 两两组合
for i in range(len(datafields)):
    for j in range(len(datafields)):
        if i != j and i < j:
            all_combinations_list.append(
                f"ts_regression(ts_zscore({datafields[i]}, 500), ts_zscore({datafields[j]}, 500), 500)"
            )
print(f"Total combinations: {len(all_combinations_list)}")  # 153, 18*17/2
for i in all_combinations_list:
    print(i)  # 打印所有组合
