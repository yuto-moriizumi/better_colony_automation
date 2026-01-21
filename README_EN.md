# Better Colony Automation (BCA) - Colony Automation Overhaul

Since Paradox has yet to fix the broken planetary automation bugs following the 4.0 update, the mid-to-late game experience has become increasingly frustrating. I decided to take matters into my own hands and fix these issues myself.

## Quick Start

1. **Global Settings**: Set the **Mineral Reserve Policy** in [Policies].
2. **Enable Automation**: Toggle [Planetary Automation] in the planet interface and configure the relevant automation categories.
3. **Fine-tuning**: Use [Planetary Decisions] to enable specific behaviors like **Build extra districts for Silos** or **Arcology Project Candidate** (only visible when eligible).

## Overview

### Construction Features

#### Smart Construction Logic
- **Build on Demand**: Construction is only triggered when there are insufficient jobs (`requires_more_job`) and no other ongoing construction. You can bypass this via Planetary Decisions to force early construction.
- **Special Buildings**: Population growth-related buildings (Clinics, Clone Vats, Revitalization Centers, Gene Clinics) will also be constructed when there are available jobs.
- **Mineral Reserve**: Added a national **Mineral Reserve Policy**. You can set a threshold; if minerals fall below this limit, automation will pause to prevent economic collapse.

#### Enhanced Automation Options
- **Medical**: Supports construction of Medical Clinics, Gene Clinics, and Cyto-Revitalization Centers.
- **Cultural Monuments**: Automatically builds and upgrades Unity-producing monument buildings.
- **Resource Silos**: Automatically builds Resource Silos.
- **Pop Assembly Management**: Non-machine empires can independently manage the automatic construction of Robot Assembly Plants.
- **Optimized UI**: Removed the "Avoid Deficit" option from vanilla, which often froze construction due to scripting edge cases.

#### New Designations
- Added specialized research worlds (Physics/Society/Engineering) and hybrid specializations like "Research + Trade" or "Industry + Trade."
- *Note: Hybrid types are currently in a "beta" state, primarily intended for Ecumenopoleis, Ring Worlds, Hive Worlds, and Machine Worlds. Trade hybrid types do not currently build trade buildings; this is planned for a future update.*

#### Building Construction
- **Priority Logic**: Auxiliary buildings (Clinics, Clone Vats, Monuments, Production Centers) are prioritized to boost planetary efficiency. Main production buildings are constructed after these are completed.
- Heavily improved vanilla logic for various planet types and fixed rare resource building construction logic.
- **Silo Construction**: By default, only one Silo is built. This limit can be lifted via Planetary Decision, which will also automatically build basic resource districts to house them.
- **Revitalization Centers**: By default, only one is built. Use Planetary Decisions to allow "Spamming" mode.

#### District Construction
- **Priority Optimization**: Prioritizes basic resource districts on specialized worlds (Energy/Mining/Farming) to resolve priority conflicts.
- **Specialized Worlds**: On Ecus/Ring Worlds/Hive/Machine worlds, the mod builds one of each non-specialized district first to unlock building slots.

### Demolition & Cleanup

#### Building Demolition
- **Mismatched Designation Removal**: When building slots are full and a building does not match the planet's current specialization, it will be automatically removed (e.g., removing a factory on a research world to make room for a lab).
- **Pop Assembly Cleanup**: When a planet is completely full (no housing, no jobs, no slots), assembly buildings (Robot Plants/Clone Vats) are removed to make room for higher-tier production. This can be toggled via policy.

#### District Demolition
- **Basic Resource Cleanup**: Enabling the "Arcology Project Candidate" decision will remove all basic resource districts (Energy/Mining/Farming) when no slots are left, paving the way for the project.
- **Housing Optimization**: Automatically removes excess city districts if the planet has extreme surplus housing and needs space for other districts.

#### Specialization (Zone) Demolition
- When manually changing a planet's designation (e.g., Research to Trade), the mod automatically removes obsolete specializations (Zones). Switching between research sub-types (e.g., Society to Physics) does not trigger removal.

### Others

- **Arcology Candidate Decision**: A planetary decision that automates the cleanup of Tier 1 districts and notifies the player when the planet is ready for the Arcology Project.
- **De-urbanization Decision**: Primarily used for testing; removes all buildings and districts. Not required for normal planetary transitions.
- **Policy Control**: Globally toggle different tiers of automatic demolition via the Policy menu.

## Compatibility

- **Building Demolition**: This feature modifies vanilla building files. It may conflict with mods that change the same buildings. If you prefer to keep other building mods, place BCA higher in the load order (though you will lose auto-demolition).
- **AI Mods**: Mods modifying AI behavior may conflict. It is recommended to place BCA at the bottom of your load order.
- **Supported Content**: Currently only supports vanilla buildings and districts.

## Changelog

红尘渡者 **previous - v0.1**

哇噗 **26-01-18 - v0.2**
- Construction now triggers only on job shortage (unless bypassed by decision).
- Added Mineral Reserve Policy.
- Optimized Medical logic (spamming mode vs. single-building limit).
- Refined Trade and Research automation; standard research is now "semi-automatic."
- Added support for Tier 1 resource construction on Volcanic worlds.
- Added "De-urbanization" decision.

哇噗 **26-01-20 - v0.3**：
- **Automatic Demolition**: Added auto-removal for buildings, districts, and zones.
- Fixed district priority conflicts.
- Optimized automation categories; Silos and FE Clinics now default to smarter logic.
- Improved support for Wilderness, Penal, Resort, Slave, Hive, and Machine worlds.
- Fixed rare resource building logic.

哇噗 **26-01-21 - v0.4**：
- Added Arcology Project Candidate decision.
- Added Robot Assembly automation toggle; fixed Medical UI issues.
- Removed the vanilla "Avoid Deficit" option.
- Improved Silo/FE Clinic construction logic to avoid "spamming" unless intended.
- Fixed Trade specialization conflicts on Hive/Machine worlds.
- General priority and bug fixes for agriculture specializations.
