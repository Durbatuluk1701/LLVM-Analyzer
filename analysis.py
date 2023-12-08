import re
import sys

filePath = "testAll.txt"


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
    bblList = [BBL("HJAKLFGHKJLDAJSFHJKASDHGJKLHASDJKHGJKDSAHJKLDGH")]
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
                r"\s*br (\w+) %(\w+), label %(\w+), label %(\w+)", line
            )
            if bblSplitLeave:
                activeBBL = False
                bblList[-1].targets.append(bblSplitLeave.group(3))
                bblList[-1].targets.append(bblSplitLeave.group(4))
                continue
    return bblList


def createDotOut(bbls: list[BBL], writePath: str) -> None:
    retStr = "digraph {\n"
    for bbl in bbls:
        retStr += bbl.dotOut()
    with open(writePath, "w") as fd:
        fd.write(retStr + "}\n")


def cfg(lines: list[str], writeDir: str) -> None:
    fnList = []
    activeFnMode = False
    for line in lines:
        # Find functions
        fnVal = re.match(r"\s*define (\w+) @(\w+)\(.+\) {", line)
        if fnVal:
            if activeFnMode:
                raise Exception("NESTED FNS!")
            activeFnMode = True
            fnList.append([fnVal.group(2)])
            continue
        if activeFnMode:
            closeMatch = re.match(r"\s*}\s*", line)
            if closeMatch:
                activeFnMode = False
                continue
            fnList[-1].append(line)
    for fn in fnList:
        # Process each fn
        createDotOut(processFn(fn[1:]), writeDir + f"/{fn[0]}.dot")


# def dataflow(lines: list[str]) -> bool:
#     # re.search('%(\w+) = call i32 @SOURCE \(\)\n(^.+$\n)*?(.+call i32 @\w+ \(\w+ %\1\))', fileText, "")
#     taintedVals = []
#     # NOTE: Do we need to worry about SINKs before SOURCES?
#     for line in lines:
#         sourceVal = re.search(r"%(\w+) = call \w+ @SOURCE .+", line)
#         if sourceVal:
#             taintedVals.push(sourceVal.group(1))
#             continue
#         # Now we search for sinks
#         taintVal = re.search(r"%(\w+) = ")
#     return False


# Access command-line arguments
arguments = sys.argv

if len(arguments) > 1:
    print("Arguments passed:", arguments[1:])
else:
    print("No arguments passed.")

with open(filePath, "r") as fd:
    filetext: list[str] = fd.readlines()
    # TODO: Manage slash on write dir

    writedir = "./"
    cfg(filetext, writedir)
    # leak = dataflow(filetext)
    # if leak:
    #     print("leak")
    # else:
    #     print("no leak")
