#!/usr/bin/env python3
import fv3.utils.gt4py_utils as utils
import gt4py.gtscript as gtscript
import fv3._config as spec
from gt4py.gtscript import computation, interval, PARALLEL
import fv3.stencils.d2a2c_vect as d2a2c
import fv3.stencils.divergence_corner as divergence_corner
import fv3.stencils.transportdelp as transportdelp
import fv3.stencils.ke_c_sw as ke_c_sw
import fv3.stencils.circulation_cgrid as circulation_cgrid
import fv3.stencils.vorticitytransport_cgrid as vorticity_transport

sd = utils.sd


@utils.stencil()
def geoadjust_ut(ut: sd, dy: sd, sin_sg3: sd, sin_sg1: sd, dt2: float):
    with computation(PARALLEL), interval(...):
        ut[0, 0, 0] = (
            dt2 * ut * dy * sin_sg3[-1, 0, 0] if ut > 0 else dt2 * ut * dy * sin_sg1
        )


@utils.stencil()
def geoadjust_vt(vt: sd, dx: sd, sin_sg4: sd, sin_sg2: sd, dt2: float):
    with computation(PARALLEL), interval(...):
        vt[0, 0, 0] = (
            dt2 * vt * dx * sin_sg4[0, -1, 0] if vt > 0 else dt2 * vt * dx * sin_sg2
        )


@utils.stencil()
def absolute_vorticity(vort: sd, fC: sd, rarea_c: sd):
    with computation(PARALLEL), interval(...):
        vort[0, 0, 0] = fC + rarea_c * vort


def compute(delp, pt, u, v, w, uc, vc, ua, va, ut, vt, divgd, omga, dt2):
    grid = spec.grid
    dord4 = True
    nord = spec.namelist["nord"]
    origin_halo1 = (grid.is_ - 1, grid.js - 1, 0)
    fx = utils.make_storage_from_shape(delp.shape, origin_halo1)
    fy = utils.make_storage_from_shape(delp.shape, origin_halo1)
    d2a2c.compute(dord4, uc, vc, u, v, ua, va, ut, vt)
    if nord > 0:
        divergence_corner.compute(u, v, ua, va, divgd)
    geo_origin = (grid.is_ - 1, grid.js - 1, 0)
    geoadjust_ut(
        ut,
        grid.dy,
        grid.sin_sg3,
        grid.sin_sg1,
        dt2,
        origin=geo_origin,
        domain=(grid.nic + 3, grid.njc + 2, grid.npz),
    )
    geoadjust_vt(
        vt,
        grid.dx,
        grid.sin_sg4,
        grid.sin_sg2,
        dt2,
        origin=geo_origin,
        domain=(grid.nic + 2, grid.njc + 3, grid.npz),
    )
    delpc, ptc = transportdelp.compute(delp, pt, w, ut, vt, omga)
    ke, vort = ke_c_sw.compute(uc, vc, u, v, ua, va, dt2)
    circulation_cgrid.compute(uc, vc, vort)
    absolute_vorticity(
        vort,
        grid.fC,
        grid.rarea_c,
        origin=grid.compute_origin(),
        domain=(grid.nic + 1, grid.njc + 1, grid.npz),
    )
    vorticity_transport.compute(uc, vc, vort, ke, v, u, fx, fy, dt2)
    return delpc, ptc