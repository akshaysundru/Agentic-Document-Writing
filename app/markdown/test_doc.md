## E XECUTIVE S UMMARY

Hitachi Rail STS (Hitachi) has been contracted to deliver and maintain an Automated Train Operation

(ATO) system for Rio Tinto Iron Ore as a part of their AutoHaul® project. This ATO system facilitates

the driverless movement of trains in a railway network in Western Australia. Because of its safety

critical nature, any modifications made to the AutoHaul® system require extensive testing before they

can be rolled out. Presently, this testing is performed manually and uses a lot of testing time and

resources. Hitachi has commissioned the design and development of an automated testing tool which

can be used to reduce the testing time and improve testing efficiency. The testing would focus on the

communication interfaces between various AutoHaul® sub-systems.


The primary aim of this project was to design and develop an integrated testing framework to support

the automated testing of the AutoHaul® project. The testing focused on testing the behaviour of the

Fiber Interface Processor (FIP) and the Train Control Sub-system (TCS) by testing the communication

interfaces between these sub-systems and other AutoHaul® sub-systems.


This report provides an overview of the AutoHaul® system and details about the specific interfaces

that testing is being automated for. A review of literature relevant to designing an automated testing

framework is also present.


This report also delivers a summary of the design and outcomes of the tool used to test the FIP’s

behaviour. This tool, called the FIP Tester, simulates the behaviour of the Interlocking (IXL) devices

that connect to the FIP. It verifies that the FIP is responding correctly to messages sent by the IXL

simulators in order to ensure that the FIP is behaving correctly. Furthermore, the report provides a

summary of the testing activities conducted to validate the behaviour of the FIP Tester.


Similarly, this report provides a summary of the design and project outcomes of enhancing a pre
existing tool, called the TCS Testing Suite. Prior to the project, this tool was developed at Hitachi to

begin to automate the TCS testing. It contains the testing framework required to automate the testing

procedure that is conducted by Hitachi.


During this project, the TCS Testing Suite’s capabilities were enhanced to make it capable of running

more complex tests. Additionally, a Log Parser which iterates through various log files and consolidates

all of the errors into a single file was developed to aid users in troubleshooting while using the TCS

Testing Suite. The report also provides a summary of the testing activities performed to validate the

behaviour of the TCS Testing Suite enhancements and the Log Parser.


Overall, the developed FIP Tester and the enhanced TCS Testing Suite can be reliably used to replace

a lot of the manual testing activities conducted at Hitachi.


Page | III


## A CKNOWLEDGEMENTS

I would like to sincerely thank a number of people who have helped me throughout this project.


Firstly, I would like to thank my supervisor Associated Professor Graeme Smith for the guidance and

advice that was provided throughout the semester which helped shape this project.


I would also like to thank the EAIT Employability team and Dr Christopher Leonardi at the University

of Queensland for all of their help in organising my placement at Hitachi Rail STS.


I would also like to thank Hitachi Rail STS, the host company, for allowing me the opportunity to work

on this project and learn about the railway industry and the AutoHaul® project. In particular I would

like to express my gratitude to my supervisory team at Hitachi, Dr Anthony MacDonald, Lionel Van

Den Berg and most of all Michal Cedrych for all of the support and advice I was given throughout the

course of the project. I would also like to thank Ujas Soni, Andrew Mijat and Benjamin Mountford at

Hitachi for all of the technical advice and support they gave me throughout the project.


Page | IV


## 2.0 T ECHNICAL B ACKGROUND

##### 2.1 T HE A UTO H AUL ® P ROJECT

The AutoHaul® project introduced an Automated Train Operation (ATO) system so that trains are able

to move autonomously on the mainline of RTIO’s railway network in Western Australia [3].


As seen in Figure 1, the three sub-systems AutoHaul® uses to ensure the safe movement of trains are

the Trainborne System, the Control Centre and the Wayside Systems [3].


The Trainborne System is installed in each AutoHaul® locomotive and uses the Automatic Train

Operations Controller (ATOC) as its primary control system. The ATOC can be thought of as the train’s

driver. It interfaces to the locomotive’s equipment to perform tasks such as braking, accelerating and

collision detection. It also communicates with the Control Centre to receive instructions and transfer

relevant data [4].


Located in Perth, the Control Centre uses the Train Control Sub-system (TCS) to control the majority

of the AutoHaul® network [3]. It manages the train routing, mission planning and provides a user

interface for operators to use.


The Wayside Systems contains a range of devices that are placed on the side of the tracks at various

points in the network. Collectively, this system performs functions such as train tracking, interlocking

and controlling intersections on the track [5].


A high level system architecture containing the sub-systems and communication interfaces relevant

for this project is provided in Figure 2. A description of the sub-systems is provided in Table 2 and

more details are given about these interfaces in Section 2.2.


Page | 2


_Figure 2 High level system architecture diagram of relevant sub-systems and interfaces_



Page | 3


_Table 2 Description of sub-systems_




|Sub-system Functionality|Col2|
|---|---|
|**WAYSIDE SYSTEMS**|**WAYSIDE SYSTEMS**|
|**Wayside Equipment**|Equipment which is placed on the trackside and is used to monitor the<br>health and status of track-based assets [6].|
|**Interlocking (IXL)**|This component of signaling systems ensures that the railway behaves in a<br>safe manner and is fail-safe [7] [8]. IXL devices do this by:<br> <br>Performing vital functions such as route setting,<br> <br>Sending signaling information to the TCS and<br> <br>Receiving commands, such as clearing signals, from the TCS.<br>Hitachi’s Microlok II is used as the IXL devices.|
|**TRAINBORNE SYSTEM**|**TRAINBORNE SYSTEM**|
|**Locomotive**<br>**Equipment**|A collection of equipment and computer systems that are used to monitor<br>and perform train operations such as interfacing with the ATOC and<br>operating the throttle and brakes [3].<br>|
|**Automatic Train**<br>**Operations**<br>**Controller (ATOC)**|The primary control system of the train. It communicates with other sub-<br>systems and controls all of the train’s operations [4].|
|**CONTROL CENTRE**|**CONTROL CENTRE**|
|**Train Control**<br>**Sub-system (TCS)**|The system used to monitor and control the railway network. It is used to<br>set routes, track train movement, manage alarms and perform monitoring<br>actions that were previously undertaken by drivers [9].|
|**Centralised Train**<br>**Control (CTC)**|A train control system that provides the network overview, shows<br>indications and allows route setting and train sheet management [10].|
|**Automation Man**<br>**Machine Interface**<br>**(AMMI)**|A user interface to all the trains and locomotives in the AutoHaul® system.<br>It allows users to access the CTC [11].|
|**Automation Server**<br>**(AS)**|A messaging service that acts as a gateway for the TCS and the rest of the<br>systems in the AutoHaul® system [5].|
|**Vital Safety Server**<br>**(VSS)**|Provides movement authorities to the train based on data from the<br>interlocking and level crossings [12]. The VSS also acts as a user interface<br>and allows users to set commands which are relayed to the rest of the<br>system.|
|**Field Interface**<br>**Processor (FIP)**|A device which connects to all of the IXLs in the field and facilitates the<br>exchange of information between the IXLs and the TCS [13].|
|**RTIO External**<br>**Systems**|A TIBCO Enterprise Message Service which acts as the interface between<br>the AutoHaul® and RTIO’s other systems [14]. RTIO External Systems are<br>used for functions such as producing an electronic train graph.|


Page | 4