from numpy import int32, abs, floor, ceil, sign, arctan2, sin, cos, zeros, inf
from numpy import maximum
from numba import njit, float64, int32, int64

# We CANNOT use fastmath because we may have NaNs.
_njit_settings = {'nogil': False, 'fastmath': True, 'cache': True}

@njit(int32[:, :](float64[:], float64[:], int64, int64), **_njit_settings)
def fast_march(x, y, mx, my):
    """Fast march points through an integerized array

    Parameters
    ----------
    x : floats
        Fractional integer locations of x coordinates of a polygons ring
    y : floats
        Fractional integer locations of y coordinates of a polygons ring
    mx : int
        Size of the x dimension for the window
    my : int
        Size of the y dimension for the window

    """
    n_segments = int32(x.size - 1)

    # Estimate initial memory buffer for intersecting pixels
    nTmp = int32(0)
    for i in range(n_segments):
        nx = maximum(1, int32(ceil(abs(x[i+1] - x[i]))))
        ny = maximum(1, int32(ceil(abs(y[i+1] - y[i]))))

        nTmp += (nx * ny)

    points = zeros((3*nTmp, 2), dtype=int32)

    # Loop over line segments in the polygon
    j = 0
    for i in range(n_segments):
        x1 = x[i]; y1 = y[i]     # Get starting point coordinate
        x2 = x[i+1]; y2 = y[i+1] # Get ending point coordinate

        # Grid cells are 1.0 X 1.0.
        fx1 = floor(x1); fy1 = floor(y1)
        fx2 = floor(x2); fy2 = floor(y2)
        cx1 = ceil(x1); cy1 = ceil(y1)

        dx = x2 - x1; dy = y2 - y1
        stepX = sign(dx); stepY = sign(dy)

        #Ray Slope related nps.
        #Straight distance to the first vertical grid boundary.
        xOffset = (cx1 - x1) if x2 > x1 else (x1 - fx1)
        # Straight distance to the first horizontal grid boundary.
        yOffset = (cy1 - y1) if y2 > y1 else (y1 - fy1)
        # Angle of ray/slope.
        angle = arctan2(-dy, dx)

        # How far to move along the ray to cross the first vertical grid cell boundary.
        ca = cos(angle); sa = sin(angle)
        tMaxX = inf; tMaxY = inf;
        tDeltaX = inf; tDeltaY = inf

        if ca != 0.0:
            tMaxX = xOffset / ca
            tDeltaX = 1.0 / ca

        if sa != 0.0:
            tDeltaY = 1.0 / sa
            tMaxY = yOffset / sa

        # Travel one grid cell at a time.
        manhattanDistance = abs(fx2 - fx1) + abs(fy2 - fy1)
        t = 0
        while t <= manhattanDistance:
            if (0 <= fx1 < mx) and (0 <= fy1 < my):
                points[j, :] = [fy1, fx1]
                j += 1
            # Only move in either X or Y coordinates, not both.
            if (abs(tMaxX) < abs(tMaxY)):
                tMaxX += tDeltaX
                fx1 += stepX
            else:
                tMaxY += tDeltaY
                fy1 += stepY
            t += 1

    return points[:j, :]