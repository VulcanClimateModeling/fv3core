import gt4py.gtscript as gtscript
from gt4py.gtscript import PARALLEL, computation, horizontal, interval, region

import fv3core._config as spec
import fv3core.stencils.a2b_ord4 as a2b_ord4
import fv3core.stencils.basic_operations as basic
import fv3core.utils.corners as corners
from fv3core.decorators import gtstencil
from fv3core.utils.typing import FloatField
import numpy as np
import fv3core.utils.gt4py_utils as utils

@gtscript.function
def remove_extra_term_south_corner(extra: FloatField, field: FloatField):
    # from __externals__ import i_start, i_end,  j_start                                                          
    # TODO: why does this not work?                                                                               
    # with horizontal(region[i_start, j_start], region[i_end + 1, j_start]):                                      
    #    field = field - extra[0, -1, 0]                                                                          
    # return field                                                                     
    return field - extra[0, -1, 0]
@gtscript.function
def remove_extra_term_north_corner(extra: FloatField, field: FloatField):
    # TODO: why does this not work?                                                                               
    # from __externals__ import i_start, i_end, j_end                                                             
    # with horizontal(region[i_start, j_end + 1], region[i_end + 1, j_end + 1]):                                  
    #     field = field + extra                                                                                   
    # return field                                                                    
    return field + extra

@gtscript.function
def damp_tmp(q, da_min_c, d2_bg, dddmp):
    tmpddd = dddmp * q
    mintmp = 0.2 if 0.2 < tmpddd else tmpddd
    maxd2 = d2_bg if d2_bg > mintmp else mintmp
    damp = da_min_c * maxd2
    return damp

@gtscript.function
def damping_nord0(
    u: FloatField,
    v: FloatField,
    ua: FloatField,
    va: FloatField,
    uc: FloatField,
    vc: FloatField,
    cosa_u: FloatField,
    cosa_v: FloatField,
    sina_u: FloatField,
    sina_v: FloatField,
    dxc: FloatField,
    dyc: FloatField,
    sin_sg1: FloatField,
    sin_sg2: FloatField,
    sin_sg3: FloatField,
    sin_sg4: FloatField,
    rarea_c: FloatField,
    ptc: FloatField,
    vort: FloatField,
    delpc: FloatField,
    ke: FloatField, d2_bg: FloatField,
    da_min_c: float,
    dt: float,
):
    from __externals__ import i_end, i_start, j_end, j_start, namelist

    #with computation(PARALLEL), interval(...):
    ptc = (u - 0.5 * (va[0, -1, 0] + va) * cosa_v) * dyc * sina_v
    with horizontal(region[:, j_start], region[:, j_end + 1]):
        ptc = u * dyc * sin_sg4[0, -1, 0] if vc > 0 else u * dyc * sin_sg2
    vort_copy = vort
    vort = (v - 0.5 * (ua[-1, 0, 0] + ua) * cosa_u) * dxc * sina_u
    with horizontal(region[i_start, :], region[i_end + 1, :]):
        vort = vort_copy
    with horizontal(region[i_start, :], region[i_end + 1, :]):
        vort = v * dxc * sin_sg3[-1, 0, 0] if uc > 0 else v * dxc * sin_sg1
    delpc = vort[0, -1, 0] - vort + ptc[-1, 0, 0] - ptc
    with horizontal(region[i_start, j_start], region[i_end + 1, j_start]):
        delpc = remove_extra_term_south_corner(vort, delpc)
    with horizontal(region[i_start, j_end + 1], region[i_end + 1, j_end + 1]):
        delpc = remove_extra_term_north_corner(vort, delpc)
    delpc = rarea_c * delpc
    delpcdt = delpc * dt
    absdelpcdt = delpcdt if delpcdt >= 0 else -delpcdt
    damp = damp_tmp(absdelpcdt, da_min_c, d2_bg, namelist.dddmp)
    vort = damp * delpc
    ke = ke + vort
    return  ptc, vort, delpc, ke
# TODO DELETE this when k_split_run removed from d_sw
@gtstencil
def damping_nord0_stencil(
        u: FloatField,
        v: FloatField,
        ua: FloatField,
        va: FloatField,
        uc: FloatField,
        vc: FloatField,
        cosa_u: FloatField,
        cosa_v: FloatField,
        sina_u: FloatField,
        sina_v: FloatField,
        dxc: FloatField,
        dyc: FloatField,
        sin_sg1: FloatField,
        sin_sg2: FloatField,
        sin_sg3: FloatField,
        sin_sg4: FloatField,
        rarea_c: FloatField,
        ptc: FloatField,
        vort: FloatField,
        delpc: FloatField,
        ke: FloatField, d2_bg: FloatField,
        da_min_c: float,
        dt: float,
):
    with computation(PARALLEL), interval(...):
        ptc, vort, delpc, ke = damping_nord0(u, v, ua, va, uc, vc,cosa_u,
                                             cosa_v, sina_u, sina_v, dxc,dyc,sin_sg1,
                                             sin_sg2, sin_sg3, sin_sg4, rarea_c, ptc,                                                                          vort, delpc, ke,d2_bg,                                                                                            da_min_c, dt)
# TODO delete this when k_split_run is removed from d_sw
@gtstencil()
def damping_nord_highorder_stencil_split(
    vort: FloatField,
    ke: FloatField,
    delpc: FloatField,
    divg_d: FloatField,
    nord_col: FloatField, d2_bg: FloatField,
    da_min_c: float,
    dddmp: float,
):
    from __externals__ import namelist
    with computation(PARALLEL), interval(...):
        dd8 = (da_min_c * namelist.d4_bg) ** (nord_col + 1)
        damp = damp_tmp(vort, da_min_c, d2_bg, dddmp)
        vort = damp * delpc + dd8 * divg_d
        ke = ke + vort

@gtstencil()
def damping_nord_highorder_stencil(
    vort: FloatField,
    ke: FloatField,
    delpc: FloatField,
    divg_d: FloatField,
    nord_col: FloatField, d2_bg: FloatField,
    da_min_c: float,
    dddmp: float,
):
    from __externals__ import namelist
    with computation(PARALLEL), interval(namelist.nord, None):
        dd8 = (da_min_c * namelist.d4_bg) ** (nord_col + 1)
        damp = damp_tmp(vort, da_min_c, d2_bg, dddmp)
        vort = damp * delpc + dd8 * divg_d
        ke = ke + vort


@gtscript.function
def vc_from_divg(divg_d: FloatField, divg_u: FloatField):
    return (divg_d[1, 0, 0] - divg_d) * divg_u


@gtscript.function
def uc_from_divg(divg_d: FloatField, divg_v: FloatField):
    return (divg_d[0, 1, 0] - divg_d) * divg_v


@gtscript.function
def redo_divg_d(uc: FloatField, vc: FloatField):
    return uc[0, -1, 0] - uc + vc[-1, 0, 0] - vc


@gtstencil()
def smagorinksy_diffusion_approx(delpc: FloatField, vort: FloatField, absdt: float):
    with computation(PARALLEL), interval(...):
        vort = absdt * (delpc ** 2.0 + vort ** 2.0) ** 0.5


def vorticity_calc(wk, vort, delpc, dt, nord, kstart, nk):
    if nord != 0:
        if spec.namelist.dddmp < 1e-5:
            vort[:, :, kstart : kstart + nk] = 0
        else:
            if spec.namelist.grid_type < 3:
                a2b_ord4.compute(wk, vort, kstart, nk, False)
                smagorinksy_diffusion_approx(
                    delpc,
                    vort,
                    abs(dt),
                    origin=(spec.grid.is_, spec.grid.js, kstart),
                    domain=(spec.grid.nic + 1, spec.grid.njc + 1, nk),
                )
            else:
                raise Exception("Not implemented, smag_corner")


@gtscript.function
def divergence_nt2(
    rarea_c: FloatField,
    divg_u: FloatField,
    divg_v: FloatField,
    divg_d: FloatField,
    uc: FloatField,
    vc: FloatField,
):
    from __externals__ import (
        i_end,
        i_start,
        j_end,
        j_start,
        local_ie,
        local_is,
        local_je,
        local_js,
    )

    divg_d = corners.fill_corners_bgrid_x(divg_d)
    with horizontal(region[local_is - 3 : local_ie + 4, local_js - 2 : local_je + 4]):
        vc = vc_from_divg(divg_d, divg_u)
    divg_d = corners.fill_corners_bgrid_y(divg_d)
    with horizontal(region[local_is - 2 : local_ie + 4, local_js - 3 : local_je + 4]):
        uc = uc_from_divg(divg_d, divg_v)
    vc, uc = corners.fill_corners_dgrid(vc, uc, -1.0)
    with horizontal(region[local_is - 2 : local_ie + 4, local_js - 2 : local_je + 4]):
        divg_d = redo_divg_d(uc, vc)
    with horizontal(region[i_start, j_start], region[i_end + 1, j_start]):
        divg_d = remove_extra_term_south_corner(uc, divg_d)
    with horizontal(region[i_start, j_end + 1], region[i_end + 1, j_end + 1]):
        divg_d = remove_extra_term_north_corner(uc, divg_d)
    # ASSUMED not grid.stretched_grid
    divg_d = basic.adjustmentfactor(rarea_c, divg_d)
    return divg_d, uc, vc


@gtscript.function
def divergence_nt1(
    rarea_c: FloatField,
    divg_u: FloatField,
    divg_v: FloatField,
    divg_d: FloatField,
    uc: FloatField,
    vc: FloatField,
):
    from __externals__ import (
        i_end,
        i_start,
        j_end,
        j_start,
        local_ie,
        local_is,
        local_je,
        local_js,
    )

    divg_d = corners.fill_corners_bgrid_x(divg_d)
    with horizontal(region[local_is - 2 : local_ie + 3, local_js - 1 : local_je + 3]):
        vc = vc_from_divg(divg_d, divg_u)
    divg_d = corners.fill_corners_bgrid_y(divg_d)
    with horizontal(region[local_is - 1 : local_ie + 3, local_js - 2 : local_je + 3]):
        uc = uc_from_divg(divg_d, divg_v)
    vc, uc = corners.fill_corners_dgrid(vc, uc, -1.0)
    with horizontal(region[local_is - 1 : local_ie + 3, local_js - 1 : local_je + 3]):
        divg_d = redo_divg_d(uc, vc)
    with horizontal(region[i_start, j_start], region[i_end + 1, j_start]):
        divg_d = remove_extra_term_south_corner(uc, divg_d)
    with horizontal(region[i_start, j_end + 1], region[i_end + 1, j_end + 1]):
        divg_d = remove_extra_term_north_corner(uc, divg_d)
    # ASSUMED not grid.stretched_grid
    divg_d = basic.adjustmentfactor(rarea_c, divg_d)
    return divg_d, uc, vc


@gtscript.function
def divergence_nt0(
    rarea_c: FloatField,
    divg_u: FloatField,
    divg_v: FloatField,
    divg_d: FloatField,
    uc: FloatField,
    vc: FloatField,
):
    from __externals__ import (
        i_end,
        i_start,
        j_end,
        j_start,
        local_ie,
        local_is,
        local_je,
        local_js,
    )

    vc = vc_from_divg(divg_d, divg_u)
    uc = uc_from_divg(divg_d, divg_v)
    divg_d = redo_divg_d(uc, vc)
    with horizontal(region[i_start, j_start], region[i_end + 1, j_start]):
        divg_d = remove_extra_term_south_corner(uc, divg_d)
    with horizontal(region[i_start, j_end + 1], region[i_end + 1, j_end + 1]):
        divg_d = remove_extra_term_north_corner(uc, divg_d)
    # ASSUMED not grid.stretched_grid
    divg_d = basic.adjustmentfactor(rarea_c, divg_d)
    return divg_d, uc, vc


@gtstencil(externals={})
def divergence_damping(
        cosa_u: FloatField, cosa_v: FloatField, sina_u: FloatField, sina_v: FloatField, dxc: FloatField,dyc: FloatField,
        sin_sg1: FloatField, sin_sg2: FloatField, sin_sg3: FloatField, sin_sg4: FloatField, rarea_c: FloatField,
        divg_u: FloatField,
        divg_v: FloatField,
        divg_d: FloatField,
        u: FloatField, v: FloatField, ua: FloatField, va: FloatField, 
        uc: FloatField,
        vc: FloatField,
        delpc: FloatField, ptc: FloatField, vort: FloatField, ke: FloatField, d2_bg: FloatField, da_min_c: float, dt: float
):
    from __externals__ import namelist, i_start, i_end, j_start, j_end
    with computation(PARALLEL), interval(0, namelist.nord):
        # TODO: using a function here results in vort and/or ke being incorrect
        #ptc, vort, delpc, ke = damping_nord0(
        #    u, v, ua, va, uc, vc,cosa_u,cosa_v, sina_u, sina_v, dxc,dyc,
        #    sin_sg1, sin_sg2, sin_sg3, sin_sg4, rarea_c,
        #    ptc,
        #    vort,
        #    delpc,
        #    ke,d2_bg,
        #    da_min_c,
        #    dt)
        ptc = (u - 0.5 * (va[0, -1, 0] + va) * cosa_v) * dyc * sina_v
        with horizontal(region[:, j_start], region[:, j_end + 1]):
            ptc = u * dyc * sin_sg4[0, -1, 0] if vc > 0 else u * dyc * sin_sg2
        vort_copy = vort
        vort = (v - 0.5 * (ua[-1, 0, 0] + ua) * cosa_u) * dxc * sina_u
        with horizontal(region[i_start, :], region[i_end + 1, :]):
            vort = vort_copy
        with horizontal(region[i_start, :], region[i_end + 1, :]):
            vort = v * dxc * sin_sg3[-1, 0, 0] if uc > 0 else v * dxc * sin_sg1
        delpc = vort[0, -1, 0] - vort + ptc[-1, 0, 0] - ptc
        with horizontal(region[i_start, j_start], region[i_end + 1, j_start]):
            delpc = remove_extra_term_south_corner(vort, delpc)
        with horizontal(region[i_start, j_end + 1], region[i_end + 1, j_end + 1]):
            delpc = remove_extra_term_north_corner(vort, delpc)
        delpc = rarea_c * delpc
        delpcdt = delpc * dt
        absdelpcdt = delpcdt if delpcdt >= 0 else -delpcdt
        damp = damp_tmp(absdelpcdt, da_min_c, d2_bg, namelist.dddmp)
        vort = damp * delpc
        ke = ke + vort
    
    with computation(PARALLEL), interval(namelist.nord, None):
        delpc = divg_d
        # TODO, can we call the same function 3 times, let gt4py do the extent analysis?
        # currently does not work because corner calculations need entire array,
        # and vc/uc need offsets
        divg_d, uc, vc = divergence_nt2(rarea_c, divg_u, divg_v, divg_d, uc, vc)
        divg_d, uc, vc = divergence_nt1(rarea_c, divg_u, divg_v, divg_d, uc, vc)
        divg_d, uc, vc = divergence_nt0(rarea_c, divg_u, divg_v, divg_d, uc, vc)


def compute(
    u,
    v,
    ua,
    va,
    uc,
    vc,
    ptc,
    vort,
    divg_d,
    delpc,
    ke,
    wk,
    d2_bg,
    dt,
    nord_col,
    kstart=0,
    nk=None,
    dd_test=False
):
    """Applies divergence damping to the momentum equations

    The divergence damping term of the momentum equation is computed and
    the vorticity, kinetic energy, divergence and C-grid winds are updated
    accordingly.
    Assumes this is not a nested grid.

    Args:
         u: x-velocity on the D-grid (in)
         v: y-velocity on the D-grid (in)
         ua: x-velocity on the A-grid (in)
         va: y-velocity on the A-grid (in)
         uc: x-velocity on the C-grid (inout)
         vc: y-velocity on the C-grid (inout)
         ptc: temperature (k) on the C-grid (inout)
         vort: vorticity (inout)
         ke: kinetic energy (inout)
         wk: volume-mean relative vorticity(in)
         d2_bg: coefficient for background second-order divergence damping. (in)
         dt: dynamics timestep (seconds) (in)
         nord: order of the damping scheme (in)
    """
    grid = spec.grid
    if dd_test:
        divergence_damping(
            grid.cosa_u,
            grid.cosa_v,
            grid.sina_u,
            grid.sina_v,
            grid.dxc,
            grid.dyc,
            grid.sin_sg1,
            grid.sin_sg2,
            grid.sin_sg3,
            grid.sin_sg4,
            grid.rarea_c,
            grid.divg_u,
            grid.divg_v,
            divg_d, u, v, ua, va,
            uc,
            vc,
            delpc, ptc, vort, ke, d2_bg, grid.da_min_c, dt,
            origin=grid.compute_origin(),
            domain=grid.domain_shape_compute(add=(1, 1, 0)),
        )
        # TODO when a2b ord4 no longer needs k_split_run, pull all of this into the stencil
        data = {}
        for varname in ["wk", "vort", "delpc", "dt"]:
            data[varname] = locals()[varname]
        col = {"nord": np.asarray([int(x) for x in nord_col[0, 0, :]])}
        kstarts = utils.get_kstarts(col, grid.npz + 1)
        utils.k_split_run(vorticity_calc, data, kstarts, col)
        damping_nord_highorder_stencil(
            vort,
            ke,
            delpc,
            divg_d, nord_col,d2_bg,
            grid.da_min_c,
            spec.namelist.dddmp,
            origin=grid.compute_origin(),
            domain=grid.domain_shape_compute(add=(1, 1, 0)),
        )    
    else:
        if nord_col == 0:
            damping_nord0(
                u,
                v,
                ua,
                va,
                uc,
                vc,
                grid.cosa_u,
                grid.cosa_v,
                grid.sina_u,
                grid.sina_v,
                grid.dxc,
                grid.dyc,
                grid.sin_sg1,
                grid.sin_sg2,
                grid.sin_sg3,
                grid.sin_sg4,
                grid.rarea_c,
                ptc,
                vort,
                delpc,
                ke,
                grid.da_min_c,
                d2_bg,
                dt,
                origin=(grid.is_, grid.js, kstart),
                domain=(grid.nic + 1, grid.njc + 1, nk),
            )
        else:
            damping_nonzero_nord(
            grid.rarea_c,
            grid.divg_u,
            grid.divg_v,
            divg_d,
            uc,
            vc,
            delpc,
            origin=(grid.is_, grid.js, kstart),
            domain=(
                grid.nic + 1,
                grid.njc + 1,
                nk,
            ),  
            )

            vorticity_calc(wk, vort, delpc, dt, nord, kstart, nk) 
    
            damping_nord_highorder_stencil_split(
                vort,
                ke,
                delpc,
                divg_d, nord_col,d2_bg,
                grid.da_min_c,
                spec.namelist.dddmp,
                origin=(grid.is_, grid.js, kstart),
                domain=(grid.nic + 1, grid.njc + 1, nk),
            )
