# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 11:28:01 2017

@author: Tom
"""
#import matplotlib

# Make sure that we are using QT5
#matplotlib.use('Qt5Agg')

import sys
import data_fns
from optimize_fns import *
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (QMainWindow, QLabel, QFileDialog, QApplication, QPushButton, QSlider, QSizePolicy, QVBoxLayout, QWidget, QComboBox)
from PyQt5.QtCore import (Qt)
import os
import pickle as pkl
import operator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import scipy.cluster.hierarchy as sch
from matplotlib import pyplot as plt
import itertools
from universe_reduction import UniverseReduction

class Launchpad(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.btn_universe = QPushButton('Load Asset Universe', self)
        self.btn_universe.move(50, 50)
        self.btn_universe.resize(200,40)
        self.btn_universe.clicked.connect(self.open_asset_universe)  

        self.txt_universe = QLabel(self)
        self.txt_universe.move(260, 50)
        self.txt_universe.resize(400,40)
  
        self.btn_prices = QPushButton('Load Historic Prices', self)
        self.btn_prices.move(50, 100)
        self.btn_prices.resize(200,40)
        self.btn_prices.clicked.connect(self.load_historic_prices)    
        
        self.txt_universe_status = QLabel(self)
        self.txt_universe_status.move(260, 100)
        self.txt_universe_status.resize(400,40)
  
        self.btn_universe_reduction = QPushButton('Asset Universe Reduction', self)
        self.btn_universe_reduction.move(50, 150)
        self.btn_universe_reduction.resize(200,40)
        self.btn_universe_reduction.clicked.connect(self.universe_reduction)

        self.cmb_optimization_method = QComboBox(self)
        self.cmb_optimization_method.addItem("Mean-Variance")
        self.cmb_optimization_method.addItem("Hierarchical Risk Parity")
        self.cmb_optimization_method.addItem("Hierarchical Risk Parity (Robust)")
        self.cmb_optimization_method.resize(200,40)
        self.cmb_optimization_method.move(260, 200)

        self.btn_optimization = QPushButton('Mean Variance Optimize', self)
        self.btn_optimization.move(50, 200)
        self.btn_optimization.resize(200,40)
        self.btn_optimization.clicked.connect(self.mean_variance_optimization)    
        
        self.lbl_optimize_status = QLabel(self)
        self.lbl_optimize_status.move(470, 200)
        self.lbl_optimize_status.resize(400,40)
        
        self.sli_vol_target = QSlider(Qt.Horizontal)
        self.sli_vol_target.setValue(10)
        self.sli_vol_target.setTickPosition(QSlider.TicksBelow)
        self.sli_vol_target.setTickInterval(1)
        self.sli_vol_target.valueChanged.connect(self.standard_deviation_changed)
 
        self.lbl_vol_target = QLabel(self)
        self.lbl_vol_target.resize(400,40)

        self.dpi = 100
        self.fig = Figure((5.0, 6.0), dpi=self.dpi)
        self.can_weights = FigureCanvas(self.fig)
        self.plt_weights = self.fig.add_subplot(111)

        self.can_efficient_frontier = FigureCanvas(self.fig)
        self.plt_efficient_frontier = self.fig.add_subplot(111)

        self.main_widget = QWidget(self)
        l = QVBoxLayout(self.main_widget)
        l.addWidget(self.can_efficient_frontier)
        l.addWidget(self.lbl_vol_target)
        l.addWidget(self.sli_vol_target)
        l.addWidget(self.can_weights)
        self.can_weights.setParent(self.main_widget)

        self.main_widget.setFocus()
        self.main_widget.move(5, 250)
        self.main_widget.resize(3000,1150)
        
        self.setGeometry(300, 300, 3010, 1500)
        self.setWindowTitle('File dialog')
        self.show()
        
        self.optimization_solutions = []
        self.fixings = pd.DataFrame()
        
        DefaultPath = 'Universe/AssetUniverse.csv'
        if os.path.exists(DefaultPath):
            self.txt_universe.setText(os.path.relpath(DefaultPath))
            self.symbols = pd.read_csv(self.txt_universe.text())
            self.update_cache_status()
        
    def open_asset_universe(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', 'Universe/AssetUniverse.csv')

        if fname[0]:
            self.txt_universe.setText(os.path.relpath(fname[0]))        
            self.symbols = pd.read_csv(self.txt_universe.text())
        else:
            self.txt_universe.setText("Select Asset Universe File")       
        
        self.update_cache_status()
            
    def load_historic_prices(self):
        #QApplication.setOverrideCursor(Qt.WaitCursor)
        fixings, info = data_fns.yahoo_prices(self.symbols, start_date='1970-01-01')
        #QApplication.restoreOverrideCursor()
        fixings.to_pickle(self.get_cache_name())   
        pkl.dump(info, open(self.get_info_cache_name(self.get_cache_name()), "wb"))
        self.update_cache_status()

    def universe_reduction(self):
        fixings_sparse = pd.read_pickle(self.get_cache_name())
        info = pkl.load(open(self.get_info_cache_name(self.get_cache_name()), "rb"))

        reduction = UniverseReduction(fixings_sparse, info)

        fname = QFileDialog.getSaveFileName(self, 'Save file', 'Universe/ReducedAssetUniverse.csv')
        if fname[0]:
            reduction.store(fname[0])
            self.txt_universe.setText(os.path.relpath(fname[0]))
            self.symbols = pd.read_csv(self.txt_universe.text())

    def mean_variance_optimization(self):
        self.lbl_optimize_status.setText("Optimization Running...")
        
        fixings_sparse = pd.read_pickle(self.get_cache_name())
        info = pkl.load(open(self.get_info_cache_name(self.get_cache_name()), "rb"))
        self.fixings = fixings_sparse[fixings_sparse.index >= max([val['start_date'] for key, val in info.items()]) ].fillna(method='ffill')

        if(self.cmb_optimization_method.currentText() == "Mean-Variance"):
            self.optimization_solutions = mean_variance(self.fixings)
            self.plot_portfolios(self.optimization_solutions)
        elif(self.cmb_optimization_method.currentText() == "Hierarchical Risk Parity"):
            self.optimization_solutions = hierarchical_risk_parity(self.fixings)
            self.plot_dendrogram(self.optimization_solutions[0]['linkage'])
            clusters = sch.fcluster(self.optimization_solutions[0]['linkage'], 0.5, 'distance')
            print(dict(itertools.groupby(zip(self.fixings.columns, clusters))))
        elif(self.cmb_optimization_method.currentText() == "Hierarchical Risk Parity (Robust)"):
            self.optimization_solutions = hierarchical_risk_parity_robust(self.fixings)
            self.plot_dendrogram(self.optimization_solutions[0]['linkage'])
        else:
            raise ValueError("Optimization method not yet implemented")
            
        self.lbl_optimize_status.setText("Optimization Complete")
        self.optimization_solutions = sorted(self.optimization_solutions, key=lambda x: x['sd'])
        self.sli_vol_target.setMinimum(self.optimization_solutions[0]['sd']*1000)
        self.sli_vol_target.setMaximum(self.optimization_solutions[-1]['sd']*1000)
        self.standard_deviation_changed()

    def get_cache_name(self):
        return os.path.normpath('Pickle/' + self.txt_universe.text().replace(".csv", ".pkl").translate(
                                str.maketrans({"\\":  r"-", "/":  r"-"})))
    
    def get_info_cache_name(self, cache):
        return cache.replace(".pkl", "_info.pkl")

    def update_cache_status(self):
        if os.path.exists(self.get_cache_name()) and os.path.exists(self.get_info_cache_name(self.get_cache_name())):
            info = pkl.load(open(self.get_info_cache_name(self.get_cache_name()), "rb"))
            status = 'Cached. Max start date: {}'.format(max([val['start_date'] for key, val in info.items()]))
        else:
            status = 'Nothing Cached @ {}'.format(self.get_cache_name())

        self.txt_universe_status.setText(status)

    def plot_portfolios(self, sols):
        for i in sols:
            self.plt_efficient_frontier.plot(i['sd'], i['mean'], 'bs')

        # Do we want to resample to just weekly/monthly fixings?
        resample = self.fixings.resample('W-MON').mean()
        returns = resample.pct_change(fill_method='pad')

        p = returns.mean().as_matrix()
        covs = returns.cov().as_matrix()
        for i, mean in enumerate(p):
            self.plt_efficient_frontier.plot(cvxpy.sqrt(covs[i,i]).value, mean, 'ro')

        self.plt_efficient_frontier.set_xlabel('Standard deviation')
        self.plt_efficient_frontier.set_ylabel('Return')
        self.can_efficient_frontier.draw()

    def plot_dendrogram(self, linkage):
        """self.plt_efficient_frontier.figure(figsize=(25, 10))
        self.plt_efficient_frontier.title('Hierarchical Clustering Dendrogram')
        self.plt_efficient_frontier.set_xlabel('sample index')
        self.plt_efficient_frontier.set_ylabel('distance')
        sch.dendrogram(
            linkage,
            leaf_rotation=90.,  # rotates the x axis labels
            leaf_font_size=8.,  # font size for the x axis labels
        )
        self.plt_efficient_frontier.draw()"""
        plt.figure(figsize=(25, 10))
        plt.title('Hierarchical Clustering Dendrogram')
        plt.xlabel('sample index')
        plt.ylabel('distance')
        sch.dendrogram(
            linkage,
            leaf_rotation=90.,  # rotates the x axis labels
            leaf_font_size=8.,  # font size for the x axis labels
        )
        plt.show()

    def draw_weights(self, sol):
        self.plt_weights.clear()
        self.plt_weights.grid(1)
        y_pos = np.arange(len(sol['wgts']))
        self.plt_weights.bar(y_pos, sol['wgts'].values())
        self.plt_weights.set_xticks(y_pos+0.5)
        self.plt_weights.set_xticklabels(sol['wgts'].keys(), rotation='vertical')
        self.can_weights.draw()

    def standard_deviation_changed(self):
        TgtVol = self.sli_vol_target.value()/1000
        self.lbl_vol_target.setText("Target Vol: {}%".format(TgtVol*100))
        sol = next(filter((lambda z, tgt=TgtVol: z['sd'] >= tgt), self.optimization_solutions))
        self.draw_weights(sol)

if __name__ == '__main__':
    app = 0
    app = QApplication(sys.argv)
    ex = Launchpad()
    sys.exit(app.exec_())