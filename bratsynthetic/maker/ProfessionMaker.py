import random

from .Maker import Maker

_jobs = [
"Academic librarian",
"Accommodation manager",
"Accountant",
"Accounting technician",
"Actor",
"Actuary",
"Acupuncturist",
"Administrator",
"Administrator",
"Adult guidance worker",
"Adult nurse",
"Advertising account executive",
"Advertising account planner",
"Advertising art director",
"Advertising copywriter",
"Aeronautical engineer",
"Agricultural consultant",
"Agricultural engineer",
"Aid worker",
"Air cabin crew",
"Air traffic controller",
"Airline pilot",
"Ambulance person",
"Amenity horticulturist",
"Analytical chemist",
"Animal nutritionist",
"Animal technologist",
"Animator",
"Applications developer",
"Arboriculturist",
"Archaeologist",
"Architect",
"Architectural technologist",
"Archivist",
"Armed forces logistics",
"Armed forces operational officer",
"Armed forces technical officer",
"Armed forces training and education officer",
"Art gallery manager",
"Art therapist",
"Artist",
"Arts administrator",
"Arts development officer",
"Associate Professor",
"Astronomer",
"Audiological scientist",
"Automotive engineer",
"Banker",
"Barista",
"Barrister",
"Barrister's clerk",
"Best boy",
"Biochemist",
"Biomedical engineer",
"Biomedical scientist",
"Bonds trader",
"Bookseller",
"Brewing technologist",
"Broadcast engineer",
"Broadcast journalist",
"Broadcast presenter",
"Building control surveyor",
"Building services engineer",
"Building surveyor",
"Buyer",
"Cabin crew",
"Call centre manager",
"Camera operator",
"Careers adviser",
"Careers information officer",
"Cartographer",
"Catering manager",
"Ceramics designer",
"Charity fundraiser",
"Charity officer",
"Chartered accountant",
"Chartered certified accountant",
"Chartered legal executive (England and Wales)",
"Chartered loss adjuster",
"Chartered management accountant",
"Chartered public finance accountant",
"Chemical engineer",
"Chemist",
"Chief Executive Officer",
"Chief Financial Officer",
"Chief Marketing Officer",
"Chief of Staff",
"Chief Operating Officer",
"Chief Strategy Officer",
"Chief Technology Officer",
"Child psychotherapist",
"Chiropodist",
"Chiropractor",
"Civil engineer",
"Civil Service administrator",
"Claims inspector",
"Clinical biochemist",
"Clinical cytogeneticist",
"Clinical embryologist",
"Clinical molecular geneticist",
"Clinical psychologist",
"Clinical research associate",
"Clinical scientist",
"Clothing",
"Colour technologist",
"Commercial art gallery manager",
"Commercial horticulturist",
"Commercial",
"Commissioning editor",
"Communications engineer",
"Community arts worker",
"Community development worker",
"Community education officer",
"Community pharmacist",
"Company secretary",
"Comptroller",
"Computer games developer",
"Conference centre manager",
"Conservation officer",
"Conservator",
"Consulting civil engineer",
"Contracting civil engineer",
"Contractor",
"Control and instrumentation engineer",
"Copywriter",
"Corporate investment banker",
"Corporate treasurer",
"Counselling psychologist",
"Counsellor",
"Curator",
"Customer service manager",
"Cytogeneticist",
"Dance movement psychotherapist",
"Dancer",
"Data processing manager",
"Data scientist",
"Database administrator",
"Dealer",
"Dentist",
"Designer",
"Development worker",
"Diagnostic radiographer",
"Dietitian",
"Diplomatic Services operational officer",
"Dispensing optician",
"Doctor",
"Dramatherapist",
"Drilling engineer",
"Early years teacher",
"Ecologist",
"Economist",
"Editor",
"Editorial assistant",
"Education administrator",
"Education officer",
"Educational psychologist",
"Electrical engineer",
"Electronics engineer",
"Embryologist",
"Emergency planning",
"Energy engineer",
"Energy manager",
"Engineer",
"Engineering geologist",
"English as a foreign language teacher",
"English as a second language teacher",
"Environmental consultant",
"Environmental education officer",
"Environmental health practitioner",
"Environmental manager",
"Equality and diversity officer",
"Equities trader",
"Ergonomist",
"Estate agent",
"Estate manager",
"Event organiser",
"Exercise physiologist",
"Exhibition designer",
"Exhibitions officer",
"Facilities manager",
"Farm manager",
"Fashion designer",
"Fast food restaurant manager",
"Field seismologist",
"Field trials officer",
"Film",
"Financial adviser",
"Financial controller",
"Financial manager",
"Financial planner",
"Financial risk analyst",
"Financial trader",
"Fine artist",
"Firefighter",
"Fish farm manager",
"Fisheries officer",
"Fitness centre manager",
"Food technologist",
"Forensic psychologist",
"Forensic scientist",
"Forest",
"Freight forwarder",
"Furniture conservator",
"Furniture designer",
"Further education lecturer",
"Futures trader",
"Gaffer",
"Games developer",
"Garment",
"General practice doctor",
"Geneticist",
"Geochemist",
"Geographical information systems officer",
"Geologist",
"Geophysical data processor",
"Geophysicist",
"Geoscientist",
"Glass blower",
"Government social research officer",
"Graphic designer",
"Haematologist",
"Health and safety adviser",
"Health and safety inspector",
"Health physicist",
"Health promotion specialist",
"Health service manager",
"Health visitor",
"Herbalist",
"Heritage manager",
"Herpetologist",
"Higher education careers adviser",
"Higher education lecturer",
"Historic buildings inspector",
"Holiday representative",
"Homeopath",
"Horticultural consultant",
"Horticultural therapist",
"Horticulturist",
"Hospital doctor",
"Hospital pharmacist",
"Hotel manager",
"Housing manager",
"Human resources officer",
"Hydrogeologist",
"Hydrographic surveyor",
"Hydrologist",
"Illustrator",
"Immigration officer",
"Immunologist",
"Industrial buyer",
"Industrial",
"Information officer",
"Information systems manager",
"Insurance account manager",
"Insurance broker",
"Insurance claims handler",
"Insurance risk surveyor",
"Insurance underwriter",
"Intelligence analyst",
"Interior and spatial designer",
"International aid",
"Interpreter",
"Investment analyst",
"Investment banker",
"IT consultant",
"IT sales professional",
"IT technical support officer",
"IT trainer",
"Jewellery designer",
"Journalist",
"Landscape architect",
"Lawyer",
"Learning disability nurse",
"Learning mentor",
"Lecturer",
"Legal executive",
"Legal secretary",
"Leisure centre manager",
"Lexicographer",
"Librarian",
"Licensed conveyancer",
"Lighting technician",
"Lobbyist",
"Local government officer",
"Location manager",
"Logistics and distribution manager",
"Loss adjuster",
"Magazine features editor",
"Magazine journalist",
"Maintenance engineer",
"Management consultant",
"Manufacturing engineer",
"Manufacturing systems engineer",
"Marine scientist",
"Market researcher",
"Marketing executive",
"Materials engineer",
"Mechanical engineer",
"Media buyer",
"Media planner",
"Medical illustrator",
"Medical laboratory scientific officer",
"Medical physicist",
"Medical sales representative",
"Medical secretary",
"Medical technical officer",
"Mental health nurse",
"Merchandiser",
"Merchant navy officer",
"Metallurgist",
"Meteorologist",
"Microbiologist",
"Midwife",
"Minerals surveyor",
"Mining engineer",
"Mudlogger",
"Multimedia programmer",
"Multimedia specialist",
"Museum education officer",
"Museum",
"Music therapist",
"Music tutor",
"Musician",
"Nature conservation officer",
"Naval architect",
"Network engineer",
"Neurosurgeon",
"Newspaper journalist",
"Nurse",
"Nutritional therapist",
"Occupational hygienist",
"Occupational psychologist",
"Occupational therapist",
"Oceanographer",
"Office manager",
"Oncologist",
"Operational investment banker",
"Operational researcher",
"Operations geologist",
"Ophthalmologist",
"Optician",
"Optometrist",
"Orthoptist",
"Osteopath",
"Outdoor activities",
"Paediatric nurse",
"Paramedic",
"Passenger transport manager",
"Patent attorney",
"Patent examiner",
"Pathologist",
"Pension scheme manager",
"Pensions consultant",
"Personal assistant",
"Personnel officer",
"Petroleum engineer",
"Pharmacist",
"Pharmacologist",
"Photographer",
"Physicist",
"Physiological scientist",
"Physiotherapist",
"Phytotherapist",
"Pilot",
"Planning and development surveyor",
"Plant breeder",
"Podiatrist",
"Police officer",
"Politician's assistant",
"Presenter",
"Press photographer",
"Press sub",
"Primary school teacher",
"Print production planner",
"Printmaker",
"Prison officer",
"Private music teacher",
"Probation officer",
"Producer",
"Product designer",
"Product manager",
"Production assistant",
"Production designer",
"Production engineer",
"Production manager",
"Professor Emeritus",
"Programme researcher",
"Programmer",
"Proofreader",
"Psychiatric nurse",
"Psychiatrist",
"Psychologist",
"Psychotherapist",
"Psychotherapist",
"Public affairs consultant",
"Public house manager",
"Public librarian",
"Public relations account executive",
"Public relations officer",
"Publishing copy",
"Publishing rights manager",
"Purchasing manager",
"Quality manager",
"Quantity surveyor",
"Quarry manager",
"Race relations officer",
"Radiation protection practitioner",
"Radio broadcast assistant",
"Radio producer",
"Radiographer",
"Ranger",
"Records manager",
"Recruitment consultant",
"Recycling officer",
"Regulatory affairs officer",
"Research officer",
"Research scientist",
"Restaurant manager",
"Retail banker",
"Retail buyer",
"Retail manager",
"Retail merchandiser",
"Risk analyst",
"Risk manager",
"Runner",
"Rural practice surveyor",
"Sales executive",
"Sales professional",
"Sales promotion account executive",
"Science writer",
"Scientific laboratory technician",
"Scientist",
"Secondary school teacher",
"Secretary",
"Seismic interpreter",
"Senior tax professional",
"Set designer",
"Ship broker",
"Site engineer",
"Social research officer",
"Social researcher",
"Social worker",
"Software engineer",
"Soil scientist",
"Solicitor",
"Sound technician",
"Special educational needs teacher",
"Special effects artist",
"Speech and language therapist",
"Sport and exercise psychologist",
"Sports administrator",
"Sports coach",
"Sports development officer",
"Sports therapist",
"Stage manager",
"Statistician",
"Structural engineer",
"Surgeon",
"Surveyor",
"Systems analyst",
"Systems developer",
"Tax adviser",
"Tax inspector",
"Teacher",
"Teaching laboratory technician",
"Technical author",
"Technical brewer",
"Technical sales engineer",
"TEFL teacher",
"Telecommunications researcher",
"Television camera operator",
"Television floor manager",
"Television production assistant",
"Television",
"Textile designer",
"Theatre director",
"Theatre manager",
"Theatre stage manager",
"Theme park manager",
"Therapeutic radiographer",
"Therapist",
"Tour manager",
"Tourism officer",
"Tourist information centre manager",
"Town planner",
"Toxicologist",
"Trade mark attorney",
"Trade union research officer",
"Trading standards officer",
"Training and development officer",
"Translator",
"Transport planner",
"Travel agency manager",
"Tree surgeon",
"Veterinary surgeon",
"Video editor",
"Visual merchandiser",
"Volunteer coordinator",
"Warden",
"Warehouse manager",
"Waste management officer",
"Water engineer",
"Water quality scientist",
"Web designer",
"Wellsite geologist",
"Writer",
"Youth worker",
]

_job_vehicles = [
 'mail car', 'firetruck', 'police car', 'icecream truck'
]

class ProfessionMaker(Maker):

    def make_one(self, input: str) -> str:
        output = 'UNMATCHED'

        if input in _job_vehicles:
            output = 'work vehicle'
        else:
            output = random.choice(_jobs)

        output = self.match_case(input, output)

        if output.upper() == 'UNMATCHED':
            output = self.match_case(random.choice(_jobs))

        return output
