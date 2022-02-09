from tkinter.tix import Tree
import matplotlib.pyplot as plt
import base64
from io import BytesIO

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
    plt.title('Different Listings Bookings')
    explosion = []
    total = sum(y) 
    for val in y:
        explode = (val/total)/5
        explosion.append(explode)
    plt.pie(y, labels=x, explode = explosion, startangle = 90, shadow=True,
    autopct=lambda p: '{:.0f}%'.format(p * total / 100)
    )
    plt.legend(title = "Room Name:", bbox_to_anchor=(0,0.3))
    # plt.xticks(rotation=45)
    plt.tight_layout()
    graph = get_graph()
    return graph