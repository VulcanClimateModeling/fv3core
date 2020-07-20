


def fill_4corners(q, direction, grid):
    if direction == "x":
        for k in range(q.shape[2]):
            if grid.sw_corner:
                q[grid.is_ - 2, grid.js - 1, k] = q[grid.is_ - 1, grid.js + 1, k]
                q[grid.is_ - 1, grid.js - 1, k] = q[grid.is_ - 1, grid.js, k]
            if grid.se_corner:
                q[grid.ie + 2, grid.js - 1, k] = q[grid.ie + 1, grid.js + 1, k]
                q[grid.ie + 1, grid.js - 1, k] = q[grid.ie + 1, grid.js, k]
            if grid.nw_corner:
                q[grid.is_ - 1, grid.je + 1, k] = q[grid.is_ - 1, grid.je, k]
                q[grid.is_ - 2, grid.je + 1, k] = q[grid.is_ - 1, grid.je - 1, k]
            if grid.ne_corner:
                q[grid.ie + 1, grid.je + 1, k] = q[grid.ie + 1, grid.je, k]
                q[grid.ie + 2, grid.je + 1, k] = q[grid.ie + 1, grid.je - 1, k]
    elif direction == "y":
        for k in range(q.shape[2]):
            if grid.sw_corner:
                q[grid.is_ - 1, grid.js - 1, k] = q[grid.is_, grid.js - 1, k]
                q[grid.is_ - 1, grid.js - 2, k] = q[grid.is_ + 1, grid.js - 1, k]
            if grid.se_corner:
                q[grid.ie + 1, grid.js - 1, k] = q[grid.ie, grid.js - 1, k]
                q[grid.ie + 1, grid.js - 2, k] = q[grid.ie - 1, grid.js - 1, k]
            if grid.nw_corner:
                q[grid.is_ - 1, grid.je + 1, k] = q[grid.is_, grid.je + 1, k]
                q[grid.is_ - 1, grid.je + 2, k] = q[grid.is_ + 1, grid.je + 1, k]
            if grid.ne_corner:
                q[grid.ie + 1, grid.je + 1, k] = q[grid.ie, grid.je + 1, k]
                q[grid.ie + 1, grid.je + 2, k] = q[grid.ie - 1, grid.je + 1, k]
    else:
        raise ValueError("Direction not recognized. Specify either x or y")


def fill2_4corners(q1, q2, direction, grid):
    if direction == "x":
        for k in range(q1.shape[2]):
            if grid.sw_corner:
                q1[grid.is_ - 2, grid.js - 1, k] = q1[grid.is_ - 1, grid.js + 1, k]
                q1[grid.is_ - 1, grid.js - 1, k] = q1[grid.is_ - 1, grid.js, k]
                q2[grid.is_ - 2, grid.js - 1, k] = q2[grid.is_ - 1, grid.js + 1, k]
                q2[grid.is_ - 1, grid.js - 1, k] = q2[grid.is_ - 1, grid.js, k]
            if grid.se_corner:
                q1[grid.ie + 2, grid.js - 1, k] = q1[grid.ie + 1, grid.js + 1, k]
                q1[grid.ie + 1, grid.js - 1, k] = q1[grid.ie + 1, grid.js, k]
                q2[grid.ie + 2, grid.js - 1, k] = q2[grid.ie + 1, grid.js + 1, k]
                q2[grid.ie + 1, grid.js - 1, k] = q2[grid.ie + 1, grid.js, k]
            if grid.nw_corner:
                q1[grid.is_ - 1, grid.je + 1, k] = q1[grid.is_ - 1, grid.je, k]
                q1[grid.is_ - 2, grid.je + 1, k] = q1[grid.is_ - 1, grid.je - 1, k]
                q2[grid.is_ - 1, grid.je + 1, k] = q2[grid.is_ - 1, grid.je, k]
                q2[grid.is_ - 2, grid.je + 1, k] = q2[grid.is_ - 1, grid.je - 1, k]
            if grid.ne_corner:
                q1[grid.ie + 1, grid.je + 1, k] = q1[grid.ie + 1, grid.je, k]
                q1[grid.ie + 2, grid.je + 1, k] = q1[grid.ie + 1, grid.je - 1, k]
                q2[grid.ie + 1, grid.je + 1, k] = q2[grid.ie + 1, grid.je, k]
                q2[grid.ie + 2, grid.je + 1, k] = q2[grid.ie + 1, grid.je - 1, k]
    elif direction == "y":
        for k in range(q1.shape[2]):
            if grid.sw_corner:
                q1[grid.is_ - 1, grid.js - 1, k] = q1[grid.is_, grid.js - 1, k]
                q1[grid.is_ - 1, grid.js - 2, k] = q1[grid.is_ + 1, grid.js - 1, k]
                q2[grid.is_ - 1, grid.js - 1, k] = q2[grid.is_, grid.js - 1, k]
                q2[grid.is_ - 1, grid.js - 2, k] = q2[grid.is_ + 1, grid.js - 1, k]
            if grid.se_corner:
                q1[grid.ie + 1, grid.js - 1, k] = q1[grid.ie, grid.js - 1, k]
                q1[grid.ie + 1, grid.js - 2, k] = q1[grid.ie - 1, grid.js - 1, k]
                q2[grid.ie + 1, grid.js - 1, k] = q2[grid.ie, grid.js - 1, k]
                q2[grid.ie + 1, grid.js - 2, k] = q2[grid.ie - 1, grid.js - 1, k]
            if grid.nw_corner:
                q1[grid.is_ - 1, grid.je + 1, k] = q1[grid.is_, grid.je + 1, k]
                q1[grid.is_ - 1, grid.je + 2, k] = q1[grid.is_ + 1, grid.je + 1, k]
                q2[grid.is_ - 1, grid.je + 1, k] = q2[grid.is_, grid.je + 1, k]
                q2[grid.is_ - 1, grid.je + 2, k] = q2[grid.is_ + 1, grid.je + 1, k]
            if grid.ne_corner:
                q1[grid.ie + 1, grid.je + 1, k] = q1[grid.ie, grid.je + 1, k]
                q1[grid.ie + 1, grid.je + 2, k] = q1[grid.ie - 1, grid.je + 1, k]
                q2[grid.ie + 1, grid.je + 1, k] = q2[grid.ie, grid.je + 1, k]
                q2[grid.ie + 1, grid.je + 2, k] = q2[grid.ie - 1, grid.je + 1, k]
    else:
        raise ValueError("Direction not recognized. Specify either x or y")


def copy_sw_corner(q, direction, grid, kslice):
    for j in range(grid.js - grid.halo, grid.js):
        for i in range(grid.is_ - grid.halo, grid.is_):
            if direction == "x":
                q[i, j, kslice] = q[j, grid.is_ - i + 2, kslice]
            if direction == "y":
                q[i, j, kslice] = q[grid.js - j + 2, i, kslice]


def copy_se_corner(q, direction, grid, kslice):
    for j in range(grid.js - grid.halo, grid.js):
        for i in range(grid.ie + 1, grid.ie + grid.halo + 1):
            if direction == "x":
                q[i, j, kslice] = q[grid.je + 1 - j + 2, i - grid.ie + 2, kslice]
            if direction == "y":
                q[i, j, kslice] = q[grid.je + j - 2, grid.ie + 1 - i + 2, kslice]


def copy_ne_corner(q, direction, grid, kslice):
    for j in range(grid.je + 1, grid.je + grid.halo + 1):
        for i in range(grid.ie + 1, grid.ie + grid.halo + 1):
            if direction == "x":
                q[i, j, kslice] = q[j, 2 * (grid.ie + 1) - 1 - i, kslice]
            if direction == "y":
                q[i, j, kslice] = q[2 * (grid.je + 1) - 1 - j, i, kslice]


def copy_nw_corner(q, direction, grid, kslice):
    for j in range(grid.je + 1, grid.je + grid.halo + 1):
        for i in range(grid.is_ - grid.halo, grid.is_):
            if direction == "x":
                q[i, j, kslice] = q[grid.je + 1 - j + 2, i - 2 + grid.ie, kslice]
            if direction == "y":
                q[i, j, kslice] = q[j + 2 - grid.ie, grid.je + 1 - i + 2, kslice]


# can't actually be a stencil because offsets are variable
def copy_corners(q, direction, grid, kslice=slice(0, None)):
    if grid.sw_corner:
        copy_sw_corner(q, direction, grid, kslice)
    if grid.se_corner:
        copy_se_corner(q, direction, grid, kslice)
    if grid.ne_corner:
        copy_ne_corner(q, direction, grid, kslice)
    if grid.nw_corner:
        copy_nw_corner(q, direction, grid, kslice)


# TODO these can definitely be consolidated/made simpler
def fill_sw_corner_2d_bgrid(q, i, j, direction, grid):
    if direction == "x":
        q[grid.is_ - i, grid.js - j, :] = q[grid.is_ - j, grid.js + i, :]
    if direction == "y":
        q[grid.is_ - j, grid.js - i, :] = q[grid.is_ + i, grid.js - j, :]


def fill_nw_corner_2d_bgrid(q, i, j, direction, grid):
    if direction == "x":
        q[grid.is_ - i, grid.je + 1 + j, :] = q[grid.is_ - j, grid.je + 1 - i, :]
    if direction == "y":
        q[grid.is_ - j, grid.je + 1 + i, :] = q[grid.is_ + i, grid.je + 1 + j, :]


def fill_se_corner_2d_bgrid(q, i, j, direction, grid):
    if direction == "x":
        q[grid.ie + 1 + i, grid.js - j, :] = q[grid.ie + 1 + j, grid.js + i, :]
    if direction == "y":
        q[grid.ie + 1 + j, grid.js - i, :] = q[grid.ie + 1 - i, grid.js - j, :]


def fill_ne_corner_2d_bgrid(q, i, j, direction, grid):
    i_end = grid.halo + grid.npx - 2  # index of last value in compute domain
    j_end = grid.halo + grid.npy - 2
    if direction == "x":
        q[i_end + i, j_end + j, :] = q[i_end + j, j_end - i + 1, :]
    if direction == "y":
        q[i_end + j, j_end + i, :] = q[i_end - i + 1, j_end + j, :]


def fill_sw_corner_2d_agrid(q, i, j, direction, grid):
    if direction == "x":
        q[grid.halo - i, grid.halo - j, :] = q[grid.halo - j, grid.halo - 1 + i, :]
    if direction == "y":
        q[grid.halo - j, grid.halo - i, :] = q[grid.halo - 1 + i, grid.halo - j, :]


def fill_nw_corner_2d_agrid(q, i, j, direction, grid):
    j_end = grid.halo + grid.npy - 2
    if direction == "x":
        q[grid.halo - i, j_end + j, :] = q[grid.halo - j, j_end - i + 1, :]
    if direction == "y":
        q[grid.halo - j, j_end + i, :] = q[grid.halo - 1 + i, j_end + j, :]


def fill_se_corner_2d_agrid(q, i, j, direction, grid):
    i_end = grid.halo + grid.npx - 2  # index of last value in compute domain
    if direction == "x":
        q[i_end + i, grid.halo - j, :] = q[i_end + j, grid.halo - 1 + i, :]
    if direction == "y":
        q[i_end + j, grid.halo - i, :] = q[i_end - i + 1, grid.halo - j, :]


def fill_ne_corner_2d_agrid(q, i, j, direction, grid):
    if direction == "x":
        q[grid.ie + i, grid.je + j, :] = q[grid.ie + j, grid.je - i + 1, :]
    if direction == "y":
        q[grid.ie + j, grid.je + i, :] = q[grid.ie - i + 1, grid.je + j, :]


def fill_corners_2d(q, grid, gridtype, direction="x"):
    for i in range(1, 1 + grid.halo):
        for j in range(1, 1 + grid.halo):
            if gridtype == "B":
                if grid.sw_corner:
                    fill_sw_corner_2d_bgrid(q, i, j, direction, grid)
                if grid.nw_corner:
                    fill_nw_corner_2d_bgrid(q, i, j, direction, grid)
                if grid.se_corner:
                    fill_se_corner_2d_bgrid(q, i, j, direction, grid)
                if grid.ne_corner:
                    fill_ne_corner_2d_bgrid(q, i, j, direction, grid)
            if gridtype == "A":
                if grid.sw_corner:
                    fill_sw_corner_2d_agrid(q, i, j, direction, grid)
                if grid.nw_corner:
                    fill_nw_corner_2d_agrid(q, i, j, direction, grid)
                if grid.se_corner:
                    fill_se_corner_2d_agrid(q, i, j, direction, grid)
                if grid.ne_corner:
                    fill_ne_corner_2d_agrid(q, i, j, direction, grid)


def fill_sw_corner_vector_dgrid(x, y, i, j, grid, mysign):
    x[grid.is_ - i, grid.js - j, :] = mysign * y[grid.is_ - j, i + 2, :]
    y[grid.is_ - i, grid.js - j, :] = mysign * x[j + 2, grid.js - i, :]


def fill_nw_corner_vector_dgrid(x, y, i, j, grid):
    x[grid.is_ - i, grid.je + 1 + j, :] = y[grid.is_ - j, grid.je + 1 - i, :]
    y[grid.is_ - i, grid.je + j, :] = x[j + 2, grid.je + 1 + i, :]


def fill_se_corner_vector_dgrid(x, y, i, j, grid):
    x[grid.ie + i, grid.js - j, :] = y[grid.ie + 1 + j, i + 2, :]
    y[grid.ie + 1 + i, grid.js - j, :] = x[grid.ie - j + 1, grid.js - i, :]


def fill_ne_corner_vector_dgrid(x, y, i, j, grid, mysign):
    x[grid.ie + i, grid.je + 1 + j, :] = mysign * y[grid.ie + 1 + j, grid.je - i + 1, :]
    y[grid.ie + 1 + i, grid.je + j, :] = mysign * x[grid.ie - j + 1, grid.je + 1 + i, :]


def fill_corners_dgrid(x, y, grid, vector):
    mysign = 1.0
    if vector:
        mysign = -1.0
    for i in range(1, 1 + grid.halo):
        for j in range(1, 1 + grid.halo):
            if grid.sw_corner:
                fill_sw_corner_vector_dgrid(x, y, i, j, grid, mysign)
            if grid.nw_corner:
                fill_nw_corner_vector_dgrid(x, y, i, j, grid)
            if grid.se_corner:
                fill_se_corner_vector_dgrid(x, y, i, j, grid)
            if grid.ne_corner:
                fill_ne_corner_vector_dgrid(x, y, i, j, grid, mysign)


def fill_corners_agrid(x, y, grid, vector):
    if vector:
        mysign = -1.0
    else:
        mysign = 1.0
    i_end = grid.halo + grid.npx - 2  # index of last value in compute domain
    j_end = grid.halo + grid.npy - 2
    for i in range(1, 1 + grid.halo):
        for j in range(1, 1 + grid.halo):
            if grid.sw_corner:
                x[grid.halo - i, grid.halo - j, :] = mysign * y[grid.halo - j, grid.halo - 1 + i, :]
                y[grid.halo - j, grid.halo - i, :] = mysign * x[grid.halo - 1 + i, grid.halo - j, :]
            if grid.nw_corner:
                x[grid.halo - i, j_end + j, :] = y[grid.halo - j, j_end - i + 1, :]
                y[grid.halo - j, j_end + i, :] = x[grid.halo - 1 + i, j_end + j, :]
            if grid.se_corner:
                x[i_end + i, grid.halo - j, :] = y[i_end + j, grid.halo - 1 + i, :]
                y[i_end + j, grid.halo - i, :] = x[i_end - i + 1, grid.halo - j, :]
            if grid.ne_corner:
                x[i_end + i, j_end + j, :] = mysign * y[i_end + j, j_end - i + 1, :]
                y[i_end + j, j_end + i, :] = mysign * x[i_end - i + 1, j_end + j, :]


def corner_ke(ke, u, v, ut, vt, i, j, dt, offsets, vsign):
    dt6 = dt / 6.0
    ke[i, j, :] = dt6 * (
        (ut[i, j, :] + ut[i, j - 1, :]) * u[i + offsets["io1"], j, :]
        + (vt[i, j, :] + vt[i - 1, j, :]) * v[i, j + offsets["jo1"], :]
        + (ut[i, j + offsets["jo1"], :] + vsign * vt[i + offsets["io1"], j, :])
        * u[i + offsets["io2"], j, :]
    )


def fix_corner_ke(ke, u, v, ut, vt, dt, grid):
    if grid.sw_corner:
        offsets = {"io1": 0, "jo1": 0, "io2": -1}
        corner_ke(ke, u, v, ut, vt, grid.is_, grid.js, dt, offsets, 1)
    if grid.se_corner:
        offsets = {"io1": -1, "jo1": 0, "io2": 0}
        corner_ke(ke, u, v, ut, vt, grid.ie + 1, grid.js, dt, offsets, -1)
    if grid.ne_corner:
        offsets = {"io1": -1, "jo1": -1, "io2": 0}
        corner_ke(ke, u, v, ut, vt, grid.ie + 1, grid.je + 1, dt, offsets, 1)
    if grid.nw_corner:
        offsets = {"io1": 0, "jo1": -1, "io2": -1}
        corner_ke(ke, u, v, ut, vt, grid.is_, grid.je + 1, dt, offsets, -1)
