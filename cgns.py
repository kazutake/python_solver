# reference page
# https://iric-solver-dev-manual-jp.readthedocs.io/ja/latest/06/03_reference.html

import sys
import iric
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LightSource
from scipy import signal, interpolate
import flow

class cgns():

    def __init__(self, f):
        
        self.fid = iric.cg_open(f, iric.CG_MODE_MODIFY)
        iric.cg_iRIC_Init(self.fid)
        # iric.cg_iRIC_InitRead(fid)

        # set grid and arid attributes
        ier = self.set_grid()

        # set time series parameters
        ier = self.set_time_parameters()

        # set flow calculation parameters
        ier = self.set_flow_parameters()


    #--------------------------------------------------
    # set grid
    #--------------------------------------------------
    def set_grid(self):
        ier = 0

        self.ni, self.nj = iric.cg_iRIC_GotoGridCoord2d()
        x, y = iric.cg_iRIC_GetGridCoord2d()
        z = iric.cg_iRIC_Read_Grid_Real_Node('Elevation')
        s = iric.cg_iRIC_Read_Grid_Real_Cell('roughness_cell')

        xx = x.reshape(self.nj, self.ni)
        yy = y.reshape(self.nj, self.ni)
        zz = z.reshape(self.nj, self.ni)
        ss = s.reshape(self.nj-1, self.ni-1)

        # 2d plot
        # fig, ax = plt.subplots()
        # ax.contourf(xx, yy, zz, 20)

        # 3d plot
        # fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))
        # ls = LightSource(270, 45)
        # rgb = ls.shade(zz, cmap=cm.gist_earth, vert_exag=0.1, blend_mode='soft')
        # surf = ax.plot_surface(xx, yy, zz, rstride=1, cstride=1, facecolors=rgb,
        #                linewidth=0, antialiased=False, shade=False)
        # plt.show()

        self.xx = xx
        self.yy = yy
        self.zz = zz
        self.ss = ss

        return ier

    #--------------------------------------------------
    # set time series parameters
    #--------------------------------------------------
    def set_time_parameters(self):
        ier = 0

        #流量条件
        t_series = iric.cg_iRIC_Read_FunctionalWithName('discharge_waterlevel', 'time')
        q_series = iric.cg_iRIC_Read_FunctionalWithName('discharge_waterlevel', 'discharge')

        #計算時間の設定
        if iric.cg_iRIC_Read_Integer('i_sec_hour') == 2:
            t_series = t_series*3600.

        t_start = t_series[0]
        t_end = t_series[len(t_series)-1]
        t_out = iric.cg_iRIC_Read_Real('tuk')

        # class変数
        self.t_series = t_series
        self.q_series = q_series
        self.dt = iric.cg_iRIC_Read_Real('dt')
        self.istart = int(t_start / self.dt)
        self.iend = int(t_end / self.dt) + 1
        self.iout = int(t_out / self.dt)

        return ier

    #--------------------------------------------------
    # set flow calculation parameters
    #--------------------------------------------------
    def set_flow_parameters(self):
        ier = 0

        self.cip = iric.cg_iRIC_Read_Integer('j_cip')
        self.conf = iric.cg_iRIC_Read_Integer('j_conf')

        return ier

    #--------------------------------------------------
    # write calculation result
    #--------------------------------------------------
    def write_calc_result(self, ctime, flw):

        ier = 0

        # # write time
        iric.cg_iRIC_Write_Sol_Time(ctime)
        
        # # write discharge
        qq = self.get_upstream_q(ctime)
        iric.cg_iRIC_Write_Sol_BaseIterative_Real('Discharge', qq)

        # # write grid
        iric.cg_iRIC_Write_Sol_GridCoord2d(self.xx.reshape(-1), self.yy.reshape(-1))

        # # write node values
        # iric.cg_iRIC_Write_Sol_Integer("Elevation", self.zz.reshape(-1))
        iric.cg_iRIC_Write_Sol_Real("Elevation", self.zz.reshape(-1))
        iric.cg_iRIC_Write_Sol_Real("VelocityX", flw.uu.reshape(-1))
        iric.cg_iRIC_Write_Sol_Real("VelocityY", flw.vv.reshape(-1))

        # # write cell values
        # iric.cg_iRIC_Write_Sol_Cell_Integer("Manning_S", self.ss.reshape(-1))
        iric.cg_iRIC_Write_Sol_Cell_Real("ManningN_c", self.ss.reshape(-1))
        iric.cg_iRIC_Write_Sol_Cell_Real("Elevation_c", flw.zz.reshape(-1))
        iric.cg_iRIC_Write_Sol_Cell_Real("Depth_c", flw.hs.reshape(-1))
        iric.cg_iRIC_Write_Sol_Cell_Real("WaterLevel_c", flw.hh.reshape(-1))

        # # write edge values
        # iric.cg_iRIC_Write_Sol_IFace_Integer(label, val)
        # iric.cg_iRIC_Write_Sol_IFace_Real(label, val)
        # # write edge values
        # iric.cg_iRIC_Write_Sol_JFace_Integer(label, val)
        # iric.cg_iRIC_Write_Sol_JFace_Real(label, val)

        return ier

    def close(self):
        ier = 0
        iric.cg_close(self.fid)
        return ier


    #--------------------------------------------------
    # set flow calculation parameters
    #--------------------------------------------------
    def get_upstream_q(self, t):

        tt = self.t_series
        qq = self.q_series
        
        #いろいろな補間関数がある
        #https://org-technology.com/posts/univariate-interpolation.html
        func = interpolate.interp1d(tt, qq)
        # func = interpolate.interp1d(tt, qq, kind="quadratic")

        q = float(func(t))
        # q = float(q.astype(np.float64))
        # print(q)
        # print(type(q))

    
        return q
