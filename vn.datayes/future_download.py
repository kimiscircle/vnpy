from .storage import *

dc = DBConfig()
api = PyApi(Config())
mc = MongodController(dc, api)
mc.download_future_D1('20010101', '20160701')
