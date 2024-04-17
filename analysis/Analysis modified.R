# Import libraries
library(readxl)
library(magrittr)
library(tidyverse)
AnnotatedInformation_new <- read_xlsx('/Users/salmaaly/Documents/Dr Osborne project/AnnotatedInformation new.xlsx')

## Critical terms in documents
df1 <- AnnotatedInformation_new %>%
  filter(Term_type== 1) %>%
  group_by(DOC_ID) %>%
summarize(sum(`DEID ENTITY_TYPE COUNT`))
df1
measure_critical <- df1 %>%
  summary('sum(`DEID ENTITY_TYPE COUNT`)')
measure_critical

# all terms in documents
df2 <- AnnotatedInformation_new %>%
  group_by(DOC_ID) %>%
  summarize(sum(`DEID ENTITY_TYPE COUNT`))
df2
measure_all <- df2 %>%
  summary('sum(\`DEID ENTITY_TYPE COUNT\`)')
measure_all


## Critical terms in MRN
df3 <- AnnotatedInformation_new %>%
  filter(Term_type== 1) %>%
  group_by(MRN) %>%
  summarize(sum(`DEID ENTITY_TYPE COUNT`))
df3
record_critical <- df3 %>%
  summary('sum(\`DEID ENTITY_TYPE COUNT\`)')
record_critical


##all terms in MRN
df4 <- AnnotatedInformation_new %>%
  group_by(MRN) %>%
  summarize(sum(`DEID ENTITY_TYPE COUNT`))
df4
record_all <- df4 %>%
  summary('sum(\`DEID ENTITY_TYPE COUNT\`)')
record_all

###calculate mode
df11 <- AnnotatedInformation_new %>%
  filter(Term_type== 1) %>%
  group_by(DOC_ID) %>%
  mutate(sumdoc_c= sum(`DEID ENTITY_TYPE COUNT`)) 
df11
df22 <- AnnotatedInformation_new %>%
  group_by(DOC_ID) %>%
  mutate(sumdoc_nc= sum(`DEID ENTITY_TYPE COUNT`))
df22
df33 <- AnnotatedInformation_new %>%
  filter(Term_type== 1) %>%
  group_by(MRN) %>%
  mutate(sumpt_c= sum(`DEID ENTITY_TYPE COUNT`))
df33
df44 <- AnnotatedInformation_new %>%
  group_by(MRN) %>%
  mutate(sumpt_nc= sum(`DEID ENTITY_TYPE COUNT`))
df44

###export data on excel
install.packages("writexl")
library("writexl")
write_xlsx(df11,"/Users/salmaaly/Documents/Dr Osborne project/df11.xlsx")
write_xlsx(df22,"/Users/salmaaly/Documents/Dr Osborne project/df22.xlsx")
write_xlsx(df33,"/Users/salmaaly/Documents/Dr Osborne project/df33.xlsx")
write_xlsx(df44,"/Users/salmaaly/Documents/Dr Osborne project/df44.xlsx")

# bernoulli distribution in r
error5 <- rbinom(42170, 1,.05)
error5

error1 <- rbinom(42170, 1,.01)
error1

error0.5 <- rbinom(42170, 1,.005)
error0.5

error0.1 <- rbinom(42170, 1,.001)
error0.1

#Simulation with 5, 1, 0.5, 0.1% errors:
new_data <- AnnotatedInformation_new %>%
  cbind(error5) %>%
  cbind(error1) %>%
  cbind(error0.1) %>%
  cbind(error0.5) 
new_data

#Associating errors with critical terms 
new_data2 <- new_data %>%
  mutate(term5= Term_type + error5) %>%
  mutate(term1= Term_type + error1) %>%
  mutate(term0.5= Term_type + error0.5) %>%
  mutate (term0.1= Term_type + error0.1)

#consistent substitution doc (error in one critical PHI)
##error 5
consistent_doc_5 <- new_data2 %>%
  filter(term5== 2) %>%
  group_by(DOC_ID) %>%
  count(term5) 
consistent_doc_5
clr5 <- (478/3617)*100
clr5

##error 1
consistent_doc_1 <- new_data2 %>%
  filter(term1== 2) %>%
  group_by(DOC_ID) %>%
  count(term1) 
consistent_doc_1
clr1 <- (92/3617)*100
clr1

##error 0.5
consistent_doc_0.5 <- new_data2 %>%
  filter(term0.5== 2) %>%
  group_by(DOC_ID) %>%
  count(term0.5) 
consistent_doc_0.5
clr0.5 <- (56/3617)*100
clr0.5

##error 0.1
consistent_doc_0.1 <- new_data2 %>%
  filter(term0.1== 2) %>%
  group_by(DOC_ID) %>%
  count(term0.1) 
consistent_doc_0.1
clr0.1 <- (9/3617)*100
clr0.1

#Inconsistent substitution doc (error in two or more critical PHI)
##error 5
Inconsistent_doc_5 <- new_data2 %>%
  filter(term5== 2) %>%
  group_by(DOC_ID) %>%
  count(term5) 
  #if_else(condition= n =2, true= 1, false= 0)
Inconsistent_doc_5 %>%
  filter(n >= 2)

Iclr5 <- (26/3617)*100
Iclr5

##error 1
Inconsistent_doc_1 <- new_data2 %>%
  filter(term1== 2) %>%
  group_by(DOC_ID) %>%
  count(term1) 
Inconsistent_doc_1
Inconsistent_doc_1 %>%
  filter(n >= 2)

Iclr1 <- (2/3617)*100
Iclr1

##error 0.5
Inconsistent_doc_0.5 <- new_data2 %>%
  filter(term0.5== 2) %>%
  group_by(DOC_ID) %>%
  count(term0.5) 
Inconsistent_doc_0.5
Inconsistent_doc_0.5 %>%
  filter(n >= 2)
Iclr0.5 <- (0/3617)*100
Iclr0.5

##error 0.1
Inconsistent_doc_0.1 <- new_data2 %>%
  filter(term0.1== 2) %>%
  group_by(DOC_ID) %>%
  count(term0.1) 
Inconsistent_doc_0.1
Inconsistent_doc_0.1 %>%
  filter(n >= 2)
Iclr0.1 <- (0/3617)*100
Iclr0.1

#consistent substitution patient (error in one critical PHI)
##error 5
consistent_pt_5 <- new_data2 %>%
  filter(term5== 2) %>%
  group_by(MRN) %>%
  count(term5) 
consistent_pt_5
clrp5 <- (107/165)*100
clrp5

##error 1
consistent_pt_1 <- new_data2 %>%
  filter(term1== 2) %>%
  group_by(MRN) %>%
  count(term1) 
consistent_pt_1
clrp1 <- (49/165)*100
clrp1

##error 0.5
consistent_pt_0.5 <- new_data2 %>%
  filter(term0.5== 2) %>%
  group_by(MRN) %>%
  count(term0.5) 
consistent_pt_0.5
clrp0.5 <- (32/165)*100
clrp0.5

##error 0.1
consistent_pt_0.1 <- new_data2 %>%
  filter(term0.1== 2) %>%
  group_by(MRN) %>%
  count(term0.1) 
consistent_pt_0.1
clrp0.1 <- (8/165)*100
clrp0.1

#Inconsistent substitution patient (error in two or more critical PHI)
##error 5
Inconsistent_pt_5 <- new_data2 %>%
  filter(term5== 2) %>%
  group_by(MRN) %>%
  count(term5) 
#if_else(condition= n =2, true= 1, false= 0)
Inconsistent_pt_5 %>%
  filter(n >= 2)

Iclrp5 <- (72/165)*100
Iclrp5

##error 1
Inconsistent_pt_1 <- new_data2 %>%
  filter(term1== 2) %>%
  group_by(MRN) %>%
  count(term1) 
Inconsistent_pt_1
Inconsistent_pt_1 %>%
  filter(n >= 2)

Iclrp1 <- (22/165)*100
Iclrp1

##error 0.5
Inconsistent_pt_0.5 <- new_data2 %>%
  filter(term0.5== 2) %>%
  group_by(MRN) %>%
  count(term0.5) 
Inconsistent_pt_0.5
Inconsistent_pt_0.5 %>%
  filter(n >= 2)
Iclrp0.5 <- (12/165)*100
Iclrp0.5

##error 0.1
Inconsistent_pt_0.1 <- new_data2 %>%
  filter(term0.1== 2) %>%
  group_by(MRN) %>%
  count(term0.1) 
Inconsistent_pt_0.1
Inconsistent_pt_0.1 %>%
  filter(n >= 2)
Iclrp0.1 <- (1/165)*100
Iclrp0.1

##graphs
graphdoc <- read_xlsx('/Users/salmaaly/Documents/Dr Osborne project/doc_strat.xlsx')
graph1 <- graphdoc %>%
  ggplot(aes(x= Error_rate, y= `PHI  leakage rate`, color= substitution_strategy))+
  geom_point(size= 7, alpha=0.7)+
  geom_line(size=1)+
  theme_minimal()+
  theme(text = element_text(size = 15)) +
  labs(x = 'Error rate')+
  labs(title = 'PHI leakage at document level')
graph1
  
graphpt <- read_xlsx('/Users/salmaaly/Documents/Dr Osborne project/pt_strat.xlsx')
graph2 <- graphpt %>%
  ggplot(aes(x= Error_rate, y= `PHI  leakage rate`, color= substitution_strategy))+
  geom_point(size= 7, alpha=0.7)+
  geom_line(size=1)+
  theme_minimal()+
  theme(text = element_text(size = 15)) +
  labs(x = 'Error rate')+
  labs(title = 'PHI leakage at patient MRN level')
graph2 

  