# Generates Python code for Groth16 verifier
import re

def print_header( out ):
    str = """
from snark.bn128 import bn128 as curve

# ============================================================================
# Curve parameters (bn128 in the case of EVM)

G1 = curve.G1
G2 = curve.G2
e = curve.pairing  # the pairing operator `e`
GT_one = curve.GT_one # representation of one in the target group of `e`
G1Point = curve.G1Point
G2Point = curve.G2Point
    """
    print(str.strip(), file=out)

def print_footer( out ):
    str = """
# ============================================================================
# REPL

from ethereum.argument_parser import parse_args

def eval( input ):
    exprs = parse_args( input )
    print( "input:" )
    for e in exprs:
        print( e )

    A = G1Point(exprs[0][0], exprs[0][1])
    B = G2Point(exprs[1][0], exprs[1][1])
    C = G1Point(exprs[2][0], exprs[2][1])
    pubSignals = exprs[3]
    ok = verifyProof(A, B, C, pubSignals)
    if ok:
        print( "verification success!" )
    else:
        print( "verification failed." )

def repl():
    while True:
        try:
            user_input = input("verifyProof> ")
            if user_input.lower() in ['exit', 'quit']:
                print("Exiting REPL.")
                break
            eval(user_input)
            print()

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    repl()
"""
    print(str.strip(), file=out)

def generate_verifier( contract, out ):
    print_header(out)
    print(file=out)

    print("""
# ============================================================================
# Verification Key data
          """, file=out)

    sv = contract.stateVars

    def ptStr(var1, var2):
        return sv[var1] + ", " + sv[var2]

    print( "alpha = G1Point(", ptStr("alphax", "alphay"), ")", file=out )
    print( f"beta = G2Point( [", ptStr("betax1", "betax2"), "]", file=out )
    print( f"              , [", ptStr("betay1", "betay2"), "] )", file=out )
    print( f"gamma = G2Point( [", ptStr("gammax1", "gammax2"), "]", file=out )
    print( f"               , [", ptStr("gammay1", "gammay2"), "] )", file=out )
    print( f"delta = G2Point( [", ptStr("deltax1", "deltax2"), "]", file=out )
    print( f"               , [", ptStr("deltay1", "deltay2"), "] )", file=out )

    # ICx variables
    ICs = []
    for v in sv:
        if re.match("IC\d+x", v):
            ICs.append(int(v[2:-1]))
            print( f"{v[:-1]} = G1Point(", ptStr(v, v[:-1]+"y"), ")", file=out )

    print(file=out)

    print( "def verifyProof( A, B, C, pubSignals ) -> bool:", file=out )
    vk_def = "Vk = "
    for i in sorted(ICs):
        ICv = "IC" + str(i)
        pubSig = "pubSignals[" + str(i-1) + "]"
        if i == 0:
            vk_def += "IC0"
        else:
            vk_def += f" + {ICv} * {pubSig}"
    print( "    " + vk_def, file=out )
    print( "    return e(-A, B) * e(alpha, beta) * e(Vk, gamma) * e(C, delta) == GT_one", file=out )
    print(file=out)
    print(file=out)

    print_footer(out)
