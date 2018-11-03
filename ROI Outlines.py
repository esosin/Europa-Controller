''' 
Need an infrastructure to read a byte stream. Byte stream will carry information about several ROIs
simultaneously.
    spliting value == 256

Per ROI
1. Shape
    a = ellipse/circle
    b = rectangle/square
    c = custom polygon mask
   
2. Opening Width (mm)
    2.a. height, width ???
    width/diam 
3. Coordinate of Center (x,y)


Shapes need to be separated by a common spliting character

Example of Byte stream:
Byte #:   0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8 
int   :        
ascii :   a  |   

'''