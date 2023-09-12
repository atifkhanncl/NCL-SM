![Python version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


# NCL-SM Dataset
### NCL-SM: Newcastle Skeletal Muscle dataset is a Fully Annotated Dataset of Images from Human Skeletal Muscle Biopsies

## NCL-SM Details:

 Download: [link](https://newcastle-my.sharepoint.com/:f:/r/personal/b6071289_newcastle_ac_uk/Documents/NCL_SM?csf=1&web=1&e=wkb6rM)  (this link is currently private as the dataset is currectly under review)

 Data directory structure: NCL-SM consist of two directories (i) IMC & (ii) IF. Each of these have 8 directories, the names of the these should explain the content, the three directories with abbrivated names i.e. 'Mask_All_AM' refer to instance segmentation mask of all analysable myofibres, 'Mask_AM_vs_NAM' refer to class mass of analysable vs non-analysable mayofibres and 'Mask_QA' refer to segmentation mask of quality assurance duplicate annotations. 

## NCL-SM Code:

### Non-transverse myofibre (NTM) detection:
The python [script](https://github.com/atifkhanncl/NCL-SM/blob/main/non_transverse_myofibre_detection.py) enables classification of  NTM in instance segmentation mask provided.

### Annotation quality assessement metrics
The [notebook](https://github.com/atifkhanncl/NCL-SM/blob/main/annotation_quality_evaluation_metrics.ipynb) walk through evaluating annotation/segmentation quality of given instance segmentation mark by comparing it to NCL-SM 'ground truth' mask

## NCL-SM Associated Clinical and Other Information 

Please refere to [clinical info](https://github.com/atifkhanncl/NCL-SM/blob/main/clinical_info.md)
