#!/usr/bin/env python3

import sys
import cv2
import numpy as np


from app.logic.field_extractor import extract_field_mask
from sklearn.cluster import DBSCAN

def detector_v4(input_image):
   
    # Convert from BGR to HSV
    hsv = cv2.cvtColor(input_image, cv2.COLOR_BGR2HSV)
   # # cv2.imshow("HSV", hsv)
    # Create a green mask (adjust lower_green and upper_green for your lighting)
    lower_green = (36, 25, 5)
    upper_green = (86, 255, 255)

    lower_white = (0, 0, 85)
    upper_white = (85,75, 255)    

    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    mask_white = cv2.inRange(hsv, lower_white, upper_white)

    field_mask = extract_field_mask(input_image)
    # cv2.imshow("Field Mask", field_mask)
    field_masked_image = cv2.bitwise_and(input_image, input_image, mask=field_mask)
    # cv2.imshow("Field Masked Image", field_masked_image)
    # Keep only the green field
    frame_masked_green = cv2.bitwise_and(input_image, input_image, mask=mask_green)
    # cv2.imshow("Frame Masked Green", frame_masked_green)
    frame_masked_white = cv2.bitwise_and(frame_masked_green, frame_masked_green, mask=mask_white)
    # cv2.imshow("Frame Masked White", frame_masked_white)
    # Convert to grayscale
    gray = cv2.cvtColor(field_masked_image, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("Gray", gray)
    # Optional simple binary threshold
    #_, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    ## cv2.imshow("Thresh", thresh)
    # Canny edge detection
    canny = cv2.Canny(gray, 1, 150, apertureSize=3, L2gradient=False)
    # cv2.imshow("Canny", canny)
    # Apply Hough Line Detection (Probabilistic)
    lines = cv2.HoughLinesP(
        canny,
        1,                # rho resolution
        np.pi / 180,      # theta resolution
        150,               # threshold
        minLineLength=50,
        maxLineGap=50
    )

    
    ## cv2.imshow("Hough Lines", lines)
    # Filter out purely vertical / horizontal lines, then keep only positive-slope (red) lines
    red_lines = []
    temp = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # Skip purely vertical lines
            if x2 - x1 == 0:
                continue
            slope = (y2 - y1) / (x2 - x1)
            # Skip slope == 0 as well
            
                # Compute line length
            length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            red_lines.append([x1, y1, x2, y2, slope, length])
            temp.append([x1, y1, x2, y2, slope])
            
    # -------------------------------------------------------------
    # Show the lines that will ultimately contribute to intersection points
    # in a separate image window so we can see them before intersection logic.
    lines_for_display = field_masked_image.copy()
    for (x1, y1, x2, y2, slope) in temp:
        # You can randomize color or keep it fixed
        # e.g., color = (0, np.random.randint(50, 255), np.random.randint(50, 255))
        cv2.line(lines_for_display, (x1, y1), (x2, y2), (0, 255, 0), 2)
    # cv2.imshow("Lines - Contributing to Intersections", lines_for_display)
    # -------------------------------------------------------------

    # Collect intersection points here
    intersection_points = []

    # Compute pairwise intersections of lines in temp
    for i in range(len(temp)):
        for j in range(i + 1, len(temp)):
            pt = line_infinite_intersection(temp[i], temp[j])
            if pt is not None:
                #print(f"Intersection of line {i} with line {j} at: {pt}")
                intersection_points.append(pt)
            #else:
                #print(f"Lines {i} and {j} are parallel (no intersection) or negligible distance.")

    # Exclude any intersection points with a non-negative y-value or non-finite values.
    intersection_points = [pt for pt in intersection_points if pt[1] < 0 and np.isfinite(pt[0]) and np.isfinite(pt[1])]

    #print(intersection_points)
    i_points = np.array(intersection_points)
    db = DBSCAN(eps=5, min_samples=3).fit(i_points)
    labels = db.labels_
    unique_labels, counts = np.unique(labels, return_counts=True)

    max_count_label = None
    max_count = 0
    for label, count in zip(unique_labels, counts):
        if label == -1:
            continue
        if count > max_count:
            max_count_label = label
            max_count = count

    if max_count_label is None:
        print("No clusters found (all outliers)")
    else:
        cluster_points = i_points[labels == max_count_label]
        representation = np.mean(cluster_points, axis=0)
        print('the main intersection point is: ', representation)
    
        # ---------------------------------------------------
        # Draw a line from the "main intersection point" to
        # the bottom-center of our image
        # ---------------------------------------------------
        # Make a copy of the original or final output image
        line_from_representation = field_masked_image.copy()

        # The bottom-center coordinate (width/2, height)
        h, w = line_from_representation.shape[:2]
        bottom_x, bottom_y = w // 2, h

        # Representation may be floating-point, so cast to int
        rx, ry = int(representation[0]), int(representation[1])

        # Draw the line in green
        cv2.line(line_from_representation, (rx, ry), (bottom_x, bottom_y), (0, 255, 0), 2)
        # cv2.imshow("Intersection -> Bottom", line_from_representation)
    
    for pt1 in intersection_points:
        pt1_x = pt1[0]
        pt1_y = pt1[1]
        for pt2 in intersection_points:
            pt2_x = pt2[0]
            pt2_y = pt2[1]
            if abs(pt1_x - pt2_x)  and pt1_y == pt2_y:
                print(f"Duplicate intersection point found: {pt1}")
            
    if not intersection_points:
        print("No valid intersections found. Returning None.")
        return None

    # If DBSCAN found no non-outlier cluster:
    # e.g.:
    if len(labels) == 0 or (max(labels) == -1):
        print("No clusters found (all outliers). Returning None.")
        return None

    # if representation is None or invalid, also return None
    if representation is None or any(np.isnan(representation)):
        return None

    return representation

def line_infinite_intersection(l1, l2):
    """
    Return the intersection (x, y) of the INFINITE lines defined by l1 and l2,
    or None if they are parallel or effectively 'next to each other.'

    Each line is [x1, y1, x2, y2, slope].
    """
    x1, y1, x2, y2, m1 = l1
    x3, y3, x4, y4, m2 = l2

    # Convert each line to Ax + By = C form
    A1 = y2 - y1
    B1 = x1 - x2
    C1 = A1 * x1 + B1 * y1

    A2 = y4 - y3
    B2 = x3 - x4
    C2 = A2 * x3 + B2 * y3

    determinant = A1 * B2 - A2 * B1

    # NEW: Return None if lines are parallel or nearly so
    if abs(determinant) < 1e-9:
        return None

    x_int = (B2 * C1 - B1 * C2) / determinant
    y_int = (A1 * C2 - A2 * C1) / determinant
    return (x_int, y_int)
    


