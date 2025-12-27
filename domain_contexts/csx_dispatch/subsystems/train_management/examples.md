# Train Management Subsystem - Benchmark Examples

## UC-TM-040: Train Departure Checklist - Validated Example

This is a benchmark example of high-quality subsystem requirements decomposed from a system-level use case. This example demonstrates proper application of CSX Railway domain conventions, template format, and glossary usage.

### System-Level Requirement (from SRS)

**UC-TM-040: Train Departure Checklist**

The system shall provide a structured Departure Checklist that guides Train Crew through mandatory pre-departure verification steps, including Job Briefing, Work Locations, Train Consist verification, PTC checks, and Dispatcher Bulletin review. The checklist shall be configurable by Administrators and shall generate notification events upon completion.

### Decomposed Subsystem Requirements (Train Management)

---

**TM-FUNC-001: Display Departure Checklist**

The Train Management Subsystem shall display the Departure Checklist when an Authorized User initiates the departure process for an Active Train.

**Parent**: UC-TM-040
**Rationale**: Provides the primary user interface for the departure workflow
**Acceptance Criteria**:
- Checklist displayed within 2 seconds of user initiation
- All configured sections visible according to configuration parameters
- User can navigate between sections

---

**TM-FUNC-002: Display Job Briefing Section**

The Train Management Subsystem shall display the Job Briefing section as the first section of the Departure Checklist and provide an option for the Authorized User to acknowledge.

**Parent**: UC-TM-040
**Rationale**: Job Briefing is mandatory first step in departure workflow
**Acceptance Criteria**:
- Section displays before other checklist sections
- Acknowledgment button/checkbox is functional
- Acknowledgment state is persistent

---

**TM-FUNC-003: Display Work Locations Section**

The Train Management Subsystem shall display the Work Locations section of the Departure Checklist and allow the Authorized User to specify geographic areas where work will be performed.

**Parent**: UC-TM-040
**Rationale**: Required for tracking crew work areas and safety coordination
**Acceptance Criteria**:
- User can add/remove multiple Work Locations
- Work Locations are validated against known geographic database
- Invalid locations generate error messages

---

**TM-FUNC-004: Display Train Consist Verification Section**

The Train Management Subsystem shall display the Train Consist verification section showing the locomotive and car list for the Active Train and allow the Authorized User to confirm accuracy.

**Parent**: UC-TM-040
**Rationale**: Ensures Train Crew verifies physical consist matches system data
**Acceptance Criteria**:
- Complete Train Consist displayed (locomotives and cars in order)
- User can mark consist as verified
- Mismatches between expected and actual consist are highlightable

---

**TM-FUNC-005: Display PTC Status Section**

The Train Management Subsystem shall display the Positive Train Control status section showing PTC system readiness and allow the Authorized User to acknowledge PTC is operational.

**Parent**: UC-TM-040
**Rationale**: PTC verification is federally mandated safety requirement
**Acceptance Criteria**:
- PTC status retrieved from PTC BOS interface
- Status displays as Operational, Degraded, or Failed
- User cannot proceed if PTC status is Failed

---

**TM-FUNC-006: Display Dispatcher Bulletin Section**

The Train Management Subsystem shall display the Dispatcher Bulletin section showing current operational bulletins and allow the Authorized User to acknowledge review.

**Parent**: UC-TM-040
**Rationale**: Ensures crew awareness of track conditions, restrictions, and special instructions
**Acceptance Criteria**:
- All bulletins applicable to train route are displayed
- Bulletins are sorted by priority (critical first)
- User must acknowledge each bulletin individually

---

**TM-FUNC-007: Validate Checklist Completion**

The Train Management Subsystem shall validate that all required sections of the Departure Checklist have been acknowledged before allowing the checklist to be marked complete.

**Parent**: UC-TM-040
**Rationale**: Ensures all mandatory steps completed before train departure
**Acceptance Criteria**:
- All acknowledgments checked before completion allowed
- Error Message displayed if any section incomplete
- Completion button disabled until all sections acknowledged

---

**TM-FUNC-008: Generate Checklist Completion Event**

The Train Management Subsystem shall generate an Information Notification Event (EV-TM.DEPARTURE.CHECKLIST.COMPLETED) when an Authorized User successfully completes the Departure Checklist.

**Parent**: UC-TM-040
**Rationale**: Notifies other subsystems and external systems (MIS, PTC BOS) of departure readiness
**Acceptance Criteria**:
- Event generated immediately upon checklist completion
- Event includes train ID, timestamp, and completing user ID
- Event delivered to configured subscribers (TC, MIS, PTC BOS)

---

**TM-CONFIG-001: Job Briefing Visibility Configuration**

The Train Management Subsystem shall allow Administrators to configure whether the Job Briefing section is displayed in the Departure Checklist via the TM.CHECKLIST.JOB_BRIEFING.VISIBLE Boolean Configuration Parameter.

**Parent**: UC-TM-040
**Rationale**: Allows operational flexibility for different railway operating practices
**Acceptance Criteria**:
- Parameter accessible via configuration interface
- Default value is `true` (visible)
- Changes take effect on next checklist initiation

---

**TM-CONFIG-002: Work Locations Visibility Configuration**

The Train Management Subsystem shall allow Administrators to configure whether the Work Locations section is displayed in the Departure Checklist via the TM.CHECKLIST.WORK_LOCATIONS.VISIBLE Boolean Configuration Parameter.

**Parent**: UC-TM-040
**Rationale**: Some operations may not require work location tracking
**Acceptance Criteria**:
- Parameter accessible via configuration interface
- Default value is `true` (visible)
- Hidden sections do not block checklist completion

---

**TM-CONFIG-003: Checklist Mandatory Configuration**

The Train Management Subsystem shall allow Administrators to configure whether Departure Checklist completion is mandatory before train departure via the TM.DEPARTURE_CHECKLIST.MANDATORY Boolean Configuration Parameter.

**Parent**: UC-TM-040
**Rationale**: Provides operational flexibility while maintaining safety option
**Acceptance Criteria**:
- Parameter accessible via configuration interface
- Default value is `true` (mandatory)
- When false, checklist can be skipped with warning message

---

## Quality Analysis of UC-TM-040 Benchmark

This benchmark demonstrates high-quality subsystem requirements:

### ✅ Completeness (Score: 1.0)
- All aspects of system requirement addressed (Job Briefing, Work Locations, Train Consist, PTC, Dispatcher Bulletin, configuration, events)
- No missing functionality from parent requirement
- Traceability maintained for all subsystem requirements

### ✅ Clarity (Score: 1.0)
- Precise, unambiguous language
- Specific trigger conditions ("when an Authorized User...")
- Clear observable behavior ("shall display," "shall validate," "shall generate")
- No vague terms (all timing, thresholds specified)

### ✅ Testability (Score: 1.0)
- Every requirement has acceptance criteria
- Pass/fail conditions clearly defined
- Observable behavior specified
- Quantitative metrics where applicable (e.g., "within 2 seconds")

### ✅ Traceability (Score: 1.0)
- All requirements trace to UC-TM-040 parent
- Clear rationale explains decomposition intent
- Requirement IDs follow TM-{TYPE}-{NNN} convention

### ✅ Domain Compliance (Score: 0.98)
- Template format followed: "The Train Management Subsystem shall..."
- Glossary terms capitalized: Active Train, Authorized User, Departure Checklist, Job Briefing, Work Locations, Train Consist, Positive Train Control, PTC BOS, Dispatcher Bulletin, Information Notification Event, Boolean Configuration Parameter
- Configuration parameter naming: TM.CHECKLIST.{SECTION}.VISIBLE pattern
- Event naming: EV-TM.{FEATURE}.{ACTION} pattern
- Minor issue: One requirement could specify update frequency

### Overall Quality Score: 0.99

## Common Patterns Demonstrated

### 1. Checklist Section Pattern
Each checklist section follows consistent structure:
- Display section
- Allow user interaction (acknowledge, specify data, confirm)
- Validate input if applicable
- Track completion state

### 2. Configuration Parameter Pattern
Optional features controlled by Boolean Configuration Parameters:
- TM.CHECKLIST.{SECTION}.VISIBLE for section visibility
- TM.{FEATURE}.MANDATORY for feature requirement level
- Default values documented in acceptance criteria

### 3. Notification Event Pattern
Significant state changes generate events:
- Event naming: EV-TM.{FEATURE}.{ACTION}
- Event data includes context (train ID, user, timestamp)
- Events distributed to relevant subscribers

### 4. Validation Pattern
User inputs validated with clear error handling:
- Validation rules explicitly specified
- Error Messages displayed on validation failure
- Completion blocked until validation passes

## Usage Guidelines

When decomposing similar use cases:

1. **Identify checklist sections** from system requirement
2. **Create display requirements** for each section
3. **Add interaction requirements** (acknowledge, input data)
4. **Create validation requirements** for data quality
5. **Add completion requirements** to tie workflow together
6. **Generate event requirements** for external notification
7. **Add configuration requirements** for operational flexibility
8. **Ensure all requirements**:
   - Use correct TM-{TYPE}-{NNN} format
   - Start with "The Train Management Subsystem shall..."
   - Capitalize glossary terms
   - Include acceptance criteria
   - Trace to parent (UC-TM-040)
