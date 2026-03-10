# -*- coding: utf-8 -*-
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from pyecharts.charts import Graph


def plot(node_list, relation_list, save_path):
    for node in node_list:
        # 设定大小
        node["itemStyle"] = {}
        if node['id'] == '问题':
            node["itemStyle"]["color"] = 'red'
        elif node['content'] == '':
            node["itemStyle"]["color"] = 'green'
        elif node['content'] != '':
            node["itemStyle"]["color"] = 'blue'

        # 设定显示的具体内容
        show_text = f"{node['id']}<br><br>{node['content']}"
        line_length = 30
        formatted_text = "<br>".join(show_text[i:i + line_length] for i in range(0, len(show_text), line_length))
        node["tooltip"] = {
            "position": "right",
            "formatter": formatted_text
        }


    init_opts = opts.InitOpts(width="100%",  # 图宽
                              height="860px",  # 图高
                              renderer="canvas",  # 渲染模式 svg 或 canvas，即 RenderType.CANVAS 或 RenderType.SVG
                              page_title="检索子图",  # 网页标题
                              theme=ThemeType.WHITE,
                              # 主题风格可选：WHITE,LIGHT,DARK,CHALK,ESSOS,INFOGRAPHIC,MACARONS,PURPLE_PASSION,ROMA,ROMANTIC,SHINE,VINTAGE,WALDEN,WESTEROS,WONDERLAND
                              bg_color="#FFFFF0",  # 背景颜色
                              js_host=""  # js主服务位置 留空则默认官方远程主服务
                              )


    # 创建关系图
    graph = (
        Graph(init_opts)
        .add(
            "",
            node_list,
            relation_list,
            repulsion=4000,
            layout="force", # force，circular
            is_draggable=True,  # 节点是否可拖拉
            edge_symbol=[None, 'arrow'],  # 线的末端
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="关系图示例"),
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(
                is_show=True,
                position="right",
                # formatter="{b}",
            ),
            tooltip_opts=opts.TooltipOpts(
                is_show=True,  # 悬浮时是否显示悬浮文字
            ),
        )
    )


    return graph
    # graph.render(save_path)
