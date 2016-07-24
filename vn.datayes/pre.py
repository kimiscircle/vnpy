from .storage import *
import pandas as pd
import os
dc = DBConfig()
api = PyApi(Config())
mc = MongodController(dc, api)
mc._collNames['futTicker'] = mc._allFutTickers()
mc._ensure_index()