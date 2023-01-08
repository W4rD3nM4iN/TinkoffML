import argparse
import sys
import ast
import os


def CreateParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile", type=str)
    parser.add_argument("outputfile", type=str)

    return parser


class Compare:
    def D(self, a, b):
        a = a
        n, m = len(a), len(b)
        if n > m:
            a, b = b, a
            n, m = m, n
        current = range(n + 1)
        for i in range(1, m + 1):
            previous, current = current, [i] + [0] * n
            for j in range(1, n + 1):
                add, remove, change = previous[j] + 1, current[j - 1] + 1, previous[j - 1]
                if a[j - 1] != b[i - 1]:
                    change += 1
                current[j] = min(add, remove, change)
        return current[n]


class NormaliseText(ast.NodeTransformer):

    def CreateText(self, filename):
        f = open(filename, 'r')
        text = ''
        for line in f.readlines():
            text += line
        return text

    def CreateTree(self, text):
        tree = ast.parse(text)
        return tree

    def CreateLine(self, tree):
        l = ast.unparse(tree).split('\n')
        for line in l.copy():

            if 'v = ' in line and line[0] == 'v' or 'import' in line:
                l.remove(line)
        l = ''.join(l)
        return l

    def visit_Name(self, tree):
        return ast.Name(id='v', ctx=tree.ctx)

    def PrepareForComparison(self, filename):
        text = self.CreateText(filename)
        tree = self.CreateTree(text)
        newtree = self.visit(tree)
        line = self.CreateLine(newtree)
        return line


if __name__ == '__main__':
    parser = CreateParser()
    args = parser.parse_args(sys.argv[1:])
    inpfile = args.inputfile
    outputfile = args.outputfile
    pref = os.path.dirname(os.path.abspath(__file__)) + '\\'

    f = open(pref + inpfile, 'r')
    f1 = open(pref + outputfile, 'w')
    pref += 'plagiat\\'
    for line in f.readlines():
        try:
            line = line.replace('/', '\\').split()
            filename_a, filename_b = pref + line[0], pref + line[1]
            a = NormaliseText().PrepareForComparison(filename_a)
            b = NormaliseText().PrepareForComparison(filename_b)
            ans = str(Compare().D(a, b) / len(a))
            f1.write(ans + '\n')
        except FileNotFoundError:
            f1.write('Такого файла нет' + '\n')
