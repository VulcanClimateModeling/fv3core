from fv3core.stencils.d2a2c_vect import d2a2c_vect

from .translate import TranslateFortranData2Py


class TranslateD2A2C_Vect(TranslateFortranData2Py):
    def __init__(self, grid):
        super().__init__(grid)
        self.in_vars["data_vars"] = {
            "uc": {},
            "vc": {},
            "u": {},
            "v": {},
            "ua": {},
            "va": {},
            "utc": {},
            "vtc": {},
        }
        self.in_vars["parameters"] = ["dord4"]
        self.out_vars = {
            "uc": grid.x3d_domain_dict(),
            "vc": grid.y3d_domain_dict(),
            "ua": {},
            "va": {},
            "utc": {},
            "vtc": {},
        }
        # TODO: This seems to be needed primarily for the edge_interpolate_4
        # methods, can we rejigger the order of operations to make it match to
        # more precision?
        self.max_error = 2e-10

    def compute(self, inputs):
        self.make_storage_data_input_vars(inputs)
        assert bool(inputs["dord4"]) is True
        del inputs["dord4"]
        d2a2c_vect(
            self.grid.cosa_s,
            self.grid.cosa_u,
            self.grid.cosa_v,
            self.grid.dxa,
            self.grid.dya,
            self.grid.rsin2,
            self.grid.rsin_u,
            self.grid.rsin_v,
            self.grid.sin_sg1,
            self.grid.sin_sg2,
            self.grid.sin_sg3,
            self.grid.sin_sg4,
            **inputs,
            origin=self.grid.compute_origin(add=(-2, -2, 0)),
            domain=self.grid.domain_shape_compute(add=(4, 4, 0)),
        )
        return self.slice_output(inputs)
