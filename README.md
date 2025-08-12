# BRATsynthetic

## About

Python tool that generates realistic synthetic text for a superset of I2B2 2014 personal health information entity types. 
A poster was published in AMIA (https://knowledge.amia.org/73035-amia-1.4612663/t004-1.4613775/t004-1.4613776/3478476-1.4613879/3478476-1.4613880?qr=1) 
and a paper is pending based on our first release [![DOI](https://zenodo.org/badge/290890218.svg)](https://zenodo.org/badge/latestdoi/290890218)

## Workflow
This tool takes annotated text from Brat (https://brat.nlplab.org) and replaces personal information with synthetic data. It will attempt to match the format of the text.

BRATsynthetic is typically used in a workflow where:
* De-identification is run using uabdeid or some other tool to generate CONLL output in IOB format
```shell
python uabdeid/predict.py \
-i [FULL PATH TO (input with PHI) .txt FILES] \
-o [FULL PATH TO (output with PHI) .conll FILES] \
-b 8 \
-e 1 \
-m bert \
--predict_only \
--input_format txt \
--cache_dir [FULL PATH TO MODEL FOLDER]
```
* uabnnlptools is then run to create .ann files from the CONLL output
```shell
python uabnlp/brat_tools/conll_to_brat.py \
-i [FULL PATH TO (input with PHI) .txt FILES] \
-o [FULL PATH TO (output with PHI) .ann FILES] \
-c [FULL PATH TO (input with PHI) .conll FILES]
```
* BRATsynthetic uses the directory of .ann files and the original text file to generate surrogate replaced text
```shell
cd BRATsynthetic
python bratsynthetic.py -c config.yaml
```
The output is a directory of fully deidentified .txt and .ann files with the replaced text (without PHI).

(Make sure you have a virtual environment for each of these tools and that it is activated before running the commands)


## Examples of Replacements

```
(.venv) (base) temp@temps-Air BRATsynthetic % python bratsynthetic.py -c config.yaml 
Processing 1 files...
  [1]: example.txt
Creating 10 replacements for DOCTOR
DoctorMaker - : JONATHAN SMITH ANDREAS -> RICHARD GILMORE
DoctorMaker - : HUONG -> JENKINS
DoctorMaker - : HUONG -> JENKINS
DoctorMaker - : NICHOLS -> SMITH
DoctorMaker - : NICHOLS -> SMITH
DoctorMaker - : TREVOR JACOBSEN -> MICHAEL WILSON
DoctorMaker - : GREGORY E KOWELSKY -> RYAN KIM
DoctorMaker - : TARANTINO, HANNAH CARROLL -> GARCIA, MATTHEW
DoctorMaker - : J. SPANO -> BRYAN BROOKS
DoctorMaker - : TARANTINO -> WILSON
Creating 22 replacements for DATE
Input: '05/11/16', Parsed: '2016-05-11 00:00:00', Fake: '2016-05-12', 'Patterned: '05/12/16'
    DateMaker - : 05/11/16 -> 05/12/16
Input: '11/2/2021', Parsed: '2021-11-02 00:00:00', Fake: '2021-10-31', 'Patterned: '10/31/2021'
    DateMaker - : 11/2/2021 -> 10/31/2021
Input: '11/2/2022', Parsed: '2022-11-02 00:00:00', Fake: '2022-11-04', 'Patterned: '11/04/2022'
    DateMaker - : 11/2/2022 -> 11/04/2022
Input: '3/16/13', Parsed: '2013-03-16 00:00:00', Fake: '2013-03-13', 'Patterned: '03/13/13'
    DateMaker - : 3/16/13 -> 03/13/13
Input: '7/26/13', Parsed: '2013-07-26 00:00:00', Fake: '2013-07-27', 'Patterned: '07/27/13'
    DateMaker - : 7/26/13 -> 07/27/13
Input: '8/16/12', Parsed: '2012-08-16 00:00:00', Fake: '2012-08-15', 'Patterned: '08/15/12'
    DateMaker - : 8/16/12 -> 08/15/12
Input: '2/28/14', Parsed: '2014-02-28 00:00:00', Fake: '2014-02-28', 'Patterned: '02/28/14'
    DateMaker - : 2/28/14 -> 02/28/14
Input: '6/17/13', Parsed: '2013-06-17 00:00:00', Fake: '2013-06-16', 'Patterned: '06/16/13'
    DateMaker - : 6/17/13 -> 06/16/13
Input: '11/', Parsed: '2024-07-11 00:00:00', Fake: '2024-07-13', 'Patterned: '2024-07-13'
    DateMaker - : 11/ -> 2024-07-13
Input: '10/2020', Parsed: '2020-10-19 00:00:00', Fake: '2020-09-19', 'Patterned: '09/2020'
    DateMaker - : 10/2020 -> 09/2020
Input: '2/23/2021', Parsed: '2021-02-23 00:00:00', Fake: '2021-02-20', 'Patterned: '02/20/2021'
    DateMaker - : 2/23/2021 -> 02/20/2021
Input: '2/25/2021', Parsed: '2021-02-25 00:00:00', Fake: '2021-02-22', 'Patterned: '02/22/2021'
    DateMaker - : 2/25/2021 -> 02/22/2021
Input: '3/16/2021', Parsed: '2021-03-16 00:00:00', Fake: '2021-03-17', 'Patterned: '03/17/2021'
    DateMaker - : 3/16/2021 -> 03/17/2021
Input: '11', Parsed: '2024-07-11 00:00:00', Fake: '2024-07-08', 'Patterned: '24'
    DateMaker - : 11 -> 24
Input: '3/19/2021', Parsed: '2021-03-19 00:00:00', Fake: '2021-03-20', 'Patterned: '03/20/2021'
    DateMaker - : 3/19/2021 -> 03/20/2021
Input: '5/2/2021', Parsed: '2021-05-02 00:00:00', Fake: '2021-05-01', 'Patterned: '05/01/2021'
    DateMaker - : 5/2/2021 -> 05/01/2021
Input: '6/20/21', Parsed: '2021-06-20 00:00:00', Fake: '2021-06-22', 'Patterned: '06/22/21'
    DateMaker - : 6/20/21 -> 06/22/21
Input: '10/12/2022', Parsed: '2022-10-12 00:00:00', Fake: '2022-10-10', 'Patterned: '10/10/2022'
    DateMaker - : 10/12/2022 -> 10/10/2022
Input: 'November 2012', Parsed: '2012-11-19 00:00:00', Fake: '2012-12-04', 'Patterned: 'December 2012'
Input: 'November 2012', Parsed: '2012-11-19 00:00:00', Fake: '2012-11-20', 'Patterned: 'Nov 2012'
    DateMaker - : November 2012 -> Nov 2012
Input: '10/31/12', Parsed: '2012-10-31 00:00:00', Fake: '2012-10-30', 'Patterned: '10/30/12'
    DateMaker - : 10/31/12 -> 10/30/12
Input: '2006', Parsed: '2006-07-19 00:00:00', Fake: '2005-10-15', 'Patterned: '2005'
Input: '2006', Parsed: '2006-07-19 00:00:00', Fake: '2007-02-03', 'Patterned: '2007'
    DateMaker - : 2006 -> 2007
Input: '11/26/2012', Parsed: '2012-11-26 00:00:00', Fake: '2012-12-08', 'Patterned: '12/08/2012'
    DateMaker - : 11/26/2012 -> 12/08/2012
Creating 5 replacements for MEDICALRECORD
    MedicalRecordMaker - : 91456244 -> 11412444
    MedicalRecordMaker - : 91456244 -> 11412444
    MedicalRecordMaker - : 91456244 -> 11412444
    MedicalRecordMaker - : 091456244 -> 604604666
    MedicalRecordMaker - : 91456244 -> 11412444
Creating 4 replacements for PATIENT
PatientMaker - : JACOBSEN -> CERVANTES
PatientMaker - : NASH -> NELSON
PatientMaker - : NASH -> PERRY
PatientMaker - : SALMAN, HASAN KUMAR -> LITTLE, RYAN
Creating 3 replacements for AGE
    AgeMaker - : 63yo -> 68yo
    AgeMaker - : 64 -> 60
    AgeMaker - : 62 -> 67
T1      DOCTOR 285 307  Jonathan Smith Andreas -> T1    DOCTOR 285 300  RICHARD GILMORE
T2      DATE 323 331    05/11/16 -> T2  DATE 316 324    05/12/16
T3      DATE 570 579    11/2/2021 -> T3 DATE 563 573    10/31/2021
T4      DATE 593 602    11/2/2022 -> T4 DATE 587 597    11/04/2022
T5      MEDICALRECORD 648 656   91456244 -> T5  MEDICALRECORD 643 651   11412444
T6      DATE 883 890    3/16/13 -> T6   DATE 878 886    03/13/13
T7      DATE 957 964    7/26/13 -> T7   DATE 953 961    07/27/13
T8      DATE 1013 1020  8/16/12 -> T8   DATE 1010 1018  08/15/12
T9      DATE 1068 1075  2/28/14 -> T9   DATE 1066 1074  02/28/14
T10     MEDICALRECORD 1079 1087 91456244 -> T10 MEDICALRECORD 1078 1086 11412444
T11     MEDICALRECORD 1165 1173 91456244 -> T11 MEDICALRECORD 1164 1172 11412444
T12     DOCTOR 1231 1236        Huong -> T12    DOCTOR 1230 1237        JENKINS
T13     DATE 1281 1288  6/17/13 -> T13  DATE 1282 1290  06/16/13
T14     DOCTOR 1679 1684        Huong -> T14    DOCTOR 1681 1688        JENKINS
T15     DATE 1790 1793  11/ -> T15      DATE 1794 1804  2024-07-13
T16     DATE 1793 1800  10/2020 -> T16  DATE 1804 1811  09/2020
T17     DATE 1948 1957  2/23/2021 -> T17        DATE 1959 1969  02/20/2021
T18     DATE 2089 2098  2/25/2021 -> T18        DATE 2101 2111  02/22/2021
T19     DATE 2313 2322  3/16/2021 -> T19        DATE 2326 2336  03/17/2021
T20     DATE 2395 2397  11 -> T20       DATE 2409 2411  24
T21     DATE 2400 2409  3/19/2021 -> T21        DATE 2414 2424  03/20/2021
T22     DATE 2444 2452  5/2/2021 -> T22 DATE 2459 2469  05/01/2021
T23     DATE 2586 2593  6/20/21 -> T23  DATE 2603 2611  06/22/21
T24     PATIENT 2605 2613       Jacobsen -> T24 PATIENT 2623 2632       CERVANTES
T25     AGE 2619 2623   63yo -> T25     AGE 2638 2642   68yo
T26     PATIENT 2634 2638       NASH -> T26     PATIENT 2653 2659       NELSON
T27     DOCTOR 2862 2869        Nichols -> T27  DOCTOR 2883 2888        SMITH
T28     DOCTOR 2910 2917        Nichols -> T28  DOCTOR 2929 2934        SMITH
T29     PATIENT 3006 3010       NASH -> T29     PATIENT 3023 3028       PERRY
T30     DATE 3041 3051  10/12/2022 -> T30       DATE 3059 3069  10/10/2022
T31     PATIENT 3053 3072       Salman, Hasan Kumar -> T31      PATIENT 3071 3083       LITTLE, RYAN
T32     MEDICALRECORD 3365 3374 091456244 -> T32        MEDICALRECORD 3376 3385 604604666
T33     DOCTOR 3402 3417        TREVOR JACOBSEN -> T33  DOCTOR 3413 3427        MICHAEL WILSON
T34     AGE 3424 3426   64 -> T34       AGE 3434 3436   60
T35     DATE 3999 4012  November 2012 -> T35    DATE 4009 4017  Nov 2012
T36     DOCTOR 4154 4172        Gregory E Kowelsky -> T36       DOCTOR 4159 4167        RYAN KIM
T37     DATE 4213 4221  10/31/12 -> T37 DATE 4208 4216  10/30/12
T38     DOCTOR 4259 4284        Tarantino, Hannah Carroll -> T38        DOCTOR 4254 4269        GARCIA, MATTHEW
T39     AGE 4331 4333   62 -> T39       AGE 4316 4318   67
T40     DATE 4389 4393  2006 -> T40     DATE 4374 4378  2007
T41     DOCTOR 4752 4760        J. Spano -> T41 DOCTOR 4737 4749        BRYAN BROOKS
T42     DOCTOR 4769 4778        Tarantino -> T42        DOCTOR 4758 4764        WILSON
T43     DATE 4787 4797  11/26/2012 -> T43       DATE 4773 4783  12/08/2012
T44     MEDICALRECORD 4952 4960 91456244 -> T44 MEDICALRECORD 4938 4946 11412444
Finished Process. Output Dir: /Users/temp/BRATsynthetic/example_deid
```

## Tags Handled

```
AGE
BIOID
CITY
COUNTRY
DATE
DEVICE
DOCTOR
EMAIL
FAX
HEALTHPLAN
HOSPITAL
IDNUM
LOCATION-OTHER
MEDICALRECORD
ORGANIZATION
PATIENT
PHONE
PROFESSION
STATE
STREET
TIME
UNDETERMINED
URL
USERNAME
ZIP
```

## Installation
There are two different `requirements.txt` files.

This can be installed with the following command:
```
pip install -r requirements.txt
```

This installs dependencies for the bratsynthetic.py script.

There are additional dependencies for [evaluation/](evaluation/).  These are in  `requirements-evaluation.txt`, which are optional.


The environment was tested on 2025-04-21 with Python 3.12.3.  The code perhaps works back to Python 3.7/3.8???



[comment]: <> (## TODO)
