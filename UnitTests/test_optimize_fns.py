import unittest

from matplotlib import pyplot as plt
import numpy as np
import random
import pandas as pd
import optimize_fns
import scipy.cluster.hierarchy as sch

class OptimizeFnsTest(unittest.TestCase):

    """def test_denerogram(self):
        # generate two clusters: a with 100 points, b with 50:
        np.random.seed(4711)  # for repeatability of this tutorial
        a = np.random.multivariate_normal([10, 0], [[3, 1], [1, 4]], size=[100, ])
        b = np.random.multivariate_normal([0, 20], [[3, 1], [1, 4]], size=[50, ])
        X = np.concatenate((a, b), )

        # generate the linkage matrix
        Z = linkage(X, 'ward')

        # calculate full dendrogram
        plt.figure(figsize=(25, 10))
        plt.title('Hierarchical Clustering Dendrogram')
        plt.xlabel('sample index')
        plt.ylabel('distance')
        dendrogram(
            Z,
            leaf_rotation=90.,  # rotates the x axis labels
            leaf_font_size=8.,  # font size for the x axis labels
        )
        plt.show()"""

    def test_hpr(self):
        #Create 6 series which are clearly in sets: increasing/decreasing/Flat
        increasing = dict([('Inc{}'.format(y), [x + random.randint(-50, 50) for x in range(0, 1000)]) for y in range(3)])
        decreasing = dict([('Dec{}'.format(y), [-x + random.randint(-50, 50) for x in range(0, 1000)]) for y in range(3)])
        flat = dict([('Flat{}'.format(y), [50*np.sin(x) + random.randint(-50, 50) for x in range(0, 1000)]) for y in range(3)])

        All = {**increasing, **decreasing, **flat}

        df = pd.DataFrame(All)

        covs = df.cov()
        corrs = df.corr()

        hrp = optimize_fns.hrp(covs, corrs)

        # calculate full dendrogram
        """        
        plt.figure(figsize=(25, 10))
        plt.title('Hierarchical Clustering Dendrogram')
        plt.xlabel('sample index')
        plt.ylabel('distance')

        sch.dendrogram(
            hrp[0]['linkage'],
            leaf_rotation=90.,  # rotates the x axis labels
            leaf_font_size=8.,  # font size for the x axis labels
        )
        plt.show()
        """

        clusters = sch.fcluster(hrp[0]['linkage'], 1, 'distance')
        self.assertEqual(clusters[0], clusters[1])
        self.assertEqual(clusters[1], clusters[2])
        self.assertEqual(clusters[3], clusters[4])
        self.assertEqual(clusters[4], clusters[5])
        self.assertEqual(clusters[6], clusters[7])
        self.assertEqual(clusters[7], clusters[8])


if __name__ == "__main__":
    unittest.main()