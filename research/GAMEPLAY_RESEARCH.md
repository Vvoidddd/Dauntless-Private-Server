# GAMEPLAY RESEARCH

## Overview

This document catalogs the game systems we can infer from the client architecture and file structure.

---

## Player & Character System

### Character Model
**Confidence:** LIKELY

From architecture, players have:
- **Account** (unique identity, login)
- **Character(s)** (one or more playable characters)
- **Attributes:**
  - Name
  - Level (1-?)
  - Experience points
  - Position (world coordinates)
  - Rotation (facing direction)
  - Health
  - Status effects (buffs/debuffs)

### Character Progression
**Confidence:** LIKELY

Evidence:
- Progression system required
- Level-based gameplay expected
- Equipment mastery (weapon XP)
- Skills/perks system (implied)

**Inferred Systems:**
- Level cap (likely 50-100)
- Experience gain from hunts
- Skill points or ability unlocks
- Weapon/armor mastery progression

---

## Combat System

### Mechanics
**Confidence:** CONFIRMED (inferred from game nature)

Dauntless is an action hunting game:

**Player Combat:**
- Melee weapons (primary)
- Ranged weapons (secondary)
- Special abilities/ultimates
- Dodge/evade mechanic
- Health/stamina resource

**Behemoth Combat:**
- Large creature with phases (likely)
- Breakable parts (confirmable from assets)
- Attack patterns/telegraphs
- Enrage mechanic (inferred)
- Death animation

### Damage Calculation
**Confidence:** LIKELY

Server must calculate:
- Base damage from weapon
- Modifiers from armor
- Critical hits
- Status effects (burning, poison, etc.)
- Part damage multipliers
- Player vs. Behemoth damage
- Healing amounts

### Hit Detection
**Confidence:** LIKELY

Server validates:
- Attack is in range
- Target is valid
- Cooldown not active
- Stamina/resources available
- Collision/line-of-sight

---

## Hunting System

### Hunt Mechanics
**Confidence:** CONFIRMED

The core gameplay loop:
1. Party forms (2-4 players, likely)
2. Matchmaking finds hunt
3. Players spawn in arena
4. Behemoth spawns
5. Combat occurs
6. Behemoth dies OR time limit
7. Loot generated
8. Rewards awarded
9. Players return to lobby

### Hunt Instance
**Confidence:** CONFIRMED

Each hunt is isolated:
- Time limit (10-30 minutes, estimate)
- Player count (party size)
- Behemoth type (different hunt types)
- Difficulty scaling (easy, normal, hard, +)
- Environmental hazards (possibly)

### Behemoth Types
**Confidence:** LIKELY

From internal project name research, expected behemoths:
- Base monsters
- Elemental variants
- Boss variants
- Unknown count (20+?)

---

## World & Exploration

### Lobby World (Ramsgate)
**Confidence:** LIKELY

Persistent social hub:
- Player spawning area
- NPC vendors
- Quest givers
- Crafting stations
- Social gathering points

**Features:**
- Player-player interaction
- NPC dialogue
- Shop browsing
- Equipment preview
- Party formation

### Hunt Arenas
**Confidence:** CONFIRMED

Separate instanced spaces:
- One per active hunt
- Destroyed on hunt end
- Contains behemoth
- Environmental objects (loot, hazards)

---

## Inventory System

### Item Types
**Confidence:** LIKELY

**Equipment:**
- Weapons (primary and secondary)
- Armor (head, chest, gloves, legs)
- Accessories/trinkets (possibly)

**Consumables:**
- Potions (health, stamina)
- Buffs (temporary enhancements)
- Quest items

**Crafting Materials:**
- Behemoth parts (used for equipment)
- Common materials
- Rare materials

### Equipment Attributes
**Confidence:** LIKELY

Each piece has:
- Name and description
- Rarity (common, rare, epic, legendary)
- Defense/damage values
- Perks/abilities
- Level requirements
- Skill bonuses

### Loadout System
**Confidence:** LIKELY

Players configure:
- Primary weapon
- Secondary weapon (if applicable)
- Armor (4 pieces)
- Consumables
- Perks/skill selection

---

## Progression & Leveling

### Character Levels
**Confidence:** LIKELY

- Base level (affects stats)
- Level cap (unknown, 50-100 range?)
- Experience requirements per level (exp table)

### Weapon Mastery
**Confidence:** LIKELY

- Each weapon type levels separately
- Weapon XP gained from use
- Perks/abilities unlocked per level
- Mastery affects damage and abilities

### Battle Pass / Seasonal Content
**Confidence:** POSSIBLE

Modern MMO pattern:
- Seasonal progression track
- Daily/weekly challenges
- Reward tiers
- Battle pass currency

### Skill Trees
**Confidence:** POSSIBLE

Ability unlocking:
- Unlock at specific levels
- Spend points on nodes
- Trees per class (if multiple classes)
- Respec costs (possibly)

---

## Party System

### Party Formation
**Confidence:** CONFIRMED

- Leader creates party
- Invites other players
- Max size (likely 4)
- Shared matchmaking queue
- Party chat

### Party Benefits
**Confidence:** LIKELY

- Grouped hunts
- Shared rewards
- Social features
- Custom lobby

---

## Matchmaking System

### Queue Types
**Confidence:** LIKELY

- Solo queue (single player)
- Party queue (full party)
- Flexible queue (join partial party)

### Matching Algorithm
**Confidence:** UNKNOWN

EOS handles matchmaking. Parameters likely:
- Player level/skill
- Difficulty selection
- Party size matching
- Queue wait time

### Hunt Assignment
**Confidence:** LIKELY

When match found:
- Hunt type selected
- Behemoth selected
- Difficulty set
- Server assigned
- Players notified

---

## Loot System

### Drop Types
**Confidence:** LIKELY

**From Behemoth:**
- Equipment (weapons, armor)
- Materials (crafting)
- Consumables
- Cosmetics (possibly)

**Rarity Distribution:**
- Common (high drop rate)
- Uncommon (medium drop rate)
- Rare (low drop rate)
- Epic (very low)
- Legendary (extremely low)

### Loot Generation
**Confidence:** LIKELY

Server calculates:
- Drop table for behemoth
- Random item selection
- Quality/rarity roll
- Rarity modifiers (party size affects?)
- Distribute to party

### Reward Currency
**Confidence:** LIKELY

- Hunt currency (gained from hunts)
- Premium currency (cosmetics)
- Battle pass currency (seasonal)

---

## Crafting System

### Crafting Mechanics
**Confidence:** POSSIBLE

- Combine materials into equipment
- Upgrade existing equipment
- Disassemble/salvage items
- Special crafting recipes

### Crafting Resources
**Confidence:** LIKELY

- Behemoth parts (primary)
- Common materials (secondary)
- Currency (cost)

---

## Social Features

### Friends List
**Confidence:** LIKELY

EOS provides:
- Add friends
- See online status
- Send messages
- Join parties

### Chat System
**Confidence:** LIKELY

- Local chat (lobby)
- Party chat
- Whispers/DMs
- Chat commands

### Guilds / Clans
**Confidence:** POSSIBLE

- Guild creation
- Guild chat
- Guild perks
- Guild progression

---

## Cosmetics & Appearance

### Character Customization
**Confidence:** LIKELY

- Character name
- Appearance (possibly)
- Transmog/appearance system (possibly)

### Equipment Cosmetics
**Confidence:** POSSIBLE

- Weapon skins
- Armor skins
- Emotes
- Victory poses

---

## Unknown Gameplay Systems

| System | Status | Evidence Needed |
|--------|--------|-----------------|
| Class System | UNKNOWN | Multiple character classes? |
| Skill System | UNKNOWN | Ability/skill tree details? |
| PvP System | UNKNOWN | Player vs. Player content? |
| Guilds/Clans | UNKNOWN | Group features? |
| Trading | UNKNOWN | Player-to-player economy? |
| Housing | UNKNOWN | Personal spaces? |
| Cosmetics | UNKNOWN | Appearance customization? |
| Events | UNKNOWN | Seasonal events? |
| Raids | UNKNOWN | Large group hunts? |
| Covenants/Factions | UNKNOWN | Faction alignment? |
| Transmog | UNKNOWN | Appearance customization? |
| Enchanting | UNKNOWN | Equipment enhancement? |

---

## Behemoth Analysis

### Known Behemoths (from Dauntless lore)
**Confidence:** POSSIBLE (may not all be in this build)

Potential types:
- Skarn (earth/rock)
- Embermane (fire)
- Drask (frost)
- Shrowd (void/dark)
- Rezakiri (light)
- Valomyr (control/buff)
- Koshai (plant/nature)
- And many others...

### Behemoth Parts
**Confidence:** LIKELY

Each behemoth has breakable parts:
- Head
- Limbs/Legs
- Tail
- Back/Spine
- Wings (if applicable)
- Other specialized parts

**Part Properties:**
- Separate health bars
- Damage multipliers
- Unique material drops
- Optional breaks

---

## Player Statistics & Tracking

### Hunt Statistics
**Confidence:** LIKELY

Tracked per hunt:
- Damage dealt
- Damage taken
- Healing given
- Part breaks
- Time alive
- Deaths

### Account Statistics
**Confidence:** LIKELY

Tracked long-term:
- Total hunts
- Win rate
- Average damage
- Playtime
- Achievements
- Ranking (possibly)

---

## Equipment Balance

### Scaling System
**Confidence:** LIKELY

Stats scale by:
- Character level
- Weapon/armor level/rarity
- Perks/affixes
- Difficulty level

### Difficulty Scaling
**Confidence:** LIKELY

Hunt difficulty affects:
- Behemoth health
- Behemoth damage
- Behemoth speed
- Loot quality
- Experience multiplier

---

## Research Limitations

### Not Yet Analyzed
1. Asset pak contents (encrypted)
2. Binary game code (not decompiled)
3. Actual hunt duration/mechanics
4. Specific loot tables
5. Exact stat formulas
6. Specific class/ability definitions

### Cannot Determine Without
1. Asset extraction tools
2. Binary reverse engineering
3. Network packet analysis
4. Running game with debugging
5. Developer documentation (unlikely to exist for private)

---

## Recommendations for Implementation

### High Priority (Core Loop)
1. Player creation and login
2. Lobby world with NPC spawning
3. Basic hunt instance
4. Simple behemoth AI
5. Combat damage calculation
6. Loot generation
7. Reward persistence

### Medium Priority (Feature Complete)
1. Party system
2. Matchmaking
3. Multiple behemoth types
4. Equipment system
5. Progression/leveling
6. Multiple difficulties

### Low Priority (Polish)
1. Cosmetics
2. Social features
3. Advanced crafting
4. Guilds/clans
5. Events
6. Leaderboards

---

**Research Status:** ⚠️ Incomplete
**Confidence:** LIKELY (based on game nature, not confirmed code)
**Blocker:** None (can implement based on assumptions)
**Next Step:** Asset extraction if possible, or proceed with implementation based on assumptions

