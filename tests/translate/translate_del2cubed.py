import fv3core.stencils.del2cubed as Del2Cubed
from fv3core.testing import TranslateFortranData2Py


class TranslateDel2Cubed(TranslateFortranData2Py):
    def __init__(self, grid):
        super().__init__(grid)
        self.compute_func = Del2Cubed.compute
        self.in_vars["data_vars"] = {"qdel": {}}
        self.in_vars["parameters"] = ["nmax", "cd", "km"]
        self.out_vars = {"qdel": {}}
