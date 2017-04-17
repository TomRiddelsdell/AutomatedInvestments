import pandas as pd
import scipy.cluster.hierarchy as sch
from optimize_fns import correl_distance
import itertools
from operator import itemgetter
import datetime as dt

class UniverseReduction(object):

    def __init__(self, fixings, asset_info):

        # cluster the assets into groups from which we can choose the most appropriate to invest in
        rets = fixings.pct_change()
        corr = pd.DataFrame(rets.corr())
        dist = correl_distance(corr)
        link = sch.linkage(dist, 'single')
        clusters = sch.fcluster(link, 1, 'distance')
        grouping_it = itertools.groupby(zip(corr.columns, clusters), itemgetter(1))

        self.grouping = [list([x[0] for x in assets[1]]) for assets in grouping_it]
        self.results = self._enrich([self._winner(group, asset_info, fixings) for group in self.grouping], asset_info)

    def _winner(self, assets, asset_info, fixings):

        fixings.ffill()

        # check if we have multiple denomination currencies available in the group
        ccy_groups = list(itertools.groupby(assets, lambda x: asset_info[x]['currency']))
        if(len(ccy_groups) > 1):
            raise NotImplementedError("We need to implement a way of choosing the desired denomination currency or comparing asssets across different currencies")

        # if removing an asset doubles our fixings history then exclude it from the group
        def fixings_start(assets):
            return(max(map(lambda x: asset_info[x]['start_date'], assets), default=dt.datetime.now()))

        filtered_assets = list(filter(
            lambda a: (dt.datetime.now() - fixings_start(assets)) > 0.5 * (dt.datetime.now() - fixings_start(filter(lambda b: b != a, assets))),
            assets))

        # check for fees

        # check for Total Return, Excess Return or Price Return

        # over the time period for which we have data on each asset in the group find the best performer
        group_fixings_start = fixings_start(filtered_assets)
        perfs = [fixings[a][-1] / fixings[a][group_fixings_start] for a in filtered_assets]

        return sorted(zip(filtered_assets, perfs), key=itemgetter(1))[-1][0]

    def _enrich(self, assets, asset_info):
        df = pd.DataFrame({x: {**{'Ticker':x}, **asset_info[x]} for x in assets})
        return(df.transpose())

    def store(self, fname):
        self.results.to_csv(fname)
