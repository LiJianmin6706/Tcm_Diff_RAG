from statsmodels.stats.contingency_tables import mcnemar

'''
gpt-4o
'''
# gpt-4o-mini：1580
# TCM-DiffRAG：4147
table = [[1376, 204],
         [2771, 1135]]

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
# gemini-2.5-flash：1377
# TCM-DiffRAG：4202
table = [[1206, 171],
         [2996, 1113]]

result_exact = mcnemar(table, exact=True)
print("精确检验 p值:", result_exact.pvalue)

result_chi2 = mcnemar(table, exact=False, correction=True)
print("卡方统计量:", result_chi2.statistic)
print("近似检验 p值:", result_chi2.pvalue)
print("###############################")


'''
qwen
'''
# qwen：1980
# TCM-DiffRAG：4323
table = [[1826, 154],
         [2497, 1009]]

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
# ds-r1：1953
# TCM-DiffRAG：4279
table = [[1887, 66],
         [2392, 1141]]

# exact=True：精确检验（小样本更稳妥）
result_exact = mcnemar(table, exact=True)
print("精确检验 p值:", result_exact.pvalue)


result_chi2 = mcnemar(table, exact=False, correction=True)
print("卡方统计量:", result_chi2.statistic)
print("近似检验 p值:", result_chi2.pvalue)
print("###############################")