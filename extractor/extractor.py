# Parse a groth16 verifier written in Solidity and generate a Python version.
from antlr4.InputStream import InputStream
from antlr4 import CommonTokenStream, ParseTreeWalker

from parser.SolidityLexer import SolidityLexer
from parser.SolidityParser import SolidityParser
from parser.SolidityListener import SolidityListener

from generator import generate_verifier

class SolidityContract:
    def __init__(self, name):
        self.name = name
        self.stateVars = dict()

    def addStateVar(self, name, expr):
        self.stateVars[name] = expr

    def __str__(self):
        return f"Contract {self.name}:\n  state vars: {self.stateVars}\n  functions: {self.functions}"


class ExtractListener(SolidityListener):
    def __init__(self):
        self.contracts = dict()
        self.currentContract = None

    def enterContractDefinition(self, ctx):
        print( "contract", ctx.identifier().getText() )
        contract = SolidityContract(ctx.identifier().getText())
        self.contracts[contract.name] = contract
        self.currentContract = contract

    def exitContractDefinition(self, ctx):
        self.currentContract = None

    def exitStateVariableDeclaration(self, ctx):
        v_id = ctx.identifier().getText()
        v_expr = ctx.expression().getText() if ctx.expression() else None
        print( f"state var: {v_id}: {v_expr}" )
        self.currentContract.stateVars[v_id] = v_expr

def parse(text, out):
    input_stream = InputStream(text)
    lexer = SolidityLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = SolidityParser(token_stream)
    tree = parser.sourceUnit()
    walker = ParseTreeWalker()
    listener = ExtractListener()
    walker.walk(listener, tree)

    has_processed = False
    for name, contract in listener.contracts.items():
        if name == "Groth16Verifier":
            if has_processed:
                raise ValueError("Multiple Groth16Verifier found")
            generate_verifier( contract, out )
            has_processed = True

def process_file(input_path, output_path):
    with open(input_path, 'r', encoding="utf-8") as f:
        with open(output_path, 'w', encoding="utf-8") as out:
            return parse(f.read(), out)

if __name__ == "__main__":
    import sys
    assert len(sys.argv) == 3
    process_file( sys.argv[1], sys.argv[2] )
