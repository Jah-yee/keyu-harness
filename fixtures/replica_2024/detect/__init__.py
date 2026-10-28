"""SIMULATED detection recipes (Phase E).

十条配方对应 docs/case/02 案例档案的"检测配方"列——把当年团队"怎么发现它"
的方法变成可运行代码。每条配方输入 context（事件流/宿主/存储/工件路径），
输出 findings（机器可读告警，含 disclosure_id/证据/配方 ID）。
阳性剧本（harness 已运行）应有告警；阴性剧本（清洁环境）必须零告警。
"""
