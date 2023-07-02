from dataclasses import dataclass
from datetime import datetime
import statistics
import sys
from enum import Enum
from typing import List
import matplotlib
import numpy as np
import time

from Rate import Rate
from debug import print_error, print_success
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import pandas as pd

class GraphCaption(Enum):
    AVG = 'average latency'
    Q05 = '5% percentile latency'
    Q95 = '95% percentile latency'
    REQUESTS_PER_MINUTE = 'requests per minute'
    LOST_REQUESTS = 'lost requests per minute'
    
def create_graph() -> None:
    df = pd.DataFrame({
        GraphCaption.AVG: [0.0],
        GraphCaption.Q05: [0.0],
        GraphCaption.Q95: [0.0],
        GraphCaption.REQUESTS_PER_MINUTE: [0.0],
        GraphCaption.LOST_REQUESTS: [0.0]
    }, index=pd.to_datetime([pd.Timestamp.now()]))

    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True)

    def on_close(event):
        nonlocal fig
        print("EXIT")
        now = datetime.now().strftime("%Y%m%d-%H%M%S")
        fig.savefig(f"load_test_{now}.png",bbox_inches='tight')
        time.sleep(1)
        sys.exit()

    fig.canvas.mpl_connect('close_event', on_close)

    line1, = ax1.plot(df.index, df[GraphCaption.AVG], label=GraphCaption.AVG.value)
    line2, = ax1.plot(df.index, df[GraphCaption.Q05], label=GraphCaption.Q05.value)
    line3, = ax1.plot(df.index, df[GraphCaption.Q95], label=GraphCaption.Q95.value)
    ax1.set_ylabel('Latency (seconds)')
    ax1.legend(loc='upper left')

    line4, = ax2.plot(df.index, df[GraphCaption.REQUESTS_PER_MINUTE], label=GraphCaption.REQUESTS_PER_MINUTE.value)
    line5, = ax2.plot(df.index, df[GraphCaption.LOST_REQUESTS], label=GraphCaption.LOST_REQUESTS.value)
    ax2.set_ylabel('Requests')
    ax2.legend(loc='upper left')

    plt.title('DataFrame Visualization')
    plt.xlabel('Timestamp')

    return (df, fig, line1, line2, line3, line4, line5, ax1, ax2)


@dataclass
class InterimResult:
    time: datetime
    latency: List[float]
    rate: Rate

def update_graph(graph_data, result: InterimResult) -> None:  
    df, fig, line1, line2, line3, line4, line5, ax1, ax2 = graph_data
    
    lost_requests = len(list(filter(lambda x: x is None, result.latency)))
    cleaned_latency = list(filter(lambda x: x is not None, result.latency))
    average = statistics.mean(cleaned_latency)
    percentile_05 = np.percentile(cleaned_latency, 5)
    percentile_95 = np.percentile(cleaned_latency, 95)

    last_row = df.iloc[-1]
    df.loc[pd.Timestamp.now()] = {
        GraphCaption.AVG: average,
        GraphCaption.Q05: percentile_05,
        GraphCaption.Q95: percentile_95,
        GraphCaption.REQUESTS_PER_MINUTE: len(result.latency) / result.rate.window * 60.0,
        GraphCaption.LOST_REQUESTS: lost_requests
    }

    line1.set_data(df.index, df[GraphCaption.AVG])
    line2.set_data(df.index, df[GraphCaption.Q05])
    line3.set_data(df.index, df[GraphCaption.Q95])
    line4.set_data(df.index, df[GraphCaption.REQUESTS_PER_MINUTE])
    line5.set_data(df.index, df[GraphCaption.LOST_REQUESTS])

    ax1.relim()
    ax1.autoscale_view()

    ax2.relim()
    ax2.autoscale_view()

    plt.draw()
    plt.pause(0.0001)
    
    if last_row[GraphCaption.AVG] < average or last_row[GraphCaption.Q05] < percentile_05 or lost_requests > len(cleaned_latency):
        print_error(f"avg: {average} 10Q: {percentile_05} lost_requests: {lost_requests}")
    else:
        print_success(f"avg: {average} 10Q: {percentile_05} lost_requests: {lost_requests}")
    