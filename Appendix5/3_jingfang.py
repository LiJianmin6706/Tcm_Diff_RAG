from statsmodels.stats.contingency_tables import mcnemar

'''
gpt-4o
'''
# gpt-4o-mini：175
# TCM-DiffRAG：1764
table = [[147, 28],
         [1617, 3220]]

# exact=True：精确检验（小样本更稳妥）
result_exact = mcnemar(table, exact=True)
print("精确检验 p值:", result_exact.pvalue)

result_chi2 = mcnemar(table, exact=False, correction=True)
print("卡方统计量:", result_chi2.statistic)
print("近似检验 p值:", result_chi2.pvalue)
print("###############################")

'''
gemini
'''
# gemini-2.5-flash：231
# TCM-DiffRAG：1819
table = [[194, 37],
         [1625, 3156]]

result_exact = mcnemar(table, exact=True)
print("精确检验 p值:", result_exact.pvalue)

result_chi2 = mcnemar(table, exact=False, correction=True)
print("卡方统计量:", result_chi2.statistic)
print("近似检验 p值:", result_chi2.pvalue)
print("###############################")


'''
qwen
'''
# qwen：190
# TCM-DiffRAG：1784
table = [[154, 36],
         [1630, 3192]]

# exact=True：精确检验（小样本更稳妥）
result_exact = mcnemar(table, exact=True)
print("精确检验 p值:", result_exact.pvalue)

result_chi2 = mcnemar(table, exact=False, correction=True)
print("卡方统计量:", result_chi2.statistic)
print("近似检验 p值:", result_chi2.pvalue)
print("###############################")

'''
ds-r1
'''
# ds-r1：336
# TCM-DiffRAG：1930
table = [[295, 41],
         [1635, 3041]]

# exact=True：精确检验（小样本更稳妥）
result_exact = mcnemar(table, exact=True)
print("精确检验 p值:", result_exact.pvalue)


result_chi2 = mcnemar(table, exact=False, correction=True)
print("卡方统计量:", result_chi2.statistic)
print("近似检验 p值:", result_chi2.pvalue)
print("###############################")