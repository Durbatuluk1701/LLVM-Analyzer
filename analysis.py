import re
import sys


class BBL:
    def __init__(self, label: str) -> None:
        self.label = label
        self.targets: list[str] = []

    def dotOut(self) -> str:
        retStr = ""
        retStr += f'{self.label} [shape=record, label=""]\n'
        for ind in range(len(self.targets)):
            retStr += f"{self.label} -> {self.targets[ind]} [label={ind+1}]\n"
        return retStr


def processFn(lines: list[str]) -> list[BBL]:
    bblList = [BBL("DONOTMAKEALABELNAMEDTHIS")]
    activeBBL = True
    for line in lines:
        # Find functions
        lblMatch = re.match(r"\s*(\w+)\s*:\s*", line)
        if lblMatch:
            if len(bblList) == 1 and activeBBL:
                bblList[0].label = lblMatch.group(1)
                continue
            if activeBBL:
                raise Exception("NESTED BBLS (how?)!")
            activeBBL = True
            bblList.append(BBL(lblMatch.group(1)))
            continue
        if activeBBL:
            bblDirectLeave = re.match(r"\s*br label %(\w+)", line)
            if bblDirectLeave:
                activeBBL = False
                bblList[-1].targets.append(bblDirectLeave.group(1))
                continue
            bblSplitLeave = re.match(
                r"\s*br [\w\*]+ %(\w+), label %(\w+), label %(\w+)", line
            )
            if bblSplitLeave:
                activeBBL = False
                bblList[-1].targets.append(bblSplitLeave.group(2))
                bblList[-1].targets.append(bblSplitLeave.group(3))
                continue
    return bblList


def createDotOut(bbls: list[BBL], writePath: str) -> None:
    retStr = "digraph {\n"
    for bbl in bbls:
        retStr += bbl.dotOut()
    with open(writePath, "w") as fd:
        fd.write(retStr + "}\n")


def quickGet(l: list[str], val: str) -> int:
    return l.index(val) if val in l else -1


def splitIntoFns(lines: list[str]) -> list[list[str]]:
    fnList: list[list[str]] = []
    activeFnMode = False
    for line in lines:
        # Find functions
        fnVal = re.match(r"\s*define [\w\*]+ @(\w+)\(.+\) {", line)
        if fnVal:
            if activeFnMode:
                raise Exception("NESTED FNS!")
            activeFnMode = True
            fnList.append([fnVal.group(1)])
            continue
        if activeFnMode:
            closeMatch = re.match(r"\s*}\s*", line)
            if closeMatch:
                activeFnMode = False
                continue
            fnList[-1].append(line)
    return fnList


""" NOTE: This function will be over-approximate
and does not check that we actually jump backwards 
in order to reach the leaked value.
Although in likelihood a tainted value by the same
name would only appear above in a phi function,
which would be needed only in the case that it is 
being jumped back to.
"""


def fixedPointLeakDetector(fnLines: list[str], origTaints: set[str]) -> bool:
    taintedVals: set[str] = set(origTaints)
    for line in fnLines:
        sourceMatch = re.match(r"\s*%(\w+) = call (\w+) @SOURCE \(.*\)", line)
        if sourceMatch:
            taintedVals.add(sourceMatch.group(1))
            continue
        taintMatch = re.match(r"\s*%(\w+)\s*=\s*(.+)", line)
        if taintMatch:
            # This is really just checking for assignments
            for val in taintedVals:
                if val in taintMatch.group(2):
                    # If a tainted val was used in the assignment
                    taintedVals.add(taintMatch.group(1))
        sinkMatch = re.match(r"\s*call (\w+) @\w+ \((.+)\)", line)
        if sinkMatch:
            # This checks for all calls
            for val in taintedVals:
                if val in sinkMatch.group(2):
                    # Tainted val has been sunk!
                    return True
    if len(origTaints) == len(taintedVals):
        # No new taints have been added, fixpoint reached
        return False
    # Otherwise keep going until fixed-point is reached
    return fixedPointLeakDetector(fnLines, taintedVals)


def main():
    sInd = quickGet(sys.argv, "-s")
    iInd = quickGet(sys.argv, "-i")
    oInd = quickGet(sys.argv, "-g")

    if iInd == -1:
        # Invalid arguments have been passed
        print("ERROR INVALID ARGUMENTS 1")
        exit(1)

    infile = sys.argv[iInd + 1]
    fd = open(infile, "r")
    filelines = fd.readlines()
    fd.close()

    if sInd == -1 and oInd != -1:
        # Do CFG
        outfile = sys.argv[oInd + 1]
        if outfile:
            if outfile[-1] != "/":
                outfile = outfile + "/"
            fnList = splitIntoFns(filelines)
            for fn in fnList:
                createDotOut(processFn(fn[1:]), outfile + f"{fn[0]}.dot")
        else:
            # No argument for the outfile was specified
            print("ERROR INVALID ARGUMENTS 2")
            exit(1)
    elif sInd != -1 and oInd == -1:
        fnList = splitIntoFns(filelines)
        for fn in fnList:
            if fixedPointLeakDetector(filelines, set()):
                print("LEAK")
                exit(0)
        print("NO LEAK")
        exit(0)
    else:
        # Invalid arguments have been passed
        print("ERROR INVALID ARGUMENTS 3")
        exit(1)


main()
