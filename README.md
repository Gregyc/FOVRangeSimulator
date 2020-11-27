# FOVRangeSimulator
calculate the visible range of the camera with specific FOV

## User input parameters (Room related)
![](https://github.com/Gregyc/FOVRangeSimulator/blob/main/images/input_room_parameters.png)
1. Room Width  (float): the room width.  valid range ( 0.0m - 30.0 m)
2. Room Height (float): the room height. valid range ( 0.0m - 30.0 m)

## User select parameters with trackbar( Camera related)

1. CamFacVDeg (int): the vertical camera face degree. valid range: 0-90 degree
![](https://github.com/Gregyc/FOVRangeSimulator/blob/main/images/CamFaceVDeg.png)
2. CamFacHDeg (int): the horizontal camera face degree. valid range: 0-180 degree
![](https://github.com/Gregyc/FOVRangeSimulator/blob/main/images/CamFaceHDeg.png)
3. CamLoc_H (int): the height to set the camera. valid range: 150-300 cm
4. CamLoc_W (int): the width to set the camera. valid range: 0 - Room Width*100 cm
5. Person_H (int): the height of the human. To check the range we can see whole human.
                      valid range: 130-200 cm

## Visible area in different side of view
![](https://github.com/Gregyc/FOVRangeSimulator/blob/main/images/vertical_visible_distance.png)
![](https://github.com/Gregyc/FOVRangeSimulator/blob/main/images/horizontal_visible_distance.png)
## Result
![](https://github.com/Gregyc/FOVRangeSimulator/blob/main/images/room_and_visible_area.png)