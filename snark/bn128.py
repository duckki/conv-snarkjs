# A wrapper class for BN128 implementation from py_ecc.
from py_ecc import optimized_bn128 as curve
from .field import FieldElement

class bn128:
    order = curve.curve_order
    prime = curve.field_modulus

    def __init__(self, pt):
        self.pt = pt

    def __neg__(self):
        return bn128(curve.neg(self.pt))

    def __add__(self, other):
        assert type(other) is bn128
        return bn128(curve.add(self.pt, other.pt))

    def __mul__(self, x):
        assert type(x) in (int, FieldElement)
        if type(x) is FieldElement:
            x = x.val
        return bn128(curve.multiply(self.pt, x))

    def __rmul__(self, x):
        return self.__mul__(x)

    def __eq__(self, other):
        return curve.eq(self.pt, other.pt)

    # `pairing` is the pairing operator `e`.
    @staticmethod
    def pairing(x, y):
        # Note: The `curve.pairing` expects `FQ2` and `FQ1` element.
        #       We want to switch their order to match EVM's `ecPairing` contract.
        return curve.pairing(y.pt, x.pt)

    @property
    def normalized(self):
        return curve.normalize(self.pt)

    def __str__(self):
        return str(self.normalized)

    @staticmethod
    def G1Point(x, y):
        return bn128((curve.FQ(x), curve.FQ(y), curve.FQ(1)))

    @staticmethod
    def G2Point(x, y):
        return bn128((curve.FQ2(x[::-1]), curve.FQ2(y[::-1]), curve.FQ2.one()))

bn128.G1 = bn128(curve.G1)
bn128.G2 = bn128(curve.G2)
bn128.GT_one = curve.FQ12.one()
