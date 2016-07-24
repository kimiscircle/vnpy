# encoding: UTF-8

import sys
import ctypes
import platform
from PyQt4 import QtCore
from vtEngine import MainEngine


# ----------------------------------------------------------------------
def main():
    """主程序入口"""
    # 重载sys模块，设置默认字符串编码方式为utf8
    reload(sys)
    sys.setdefaultencoding('utf8')

    # 设置Windows底部任务栏图标
    if platform.uname() == 'Windows':
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('vn.trader')

        # 初始化Qt应用对象
    app = QtCore.QCoreApplication(sys.argv)

    # 初始化主引擎和主窗口对象
    mainEngine = MainEngine()

    # 在主线程中启动Qt事件循环
    sys.exit(app.exec_())

    # 连接mongo数据库
    mainEngine.dbConnect()

    # 连接CTP接口
    mainEngine.connect('CTP')


if __name__ == '__main__':
    main()
