[![Build Status](https://travis-ci.com/BostonUniversitySeniorDesign/2019-miniproject.svg?branch=master)](https://travis-ci.com/BostonUniversitySeniorDesign/2019-miniproject)

Please see the
[Wiki](https://github.com/BostonUniversitySeniorDesign/2019-miniproject/wiki)
for the EC463 hardware Miniproject.

![FFT-based lane automobile detection](https://raw.githubusercontent.com/BostonUniversitySeniorDesign/2019-miniproject/master/examples/out.gif)

Machine learning / computer vision methods are not necessary for this task, thanks to the h.264 motion vectors output by the GPU from the Picamera.
Since we know cars usually travel within a road lane, we can exploit this fact to greatly simplify the processing to be nearly 100x faster using plain Python or GNU Octave code than is achievable with OpenCV.



## Programs

`CaptureMotion.py`
captures h.264 motion vectors from the camera as computed by the GPU, and stores them to `motion.h5`

`CountMotion.py`
counts moving objects in lanes using FFT of spatial motion data
