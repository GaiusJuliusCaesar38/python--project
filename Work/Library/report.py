import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def create_report(counts1, counts2):
    df = pd.DataFrame({'Interval 1' : counts1,
                       'Interval 2' : counts2})
    x = np.arange(len(df))  
    width = 0.35

    fig, ax = plt.subplots(figsize=(5,5))
    rects1 = ax.bar(x - width/2, df['Interval 1'], width)
    rects2 = ax.bar(x + width/2, df['Interval 2'], width)

    df.to_excel(os.path.join(os.getcwd(), 'Output', f'{time.strftime("%Y%m%d-%H%M%S")}.xlsx'))    
    plt.show()
