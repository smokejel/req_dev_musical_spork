# CSX Dispatch Core System Overview

## System Purpose

The CSX Dispatch Core System is a distributed software platform for managing railway operations, including train movement control, signal management, bridge operations, and operational data management. The system provides Dispatchers and railway operators with real-time visibility and control over railway infrastructure and train movements.

## System Architecture

### Major Subsystems

The Core System is decomposed into three primary subsystems:

1. **Train Management Subsystem (TM)**
   - Purpose: Manage train operational data, profiles, and crew information
   - Key Functions: Train list display, train profile management, departure checklists, crew assignments
   - Primary Users: Dispatchers, Train Crew, Operations Managers

2. **Traffic Control Subsystem (TC)**
   - Purpose: Control track signals, routes, and movement authorities
   - Key Functions: Signal control, route management, track authority allocation, movement planning
   - Primary Users: Dispatchers, Traffic Controllers

3. **Bridge Control Subsystem (BC)**
   - Purpose: Monitor and control movable bridge operations
   - Key Functions: Bridge position monitoring, bridge movement control, safety interlocks
   - Primary Users: Bridge Operators, Dispatchers

### External Interfaces

The system integrates with external enterprise and safety systems:

- **Management Information System (MIS)**: Provides train scheduling, planning data, and enterprise reporting
- **Positive Train Control Back Office Server (PTC BOS)**: Manages PTC safety overlay and enforcement
- **Field Devices**: Signals, switches, detectors, and bridge controls connected via field networks

## Subsystem Allocation Principles

When decomposing system requirements into subsystem requirements, follow these allocation guidelines:

### Train Management Allocation

Allocate to Train Management when requirements involve:
- Train data display, creation, modification
- Train profiles, consists, or sheets
- Crew assignments and Crew Sets
- Departure Checklists or operational procedures
- Train-specific configuration parameters

**Examples**:
- "Display list of active trains" → Train Management
- "Validate train consist data" → Train Management
- "Manage crew assignments" → Train Management

### Traffic Control Allocation

Allocate to Traffic Control when requirements involve:
- Signal control or signal displays
- Route management or track authority
- Control Point operations
- Track occupancy or movement planning
- Dispatcher control actions for train movements

**Examples**:
- "Send signal command to field device" → Traffic Control
- "Allocate track authority" → Traffic Control
- "Plan train movement route" → Traffic Control

### Bridge Control Allocation

Allocate to Bridge Control when requirements involve:
- Movable Bridge position monitoring
- Bridge movement control
- Bridge safety interlocks or locks
- Bridge-specific alarms or notifications

**Examples**:
- "Monitor bridge position status" → Bridge Control
- "Control bridge raising operation" → Bridge Control
- "Prevent train movement when bridge unlocked" → Bridge Control

### Cross-Subsystem Requirements

Some system requirements involve multiple subsystems and should be decomposed into multiple subsystem requirements with clear interfaces:

**Example**: "The system shall prevent train movement when a movable bridge is not locked"
- **TC Requirement**: Traffic Control shall query Bridge Control for bridge lock status before granting Track Authority
- **BC Requirement**: Bridge Control shall provide bridge lock status via API interface
- **Interface**: RESTful API endpoint, 1Hz update rate

## Quality Standards

All subsystem requirements must meet these quality criteria:

1. **Completeness**: All aspects of parent requirement addressed
2. **Clarity**: Precise, unambiguous language
3. **Testability**: Observable behavior with pass/fail criteria
4. **Traceability**: Clear parent-child linkage to system requirements
5. **Domain Compliance** (when using CSX domain context):
   - Follow template format (SUBSYSTEM-TYPE-NUMBER)
   - Use glossary terms with correct capitalization
   - Include subsystem name in requirement statement

## Operational Context

### Railway Operations Fundamentals

Railway operations follow strict safety protocols:
- Trains operate under movement authorities granted by Dispatchers
- Signals communicate movement permissions to Train Crew
- Track Segments are protected by Control Points and signals
- Safety-critical operations (e.g., bridge movements, signal changes) require multiple verification steps

### Safety Considerations

When decomposing safety-related requirements:
- Maintain explicit failure modes and safety interlocks
- Preserve timing constraints for safety-critical operations
- Ensure traceability to regulatory standards (FRA, AAR, etc.)
- Include validation and error handling for all safety checks

## Common Requirement Patterns

### Configuration Parameters

Many features are controlled by Boolean Configuration Parameters:

**Pattern**: "The [Subsystem] shall allow Administrators to configure whether [feature] is enabled via the [PARAMETER_NAME] configuration parameter."

**Example**: "The Train Management Subsystem shall allow Administrators to configure whether the Departure Checklist is mandatory via the TM.DEPARTURE_CHECKLIST.MANDATORY parameter."

### Notification Events

System state changes trigger Notification Events:

**Pattern**: "The [Subsystem] shall generate a [EVENT_TYPE] Notification Event when [condition occurs]."

**Example**: "The Train Management Subsystem shall generate an Information Notification Event when an Authorized User completes the Departure Checklist."

### Data Validation

User inputs and external data require validation:

**Pattern**: "The [Subsystem] shall validate [data field] to ensure [validation rule], and display an Error Message if validation fails."

**Example**: "The Traffic Control Subsystem shall validate route requests to ensure no conflicting Track Authorities exist, and display an Error Message if conflicts are detected."
