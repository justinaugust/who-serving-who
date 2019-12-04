# Who's Serving Who?
## General Assembly DSI Capstone Project
_Justin August_, General Assembly Data Science Immersive Fall 2019, SF Campus



## Table of Contents
1. [Context](#Context)
2. [Initial Proposal & Check In Updates](#Initial-Proposal)
3. [Data Sources, Collection & Storage](#Data)
4. [Visualization](#Visualization)
5. [Web Access](#Web-Access)
6. [Future Plans](#Future-Plans)
7. [Media & Demonstration Links](#Media-&-Demonstration-Links)


## Context
Oakland Schools in 2019 face many challenges and thus so do parents and students when deciding where to send their child. Due to the low overall achievement of Oakland's schools, each student is eligible to request placement in another school. Historically the "desirable" schools have been located in predominately affluent, whiter areas of the city with those students' outcomes skewing the overall results.

How and where should parents of color look to find a school that has high student outcomes for children like their own?

## Initial Proposal
|Project Name|Goal / Outcome|Audience|Metrics|Data Source|Pros|Cons|Reasonable|
|---|---|---|---|---|---|---|---|
|School Success Map / Who's Serving Who?|Create a model that can predict a child's probability of achieving different success metrics at each school. Based on widely aggregated data such as socioeconomic indicators, learning differences, gender/sex, race/ethnicity, etc. Turn this into a web app where you can enter this information in - or exclude some - to find out the probability of schools serving your child well based on an outcome of your choosing.|Parents, Students|GPA, College Acceptance, Reading levels, Math Levels, High Stakes Tests, SAT/ACT Scores, High School graduation rates|State school information, ??|Content Knowledge, usable, important|Lots of data, perhaps too mission critical for some?|Initial Component|

### Update for Check-In 2

#### This Iteration
##### Definites
- Outcoming correlations on CAASSP by:
    - Ethnicity
    - Race
    - Gender
    - Immigration Status
    - EL Proficiency
- Interactive Map 
- Enter your child's demo info, get a map
- SQL Back End using SQLAlchemy + PostgresSQL

##### Stretch Goals
- Trend in outcomes over time
- Mobile Friendly

## Data
### Sources
#### California Department of Education

#### National Center of Education Statistics

#### City of Oakland

### Cleaning

### Storage
#### PostgresSQL Structure



## Visualization
Altair

## Web Access
Flask
Heroku


## Future Plans
### Moving Slow & Not Breaking Things
|Pros|Cons|
|---|---|
|Increased access of information to parents
Matching students to schools
Uses an Intersectional Identity first approach
|Increased segregation of students
Justification for school closures
Does not address underlying issues of different achievement levels
Currently based solely on high stakes testing
 |

### Collaborations
Currently in contact with Studio Pathways and Educate78, two Oakland-based Education organizations for guidance on improvements, deployment and potential use of this app.

### Immediate Feature Additions
- Historical trendlines for proficiency scores
- GreatSchools API Information
- School Level reports

### Long-Term Feature Additions
- Inclusion of non-High Stakes test metrics
	- Attendance
	- Teacher Tenure
	- Staff Makeup
	- Pedagogical Outlook
- Mobile-friendly
- Commute Calculation


## Media & Demonstration Links
- [Google Slides](https://docs.google.com/presentation/d/1DCa1Db2Y9ZnPJ1c0GazXoVGmBHjDkCz7hdzOmm3LE64/edit?usp=sharing)
- [App Website](https://who-serving-who.herokuapp.com/)
