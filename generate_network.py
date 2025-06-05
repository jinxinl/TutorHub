import networkx as nx
import json
import matplotlib
matplotlib.use('Agg')  # 使用纯图像生成后端，避免 Tkinter 问题
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def get_data():
    with open("dataset/processed/AlumniRelation.json","r",encoding="utf-8") as f:
        tutor_school_dict = json.load(f) #[{school:[tutor1 ,tutor2]}]
    with open("dataset/processed/TutorRelation.json", "r", encoding="utf-8") as f:
        tutor_rel_dict = json.load(f) #[tutor]

    return tutor_school_dict,tutor_rel_dict

#tutor_school_dict,tutor_rel_list = get_data()
#print(tutor_school_dict)
#print(tutor_rel_list)

#对数据库中的alumnirelation表做一些转化，变为{name:[alumni1 ,alumn2]}的形式
def transform_alumni_relation(name,tutor_school_dict):
    alumni_list = []
    for key,value in tutor_school_dict.items():
        if name in value:
            for alumni_name in value:
                if alumni_name != name:
                    alumni_list.append(alumni_name)

    return alumni_list



def create_graph(name,data,title=''):
    if data is None:
        # 如果 data 为空，返回一个默认的图像
        plt.figure(figsize=(4, 3), dpi=500)
        plt.text(0.5, 0.5, "No academic relationship available", ha='center', va='center', fontsize=10)
        plt.axis('off')
        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        #plt.show()
        return img_base64

    G = nx.Graph()
    for num in range(len(data)):
        G.add_edge(name,data[num])

    #节点大小设置，与度有关，度越大，节点越大
    node_size = [G.degree(i)**0.35*80 for i in G.nodes()]

    #设置颜色，随机
    colors = ['#43CD80','DeepPink','orange','#008B8B','purple','#63B8FF','#BC8F8F','#3CB371','b','orange','y','c','#838B8B','purple','olive','#A0CBE2','#4EEE94']*500
    colors = colors[0:len(G.nodes)]

    #设置显示图片的大小
    plt.figure(figsize=(4,3),dpi=500)

    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    nx.draw_networkx(G,
                     pos=nx.spring_layout(G,iterations=27),
                     node_color=colors,
                     edge_color='#2E8B57',
                     font_size=2.5,
                     node_size=node_size,
                     alpha=0.98,
                     width=0.1
                     )
    plt.title(title)
    plt.axis('off')
    #plt.show()

    #使用BytesIO保存图片
    buf = BytesIO()
    plt.savefig(buf,format='png')
    plt.close()
    buf.seek(0)

    #将图片编码为base64，便于在html中嵌入
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    return img_base64
