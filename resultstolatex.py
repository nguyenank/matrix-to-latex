def toArray(d):
    """
    takes a nested list of two-element lists with symbols as the first element and bounding boxes as
    values as the second element and returns a list of the brackets of the matrix
    and a 2d array representing the corresponding matrix
    """

    centersD = list(map(lambda x: [centerFromCorners(x[1]), x[0]],d))

    # deal with brackets
    brackets = list(map(lambda x: x[1], list(filter(lambda x: x[1] in ["(", ")", "[","]","{","}"], centersD))))
    centersD = list(filter(lambda x: x[1] not in ["(", ")", "[","]","{","}"], centersD))

    # find margin of error for rows: 10% of overall vertical distance
    yCoords = list(map(lambda x:x[0][1], centersD))
    margin = (max(yCoords)-min(yCoords))//10
    elements = []
    while len(centersD) > 0:
        # find object closest to the top of image
        [yCoord, element] = min(map(lambda x: [x[0][1],x], centersD))
        # find all elements with center within margin of error of that element
        rowElements = list(filter(lambda x: withinMargin(x[0][1], yCoord, margin), centersD ))
        for elem in rowElements:
            centersD.remove(elem)
        # sort by x-coordinates
        xCoordElements = list(map(lambda x: [x[0][0],x[1]], rowElements))
        xCoordElements.sort()
        row = list(map(lambda x: x[1], xCoordElements))
        elements += [row]
    return [brackets, elements]

def toLatex(brackets, elements):
    """
    takes in a list of the opening and closing brackets of a matrix
    and a 2d array of the elements and returns the latex code corresponding
    to that matrix
    """
    start = end = ""
    if "(" in brackets:
        start = "$\\begin{pmatrix} "
        end = "\\end{pmatrix}$"
    elif "[" in brackets:
        start = "$\\begin{bmatrix} "
        end = "\\end{bmatrix}$"
    elif "{" in brackets:
        start = "$\\begin{Bmatrix} "
        end = "\\end{Bmatrix}$"
    s = start
    for row in elements:
        for element in row:
            s += element
            s+= " & "
        s = s[:-2] # remove last "& "
        s+= "\\\\ "
    return s[:-3]+end


def withinMargin(testvalue, mainvalue, margin):
    """
    returns true if and only if testvalue is within margin of mainvalue
    """
    return (testvalue <= mainvalue+margin) and (testvalue>=mainvalue-margin)

def centerFromCorners(coordinates):
    """
        for a list of coordinates in the form [xmin, xmax, ymin, ymax],
        returns [x_center, y_center]
    """
    [xmin, xmax, ymin, ymax] = coordinates
    return [(xmin + xmax) // 2, (ymin + ymax) // 2]

test = [['1', [312, 317, 65, 133]], ['4', [409, 461, 57, 99]],
['3', [553, 616, 48, 118]], ['- 1', [227, 328, 171, 253]],
['0', [417, 476, 191, 252]], ['3', [553, 627, 190, 264]],
['1', [295, 298, 311, 401]], ['8', [412, 476, 307, 395]],
['9', [549, 610, 305, 396]], ['(', [134, 219, 64, 422]],
[')', [640, 691, 23, 423]]]

[brackets, elements] = toArray(test)
print(toLatex(brackets, elements))
