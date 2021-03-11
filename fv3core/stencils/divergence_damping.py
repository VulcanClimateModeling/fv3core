from typing import Optional

import gt4py.gtscript as gtscript
from gt4py.gtscript import PARALLEL, computation, horizontal, interval, region

import fv3core._config as spec
import fv3core.stencils.a2b_ord4 as a2b_ord4
import fv3core.stencils.basic_operations as basic
import fv3core.utils.corners as corners
from fv3core.decorators import gtstencil
from fv3core.utils.typing import FloatField, FloatFieldIJ


@gtstencil()
def damping_nord0(
    u: FloatField,
    v: FloatField,
    ua: FloatField,
    va: FloatField,
    uc: FloatField,
    vc: FloatField,
    cosa_u: FloatFieldIJ,
    cosa_v: FloatFieldIJ,
    sina_u: FloatFieldIJ,
    sina_v: FloatFieldIJ,
    dxc: FloatFieldIJ,
    dyc: FloatFieldIJ,
    sin_sg1: FloatFieldIJ,
    sin_sg2: FloatFieldIJ,
    sin_sg3: FloatFieldIJ,
    sin_sg4: FloatFieldIJ,
    rarea_c: FloatFieldIJ,
    ptc: FloatField,
    vort: FloatField,
    delpc: FloatField,
    ke: FloatField,
    da_min_c: float,
    d2_bg: float,
    dt: float,
):
    from __externals__ import i_end, i_start, j_end, j_start, namelist

    with computation(PARALLEL), interval(...):
        ptc = (u - 0.5 * (va[0, -1, 0] + va) * cosa_v) * dyc * sina_v
        with horizontal(region[:, j_start], region[:, j_end + 1]):
            ptc = u * dyc * sin_sg4[0, -1] if vc > 0 else u * dyc * sin_sg2
        vort_copy = vort
        vort = (v - 0.5 * (ua[-1, 0, 0] + ua) * cosa_u) * dxc * sina_u
        with horizontal(region[i_start, :], region[i_end + 1, :]):
            vort = vort_copy
        with horizontal(region[i_start, :], region[i_end + 1, :]):
            vort = v * dxc * sin_sg3[-1, 0] if uc > 0 else v * dxc * sin_sg1
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


@gtstencil()
def damping_nord_highorder_stencil(
    vort: FloatField,
    ke: FloatField,
    delpc: FloatField,
    divg_d: FloatField,
    da_min_c: float,
    d2_bg: float,
    dddmp: float,
    dd8: float,
):
    with computation(PARALLEL), interval(...):
        damp = damp_tmp(vort, da_min_c, d2_bg, dddmp)
        vort = damp * delpc + dd8 * divg_d
        ke = ke + vort


@gtscript.function
def vc_from_divg(divg_d: FloatField, divg_u: FloatFieldIJ):
    return (divg_d[1, 0, 0] - divg_d) * divg_u


@gtscript.function
def uc_from_divg(divg_d: FloatField, divg_v: FloatFieldIJ):
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
def update_divg_d(
    rarea_c: FloatFieldIJ, divg_d: FloatField, uc: FloatField, vc: FloatField
):
    from __externals__ import i_end, i_start, j_end, j_start

    divg_d = redo_divg_d(uc, vc)
    with horizontal(region[i_start, j_start], region[i_end + 1, j_start]):
        divg_d = remove_extra_term_south_corner(uc, divg_d)
    with horizontal(region[i_start, j_end + 1], region[i_end + 1, j_end + 1]):
        divg_d = remove_extra_term_north_corner(uc, divg_d)
    # ASSUMED not grid.stretched_grid
    divg_d = basic.adjustmentfactor(rarea_c, divg_d)
    return divg_d


@gtscript.function
def divergence_subsequent(
    rarea_c: FloatFieldIJ,
    divg_u: FloatFieldIJ,
    divg_v: FloatFieldIJ,
    divg_d: FloatField,
    uc: FloatField,
    vc: FloatField,
):
    from __externals__ import local_ie, local_is, local_je, local_js

    divg_d = corners.fill_corners_bgrid_x(divg_d)
    with horizontal(region[local_is - 3 : local_ie + 4, local_js - 2 : local_je + 4]):
        vc = vc_from_divg(divg_d, divg_u)
    divg_d = corners.fill_corners_bgrid_y(divg_d)
    with horizontal(region[local_is - 2 : local_ie + 4, local_js - 3 : local_je + 4]):
        uc = (divg_d[0, 1, 0] - divg_d) * divg_v  # uc_from_divg(divg_d, divg_v)
    vc, uc = corners.fill_corners_dgrid(vc, uc, -1.0)
    divg_d = update_divg_d(rarea_c, divg_d, uc, vc)
    return divg_d, uc, vc

@gtscript.function
def divergence_subsequent1(
    rarea_c: FloatFieldIJ,
    divg_u: FloatFieldIJ,
    divg_v: FloatFieldIJ,
    divg_d: FloatField,
    uc: FloatField,
    vc: FloatField,
):
    from __externals__ import local_ie, local_is, local_je, local_js
    divg_d = corners.fill_corners_bgrid_x(divg_d)
    with horizontal(region[local_is - 2 : local_ie + 3, local_js - 1 : local_je + 3]):
        vc = vc_from_divg(divg_d, divg_u)
    divg_d = corners.fill_corners_bgrid_y(divg_d)
    with horizontal(region[local_is - 1 : local_ie + 3, local_js - 2 : local_je + 3]):
        uc = (divg_d[0, 1, 0] - divg_d) * divg_v #uc_from_divg(divg_d, divg_v)
    vc, uc = corners.fill_corners_dgrid(vc, uc, -1.0)
    divg_d = update_divg_d(rarea_c, divg_d, uc, vc)
    return divg_d, uc, vc


@gtscript.function
def divergence_at_nord(
    rarea_c: FloatFieldIJ,
    divg_u: FloatFieldIJ,
    divg_v: FloatFieldIJ,
    divg_d: FloatField,
    uc: FloatField,
    vc: FloatField,
):
    from __externals__ import local_ie, local_is, local_je, local_js
    with horizontal(region[local_is - 1 : local_ie + 2, local_js : local_je + 2]):
        vc = vc_from_divg(divg_d, divg_u)
    with horizontal(region[local_is : local_ie + 2, local_js - 1 : local_je + 2]):
        uc = uc_from_divg(divg_d, divg_v)
    divg_d = update_divg_d(rarea_c, divg_d, uc, vc)
    return divg_d, uc, vc


@gtstencil()
def damping_nonzero_nord(
    rarea_c: FloatFieldIJ,
    divg_u: FloatFieldIJ,
    divg_v: FloatFieldIJ,
    divg_d: FloatField,
    uc: FloatField,
    vc: FloatField,
    delpc: FloatField,
):

    with computation(PARALLEL), interval(...):
        delpc = divg_d
        # TODO, can we call the same function 3 times, let gt4py do the extent analysis?
        # currently does not work because corner calculations need entire array,
        # and vc/uc need offsets
        # Another TODO: once there is an idea of 'repetition', we need to loop
        # namelist.nord times, not always 3 times, that is just what we have
        # it set to. nord = 0, 1, or 2 are possible options
        divg_d, uc, vc = divergence_subsequent(rarea_c, divg_u, divg_v, divg_d, uc, vc)
        divg_d, uc, vc = divergence_subsequent1(rarea_c, divg_u, divg_v, divg_d, uc, vc)
        divg_d, uc, vc = divergence_at_nord(rarea_c, divg_u, divg_v, divg_d, uc, vc)


def compute(
    u: FloatField,
    v: FloatField,
    ua: FloatField,
    va: FloatField,
    uc: FloatField,
    vc: FloatField,
    ptc: FloatField,
    vort: FloatField,
    divg_d: FloatField,
    delpc: FloatField,
    ke: FloatField,
    wk: FloatField,
    d2_bg: float,
    dt: float,
    nord: int,
    kstart: int = 0,
    nk: Optional[int] = None,
):
    """Applies divergence damping to the momentum equations

    The divergence damping term of the momentum equation is computed using
    the double laplacian of the horizontal divergence oon a Lagrangian surface.
    The vorticity, kinetic energy, divergence and C-grid winds are updated
    accordingly.
    Assumes this is not a nested grid.

    Args:
         u: x-velocity on the D-grid (in)
         v: y-velocity on the D-grid (in)
         ua: x-velocity on the A-grid (in)
         va: y-velocity on the A-grid (in)
         uc: x-velocity on the C-grid (inout)
         vc: y-velocity on the C-grid (inout)
         ptc: potential temperature (k) on the C-grid (inout)
         vort: vorticity (inout)
         ke: kinetic energy (inout)
         wk: volume-mean relative vorticity(in)
         d2_bg: coefficient for background second-order divergence damping. (in)
         dt: dynamics timestep (seconds) (in)
         nord: order of the damping scheme (in)
    """
    grid = spec.grid
    if nk is None:
        nk = grid.npz - kstart
    if nord == 0:
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
            origin=(grid.is_, grid.js, kstart),  # (grid.isd, grid.jsd, kstart),
            domain=(
                grid.nic + 1,
                grid.njc + 1,
                nk,
            ),  # (grid.nid + 1, grid.njd + 1, nk),
        )

        vorticity_calc(wk, vort, delpc, dt, nord, kstart, nk)
        # TODO put this inside of stencil when grid variables an be externals
        if grid.stretched_grid:
            dd8 = grid.da_min * spec.namelist.d4_bg ** (nord + 1)
        else:
            dd8 = (grid.da_min_c * spec.namelist.d4_bg) ** (nord + 1)
        damping_nord_highorder_stencil(
            vort,
            ke,
            delpc,
            divg_d,
            grid.da_min_c,
            d2_bg,
            spec.namelist.dddmp,
            dd8,
            origin=(grid.is_, grid.js, kstart),
            domain=(grid.nic + 1, grid.njc + 1, nk),
        )
