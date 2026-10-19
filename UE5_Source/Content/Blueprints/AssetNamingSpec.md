# Asset Naming Specification

All assets must follow this naming convention for consistency and searchability.

## Prefixes by Asset Type

| Prefix | Asset Type | Example |
|--------|------------|---------|
| BP_ | Blueprint | BP_Forgemaster_Character |
| WP_ | Weapon Blueprint | WP_Sword_Short |
| CD_ | Companion Blueprint | CD_Fairy |
| EN_ | Enemy Blueprint | EN_Skeleton_Basic |
| IT_ | Item Blueprint | IT_Potion_Health |
| OB_ | Object Blueprint | OB_Candle_Breakable |
| UI_ | UMG Widget | UI_HealthBar |
| WB_ | Widget Blueprint | WB_MainMenu |
| SM_ | Static Mesh | SM_Castle_Wall_01 |
| SK_ | Skeletal Mesh | SK_Forgemaster_Body |
| AN_ | Animation Sequence | AN_Attack_Light1 |
| AM_ | Animation Montage | AM_Combo_Sword |
| AB_ | Animation Blueprint | AB_Forgemaster_Character |
| MAT_ | Material | MAT_Forgemaster_Skin |
| MI_ | Material Instance | MI_Sword_Silver |
| T_ | Texture | T_Forgemaster_Face_D |
| T_N_ | Texture Normal | T_Forgemaster_Face_N |
| T_M_ | Texture Metallic | T_Forgemaster_Face_M |
| T_R_ | Texture Roughness | T_Forgemaster_Face_R |
| S_ | Sound Cue | S_Combat_Swing_Sword |
| S_M_ | Sound Wave (Mono) | S_M_Footstep_Stone |
| S_S_ | Sound Wave (Stereo) | S_S_Music_Castle |
| NS_ | Niagara System | NS_WeaponTrail_Sword |
| NC_ | Niagara Emitter | NC_Spark |
| L_ | Level | L_Chap_01_AbandonedCastle |
| DT_ | Data Table | DT_WeaponData |
| IF_ | Interface | IF_Damageable |

## Chapter Prefixes
All chapter-specific assets should include the chapter number:

| Prefix | Chapter |
|--------|---------|
| Chap01_ | Abandoned Castle |
| Chap02_ | Baljhet Mountains |
| Chap03_ | Garibaldi Temple |
| Chap04_ | Mortvia Aqueduct |
| Chap05_ | Forest of Jigramunt |
| Chap06_ | Cordova Town |
| Chap07_ | Eneomaos Machine Tower |
| Chap08_ | Aiolon Ruins |
| Chap09_ | Infinite Corridor |
| Chap10_ | Dracula's Castle |

Example: `SM_Chap03_Temple_Column_01`

## Texture Naming
Texture files should include the map type suffix:

| Suffix | Map Type |
|--------|----------|
| _D | Diffuse/Albedo |
| _N | Normal |
| _M | Metallic |
| _R | Roughness |
| _A | Ambient Occlusion |
| _E | Emissive |
| _S | Specular |

Example: `T_Enemy_Skeleton_Body_D`

## Material Naming
| Prefix | Use |
|--------|-----|
| MAT_ | Base material |
| MI_ | Material instance |
| M_ | Material function |

Example: `MI_Enemy_Skeleton_Body`

## Import Settings (recommended)
| Asset Type | Compression | Mip Gen | SRGB |
|------------|-------------|---------|------|
| Textures (Diffuse) | BC1 | Yes | Yes |
| Textures (Normal) | BC5 | Yes | No |
| Textures (Mask) | BC1 | Yes | No |
| Sounds (SFX) | ADPCM | N/A | N/A |
| Sounds (Music) | Vorbis | N/A | N/A |
| Meshes (FBX) | N/A | Yes | N/A |

## Prohibited Names
Do NOT use these names (copyrighted):
- Hector, Isaac, Julia, Trevor Belmont, Dracula, Castlevania, Kuran, Innocent Devil (use "Companion" instead)
- Konami, PlayStation, PS2

## Example Asset List
```
SM_Forgemaster_Body_01
SM_Forgemaster_Cloth_01
SK_Forgemaster_Character
AN_Forgemaster_Idle
AN_Forgemaster_Attack_Light1
AM_Forgemaster_Combo_Sword
AB_Forgemaster_Character
BP_Forgemaster_Character
WP_Sword_Short
EN_Skeleton_Basic
CD_Fairy
IT_Potion_Health
OB_Candle_Breakable
UI_HealthBar
NS_WeaponTrail_Sword
S_Combat_Swing_Sword
DT_WeaponData
L_Chap_01_AbandonedCastle
```

## Asset Organization (Content Browser)
```
Content/
├── Blueprints/
│   ├── Characters/
│   ├── Combat/
│   ├── Companions/
│   ├── Enemies/
│   ├── Items/
│   ├── Level/
│   └── UI/
├── Maps/
│   ├── Chap_01_AbandonedCastle/
│   ├── Chap_02_BaljhetMountains/
│   └── ...
├── Materials/
│   ├── Characters/
│   ├── Environment/
│   ├── Items/
│   └── Weapons/
├── Meshes/
│   ├── Characters/
│   ├── Enemies/
│   ├── Environment/
│   ├── Items/
│   └── Weapons/
├── Textures/
│   ├── Characters/
│   ├── Environment/
│   ├── Items/
│   └── Weapons/
├── Animations/
│   ├── Characters/
│   ├── Enemies/
│   ├── Companions/
│   └── Weapons/
├── Audio/
│   ├── SFX/
│   ├── Music/
│   ├── Ambient/
│   └── UI/
├── VFX/
│   ├── Combat/
│   ├── Companion/
│   ├── Environment/
│   └── Item/
├── DataTables/
├── Localization/
└── Movies/ (original cutscenes only)
```

All assets must be original creations — no extracted game assets.