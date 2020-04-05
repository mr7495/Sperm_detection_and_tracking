This folder contains tracking algorithms and the code used in this paper : https://arxiv.org/abs/2002.04034

The code used for improving motile objects detection accuracy on RetinaNet is available on https://github.com/mr7495/RetinaNet_Motile_objects_Detection.

The modified CSR-DCF is a multi target tracker that uses CSR-DCF tracker as its core and works with both of tracking algorithms and the detected objects of the video frames.
We have tested our tracker on the 9 video samples of sperms with the detections and achieved 96.46% F1 score and also we have tested it on 36 videos with the ground truth instead of the detections and the results have shown 100% accuracy with no false track based on our evaluation method.
This is a result of excellent performance of this tracker.
The main code is in the modified csr-dcf.py file.
A sample of our Ground-truth data is also shared in annotation sample.csv.

Our trained neural network based on 3 concatenated frames have been shared on: https://drive.google.com/open?id=1pN3A-tWJOphRdTZ7cPhJTnTIhoiGrcWv

You can contact the developer by this email : mr7495@yahoo.com
