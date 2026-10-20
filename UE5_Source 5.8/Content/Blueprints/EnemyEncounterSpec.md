# Enemy Encounter Specification

This document specifies enemy placement per chapter, based on the Bradygames
guide bestiary and PS2 disc analysis.

## Chapter 1: Abandoned Castle
- **Skeleton** (3): Entrance Hall - Basic undead, weak to Holy
- **Zombie** (2): Entrance Hall - Slow, weak to Fire
- **Ghoul** (2): Chapel - Undead, weak to Holy
- **Sentinel Knight** (1): Boss Arena - Chapter 1 boss, weak to Holy/Dark

## Chapter 2: Baljhet Mountains
- **Harpy** (4): Mountain Pass - Flying, weak to Ice
- **Bat** (6): Cave Entrance - Flying, weak to Ice
- **Mountain Beast** (2): Summit - Ground beast, weak to Fire
- **Sky Drake** (1): Boss Arena - Chapter 2 boss, weak to Ice/Wind

## Chapter 3: Garibaldi Temple
- **Temple Guardian** (3): Nave - Holy guardian, weak to Dark
- **Cultist** (4): Crypt - Human enemy, weak to Light
- **Dark Priest** (2): Bell Tower - Dark magic user, weak to Light
- **High Inquisitor** (1): Boss Arena - Chapter 3 boss, weak to Light/Dark

## Chapter 4: Mortvia Aqueduct
- **Water Creature** (3): Water Chamber - Water enemy, weak to Lightning
- **Aqueduct Guard** (2): Bridge Crossing - Guard enemy, weak to Fire/Iron
- **Aqueduct Sentinel** (1): Boss Arena - Chapter 4 boss, weak to Fire/Iron

## Chapter 5: Forest of Jigramunt
- **Forest Stalker** (4): Forest Edge - Nature enemy, weak to Fire
- **Nature Spirit** (3): Deep Forest - Spirit enemy, weak to Fire/Poison
- **Forest Warden** (1): Boss Arena - Chapter 5 boss, weak to Fire/Poison

## Chapter 6: Cordova Town
- **Town Guard** (5): Town Square - Human guard, weak to Slash/Blunt
- **Citizen** (8): Town Square - Non-combat NPC
- **Town Captain** (1): Boss Arena - Chapter 6 boss, weak to Slash/Blunt

## Chapter 7: Eneomaos Machine Tower
- **Clockwork Soldier** (4): Gear Chamber - Mechanical, weak to Fire/Lightning
- **Mechanical Trap** (6): Steam Room - Trap enemy, weak to Fire/Lightning
- **Tower Automaton** (1): Boss Arena - Chapter 7 boss, weak to Fire/Lightning

## Chapter 8: Aiolon Ruins
- **Ruin Guardian** (3): Ruin Entrance - Ancient construct, weak to Light/Dark
- **Ancient Construct** (2): Sunken Courtyard - Ancient construct, weak to Light/Dark
- **Ruin Sentinel** (1): Boss Arena - Chapter 8 boss, weak to Light/Dark

## Chapter 9: Infinite Corridor
- **Corridor Phantom** (5): Corridor Loop - Phantom enemy, weak to Light/Dark
- **Surreal Entity** (3): Mirror Chamber - Surreal enemy, weak to Light/Dark
- **Mirror Entity** (1): Boss Arena - Chapter 9 boss, weak to Light/Dark

## Chapter 10: Dracula's Castle
- **Castle Elite** (6): Grand Hall - Elite enemy, weak to Dark/Light
- **Final Boss** (1): Throne Room - Chapter 10 boss, no specific weakness

## Steal System
- Enemies marked `CanBeStolen = true` can have items stolen
- Steal window appears when enemy turns purple (timing varies per enemy)
- Successful steal yields the listed `StealItem`

## Respawn Behavior
- Enemies respawn when player leaves and re-enters a room
- Cleared rooms remain unlocked (red bars drop)
- Save rooms are always safe zones (no enemies)