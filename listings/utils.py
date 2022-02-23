from telnetlib import PRAGMA_HEARTBEAT
from tkinter.tix import Tree
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import seaborn as sns
import pandas as pd

def get_graph():
    buffer  = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

def get_plot_pie(x,y):
    plt.switch_backend('AGG')
    plt.figure(figsize=(9,4.5))
    plt.title('Different Listings Bookings Till Now')
    explosion = []
    total = sum(y) 
    color = sns.color_palette('pastel')
    for val in y:
        explode = (val/total)/5
        explosion.append(explode)
    plt.pie(y, labels=x, explode = explosion, startangle = 90, shadow=True, colors = color,
            autopct=lambda p: '{:.0f}%'.format(p * total / 100)
            )
    plt.legend(title = "Room Name:", bbox_to_anchor=(0,0.3))
    # plt.xticks(rotation=45)
    plt.tight_layout()
    graph = get_graph()
    return graph

month_val = {
    '1'  : 'Janaury',
    '01'  : 'Janaury',
    '2'  : 'Feburary',
    '02'  : 'Feburary',
    '3'  : 'March',
    '03'  : 'March',
    '4'  : 'April',
    '04'  : 'April',
    '5'  : 'May',
    '05'  : 'May',
    '6'  : 'June',
    '06'  : 'June',
    '7'  : 'July',
    '07'  : 'July',
    '8'  : 'August',
    '08'  : 'August',
    '9'  : 'September',
    '09'  : 'September',
    '10' : 'October',
    '11' : 'November',
    '12' : 'December',
}

def addlabels(x,y):
    for i in range(len(x)):
        plt.text(i,y[i],y[i])

def get_booking_details_bar(x, y, year, month):
    
    new_list = []   
    for index, value in enumerate(x):
        item = [value, y[index]]
        new_list.append(item)
    df = pd.DataFrame (new_list, columns = ['TYPE', 'COUNT'])
    plt.switch_backend('AGG')
    plt.figure(figsize=(10,5))
    fig, ax = plt.subplots(1)
    plt.title(f'Total, Current, Completed and Cancelled Bookings for {year},{month_val[month]}')
    sns.barplot(x = 'TYPE', y = 'COUNT', data = df)
    show_values_on_bars(ax)
    plt.xticks(rotation=2)
    plt.xlabel("Type", fontweight ='bold', fontsize = 15)
    plt.ylabel("Count", fontweight ='bold', fontsize = 15)
    plt.tight_layout()
    graph = get_graph()
    return graph

import numpy as np
def earning_details_bar(x, y1, y2, y3, year, month):
    plt.switch_backend('AGG')
    plt.figure(figsize=(8,4))
    barWidth = 0.20
    br1 = np.arange(len(y1))
    br2 = [x + barWidth for x in br1]
    br3 = [x + barWidth for x in br2]

    plot1 = plt.bar(br1, y1, color ='r', width = barWidth,
             label ='Total Amount')
    autolabel(plot1)
    plot2 = plt.bar(br2, y2, color ='g', width = barWidth,
             label ='Tax Amount')
    autolabel(plot2)
    plot3 = plt.bar(br3, y3, color ='b', width = barWidth,
              label ='Actual Amount')
    autolabel(plot3)

    plt.xlabel('Status', fontweight ='bold', fontsize = 15)
    plt.ylabel('Amount', fontweight ='bold', fontsize = 15)

    plt.xticks([r + barWidth for r in range(len(x))], x)
    plt.xticks(rotation=1)
    plt.legend()
    plt.title(f'Total Cash flow for {year},{month_val[month]}')

    plt.tight_layout()
    graph = get_graph()
    return graph

def autolabel(rects):
    for rect in rects:
        h = rect.get_height()
        plt.text(rect.get_x()+rect.get_width()/2., 1.001*h, '%d'%int(h),
                ha='center', va='bottom')

def show_values_on_bars(axs):
    def _show_on_single_plot(ax):        
        for p in ax.patches:
            _x = p.get_x() + p.get_width() / 2
            _y = p.get_y() + p.get_height()
            value = '{:.2f}'.format(p.get_height())
            ax.text(_x, _y, value, ha="center") 

    if isinstance(axs, np.ndarray):
        for idx, ax in np.ndenumerate(axs):
            _show_on_single_plot(ax)
    else:
        _show_on_single_plot(axs)