import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

class StatisticalAnalysis:
    def __init__(self, data):
        self.data = np.array(data)

    def mean(self):
        return np.mean(self.data)

    def std_dev(self):
        return np.std(self.data, ddof=1)

    def std_error(self):
        return self.std_dev() / np.sqrt(len(self.data))

    def max_semi_dispersion(self):
        return (np.max(self.data) - np.min(self.data)) / 2

    def summary(self):
        return {
            "mean": self.mean(),
            "std_dev": self.std_dev(),
            "std_error": self.std_error(),
            "min": np.min(self.data),
            "max": np.max(self.data),
            "median": np.median(self.data),
            "skewness": stats.skew(self.data),
            "kurtosis": stats.kurtosis(self.data),
            "max_semi_dispersion": self.max_semi_dispersion()
        }

    def create_histogram(self, bins=10, density=False):
        fig, ax = plt.subplots()
        ax.hist(self.data, bins=bins, density=density)
        ax.set_title("Istogramma dei dati")
        ax.set_xlabel("Valore")
        ax.set_ylabel("Frequenza" if not density else "Densità")
        
        mean = self.mean()
        std = self.std_dev()
        ax.axvline(mean, color='r', linestyle='dashed', linewidth=2, label=f'Media: {mean:.2f}')
        ax.axvline(mean + std, color='g', linestyle='dashed', linewidth=2, label=f'Dev. Std: {std:.2f}')
        ax.axvline(mean - std, color='g', linestyle='dashed', linewidth=2)
        
        ax.legend()
        
        return fig, ax
