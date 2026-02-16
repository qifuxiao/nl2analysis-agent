'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-14 02:31:47
FilePath: /alexqi/develop/nl2analysis-agent/app/analysis/chart.py
'''
import pandas as pd
import plotly.express as px

def generate_chart_html(data: list[dict], title: str) -> str:
    df = pd.DataFrame(data)
    if df.empty or len(df.columns) < 2:
        return "<p>暂无可视化数据</p>"

    x, y = df.columns[:2]
    fig = px.bar(df, x=x, y=y, title=title)
    return fig.to_html(full_html=False)
