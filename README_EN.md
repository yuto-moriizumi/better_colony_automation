# Better Colony Automation (BCA) - Colony Automation Overhaul (4.3)

https://github.com/StellarWarp/better_colony_automation/blob/master/README_EN.md

Since Paradox never fixed planetary automation bugs after the 4.0 update, late-game automation has been frustrating. This mod fully reworks vanilla planetary automation, fixes many issues and adds improved controls.

Feedback / Contact: QQ 153870310

Quick link: [Stellar AI Compatibility Mod](https://steamcommunity.com/sharedfiles/filedetails/?id=3674208064)

## Quick Start

1. **Global Settings**: Set the **Mineral Reserve Policy** in the \[Policies\] menu.
2. **Enable Automation**: Toggle \[Planetary Automation\] on the planet UI and configure automation categories.
3. **Hybrid Planning & District Build Settings**: A planet UI is provided to configure hybrid planning and district build preferences.
4. **Misc Settings**: Some options (e.g., Revitalization spamming) remain controlled via Planetary Decisions.

## Overview

### Construction Features

#### Smart Construction Logic
- **Build on Demand**: Construction triggers only when there are insufficient jobs and no other ongoing construction. Can be bypassed by decisions to force early builds.
- **Special Buildings**: Population growth buildings (Clinics, Clone Vats, Revitalization Centers, Gene Clinics) and beneficial auxiliary buildings will be built when jobs are available.
- **Mineral Reserve**: Added a national **Mineral Reserve Policy**. If minerals fall below the threshold, automation pauses to prevent economic collapse.

#### Expanded Automation Options
- **Medical**: Supports basic clinics, gene clinics, and cyto-revitalization centers.
- **Unity Monuments**: Automatically builds and upgrades unity-producing monuments.
- **Resource Silos**: Automatically builds resource silos.
- **Pop Assembly Management**: Non-machine empires can independently manage Robot Assembly Plant construction.
- Removed the vanilla "Avoid Deficit" option because it often blocks construction.

#### Hybrid Planning Management
- Previous hybrid planet types were removed; a GUI now allows hybrid planning settings.
- Note: Secondary hybrid settings may not match actual specialized slots on some special planets (Ecumenopoleis, Ring Worlds, Hive, Machine Worlds). Manual adjustment may be required.

#### Building Construction
- Priority is given to auxiliary buildings (Clinics, Clone Vats, Monuments, Production Centers) to boost planet efficiency. Main production buildings are built after auxiliaries.
- Greatly improved vanilla logic for many planet types and fixed rare resource building logic.
- **Silos**: Default builds only one Silo. GUI can lift the limit and will auto-build basic resource districts to house them.
- **Revitalization Centers**: Default builds only one; a Planetary Decision enables spamming mode.

#### District Construction
- GUI-configurable build plans; the mod will automatically build districts per plan.
- For basic `resource` worlds (Energy/Mining/Farming), the mod dynamically balances City vs Resource district ratio for optimal output.
- Specialized worlds (Ecumenopoleis/Ring/Hive/Machine) build one of each non-specialized district first to unlock buildings.
- District replacement management is available via UI.

### Demolition & Cleanup

#### Building Demolition
- **Mismatched Function Removal**: If slots are full and buildings don't match the planet's specialization, the mod will remove them (e.g., factory removed on a research planet to make room for a lab).
- **Pop Assembly Cleanup**: When a planet is completely full (no housing, no jobs, no slots), assembly buildings will be removed to free space for higher-tier production. This is toggleable by policy.
- **Freeing Space by Removing Job-Only Buildings**: The mod can remove buildings that only provide jobs (like basic research labs) to free slots for higher-tier buildings when needed.

#### District Demolition
- In automated district management, the mod will remove and rebuild districts to maximize output.
- **Arcology Candidate**: Enabling the Arcology candidate decision will remove basic resource districts when preparing for the project.

#### Zone (specialization) Demolition
- Any zone not included in the GUI planning will be removed when managing specializations.

### Advanced Build Plans
- Supports advanced planning for `resource` planets:
  1. **Optimal Build**: Chooses buildings/districts/zones that maximize output in the shortest time.
  2. **District Replacement**: If replacing a district increases output, the mod will perform demolition & construction.
- District management for advanced plans is toggleable via GUI.

### Other
- **Arcology Candidate Decision**: Prepares a planet for the Arcology Project by removing resource districts and notifies the player when ready.
- **De-urbanization Decision**: For testing; removes all buildings and districts.
- **Policy Control**: Global policies to toggle demolition tiers and other behaviors.

## Compatibility

- **Building Demolition** previously modified vanilla building files and could conflict with mods changing the same files. The mod has been rewritten so automatic demolition no longer depends on modifying vanilla building files, reducing conflicts.
- Mods that change AI behavior may conflict; load order recommendations may apply.
- Currently supports only vanilla buildings and districts.

## Compatible Mods

- [Stellar AI Compatibility Mod](https://steamcommunity.com/sharedfiles/filedetails/?id=3674208064)

## Changelog

红尘渡者 previous - v0.1

哇噗 **26-01-18 - v0.2**
- Construction now triggers only on job shortage (unless bypassed by decision).
- Added Mineral Reserve Policy.
- Optimized Medical logic (spamming mode vs. single-building limit).
- Refined Trade and Research automation; standard research is now "semi-automatic."
- Added support for Tier 1 resource construction on Volcanic worlds.
- Added "De-urbanization" decision.

哇噗 **26-01-20 - v0.3**
- **Automatic Demolition**: Added auto-removal for buildings, districts, and zones.
- Fixed district priority conflicts.
- Optimized automation categories; Silos and FE Clinics now default to smarter logic.
- Improved support for Wilderness, Penal, Resort, Slave, Hive, and Machine worlds.
- Fixed rare resource building logic.

哇噗 **26-01-21 - v0.4**
- Added Arcology Project Candidate decision.
- Added Robot Assembly automation toggle; fixed Medical UI issues.
- Removed the vanilla "Avoid Deficit" option.
- Improved Silo/FE Clinic construction logic to avoid "spamming" unless intended.
- Fixed Trade zone conflicts on Hive/Machine worlds.
- General priority and bug fixes for agriculture zones.

哇噗 **26-01-21 - v0.4.1**
- Gene Clinics will build when jobs are available.

哇噗 **26-01-24 - v0.5**
- Intro & Updates: Added a welcome window on game start and update log notifications for existing saves.
- Basic Resource Logic: Reworked Mining, Energy, and Farming logic to fix conflicts between City and Resource districts.
- Dynamic Balancing: Mod now maintains optimal ratio of City to Resource districts on basic `resource` worlds.

哇噗 **26-01-24 - v0.5.1**
- Fixed energy output calculation error that caused city district ratio to be too low.
- Fixed issue where boost zones were not removed when switching between basic `resource` designations.

哇噗 **26-01-25 - v0.5.2**
- Fixed and improved rare resource building automation logic: After building an Ancient Refinery, no other rare resource buildings will be constructed.
- Fixed issue where Robot Assembly options were still displayed when robots were disabled or Gene Ascension was chosen.

哇噗 **26-01-25 - v0.5.3**
- Fixed a naming error that caused energy calculation issues.

哇噗 **26-01-25 - v0.5.4**
- Added decisions to adjust rare resource building behavior.
- Improved decision texts and icons for readability.
- Fixed pop assembly building being constructed under removal conditions.

哇噗 **26-01-25 - v0.5.5**
- Adjusted decision texts and icons; fixed toggle inconsistencies.
- Rare resource construction adjustments: rare resource decisions now show only on industrial planets; for `resource` districts, rare resource buildings are prioritized as appropriate.
- Fixed some buildings missing Mineral Reserve constraints.

哇噗 **26-02-20 - v1.0.0**
- Added GUI for hybrid planning and district build settings; removed old hybrid planet types.
- Hybrid-planned planets can auto-build/replace districts and build corresponding buildings.
- Auxiliary/gain buildings will be built when jobs are available.
- Rewrote basic `resource` planet building logic; now selects optimal build choices based on benefit and supports nearly all planet types.

哇噗 **26-02-27 - v1.2.0**
- Added Job Reserve Policy: set a reserved jobs number; building triggers when available jobs fall below it.
- UI for district replacement management added.
- Finer demolition controls: buildings, districts, and zone demolition can be toggled independently.
- Fixed incorrect district construction bugs and several other issues.

哇噗 **26-02-28 - v1.3**
- Rewrote automatic building demolition so it no longer depends on modifying vanilla building files — reduces conflicts with mods that change buildings.
- Added support for demolishing job-only buildings (e.g., basic research labs) to free slots for higher-tier buildings.
- Fixed cases where zone construction could stop unexpectedly.
- Adjusted construction priorities: auxiliary/gain buildings build when there's spare job capacity; job-only buildings are deferred until districts are full.

---

## Contribute

This mod currently supports common vanilla buildings and districts. To add support for other modded buildings/districts, contribute via:

https://github.com/StellarWarp/better_colony_automation

This project is licensed under GNU GPLv3.
