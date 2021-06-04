import numpy as np
import cgns

class flow():

    def __init__(self, c):

        ier = 0

        #流れ計算の初期条件を設定する
        self.uu = np.zeros(c.nj*c.ni, dtype = np.float64).reshape(c.nj, c.ni)
        self.vv = np.zeros(c.nj*c.ni, dtype = np.float64).reshape(c.nj, c.ni)
        self.hs = np.zeros((c.nj-1)*(c.ni-1), dtype = np.float64).reshape(c.nj-1, c.ni-1)
        self.zz = 0.25*(c.zz[0:c.nj-1,0:c.ni-1]+c.zz[1:c.nj,0:c.ni-1]+c.zz[0:c.nj-1,1:c.ni]+c.zz[1:c.nj,1:c.ni])
        self.hh = self.hs + self.zz

        #初期流量
        q0 = c.get_upstream_q(0)


    def update(self):

        ier = 0

        


        return ier
