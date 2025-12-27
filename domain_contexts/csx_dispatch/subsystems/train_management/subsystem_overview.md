# Train Management Subsystem Overview

## Purpose

The Train Management Subsystem (TM) is responsible for managing train operational data, including train profiles, consists, crew assignments, and operational procedures such as departure checklists. The subsystem provides Authorized Users with visibility into active trains and tools for managing train-related information.

## Key Responsibilities

1. **Train Data Management**
   - Display lists of active trains with current status
   - Create, modify, and delete train profiles
   - Manage train consists (locomotive and car compositions)
   - Store and retrieve Train Sheet data

2. **Crew Management**
   - Assign Crew Sets to trains
   - Track crew availability and qualifications
   - Manage crew change operations

3. **Operational Procedures**
   - Implement Departure Checklist workflow
   - Support pre-departure verification steps (Job Briefing, Work Locations, Train Consist, PTC checks)
   - Generate operational notifications and events

4. **Configuration Management**
   - Provide configurable parameters for TM features
   - Allow Administrators to enable/disable optional features
   - Manage default values and visibility controls

## Primary Actors

- **Authorized User**: General authenticated user interacting with TM functions
- **Dispatcher**: Railway operator managing train movements and operations
- **Train Crew**: Personnel operating trains who may interact with TM data
- **Administrator**: User configuring TM subsystem parameters

## External Interfaces

### Outbound Interfaces (TM provides data to):
- **Traffic Control Subsystem**: Train operational status, Train consist data for movement planning
- **Management Information System (MIS)**: Train operational reports, completed checklist data
- **Positive Train Control BOS**: Train profile data, PTC configuration status

### Inbound Interfaces (TM receives data from):
- **MIS**: Train scheduling data, crew roster information
- **Traffic Control Subsystem**: Track occupancy data, current train locations

## Requirement Allocation Guidelines

Allocate requirements to Train Management when they involve:

### Core TM Functions:
- ✅ Display, create, modify train data
- ✅ Manage Train Profiles, Train Consists, Train Sheets
- ✅ Crew Set assignment and management
- ✅ Departure Checklist workflow and sections (Job Briefing, Work Locations, etc.)
- ✅ TM-specific configuration parameters (e.g., TM.DEPARTURE_CHECKLIST.*)

### NOT Train Management (allocate elsewhere):
- ❌ Signal control or track authority (→ Traffic Control)
- ❌ Bridge position monitoring (→ Bridge Control)
- ❌ Route planning or movement planning (→ Traffic Control)
- ❌ Field device communication (→ Traffic Control or Bridge Control)

## Common Requirement Patterns for TM

### Train List Display

**Pattern**: Display trains with status, location, and operational details

**Example**: "The Train Management Subsystem shall display a list of all Active Trains with their current status, location, and assigned Crew Set."

### Departure Checklist Sections

**Pattern**: Implement checklist sections with user acknowledgment

**Example**: "The Train Management Subsystem shall display the Job Briefing section of the Departure Checklist and provide an option for the Authorized User to acknowledge."

### Configuration Parameters

**Pattern**: Provide Boolean Configuration Parameters for feature enablement

**Example**: "The Train Management Subsystem shall allow Administrators to configure whether the Work Locations section of the Departure Checklist is displayed via the TM.CHECKLIST.WORK_LOCATIONS.VISIBLE parameter."

### Notification Events

**Pattern**: Generate events on significant state changes

**Example**: "The Train Management Subsystem shall generate an Information Notification Event when an Authorized User completes the Departure Checklist."

### Data Validation

**Pattern**: Validate train data and display errors for invalid inputs

**Example**: "The Train Management Subsystem shall validate Train Consist data to ensure all referenced cars exist in the system, and display an Error Message if unknown cars are specified."

## Naming Conventions

### Requirement IDs:
- Format: `TM-{TYPE}-{NNN}`
- Examples: `TM-FUNC-001`, `TM-PERF-005`, `TM-INTF-012`

### Configuration Parameters:
- Format: `TM.{FEATURE}.{PARAMETER}`
- Examples: `TM.DEPARTURE_CHECKLIST.MANDATORY`, `TM.CHECKLIST.JOB_BRIEFING.VISIBLE`

### Notification Events:
- Format: `EV-TM.{FEATURE}.{EVENT_NAME}`
- Examples: `EV-TM.DEPARTURE.CHECKLIST.COMPLETED`, `EV-TM.TRAIN.STATUS.CHANGED`

## Typical TM Use Cases

### UC-TM-040: Train Departure Checklist

**System Goal**: Enable Train Crew to complete pre-departure verification steps

**TM Subsystem Responsibilities**:
- Display Departure Checklist with multiple sections (Job Briefing, Work Locations, Train Consist, PTC, Dispatcher Bulletin)
- Allow user acknowledgment of each section
- Validate checklist completion before allowing train departure
- Generate notification event on checklist completion
- Support configurable visibility of checklist sections

**See**: `examples.md` for detailed UC-TM-040 requirements benchmark

### UC-TM-010: Active Train List Display

**System Goal**: Provide Dispatchers with real-time view of active trains

**TM Subsystem Responsibilities**:
- Display list of all Active Trains
- Show train ID, status, location, Crew Set for each train
- Update train data at specified refresh rate (e.g., 5 seconds)
- Allow sorting and filtering of train list
- Provide drill-down to detailed train information

## Quality Expectations

All TM requirements must:
- Follow TM-{TYPE}-{NNN} ID format
- Use glossary terms with correct capitalization
- Begin statement with "The Train Management Subsystem shall..."
- Include specific trigger conditions (e.g., "When an Authorized User...")
- Specify observable behavior (e.g., "display," "validate," "generate")
- Provide measurable acceptance criteria (e.g., "within 5 seconds," "with 99% accuracy")
