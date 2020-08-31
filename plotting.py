import matplotlib.pyplot as plt


def plot_pie(labels, sizes):

    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    # labels = 'Frogs', 'Hogs', 'Dogs', 'Logs'
    # sizes = [15, 30, 45, 10]

    fig, ax = plt.subplots()
    fig.suptitle('Your month costs', fontsize=30)
    ax.pie(sizes, labels=labels, autopct='%1.0f%%',
            shadow=True, startangle=90, textprops={'fontsize': 20, 'name': 'sans'})
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    return fig, ax


def fig2img(fig):
    """Convert a Matplotlib figure to a PIL Image and return it"""
    import io
    from PIL import Image
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    img = Image.open(buf)
    return img
