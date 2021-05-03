# Sperm detection and tracking in phase-contrast microscopy image sequences using deep learning and modified CSR-DCF


This repo presents the code of **the paper [arxiv.org/abs/2002.04034](https://arxiv.org/abs/2002.04034)**
Our developed modified CSR-DCF multi-tracker for tracking sperms in video frames is described in this repo. This algorithm has shown significant results in challenging conditions.


The code used for improving motile objects detection on RetinaNet (the detection phase of the paper) is available at https://github.com/mr7495/RetinaNet_Motile_objects_Detection.

The [modified CSR-DCF](modified_csr-dcf.py) is a multi target tracker that uses CSR-DCF tracker as its core and works with both of tracking algorithms and the detected objects of the video frames.

The graphical abstract of our paper is presented in the next figure:

<p align="center">
	<img src="images/graphical_abstract-1.jpg" alt="photo not available" width="80%" height="70%">
	<br>
	<em>Graphical Abstract</em>
</p>

We have tested our tracker on the 9 video samples of sperms with the detections and achieved **96.61%** F1 score and also we have tested it on 36 videos with the ground truth instead of the detections and the results have shown **100%** accuracy with no false track based on our evaluation method. This is a result of excellent performance of this tracker.

|  Tracker | Recall | Precision | F1 | Accuracy | 
|:-----:|:--------------------:|:------------:|:--------:|:-------------------:|
|  CSR-DCF |         90.51        |     89.63   |   90.06   |  81.93  |
|  Modified CSR-DCF |        97.32        |     95.92   |   96.61   |  93.45  |

The comparison table between our proposed tracker and CSR-DCF



**The main code is in the modified [csr-dcf.py](modified_csr-dcf.py) file.**

**You need the csv file of the detected sperms in the input video to run modified_csr-dcf.py and so you can use [https://github.com/mr7495/RetinaNet_Motile_objects_Detection/blob/master/RetinaNet_testing_on_video(For_counting).ipynb](https://github.com/mr7495/RetinaNet_Motile_objects_Detection/blob/master/RetinaNet_testing_on_video(For_counting).ipynb) 
for generating the csv file.**

**The code for extracting motility parameters is available on [Github_motility_parameters_extractor.py](Github_motility_parameters_extractor.py).**

A sample of our Ground-truth data is also shared in annotation [annotation_sample.csv](annotation_sample.csv).

The next figures show some of the tracked sperms:

<img src="/images/tracka-1.jpg" width="50%"><img src="/images/trackb-1.jpg" width="50%">

**The training model of our trained neural network based on 3 concatenated frames have been shared on:** 

https://drive.google.com/file/d/14ufFO8GKbE5Qlrm3wloHKQcsnudwHeSR/view?usp=sharing


**The inference version of our trained neural network based on 3 concatenated frames have been shared on:** 

https://drive.google.com/open?id=1pN3A-tWJOphRdTZ7cPhJTnTIhoiGrcWv

You can refer to https://github.com/fizyr/keras-retinanet to learn more about the differences between the training and inference models.

If you find our work effective, please cite it by:

```
@article{rahimzadeh2020sperm,
  title={Sperm detection and tracking in phase-contrast microscopy image sequences using deep learning and modified CSR-DCF},
  author={Rahimzadeh, Mohammad and Attar, Abolfazl and others},
  journal={arXiv preprint arXiv:2002.04034},
  year={2020}
}
```
You can contact the developer by this email : mr7495@yahoo.com
