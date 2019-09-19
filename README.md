[![Actions Status](https://github.com/BostonUniversitySeniorDesign/2019-hardware-miniproject/workflows/ci_python/badge.svg)](https://github.com/BostonUniversitySeniorDesign/2019-hardware-miniproject/actions)
[![Actions Status](https://github.com/BostonUniversitySeniorDesign/2019-hardware-miniproject/workflows/ci_octave/badge.svg)](https://github.com/BostonUniversitySeniorDesign/2019-hardware-miniproject/actions)


Please see the
[Wiki](https://github.com/BostonUniversitySeniorDesign/2019-hardware-miniproject/wiki)
for the EC463 hardware Miniproject.

![FFT-based lane automobile detection](https://raw.githubusercontent.com/BostonUniversitySeniorDesign/2019-hardware-miniproject/master/examples/out.gif)

Machine learning / computer vision methods are not necessary for this task, thanks to the h.264 motion vectors output by the GPU from the Picamera.
Since we know cars usually travel within a road lane, we can exploit this fact to greatly simplify the processing to be nearly 100x faster using plain Python or GNU Octave code than is achievable with OpenCV.

## configuration

The file config.ini holds the parameters used to filter and plot the video.
At the moment, up to four lanes of traffic can be configured--just leave lane(s) blank if you don't want to use them.

## Python

`CaptureMotion.py`
captures h.264 motion vectors from the camera as computed by the GPU, and stores them to `motion.h5`

`CountMotion.py`
counts moving objects in lanes using FFT of spatial motion data

For running the script automatically, it's handy to have a main script that calls CaptureMotion.py and then runs CountMotion.py.
The script CaptureAndCount.py does this.
