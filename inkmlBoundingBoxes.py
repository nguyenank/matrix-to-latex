import xml.etree.ElementTree as ET
import itertools
from math import inf, dist
from copy import deepcopy


def flatten(listOfLists):
    # taken directly from recipes in itertools documentation
    "Flatten one level of nesting"
    return list(itertools.chain.from_iterable(listOfLists))


def extractFromInkML(filename):
    """
    INPUTS:
        filename: string filepath to an inkml file
    OUTPUTS:
    a list of length three: [elements, latex, traceGroups]
        elements: the elements of the matrix in RC format of nested lists
        latex: the string of latex corresponding to the matrix
        coordinates: a nested list of coordinates, where the nth item
            is the list of coordinates corresponding to the nth trace
        traceGroups: a dictionary where keys are the symbols comprising the matrix and
            the values are lists of traces corresponding to those symbols
    """
    with open(filename) as f:
        s = " ".join([x.strip() for x in f])
        # annotations like comments, so not normally read in xml
        # but we need the information in there
        # so need to change their name to be able to read them
        s = s.replace("annotation", "truth")

    ns = {
        'ink': "http://www.w3.org/2003/InkML"
    }  # namespace prefix to all tags
    root = ET.fromstring(s)
    # get LaTeX info, always second node of root
    latex = root[1].text

    # get all trace coordinates
    traces = [trace.text for trace in root.findall('ink:trace', ns)]

    def cleanText(trace):
        # remove whitespace
        return [x.strip().split(" ") for x in trace.strip().split(",")]

    coordinates = [cleanText(x) for x in traces]

    # get traceGroups
    traceGroups = {}
    # last node of root always traceGroups
    for child in root[len(root) - 1]:
        if not child.attrib == {'type': 'truth'}:  # skips info node
            symbol = child[0].text
            traceNumbers = []
            for trace in range(1,
                               len(child) - 1):  # stop before last annotation
                traceNumbers += [int(child[trace].attrib['traceDataRef'])]
            if symbol not in traceGroups:
                # isn't in dictionary yet
                traceGroups[symbol] = [traceNumbers]
            else:
                # append to existing list
                traceGroups[symbol] += [traceNumbers]
    return (latex, coordinates, traceGroups)


def latexToElements(latex):
    """
        NOTE: only works for single matrices that are ENCLOSED by
        some delimiters OTHER than double pipes (|| ... ||)

        for a string containing a matrix in latex format,
        returns a list of two elements:
            the first is a nested list of the elements inside the matrix, in RC order
            the second is the string of the opening and closing bracket for the matrix
    """
    # first, want to get rid of enclosing matrix tags
    begin = "matrix}"  # want to capture everything after this
    end = "\\end"  # want to capture everything before this
    bracketDictionary = {"p": "()", "b": "[]", "B": "{}"}

    bracketSymbol = latex[latex.find(begin) - 1]
    elementText = latex[latex.find(begin) + 7:latex.find(end)].strip()
    split = [row.strip().split("&") for row in elementText.split("\\\\")]
    return [[[element.strip() for element in x] for x in split],
            bracketDictionary[bracketSymbol]]


def centerFromCoordinates(coordinates):
    """
    takes a list of coordinates in the form
     [[x1,y1], [x2,y2], ..., [xn,yn]]
     and returns [X,Y], where X is the center x coordinate
     of the list and Y is the center y coordinate
    """
    # order: min x, max x, min y, max y
    xs = [int(coord[0]) for coord in coordinates]
    ys = [int(coord[1]) for coord in coordinates]
    return [(min(xs) + max(xs)) // 2, (min(ys) + max(ys)) // 2]


def centerFromCorners(coordinates):
    [xmin, xmax, ymin, ymax] = coordinates
    return [(xmin + xmax) // 2, (ymin + ymax) // 2]


def minmaxFromCoordinates(coordinates):
    """
    takes a list of coordinates in the form
     [[x1,y1], [x2,y2], ..., [xn,yn]]
     and returns [xmin,xmax, ymin, ymax]
    """
    xs = [int(coord[0]) for coord in coordinates]
    ys = [int(coord[1]) for coord in coordinates]
    return [min(xs), max(xs), min(ys), max(ys)]


def elementsToBoundingBoxes(elements, brackets, tg, imageXY, coordinates):
    """
    INPUTS:
        elements: the elements of the matrix in RC format of nested lists
        brackets: a string containing the opening and closing brackets for the matrix
        tg: a dictionary where keys are the symbols comprising the matrix and
            the values are lists of traces corresponding to those symbols
        imageXY: the min and max x,y coordinates of all traces
        coordinates: a nested list of coordinates, where the nth item
            is the list of coordinates corresponding to the nth trace
    OUTPUTS:
        a list of dictionaries, where for each dictionary:
            keys: individual characters and full element for each element of the matrix
                and the brackets
            elements: the bounding boxes for each character/element
    """
    traceGroups = deepcopy(tg)
    [xmin, xmax, ymin, ymax] = imageXY
    d = []
    # need rows and columns to calculate rough position
    for r in range(len(elements)):
        for c in range(len(elements[0])):
            ed = {}
            overallBox = [inf, -inf, inf, -inf]
            for character in elements[r][c]:

                if character not in traceGroups:  # ignoring spaces and the like
                    continue
                potentialTraces = traceGroups[character]
                if len(potentialTraces) == 1:  # only one potential trace
                    minmax = minmaxFromCoordinates(
                        coordinates[potentialTraces[0][0]])
                    traceGroups[character].remove(potentialTraces[0])
                else:
                    # calculate via grid roughly where we would expect the corresponding trace to be
                    # origin in top left corner
                    centerCoordX = int(
                        (xmin + xmax) / len(elements[0]) * (0.5 + c))
                    centerCoordY = int(
                        (ymin + ymax) / len(elements) * (r + 0.5))
                    # find trace with its center closest to the expected center
                    closestTraces = min([[
                        dist(
                            centerFromCoordinates(
                                flatten(
                                    [coordinates[trace] for trace in traces])),
                            [centerCoordX, centerCoordY]), traces
                    ] for traces in potentialTraces])
                    print([[
                        centerFromCoordinates(
                            flatten([coordinates[trace] for trace in traces])),
                        [centerCoordX, centerCoordY], traces
                    ] for traces in potentialTraces])
                    print([centerCoordX, centerCoordY])
                    print(closestTraces)
                    traceNumbers = closestTraces[1]
                    minmax = minmaxFromCoordinates(
                        flatten([coordinates[trace]
                                 for trace in traceNumbers]))
                    traceGroups[character].remove(traceNumbers)
                overallBox = [
                    min(x, y) if ind % 2 == 0 else max(x, y)
                    for ind, (x, y) in enumerate(zip(overallBox, minmax))
                ]
                ed[character] = minmax
            ed[elements[r][c]] = overallBox
            d += [ed]
    # deal with brackets
    for character in brackets:
        # assumes no duplicate bracket characters in matrix, and that
        # for vertical matrices brackets are drawn left to right
        traces = traceGroups[character][0]
        minmax = minmaxFromCoordinates(coordinates[traces[0]])
        traceGroups[character].remove(traces)
        ed = {}
        ed[character] = minmax
        d += [ed]

    return d


[latex, coordinates,
 traceGroups] = extractFromInkML("RIT_MatrixTest_2014_3.inkml")
[elements, brackets] = latexToElements(latex)
imageXY = minmaxFromCoordinates(flatten(coordinates[1:len(coordinates) - 1]))
a = elementsToBoundingBoxes(elements, brackets, traceGroups, imageXY,
                            coordinates)
