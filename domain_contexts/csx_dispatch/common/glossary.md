# CSX Dispatch Domain Glossary

## Capitalization Rules

All terms listed in this glossary MUST be capitalized as shown when used in requirements, documentation, and specifications.

## Core System Terms

| Term | Abbreviation | Definition |
|------|--------------|------------|
| Train Management Function | TMF | Software component responsible for train data management, display, and operator interaction |
| Train Management Subsystem | TM | Subsystem managing train profiles, consists, sheets, and crew assignments |
| Traffic Control Subsystem | TC | Subsystem managing signal control, route management, and track authorities |
| Bridge Control Subsystem | BC | Subsystem managing bridge operations, status monitoring, and safety protocols |
| Use Case | UC | Specific scenario describing system behavior from user perspective |
| System Requirement Specification | SRS | Document defining system-level requirements |
| Subsystem Requirement Specification | SSRS | Document defining subsystem-level requirements |

## Train Management Terms

| Term | Abbreviation | Definition |
|------|--------------|------------|
| Active Train | - | A train currently in operation and tracked by the system |
| Train List | - | Display component showing current trains and their operational status |
| Train Profile | - | Configuration data defining train characteristics (length, weight, locomotive type) |
| Train Consist | - | List of railroad cars and locomotives making up a specific train |
| Train Sheet | - | Document containing operational details for a specific train movement |
| Crew Set | - | Assigned personnel responsible for operating a train |
| Departure Checklist | - | Mandatory pre-departure verification steps for train operations |
| Job Briefing | - | Safety and operational briefing section of Departure Checklist |
| Work Location | - | Geographic area where train crew will perform work activities |

## Traffic Control Terms

| Term | Abbreviation | Definition |
|------|--------------|------------|
| Control Point | CP | Location where track switches and signals can be remotely controlled |
| Track Segment | - | Section of track between two Control Points |
| Signal | - | Wayside device displaying track authorization and movement authority |
| Route | - | Path through the track network from origin to destination Control Point |
| Track Authority | - | Permission granted to occupy a specific Track Segment |
| Dispatcher | - | Railway operator responsible for controlling train movements in a territory |
| Movement Planner | - | System component for planning and managing train movements |

## Bridge Control Terms

| Term | Abbreviation | Definition |
|------|--------------|------------|
| Movable Bridge | - | Bridge with sections that can be raised, lowered, or rotated |
| Bridge Position | - | Current physical state of bridge (e.g., Down and Locked, Up, In Transit) |
| Bridge Lock | - | Safety mechanism preventing train movement when bridge is not secured |
| Bridge Operator | - | Personnel authorized to control movable bridge operations |

## Actor Terms

| Term | Abbreviation | Definition |
|------|--------------|------------|
| Authorized User | - | System user with authenticated credentials and assigned permissions |
| Operator | - | General term for human user interacting with the system |
| Administrator | - | User with elevated privileges for system configuration and management |
| Field Personnel | - | Railway workers operating equipment in physical locations along the track |

## Interface Terms

| Term | Abbreviation | Definition |
|------|--------------|------------|
| Management Information System | MIS | External enterprise system providing train scheduling and planning data |
| Positive Train Control Back Office Server | PTC BOS | External system managing Positive Train Control safety overlay |
| Human-Machine Interface | HMI | Graphical user interface for operator interaction with the system |
| Application Programming Interface | API | Software interface for system-to-system communication |

## Configuration Terms

| Term | Abbreviation | Definition |
|------|--------------|------------|
| Configuration Parameter | - | System setting that can be modified by authorized personnel |
| Boolean Configuration Parameter | - | Configuration setting with true/false or enabled/disabled values |
| Visibility Control | - | Configuration determining whether UI elements are displayed |
| Default Value | - | Pre-configured parameter value used when no override is specified |

## Event and Notification Terms

| Term | Abbreviation | Definition |
|------|--------------|------------|
| Notification Event | - | System-generated message alerting users or external systems of state changes |
| Event Type | - | Classification of notification (e.g., Information, Warning, Error) |
| Event Severity | - | Criticality level of a notification event |
| Event Log | - | Persistent storage of system events for audit and troubleshooting |

## Data Validation Terms

| Term | Abbreviation | Definition |
|------|--------------|------------|
| Data Validation | - | Process of verifying data conforms to defined rules and constraints |
| Validation Rule | - | Specific criterion data must satisfy (e.g., format, range, dependency) |
| Validation Failure | - | Condition where data does not meet validation criteria |
| Error Message | - | User-facing text describing a validation failure or system error |

## Examples of Correct Usage

### ✅ Correct Capitalization

"When an Authorized User initiates the Departure Checklist, the Train Management Subsystem shall display the Job Briefing section and provide an option for the Authorized User to acknowledge."

"The Traffic Control Subsystem shall update Track Authority status when a Train enters or exits a Control Point."

"The Bridge Control Subsystem shall prevent Train movement when the Movable Bridge is not in Down and Locked position."

### ❌ Incorrect Capitalization

"When an authorized user initiates the departure checklist, the train management subsystem shall display the job briefing section."
*(All glossary terms should be capitalized)*

"The traffic control subsystem shall update track authority when a train enters a control point."
*(Missing capitals on Traffic Control Subsystem, Track Authority, Train, Control Point)*

## Glossary Maintenance

This glossary is the authoritative source for domain terminology. When adding new terms:

1. Use Title Case for multi-word terms
2. Provide clear, concise definitions
3. Include abbreviations where standard acronyms exist
4. Ensure consistency with existing terms
5. Update all affected documentation when terms change
