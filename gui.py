from musicwordcloud import cloud_hook
from wordcloud import WordCloud
import matplotlib.pyplot as plot
from multiprocessing import freeze_support


if __name__ == "__main__":
    freeze_support()
    print("Attempting to create wordcloud from hook")
    wc: WordCloud = cloud_hook("Seether")
    if wc:
        plot.figure(figsize=(8, 8), facecolor=None)
        plot.imshow(wc)
        plot.axis("off")
        plot.tight_layout(pad=0)
        plot.show()
