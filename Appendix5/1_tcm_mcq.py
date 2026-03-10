from statsmodels.stats.contingency_tables import mcnemar

'''
gpt-4o
'''
# gpt-4o-mini：292
# TCM-DiffRAG：562
table = [[287, 5],
         [275, 33]]

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
# gemini-2.5-flash：454
# TCM-DiffRAG：557
table = [[421, 33],
         [136, 10]]

result_exact = mcnemar(table, exact=True)
print("精确检验 p值:", result_exact.pvalue)

result_chi2 = mcnemar(table, exact=False, correction=True)
print("卡方统计量:", result_chi2.statistic)
print("近似检验 p值:", result_chi2.pvalue)
print("###############################")


'''
qwen
'''
# qwen：556
# TCM-DiffRAG：571
table = [[549, 7],
         [22, 22]]

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
# ds-r1：561
# TCM-DiffRAG：574
table = [[558, 3],
         [16, 1]]

# exact=True：精确检验（小样本更稳妥）
result_exact = mcnemar(table, exact=True)
print("精确检验 p值:", result_exact.pvalue)


result_chi2 = mcnemar(table, exact=False, correction=True)
print("卡方统计量:", result_chi2.statistic)
print("近似检验 p值:", result_chi2.pvalue)
print("###############################")