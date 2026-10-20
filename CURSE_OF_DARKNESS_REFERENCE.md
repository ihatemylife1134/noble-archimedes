# Castlevania: Curse of Darkness — Game Reference
**Asset Generation · Story · Level Building**

Synthesized from a full-playthrough video series, community game guides (StrategyWiki, Castlevania Fandom/Archives, RPG Classics, Almar's Guides), and the documented structure of the BradyGames/official strategy guides. This is a factual **design reference** for an original fan recreation — no game code, models, textures, audio, or video are reproduced here.

## 1. Fact sheet
| Field | Value |
|---|---|
| Title | Castlevania: Curse of Darkness |
| JP title | Akumajō Dracula: Yami no Juin ("Demon Castle Dracula: Curse of Darkness") |
| Developer / Publisher | Konami |
| Director | Takashi Takeda |
| Producer / Writer | Koji Igarashi |
| Programmer | Shuichi Hirohara |
| Artist | Ayami Kojima |
| Composers | Michiru Yamane, Yuka Watanabe |
| Platforms | PlayStation 2, Xbox |
| Release | NA Nov 1, 2005 · JP Nov 24, 2005 (PS2) · EU Feb 17, 2006 |
| Genre | 3D action RPG / hack-and-slash (Metroidvania-style connected world) |
| Setting / chronology | Year 1479, three years after Castlevania III: Dracula's Curse (1476); direct sequel |
| Engine | Reuses the Castlevania: Lament of Innocence (2003) engine; 4th 3D Castlevania |
| Protagonist | Hector (a Devil Forgemaster) |
| Modes | Single player; bonus **Trevor Mode**; **Crazy (Hard) Mode** |

## 2. Story

### 2.1 Premise & setting
Three years after Trevor Belmont slew Dracula, the Count's curse still poisons Wallachia, spreading plague, mob violence, heresy, and monster outbreaks. **Devil Forgemasters** — humans who forge living weapons and "Innocent Devils" — exist on the margins. **Hector**, once Dracula's Forgemaster, betrayed the Count, gave up his powers, and settled down to marry **Rosaly**. When his rival Forgemaster **Isaac** (who stayed loyal to Dracula) has Rosaly burned as a witch, Hector reclaims his powers to hunt Isaac — and is unwittingly steered toward resurrecting Dracula.

### 2.2 Full synopsis (act-by-act)
Hector reaches the **Abandoned Castle** to confront Isaac. Isaac mocks Hector's humanity and dares him to regain his powers. Hector accepts and the pursuit begins. Inside he meets **Zead**, a kindly priest who always points him toward Isaac, and forges his first **Fairy-type** Innocent Devil.

In the **Baljhet Mountains** he meets **Julia Laforeze**, an exiled witch running a small shop who also offers to hold unused Innocent Devils. He defeats a **Wyvern** and forges a **Battle-type** companion.

At the **Garibaldi Temple** he meets **Saint Germain**, who urges him to abandon his revenge, and crosses blades for the first time with **Trevor Belmont**, who distrusts all Forgemasters. The fight teaches his Battle-type **Brute Force**, opening the way onward.

Through the **Mortvia Aqueduct** (a **Bird-type** joins him) and the **Forest of Jigramunt** (he defeats the **Minotaurus** and spies open hostility between Zead and Saint Germain), he reaches **Cordova Town**. There he forges a **Mage-type**, learns Julia is Isaac's sister, and fights **Isaac** without finishing him.

In the **Eneomaos Machine Tower** he forges a **Devil-type**. Saint Germain challenges Hector directly, then relents, speaking of a "new destiny." In the **Aiolon Ruins**, Hector finds Isaac and Trevor already fighting; Isaac flees, and Trevor finally agrees to collaborate.

To reach Isaac, Trevor uses his own blood to open the **Infinite Corridor**. At its end Hector defeats **Dullahan**, but the battle's energy unseals Dracula's Castle — Isaac's plan all along — and Isaac stabs Trevor and leaves him for dead. Julia tends to Trevor.

Inside **Dracula's Castle**, Hector defeats **Isaac**. About to kill him in rage, he remembers Julia's warning that the curse feeds on hatred — too late. Zead reveals he is **Death**, and that the Forgemasters' duel was staged so a hate-filled, blood-stained Hector could become Dracula's vessel. Hector rejects the curse, overcomes **Death**, defeats a still-weak **Dracula**, and uses his Devil Forgery to break the curse forever. Julia rescues him and they begin a new life; Saint Germain departs to the far future.

### 2.3 Story beat → area map
| # | Area | Story beat | Boss |
|---|---|---|---|
| 1 | Abandoned Castle | Confront Isaac; meet Zead; forge Fairy | Crazy Armor |
| 2 | Baljhet Mountains | Meet Julia; forge Battle | Wyvern |
| 3 | Garibaldi Temple | Meet Saint Germain; first Trevor fight; Brute Force | Trevor (Lv.16) |
| 4 | Mortvia Aqueduct | Forge Bird; cross water | Skeleton Diver |
| 5 | Forest of Jigramunt | Witness Zead vs. Germain rivalry | Minotaurus |
| 6 | Cordova Town | Julia = Isaac's sister; first Isaac fight | Isaac (Lv.34) |
| 7 | Eneomaos Machine Tower | Forge Devil; Germain tests Hector | Saint Germain |
| 8 | Aiolon Ruins | Isaac vs. Trevor; Trevor allies with Hector | — |
| 9 | Abandoned Castle (return) | Trevor rematch; opens Infinite Corridor | Trevor (Lv.40) |
| 10 | Infinite Corridor | Dullahan guardian; castle unsealed; Trevor stabbed | Dullahan |
| 11 | Dracula's Castle | Kill Isaac; Zead = Death; break the curse | Isaac → Death → Dracula |

Optional bosses: **Legion** and **Nuculais** (Garibaldi Temple). Trevor Mode: **Trevor Doppelganger** at Lv.16 and Lv.40.

### 2.4 Characters
- **Hector** — protagonist. Devil Forgemaster who abandoned Dracula, lost Rosaly to Isaac's scheme, and reclaims his powers for revenge. Wields every melee weapon class and summons Innocent Devils.
- **Trevor C. Belmont** — the hunter who slew Dracula in 1476. Distrusts Hector at first, then allies with him; opens the Infinite Corridor with his blood. Bonus playable mode (Vampire Killer whip + classic subweapons: knife, axe, holy water, cross, stopwatch).
- **Isaac** — antagonist Forgemaster loyal to Dracula; orchestrates Rosaly's death and the resurrection plot. Forges his own devils: **Abel** (his "The End"), **Iytei**, **Rasetz**. Becomes Dracula's vessel.
- **Zead / Death** — Death disguised as a kindly priest; guides Hector to ensure the curse transfers to him.
- **Dracula** — resurrected in the finale; defeated while still weak.
- **Julia Laforeze** — witch, Isaac's sister, resembles Rosaly; runs a shop and stores unused Innocent Devils; warns Hector against the curse.
- **Saint Germain** — gentleman time-traveler maintaining "the flow of a greater will"; opposes Zead; runs a shop and tests Hector. Based on the real Count of St. Germain.
- **Rosaly** — Hector's wife/fiancée, burned at the stake before the game (flashback/manga only).

## 3. Core systems (design constraints for assets & levels)

### 3.1 Combat
- **Attack** builds standard combos; **Finish** ends them in a heavier finishing attack that varies per weapon and combo length. Stronger weapons unlock longer combo chains.
- **Guard** blocks; **Evade/Quick Step** grants brief invincibility; precise timing enables a **Perfect Guard**.
- **Chain Attack**: with a Battle- or Devil-type ID, after a combo's final hit ("Chain!" flash) press attack to trigger a timed team attack.
- **Steal**: when an enemy shows a **purple lock** (specific animation windows), press the steal/guard input at the right moment to take its rare item instead of relying on a drop.

### 3.2 Weapon classes
One-handed swords · two-handed swords · one-handed axes · two-handed axes · spears · knuckles/brass knuckles · **special** weapons (tonfas, gatling guns, etc.). Each class has distinct combo sets. Trevor adds **whips** and **sub-weapons**.

### 3.3 Elements / damage
Fire · Ice · Thunder · Earth · Holy/Light · Dark/Curse, plus physical (slash/pierce/blunt). Enemies have both weaknesses and tolerances, driving Innocent Devil spell selection.

### 3.4 Devil Forgery & Innocent Devils
Six types (Fairy, Battle, Bird, Mage, Devil, Pumpkin). Innocent Devils are summoned allies with their own **Heart** pool that doubles as health and ability fuel. Modes: **Auto** (free skill use), **Command** (Triangle-trigger), **Guard** (block). Forms change by collecting **Evo Crystals** (five colors tied to the five weapon classes). Passive stat transfer: Fairy→Luck · Battle→Strength · Bird→Constitution · Mage→STR/CON · Devil→STR/CON/LCK · Pumpkin→large all.

### 3.5 Economy & progression
**Gold** (shops) · **Hearts** (ID fuel) · **Evo Crystals** (evolution) · **items** (recovery/status) · **materials** (forging). **Combine/Forge** crafts weapons, armor, accessories from 40 materials (§5.6). **Save rooms** full-heal/save, **warp chairs** allow area return, the **map** tracks per-area completion %, and **Memorial Tickets** are rare findables.

## 4. Innocent Devil compendium
Notation: *Form* — abilities (→ evolves-to + crystal cost).

### 4.1 Fairy-Type (found: Abandoned Castle 2F) — healer, cannot be hit
- **Infant Fairy** — Unlock, Heal Lv.1 (→ Leaffle 40 Red/Yellow · Herbest 40 Blue/Green/White)
- **Leaffle** — Time Heal, Poison Powder (→ Honey Bee 70 Blue/Yellow/White · Killer Bee 70 Red/Green)
- **Herbest** — Antidote, Heal Lv.2 (→ Killer Bee · Hornet 70 Blue/Yellow/White)
- **Honey Bee** — Healing Field (→ Proboscis Fairy 90 White · Tiramisu 90 Red/Blue/Green/Yellow)
- **Killer Bee** — Heal Lv.3, Curse Breaker (→ Tiramisu 90 Blue/White · Tiara 90 Red/Green/Yellow)
- **Hornet** — Stone Breaker, Lucky Slot (→ Tiara · Comet Star 90 Yellow/White)
- **Proboscis Fairy** — Press It & See, Just a Little, Skull Bomb, Refresh
- **Tiramisu** — Gold Heal, Decipher, Invincible Vase
- **Tiara** — Healing Drop, Crystal Skull
- **Comet Star** — Twinkle Shot, Lullaby, Heal Lv.4

### 4.2 Battle-Type (found: Baljhet Mountains) — bruiser
- **Magmard** — Aura Blast, Brute Force (→ Speed Mail 40 Blue/Yellow/Green · Golem 40 Red/White)
- **Speed Mail** — Heavenly Sword (→ Rasetz 90 Blue/White · Corpsey 90 Red/Green/Yellow)
- **Golem** — Hip Press, Hip Press Lv.2 (→ Iytei 90 White · Juggernaut 70 "all but White")
- **Iytei** — Shoulder Ride, Ultra Scream (final)
- **Juggernaut** — Homing Eye, Brute Force Lv.2 (→ Ironside 90 Blue/White · Liquid Golem 90 Red/Green/Yellow)
- **Rasetz** — Grand Wave, Glow Soul (final)
- **Corpsey** — Grand Wave, Bone Storm (final)
- **Ironside** — Chain Punch, Machine Gun Shot (final)
- **Liquid Golem** — Mercury Sphere, Magma Mode (final)

### 4.3 Bird-Type (found: Mortvia Aqueduct) — flight/glide
- **Crow** — Glide (→ Goldfinch 40 Green/Yellow/White · Skull Wing 40 Red/Blue)
- **Goldfinch** — Caltrops (→ Khaos 70 any)
- **Skull Wing** — Carpet Bombs, Bone Shot (→ Phoenix 90 Green/Yellow/White · Wingosaurus 70 Red/Blue)
- **Khaos** — Sphere of Darkness (→ Blagsdeath 90 Red/Green/Yellow · Gargoyle 90 Blue/White)
- **Phoenix** — Big Bang, Fire Bird (final)
- **Wingosaurus** — Long Glide, Deadly Absorb (→ Indigo 90 Green/Yellow · Crimson 90 Red/Blue/White)
- **Blagsdeath** — Beat Progress (final)
- **Gargoyle** — Conflict Fall, Force Cannon (final)
- **Indigo** — Icicle Shot, Blizzard Breath (final)
- **Crimson** — Ignition Blow, Flame Breath (final)

### 4.4 Mage-Type (found: Cordova Town) — elemental magic; Time Stop / Purify
- **Wood Rod** — Time Stop, Lightning Strike (→ Scissor Rod 40 Red/Yellow · Talon Rod 40 Blue/Green/White)
- **Scissor Rod** — Floating B, Sorcery Flame (→ Nautilus Rod 70 Green/Yellow/White · Ogre Rod 70 Red/Blue)
- **Talon Rod** — Circle Scissors, Freeze (→ Ogre Rod 70 Red/Blue/White · Goat Head 70 Green/Yellow)
- **Nautilus Rod** — Purify, Satellite B (→ Eyeball Rod 90 Blue/Green · Embryo Rod 90 Red/Yellow/White)
- **Ogre Rod** — Agnea, Synchron Saucer B (→ Embryo Rod 90 Red/Green · Crystal Rod 90 Blue/Yellow/White)
- **Goat Head** — Argent B, Salamander (→ Crystal Rod 90 "all but White" · Twinkle Rod 90 White)
- **Eyeball Rod** — Tension Boost, Homing (final)
- **Embryo Rod** — Explosion B, Demonic Disaster (final)
- **Crystal Rod** — Shield, Meteo (final)
- **Twinkle Rod** — Twinkle Star, Dancing Stars (final)

### 4.5 Devil-Type (found: Eneomaos Machine Tower) — linear; Magic Circle
- **Gale** — Magic Circle (→ Brow 200 any)
- **Brow** — M. Circle Scissors, Needle Magic Circle (→ The End 100 with the Chauve-souris spear)
- **The End** — Exploding M. Circle (final)

### 4.6 Pumpkin-Type (secret/optional; base form via Pumpkin Mace ritual) — stat stick
- **Pumpkin** — Pose (→ Queen 70 Yellow · Bloody 70 Blue · Tiny King 70 Red · Clown Nose 70 White · New Deli 70 Green)
- **Bloody** → **Cursed Pumpkin** (100 with Death's Scythe) · **Tiny King** → **Whimsical Angel** (100 with Short Sword) · **Clown Nose** → **Genius Chef** (100 with Frying Pan). All evolutions are cosmetic.

## 5. Asset generation reference
Counts are "distinct models/rigs to author" for an original recreation.

### 5.1 Characters (rigged/skinned)
Hector · Trevor Belmont (ally + playable) · Isaac (+ his 3 separate devils Abel/Iytei/Rasetz) · Julia Laforeze · Zead/Death (two forms) · Saint Germain · Rosaly (flashback) · Dracula (humanoid final form).

### 5.2 Innocent Devil models — 51 forms
Fairy 10 · Battle 9 · Bird 10 · Mage 10 · Devil 3 · Pumpkin 9. Each needs: mesh, rig, silhouette/palette, the signature "pink crystal" marker, idle/fly/walk/attack/skill animations, and a petrified "statue" state for its acquisition room.

### 5.3 Enemy bestiary — 51 families (plus level-variant names)
- **Skeletons/undead**: Skeleton, Red Skeleton, Gold Skeleton, Skeleton Rider, Skeleton Blades, Skeleton Soldier, Were-Panther Skeleton, Wight, Ghoul, Zombie, Assassin Zombie*, Dead Fencer, Dead Nobles, Ghost Swordsmen.
- **Armor/knights**: Knight (Armor Knight), Great Armor, Final Guard, Iron Gladiator, Executioner, Crazy Armor.
- **Demons/devils**: Lesser Demon, Flame Demon, Frost Demon, Thunder Demon, Efreet, Alastor, Amduscias, Azaghal, Gaibon, Slogra, Evil Core, Jin, Vassago, Ripper, Flea Man, Hunchback.
- **Beasts**: Wolf (Fenrir), Warg, Basilisk, Cockatrice, Lizard Man, Unicorn, Cyclops (Red Ogre), Merman (Fishman), White Dragon (Frost/Thunder Dragon), Harpy.
- **Casters/spectres**: Wizard (Dark Warlock), Necromancer, Ectoplasm, Ghost (Spirit).
- **Others**: Orc (Sniper Orc), Thief, Mad Diver, Lizard Shaman*, Duke Mirage*.
(* = also appear as named variants in later areas.)

### 5.4 Bosses (build as unique arena-scale rigs)
Required fights: **Crazy Armor, Wyvern, Trevor (Lv.16 & Lv.40), Skeleton Diver, Minotaurus, Isaac (Lv.34 & Lv.50), Saint Germain, Dullahan, Death, Dracula**.
Optional: **Legion, Nuculais** (Garibaldi Temple). Trevor Mode: **Trevor Doppelganger** (Lv.16 & Lv.40).

### 5.5 Weapons
One base mesh family per class with tier/material variants (bronze → steel → Midas, etc.): 1H/2H swords, 1H/2H axes, spears, knuckles, special weapons (tonfas, gatling guns). Trevor assets: Vampire Killer whip, knife, axe, holy water, cross, stopwatch.

### 5.6 Items, materials & consumables
**40 forge materials** (10 families × 4): **Alloys** — Bronze, Aluminum, Devil Iron, Orichalcum · **Steels** — Steel, Indigo Steel, White Steel, Red Steel · **Composites** — Carbon Steel, Damascus Steel, Ceramics, Adamantine · **Memories** — Wild Memory, Ancient Memory, Forgotten Memory, Immortal Fragment · **Slates** — Jet Black, Spirit of Fuji, Galtite, Midas' Gold · **Stones** — Aquamarine, Jade, Dragon Scale, Frenzy of Wind · **Ambers** — Ceremonial Tool, Sun Tears, Beelzebub's Seal, Death's Pulse · **Crystals** — Lightning Stone, Purple Glitter, Angel Halo, Dark Crystal · **Veins** — Knight's Vein, Holy Man's Vein, Devil's Vein, Vampire Blood · **Matters** — Phlogiston, Ether, Dark Matter, Miracle Egg.

**Recovery/food** (author original pickups): Potion/High Potion/X(-S) Potion, Wine, Milk, Tomato Juice, Ice Cream, Borscht, Ramen, Rice, Pork Bowl, Hamburger, Cheese, Sunnyside Up Egg, Piroshki, French Fries, Garlic, etc. **Utility**: Antidote/Antivenom, Uncurse Potion, Invisibility Potion, Memorial Ticket, Moai (bonus). **Accessories**: HP Max Up, ATK Up, Rare Ring, Dragon Crest, Stun Resist Ring. Each item needs an icon + 3D pickup mesh.

### 5.7 Environment archetypes
- **Castle** (Abandoned/Dracula's): stone corridors, great hall, throne room, drawbridge, towers, moat, cellars, laboratory.
- **Mountains & forest**: carved mountain roads, forest loops, flooded riverbanks, crystal caves, fossils, ancient-civilization ruins.
- **Cathedral/temple**: stained glass, altars, crypts/catacombs, courtyards, basement.
- **Aqueduct**: flooded channels, water gates, bridges, pump rooms.
- **Town/ruins**: Cordova streets & plazas, Aiolon forgotten ruins.
- **Machine tower**: gears, clockwork, elevators, machinery corridors.
- **Infinite Corridor**: surreal parallel-world halls, glyphs/seals.

### 5.8 Props & interactables
Candles (breakable → hearts/items) · treasure chests (some need Fairy **Unlock**) · save points · warp chairs · breakable cracked walls (secret items) · heavy iron doors (**Brute Force**) · narrow gaps (**Magic Circle**) · gaps/long gaps (**Glide/Long Glide**) · timed doors (**Time Stop**) · red-bar "locked room" barriers · map checker (colored completion %) · collectible chairs · memorial/statue inscriptions (Fairy **Decipher**) · secret switches (**Press It & See**) · drawbridge & machinery switches · Moai statue.

### 5.9 Audio
Score cues (from guides): Abandoned Castle · Garibaldi Courtyard · Garibaldi Temple · Catacombs of Grief and Sadness · The Forest of Jigramunt · The Cave of Jigramunt · Eneomaos Machine Tower · Aiolon Ruins · Aiolon Cave Temple · Dracula's Castle · Insane Aristocracy · The Dark Holy Man · A Toccata into Blood Soaked Darkness · Metamorphosis to the Black Abyss of Death (+ "Bloody Tears" remix cameo). SFX: weapon swings/hits, guards/perfect-guard, evade, chain-attack, steal lock, ID skills, forge/combine, UI, ambient (crickets, water, clockwork machinery).

### 5.10 VFX & UI
VFX: fire/ice/thunder/earth/holy/dark spell bursts, weapon trails, magic circles, ID summon/evolve, purple-lock steal prompt, Dracula resurrection glyph. UI/HUD: HP & Heart bars, ID status window, combo counter, map %, item wheel, Combine/Forge menu, shop, save prompt, bestiary.

## 6. Level building reference

### 6.1 World map & connectivity
Backtracking hubless chain: **Abandoned Castle ⇄ Baljhet Mountains ⇄ Garibaldi Temple ⇄ Mortvia Aqueduct ⇄ Forest of Jigramunt ⇄ Cordova Town ⇄ Eneomaos Machine Tower ⇄ Aiolon Ruins ⇄ Infinite Corridor ⇄ Dracula's Castle.** Cross-links: Abandoned Castle → Aiolon Ruins (mountainside) and → Infinite Corridor (gateway); Forest of Jigramunt → Abandoned Castle (tunnel) and → Tower of Eternity (Long Glide); Garibaldi area → Tower of Evermore.

### 6.2 Area build sheets
| # | Area | Theme / biome | ID / upgrade | Boss | Notable enemies | Key items / gates |
|---|---|---|---|---|---|---|
| 1 | Abandoned Castle | Castle, cave, lab, ruins (NES CV1 homage) | Fairy | Crazy Armor (+ Trevor Lv.40 rematch) | Executioner, Ghost, Merman, Skeleton Blaze, Zombie, Wizard, Armor Knight, Cyclops, White Dragon | Potion, Moai, Memorial Ticket, Wine, Map, Dragon Crest, Aluminum; save/warp |
| 2 | Baljhet Mountains | Mountain paths, cliffs | Battle (Magmard) | Wyvern | Orc, Skeleton, Flea Man, Fenrir/Warg, Harpy | Dragon Scale, Dark Crystal; Julia's shop |
| 3 | Garibaldi Temple | Cathedral + catacombs | Brute Force (after Trevor) | Trevor Lv.16; optional Legion/Nuculais | Orc, Flea Man, Cyclops, Wizard, Skeleton, Efreet, Dead Fencer, Lesser Demon, Bone Soldier, Slogra, Thief, Ectoplasm | Knight's Vein, Holy Man's Vein, Ceremonial Tool, Sun Tears, Steel; meet Germain |
| 4 | Mortvia Aqueduct | Flooded aqueduct, water gates | Bird (Crow/Glide) | Skeleton Diver | Merman, Mad Diver, Ectoplasm, Vassago | Angel Halo, Spirit of Fuji, Aquamarine, Dark Matter |
| 5 | Forest of Jigramunt | Forest + crystal cave | (Mage path onward) | Minotaurus | Dark Warlock, Bone Soldier, Spirit, Thunder Dragon, Thief, Basilisk, Lizardman, Wolf Skeleton, Sniper Orc, Vassago, Red Ogre, Great Armor | Devil's Vein, Carbon Steel, Indigo Steel, Ether, Rare Ring |
| 6 | Cordova Town | Town streets/plaza | Mage (Wood Rod) | Isaac Lv.34 | Thief, Ghoul, Wight, Assassin Zombie | Damascus Steel, Ether; Julia = Isaac's sister |
| 7 | Eneomaos Machine Tower | Clock/machine tower, elevators | Devil (Gale/Magic Circle) | Saint Germain | White Gravial, Lizard Shaman, Death Ripper, Dead Fencer, Sniper Orc, Flame Demon, Iron Gladiator, Necromancer, Harpy, Vassago, Wight, Great Armor | — (climb/mechanisms) |
| 8 | Aiolon Ruins | Forgotten-civilization ruins | — | — | Bone Soldier, Rapid Sniper, Spirit, Armored Sprinter, Undead Lord, Vassago, Wight, Assassin Zombie, Gaibon, Necromancer, Great Armor, Fishman, Skeleton Trooper, Jin, Slogra, Flame/Thunder Demon, White Dragon | gateway to Infinite Corridor; Trevor allies |
| 9 | Infinite Corridor | Parallel-world corridor | — | Dullahan | high-tier variants | seal → summon castle |
| 10 | Dracula's Castle | Castle exterior + interior + boss rooms | — | Isaac Lv.50 → Death → Dracula | Thief, Gi-Lee, Spirit, Armored Sprinter, Assassin Zombie, Frost Demon, Skeleton, Undead Lord, Amduscias, Frost Dragon, Rapid Sniper, Flea Man, Death Ripper, Vassago, Final Guard, Zombie, Ghoul, Slogra, Efreet, Jin, Gaibon, Harpy, Cyclops, Executioner, Iron Gladiator, Red Ogre | Miracle Egg, Adamantine, Orichalcum, Death's Pulse, Vampire Blood |
| 11 | Tower of Eternity | Optional tower | Long Glide required | — | — | treasure |
| 12 | Tower of Evermore | Optional tower | Long Glide required | — | Efreet, Orc | Vampire Blood, treasure |

### 6.3 Room & layout conventions
- **Rooms** interconnect via doors; **red-bar "locked" rooms** seal until the room's enemies are swept.
- **Green-door ID rooms** house a petrified ID statue → release it to forge that type.
- **Save rooms** full-heal + save; **warp chairs** enable returning to visited areas.
- **Candles** are breakable → hearts/gold/items. **Treasure chests** may require Fairy **Unlock**.
- **Cracked walls** hide secrets (HP Max Up, XS Potion). The **map** fills by colored completion %; Dracula's Castle splits into three 100% maps (exterior/interior/boss = 300%).

### 6.4 Ability gating map
| Gate / obstacle | Required Innocent Devil ability |
|---|---|
| Locked treasure chests | Fairy — **Unlock** |
| Eneomaos inscriptions | Fairy Tiramisu — **Decipher** |
| Hidden switches | Fairy Proboscis Fairy — **Press It & See** |
| Heavy iron doors | Battle — **Brute Force** (after 1st Trevor fight); Lv.2 via Juggernaut |
| "Bowling-pin" statues / high ledges | Battle Iytei — **Shoulder Ride** |
| Floor pressure switches | Battle Golem — **Hip Press** |
| Gaps | Bird Crow — **Glide** |
| Long gaps (Tower of Evermore, Infinite Corridor) | Bird Wingosaurus — **Long Glide** |
| Timed doors | Mage Wood Rod — **Time Stop** |
| Red (Blood) Skeletons | Mage Nautilus/Embryo Rod — **Purify** |
| Narrow gaps / floor holes | Devil Gale — **Magic Circle** |

### 6.5 Difficulty/modes
**Normal** · **Crazy Mode** (enemy remixes, notably Garibaldi Temple) · **Trevor Mode** (separate playthrough with whip/subweapons and Doppelganger bosses).

## 7. UE5 implementation mapping (Noble Archimedes)
Map each reference item to the existing framework under `UE5_Source/`:
- **Characters** → `HectorCharacter`, companions via `NobleArchimedesInnocentDevilComponent`.
- **Combat** → `NobleArchimedesCombatComponent` (combos, Perfect Guard, Quick Step, Chain Attack, Steal/Death Doll).
- **Innocent Devils** → `InnocentDevilDataTable` / `InnocentDevilEvolutionTable`; each of the **51 forms** = Skeletal Mesh + ability DataAsset + petrified-state mesh.
- **Forge/items** → `NobleArchimedesWeaponForge` + `Weapon/Material/Recipe` CSVs (40 materials, recipes).
- **Enemies** → `EnemyDataTable` (51 families + level variants) + `BehaviorTreeSpec` + `EnemyEncounterSpec` (per-chapter placement above).
- **Levels** → `ChapterProgressionTable` + `LevelSpec` / `LevelDesignSpec_Extended`; build **12 streaming areas (+2 optional towers)** with the room conventions and ability gates in §6.
- **Assets** → `AssetNamingSpec`, `AnimationSpec`, `AudioSpec`, `ParticleSpec`, `UI_WidgetSpec`, `WeaponSpec`.

## 8. Compliance & scope note
This document is a factual game-design reference for an original fan recreation. No game code, models, textures, captures, audio, or video were extracted; the names, structure, and mechanics listed here are research for re-authoring original assets and original level layouts, not reproductions of Konami's copyrighted materials. Castlevania and its content belong to Konami and their respective rights holders.