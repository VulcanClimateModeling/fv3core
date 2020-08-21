import fv3core.utils.gt4py_utils as utils
import gt4py.gtscript as gtscript
from gt4py.gtscript import computation, interval, PARALLEL

sd = utils.sd


@utils.stencil()
def adjustmentfactor_stencil(adjustment: sd, q_out: sd):
    with computation(PARALLEL), interval(...):
        q_out[0, 0, 0] = q_out * adjustment


@utils.stencil()
def adjust_divide_stencil(adjustment: sd, q_out: sd):
    with computation(PARALLEL), interval(...):
        q_out[0, 0, 0] = q_out / adjustment


@utils.stencil()
def multiply_stencil(in1: sd, in2: sd, out: sd):
    with computation(PARALLEL), interval(...):
        out[0, 0, 0] = in1 * in2


@utils.stencil()
def divide_stencil(in1: sd, in2: sd, out: sd):
    with computation(PARALLEL), interval(...):
        out[0, 0, 0] = in1 / in2


@utils.stencil()
def addition_stencil(in1: sd, in2: sd, out: sd):
    with computation(PARALLEL), interval(...):
        out[0, 0, 0] = in1 + in2


@utils.stencil()
def add_term_stencil(in1: sd, out: sd):
    with computation(PARALLEL), interval(...):
        out[0, 0, 0] = out + in1


@utils.stencil()
def add_term_two_vars(in1: sd, out1: sd, in2: sd, out2: sd):
    with computation(PARALLEL), interval(...):
        out1[0, 0, 0] = out1 + in1
        out2[0, 0, 0] = out2 + in2


@utils.stencil()
def multiply_constant(in1: sd, in2: float, out: sd):
    with computation(PARALLEL), interval(...):
        out[0, 0, 0] = in1 * in2


@utils.stencil()
def multiply_constant_inout(inout: sd, in_float: float):
    with computation(PARALLEL), interval(...):
        inout[0, 0, 0] = in_float * inout


@utils.stencil()
def floor_cap(var: sd, floor_value: float):
    with computation(PARALLEL), interval(0, None):
        var[0, 0, 0] = var if var > floor_value else floor_value


@gtscript.function
def absolute_value(in_array):
    abs_value = in_array if in_array > 0 else -in_array
    return abs_value


@gtscript.function
def sign(a, b):
    asignb = abs(a)
    if b > 0:
        asignb = asignb
    else:
        asignb = -1.0 * asignb
    return asignb


@gtscript.function
def min_fn(a, b):
    return a if a < b else b


@gtscript.function
def max_fn(a, b):
    return a if a > b else b


@gtscript.function
def dim(a, b):
    diff = a - b if a - b > 0 else 0
    return diff
