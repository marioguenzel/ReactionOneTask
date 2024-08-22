"""
Basis from https://github.com/tu-dortmund-ls12-rt/end-to-end_mixed/blob/master/e2e/plot.py
"""

import matplotlib.pyplot as plt
from matplotlib.ticker import (AutoMinorLocator)
import tikzplotlib


def plot(data, filename, xticks=None, title='', yticks=None, ylimits=None, yscale='linear', yaxis_label=""):
    fig, ax = plt.subplots()
    ax.set_title(title)
    ax.boxplot(data,
               boxprops=dict(linewidth=4, color='blue'),
               medianprops=dict(linewidth=4, color='red'),
               whiskerprops=dict(linewidth=4, color='black'),
               capprops=dict(linewidth=4),
               whis=[0, 100])

    if xticks is not None:
        plt.xticks(list(range(1, len(xticks) + 1)), xticks)
    else:
        plt.xticks([])

    if yticks is not None:
        plt.yticks(yticks)
    if ylimits is not None:
        ax.set_ylim(ylimits)

    plt.yscale(yscale)

    ax.tick_params(axis='x', rotation=0, labelsize=20)
    ax.tick_params(axis='y', rotation=0, labelsize=20)

    ax.set_ylabel(yaxis_label, fontsize=20)

    plt.grid(True, color='lightgray', which='both', axis='y', linestyle='-')
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.tick_params(which='both', width=2)
    ax.tick_params(which='major', length=7)

    plt.tight_layout()  # improve margins for example for yaxis_label

    # plt.show()
    tikzplotlib.save(filename + ".tex")
    fig.savefig(filename + ".pdf")
    plt.close(fig)
    print(f'plot {filename} created')


def create_normalized_plots(selected_analysis_methods, 
                            selected_normalization_methods, 
                            output_dir):
    for baseline in selected_normalization_methods:
        for method in selected_analysis_methods:
            if method.latencies != []:
                plot(method.normalize(baseline), 
                            output_dir + method.name_short + "_normalized_to_" + baseline.name_short, 
                            title=method.name_short + " (normalized to " + baseline.name_short + ")",
                            ylimits=(0, 1.0)
                )

        # only do comparison if there is something to compare
        if len(selected_analysis_methods) >= 2:
            plot([method.normalize(baseline) for method in selected_analysis_methods], 
                        output_dir + "normalized_to_" + baseline.name_short, 
                        xticks=[method.name_short for method in selected_analysis_methods], 
                        title="Relative Comparison (normalized to " + baseline.name_short + ")",
                        ylimits=(0, 1.0))


def create_absolute_plots(selected_analysis_methods, 
                          output_dir):
    for method in selected_analysis_methods:
        if method.latencies != []:
            plot(method.latencies, output_dir + method.name_short)

    # only do comparison if there is something to compare
    if len(selected_analysis_methods) >= 2:
        plot([method.latencies for method in selected_analysis_methods], 
                    output_dir + "absolute", 
                    xticks=[method.name_short for method in selected_analysis_methods], 
                    title="Absolute Comparison"
        )