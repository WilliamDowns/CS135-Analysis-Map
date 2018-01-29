## Description

Final project from CS135 (Diving into the Deluge of Data). Displays current temperature and wind data across the U.S. or a sub region of the U.S.

## Instructions to run the code
 -User should have Python 3 up-to-date, as well as pip and requests.
 -Type 'python3 map.py boundaries output section' in the command line, where
  -boundaries is a csv file with lat/long values tracing state boundaries (ex: states.csv).
  -output is the name of a file containing the saved and completed image (ex: map.png).
  -section is the area of the US map to be plotted. Acceptable inputs include state names and regions (New_England, Mid_Atlantic, Southeast, Midwest, Great_Plains, Northwest, Southwest) with proper capitalization. Any input for section that is not a state name or region will return the map of the entire continental US, including leaving the section argument blank. Also note that states and regions with two words must have an underscore separating the words so that the two words are not interpreted as separate arguments.
 -To view the map, open the file saved under the input to the 'output' argument.

##Potential Improvements
 -Refined gridding system employing natural neighbor interpolation to improve performance and station weighting system.
 -Add legitimate wind barbs rather than current system which only allows for relative comparisons of wind speed between different areas.

