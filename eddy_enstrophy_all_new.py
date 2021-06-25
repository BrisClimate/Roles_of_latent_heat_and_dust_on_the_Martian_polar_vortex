'''
Calculates and plots eddy enstrophy for OpenMARS, Isca - all years and exps.
'''

import numpy as np
import xarray as xr
import os, sys

import analysis_functions as funcs
import colorcet as cc
import string

from cartopy import crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import (cm, colors,cycler)
import matplotlib.path as mpath
import matplotlib
from matplotlib.legend_handler import HandlerTuple

import pandas as pd

from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

if __name__ == "__main__":

    if plt.rcParams["text.usetex"]:
        fmt = r'%r \%'
    else:
        fmt = '%r'

    theta0 = 200.
    kappa = 1/4.0
    p0 = 610.

    EMARS = False
    SD = False
    ilev = 350
    norm = False

    latmax = 90
    latmin = 60

    figpath = 'Thesis/eddy_enstrophy/'

    if EMARS == True:
        PATH = '/export/anthropocene/array-01/xz19136/EMARS'
        files = '/*isentropic*'
        reanalysis = 'EMARS'
    else:
        reanalysis = 'OpenMARS'
        PATH = '/export/anthropocene/array-01/xz19136/OpenMARS/Isentropic'
        files = '/*isentropic*'
    
    if norm == True:
        NORM = '_norm'
        ymin = - 0.5
        ymax = 9.4
        tics = [0,1,2,3,4,5,6,7,8,9]
    else:
        NORM = ''
        ymin = - 1
        ymax = 55
        tics = [0,10,20,30,40,50]

    if SD == True:
        sd = '_SD'
    else:
        sd = ''

    linestyles = ['solid', 'dotted','dashed', 'dashdot']
    cols = ['#5F9ED1', '#C85200','#898989']
    labs = ["MY 24-27", "MY 28", "MY 29-32"]
    newlabel = ['Northern\nsummer solstice', 'Northern\nwinter solstice']
    newpos = [90,270]
    
    fig, axs = plt.subplots(2, 2, figsize = (16.6,15))

    for i, ax in enumerate(fig.axes):
        ax.set_xlim([0,360])
        ax.tick_params(length = 6, labelsize = 18)

        ax.set_ylim([ymin,ymax])
        ax.set_yticks(tics)

        ax2 = ax.twiny()
        ax2.set_xticks(newpos)
        ax2.set_xticklabels(newlabel,fontsize=18)

        ax2.xaxis.set_ticks_position('top')
        ax2.xaxis.set_label_position('top') 
        ax2.tick_params(length = 6)
        ax2.set_xlim(ax.get_xlim())

        ax.text(-0.04, 1.01, string.ascii_lowercase[i], size = 20,
                    transform = ax.transAxes, weight = 'bold')

        
        ax3 = ax.twinx()
        ax3.tick_params(length = 6, labelsize = 18)
        
        ax3.yaxis.set_label_position('right')
        ax3.yaxis.set_ticks_position('right')

        
        ax3.set_ylim([-0.05,1])
        
        
        ax3.set_yticks([])
        ax3.set_yticklabels([])

        if i == 0:# or i == 3:
            ax.text(0.01, 0.95, reanalysis, size = 18,
                        transform = ax.transAxes, weight = 'bold')
            ax.set_ylabel('eddy enstrophy (MPVU$^2$)', fontsize = 20)
            ax3.plot(np.linspace(265,310,20),np.zeros(20), color = 'k',
                 linewidth = '3.5',)
            
            ax.set_xticklabels([])
        elif i == 1:
            ax.text(0.01, 0.9, 'Process-attribution\nsimulations', size = 18,
                        transform = ax.transAxes, weight = 'bold')
            ax.set_yticklabels([])
            ax.set_xticklabels([])
        elif i == 2:# or i == 4:
            ax.text(0.01, 0.9, 'Yearly\nsimulations', size = 18,
                        transform = ax.transAxes, weight = 'bold')
            ax.set_ylabel('eddy enstrophy (MPVU$^2$)', fontsize = 20)
            ax3.plot(np.linspace(265,310,20),np.zeros(20), color = 'k',
                 linewidth = '3.5',)
            ax.set_xlabel('solar longitude (degrees)', fontsize = 20)
            ax2.set_xticklabels([])
        else:
            ax.text(0.01, 0.9, 'Process-attribution\nsimulations', size = 18,
                        transform = ax.transAxes, weight = 'bold')
            ax.set_yticklabels([])
            ax.set_xlabel('solar longitude (degrees)', fontsize = 20)
            ax2.set_xticklabels([])

        #elif i == 5:
        #    ax.text(0.03, 0.88, 'Process-attribution\nsimulations', size = 20,
        #                transform = ax.transAxes, weight = 'bold')
        #    ax.set_yticklabels([])
    
        #if i > 2:
        #    ax.set_xlabel('solar longitude (degrees)', fontsize = 20)
        #    
        #else:
        #    ax2.set_xticklabels(newlabel,fontsize=18)
        #    ax.set_xticklabels([])
        



    plt.subplots_adjust(hspace=.06, wspace = 0.05)




    plt.savefig(figpath+'eddy_enstrophy_new_'+str(ilev)+'K_'+reanalysis+sd+NORM+'.pdf',
            bbox_inches = 'tight', pad_inches = 0.1)

    


    
    d = xr.open_mfdataset(PATH+files, decode_times=False, concat_dim='time',
                           combine='nested',chunks={'time':'auto'})

    if EMARS==True:
        d["Ls"] = d.Ls.expand_dims({"lat":d.lat})
        #d = d.rename({"pfull":"plev"})
        #d = d.rename({"t":"tmp"})
        smooth = 200
        yearmax = 32
    else:
        smooth = 250
        d = d.sortby('time', ascending=True)
        yearmax = 33

    d = d.where(d.lat > latmin, drop = True)
    d = d.where(d.lat < latmax, drop = True)
    d = d.sel(ilev = ilev, method='nearest').squeeze()
    
    reanalysis_clim = []
    reanalysis_ls = []

    c = []

    for i in list(np.arange(24,yearmax,1)):
        di = d.where(d.MY == i, drop=True)
        print(i)
        di["Ls"] = di.Ls.sel(lat=di.lat[0]).sel(lon=di.lon[0])
        if EMARS == True:
            di = di.sortby(di.Ls, ascending=True)
        di = di.transpose("lat","lon","time")
        di = di.sortby("lat", ascending = True)
        di = di.sortby("lon", ascending = True)

        # Lait scale PV
        theta = di.ilev
        print("Scaling PV")
        laitPV = funcs.lait(di.PV, theta, theta0, kappa = kappa)
        di["scaled_PV"] = laitPV

        Zi = funcs.calc_eddy_enstr(di.scaled_PV) * 10**8
        if norm == True:
            qbar = laitPV.mean(dim='lat').mean(dim='lon')
            Zi = Zi/(qbar * 10 **4)
        
        if i != 28:
            reanalysis_clim.append(Zi)
        
        Ls = di.Ls
        if i != 28:
            reanalysis_ls.append(Ls)
        
        Zi = Zi.chunk({'time':'auto'})
        Zi = Zi.rolling(time=smooth,center=True)

        Zi = Zi.mean()

        Zi = Zi.load()
        
        ax = axs[0,0]
        if i < 28:
            color = cols[0]
            label = labs[0]
            w = '1.2'
        elif i == 28:
            color = cols[1]
            label = labs[1]
            w = '2'
        else:
            color = cols[2]
            label = labs[2]
            w = '1.2'


        ci, = ax.plot(Ls, Zi, label = label, color = color,
                     linestyle = '-', linewidth = w)

        c.append(ci)
                     
        plt.savefig(figpath+'eddy_enstrophy_new_' +str(ilev)+ 'K_'+reanalysis+sd+NORM+'.pdf',
            bbox_inches = 'tight', pad_inches = 0.1)

    c0 = [[c[j]] for j in [0,4,5]]
    
    axs[0,0].legend([tuple(c0[j]) for j in range(len(labs))], [i for i in labs],
                 fontsize = 14, loc = 'upper center', handlelength = 3,
            handler_map={tuple: HandlerTuple(ndivide=None)})

    ls0 = np.arange(0,360,0.05)
    for i in range(len(reanalysis_clim)):
        reanalysis_clim[i] = reanalysis_clim[i].assign_coords(time = (reanalysis_ls[i].values))
        reanalysis_clim[i] = reanalysis_clim[i].assign_coords(my = (i+24))
        
        x = reanalysis_clim[i]
        x.load()
        x = x.interp({"time" : ls0})#,
                            #kwargs={"fill_value":np.nan})
        reanalysis_clim[i] = x
    
    year_open = xr.concat(reanalysis_clim, dim = "my")
    year_open = year_open.mean(dim="my",skipna=True)
    year_open = year_open.chunk({'time':'auto'})
    year_open = year_open.rolling(time=100,center=True)
    year_open = year_open.mean().compute()

    c = []
    f = []

    clim0, = axs[0,1].plot(ls0,year_open, label="Reanalysis",color='k',
                         linestyle='-',linewidth='2.0')
    clim1, = axs[1,1].plot(ls0,year_open, label="Reanalysis",color='k',
                         linestyle='-',linewidth='2.0')

    c.append(clim0)
    f.append(clim1)
    
    plt.savefig(figpath+'eddy_enstrophy_new_'+str(ilev)+'K_'+reanalysis+sd+NORM+'.pdf',
                bbox_inches='tight',pad_inches=0.1)


    
    exp = ['soc_mars_mk36_per_value70.85_none_mld_2.0',
           'soc_mars_mk36_per_value70.85_none_mld_2.0_lh_rel',
           'soc_mars_mk36_per_value70.85_none_mld_2.0_cdod_clim_scenario_7.4e-05',
           'soc_mars_mk36_per_value70.85_none_mld_2.0_cdod_clim_scenario_7.4e-05_lh_rel',
           'soc_mars_mk36_per_value70.85_none_mld_2.0_with_mola_topo',
           'soc_mars_mk36_per_value70.85_none_mld_2.0_with_mola_topo_lh_rel',
           'soc_mars_mk36_per_value70.85_none_mld_2.0_with_mola_topo_cdod_clim_scenario_7.4e-05',
           'soc_mars_mk36_per_value70.85_none_mld_2.0_with_mola_topo_cdod_clim_scenario_7.4e-05_lh_rel']

    labels = [
        'Reanalysis','Control', 'LH', 'D', 'LH+D',
        'Reanalysis','T', 'LH+T', 'D+T', 'LH+D+T',
        ]

    location = ['triassic','triassic', 'anthropocene', 'anthropocene',
                'triassic','triassic', 'anthropocene', 'silurian']

    #filepath = '/export/triassic/array-01/xz19136/Isca_data'
    start_file = [33, 33, 33, 33, 33, 33, 33, 33]
    end_file = [99, 99, 99, 99, 99, 99, 99, 139]

    #axes.prop_cycle: cycler('color', ['006BA4', 'FF800E', 'ABABAB', '595959', '5F9ED1', 'C85200', '898989', 'A2C8EC', 'FFBC79', 'CFCFCF'])
    #color = plt.cm.
    #matplotlib.rcParams['axes.prop_cycle'] = cycler('color', color)
    colors = [
        '#56B4E9',
        '#0072B2',
        #'#F0E442',
        '#E69F00',
        #'#009E73',
        #'#CC79A7',
        '#D55E00',
        #'#000000',
        ]
    freq = 'daily'

    interp_file = 'atmos_'+freq+'_interp_new_height_temp_isentropic.nc'

    for i in range(len(start_file)):
        print(exp[i])
        

        filepath = '/export/' + location[i] + '/array-01/xz19136/Isca_data'
        start = start_file[i]
        end = end_file[i]

        _, _, i_files = funcs.filestrings(exp[i], filepath, start, end, interp_file)

        d = xr.open_mfdataset(i_files, decode_times=False, concat_dim='time',
                            combine='nested')

        # reduce dataset
        d = d.astype('float32')
        d = d.sortby('time', ascending=True)
        d = d.sortby('lat', ascending=True)
        d = d.sortby('lon', ascending=True)
        d = d[["PV", "mars_solar_long"]]

        d["mars_solar_long"] = d.mars_solar_long.sel(lon=0)
        d = d.where(d.mars_solar_long != 354.3762, other=359.762)
        d = d.where(d.mars_solar_long != 354.37808, other = 359.7808)

        d, index = funcs.assign_MY(d)

        x = d.sel(ilev=ilev, method='nearest').squeeze()

        x = x.where(d.lat > latmin, drop = True)
        x = x.where(d.lat < latmax, drop = True)

        print('Averaged over '+str(np.max(x.MY.values))+' MY')

        x = x.transpose("lat","lon","time")
        theta = x.ilev
        print("Scaling PV")
        laitPV = funcs.lait(x.PV, theta, theta0, kappa = kappa)
        x["scaled_PV"] = laitPV
        ens = funcs.calc_eddy_enstr(x.scaled_PV) * 10**8
        if norm == True:
            qbar = laitPV.mean(dim='lat').mean(dim='lon')
            ens = ens/(qbar * 10 **4)


        x["ens"] = ens

        dsr, N, n = funcs.make_coord_MY(x, index)

        year_mean = dsr.mean(dim='MY')
        
        Ls = year_mean.mars_solar_long[0,:]
        year_mean = year_mean.ens.chunk({'new_time':'auto'})
        year_mean = year_mean.rolling(new_time=25,center=True)
        year_mean = year_mean.mean()

        linestyle = '-'
        if i<4:
            ax = axs[0,1]
            label = labels[i+1]
            color = colors[i]
            c1, = ax.plot(Ls, year_mean, label = label, color = color,
                    linewidth = '1.5', linestyle = linestyle)
            c.append(c1)
        else:
            ax = axs[1,1]
            label = labels[i+2]
            color = colors[i-4]
            c1, = ax.plot(Ls, year_mean, label = label, color = color,
                    linewidth = '1.5', linestyle = linestyle)
            f.append(c1)
        
        if SD == True:
            year_max = dsr.max(dim='MY')
            year_min = dsr.min(dim='MY')
            year_max = year_max.ens.chunk({'new_time':'auto'})
            year_max = year_max.rolling(new_time=25,center=True)
            year_max = year_max.mean()
            year_min = year_min.ens.chunk({'new_time':'auto'})
            year_min = year_min.rolling(new_time=25,center=True)
            year_min = year_min.mean()
    
            ax.fill_between(Ls, year_min, year_max, color=color, alpha=.1)
        

        plt.savefig(figpath+'eddy_enstrophy_new_'+str(ilev)+'K_'+reanalysis+sd+NORM+'.pdf',
                bbox_inches='tight',pad_inches=0.1)

    c0 = [[c[j]] for j in range(len(c))]
    c1 = [[f[j]] for j in range(len(f))]

    axs[0,1].legend([tuple(c0[j]) for j in range(len(c0))], [i for i in labels[:5]],
                 fontsize = 14, loc = 'center left', handlelength = 3,
            handler_map={tuple: HandlerTuple(ndivide=None)})


    axs[1,1].legend([tuple(c1[j]) for j in range(len(c1))], [i for i in labels[5:]],
                 fontsize = 14, loc = 'center left', handlelength = 3,
            handler_map={tuple: HandlerTuple(ndivide=None)})

    plt.savefig(figpath+'eddy_enstrophy_new_'+str(ilev)+'K_'+reanalysis+sd+NORM+'.pdf',
                bbox_inches='tight',pad_inches=0.1)

    
    exp = ['soc_mars_mk36_per_value70.85_none_mld_2.0_with_mola_topo_cdod_clim_MY24_7.4e-05_lh_rel',
           'soc_mars_mk36_per_value70.85_none_mld_2.0_with_mola_topo_cdod_clim_MY25_7.4e-05_lh_rel',
           'soc_mars_mk36_per_value70.85_none_mld_2.0_with_mola_topo_cdod_clim_MY26_7.4e-05_lh_rel',
           'soc_mars_mk36_per_value70.85_none_mld_2.0_with_mola_topo_cdod_clim_MY27_7.4e-05_lh_rel',
           'soc_mars_mk36_per_value70.85_none_mld_2.0_with_mola_topo_cdod_clim_MY28_7.4e-05_lh_rel',
           'soc_mars_mk36_per_value70.85_none_mld_2.0_with_mola_topo_cdod_clim_MY29_7.4e-05_lh_rel',
           'soc_mars_mk36_per_value70.85_none_mld_2.0_with_mola_topo_cdod_clim_MY30_7.4e-05_lh_rel',
           'soc_mars_mk36_per_value70.85_none_mld_2.0_with_mola_topo_cdod_clim_MY31_7.4e-05_lh_rel',
           'soc_mars_mk36_per_value70.85_none_mld_2.0_with_mola_topo_cdod_clim_MY32_7.4e-05_lh_rel',]

    location = ['silurian','silurian', 'silurian', 'silurian',
                'silurian','silurian', 'silurian', 'silurian', 'silurian']
    

    freq = 'daily'

    interp_file = 'atmos_'+freq+'_interp_new_height_temp_isentropic.nc'

    #filepath = '/export/triassic/array-01/xz19136/Isca_data'
    start_file=[30, 35, 35, 35, 35, 35, 35, 35, 35]
    end_file = [80, 99, 88, 99, 99, 96, 99, 99, 88]

    c = []

    for i in range(len(exp)):
        print(exp[i])

        filepath = '/export/' + location[i] + '/array-01/xz19136/Isca_data'
        start = start_file[i]
        end = end_file[i]

        _ ,_ , i_files = funcs.filestrings(exp[i], filepath, start,
                                        end, interp_file)

        d = xr.open_mfdataset(i_files, decode_times=False, concat_dim='time',
                            combine='nested',chunks={'time':'auto'})

        # reduce dataset
        d = d.astype('float32')
        d = d.sortby('time', ascending=True)
        d = d.sortby('lat', ascending=True)
        d = d.sortby('lon', ascending=True)
        d = d[["PV", "mars_solar_long"]]

        d["mars_solar_long"] = d.mars_solar_long.sel(lon=0)
        d = d.where(d.mars_solar_long != 354.3762, other=359.762)
        print(d.mars_solar_long[0].values)

        d, index = funcs.assign_MY(d)

        x = d.sel(ilev=ilev, method='nearest').squeeze()

        x = x.where(d.lat > latmin, drop = True)
        x = x.where(d.lat < latmax, drop = True)

        print('Averaged over '+str(np.max(x.MY.values))+' MY')

        x = x.transpose("lat","lon","time")
        theta = x.ilev
        print("Scaling PV")
        laitPV = funcs.lait(x.PV, theta, theta0, kappa = kappa)
        x["scaled_PV"] = laitPV
        ens = funcs.calc_eddy_enstr(x.scaled_PV) * 10**8
        if norm == True:
            qbar = laitPV.mean(dim='lat').mean(dim='lon')
            ens = ens/(qbar * 10 **4)

        x["ens"] = ens

        dsr, N, n = funcs.make_coord_MY(x, index)
        year_mean = dsr.mean(dim='MY')
        Ls = year_mean.mars_solar_long[0,:]
        year_mean = year_mean.ens.chunk({'new_time':'auto'})
        year_mean = year_mean.rolling(new_time=25,center=True)
        year_mean = year_mean.mean()

        ax = axs[1,0]
        linestyle = '-'
        
        if i < 4:
            color = cols[0]
            w = '1.2'
            label = labs[0]
        elif i == 4:
            color = cols[1]
            label = labs[1]
            w = '2'
        else:
            color = cols[2]
            label = labs[2]
            w = '1.2'

        c1, = ax.plot(Ls, year_mean, label = label, color=color,
                    linestyle=linestyle, linewidth = w)

        c.append(c1)

        plt.savefig(figpath+'eddy_enstrophy_new_'+str(ilev)+'K_'+reanalysis+sd+NORM+'.pdf',
                    bbox_inches='tight',pad_inches=0.1)
    
    c1 = [[c[j]] for j in [0,4,5]]

    axs[1,0].legend([tuple(c1[j]) for j in [0,1,2]], [i for i in labs],
                 fontsize = 14, loc = 'center left', handlelength = 3,
            handler_map={tuple: HandlerTuple(ndivide=None)})

    plt.savefig(figpath+'eddy_enstrophy_new_'+str(ilev)+'K_'+reanalysis+sd+NORM+'.pdf',
                bbox_inches='tight',pad_inches=0.1)
