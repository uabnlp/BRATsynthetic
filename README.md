# BRATsynthetic

## About

Python tool that generates realistic synthetic text for a superset of I2B2 2014 personal health information entity types. 
A poster was published in AMIA (https://knowledge.amia.org/73035-amia-1.4612663/t004-1.4613775/t004-1.4613776/3478476-1.4613879/3478476-1.4613880?qr=1) 
and a paper is pending.

This tool takes annotated text from Brat (https://brat.nlplab.org) and replaces personal information with synthetic data. It will attempt to match the format of the text.

## Examples of Replacements

```
CityMaker: Bristow -> East Michael
DateMaker: 11/34 -> 01/01
DateMaker: 2083-08-05 -> 1992-07-06
DateMaker: 2090 -> 1979
DateMaker: Jul 27, 2094 -> Aug 23, 1988
DateMaker: March -> December
DateMaker: November 2067 -> October 1998
DoctorMaker: Samantha G Noland -> Brittany Barker
HospitalMaker: BMH -> HCH
HospitalMaker: Janesville -> Dekalb
HospitalMaker: Senior Care Clinic -> Madison Hospital
HospitalMaker: TRUMBULL MEMORIAL HOSPITAL -> EVERGREEN MEDICAL CENTER
LocationOtherMaker: long island -> grocery store
MedicalRecordMaker: 258-16-49-2 -> 212-04-01-2
MedicalRecordMaker: 3246:F13427 -> 1586:N11853
OrganizationMaker: THX industries -> Smith-Salas
PatientMaker: DALEY,WADE -> JACKSON, JENNIFER
PatientMaker: Neill -> Guerrero
ProfessionMaker: manager -> advertising copywriter
ProfessionMaker: Quarry Worker -> Technical Sales Engineer
StateMaker: FL -> NY
StateMaker: Maryland -> Ohio
StreetMaker: 976 Clinton Street -> 4631 Alicia Mount
```

## Usage:

`bratsynthetic -i INPUT_DIR -o OUTPUT_DIR`

* `INPUT_DIR` - directory with BRAT files annotated with personal information tags.
* `OUTPUT_DIR` - directory to output text files with synthetic personal information

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


[comment]: <> (## TODO)

