#!/bin/bash

antlr -Dlanguage=Python3 grammar/Solidity.g4 -o parser -Xexact-output-dir -visitor
