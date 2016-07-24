from .storage import *
dc = DBConfig()
api = PyApi(Config())
mc = MongodController(dc, api)
mc.update_future_D1() 