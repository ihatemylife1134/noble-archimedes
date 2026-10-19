# UI Widget Specification

## WB_MainMenu (Main Menu)
- Background: Castle silhouette
- Buttons: New Game, Load Game, Options, Quit
- Version text: "Noble Archimedes - Fan Recreation v0.3.0"
- Legal text: "Private use only - Educational purposes"

## WB_HUD (Heads-Up Display)
- Health Bar: Green, top-left
- Mana Bar: Blue, top-left below health
- Combo Counter: Center-top, shows current combo stage (1-3)
- Weapon Icon: Top-right, shows equipped weapon type
- Companion Status: Top-right below weapon, shows active companion + mode
- Chapter Indicator: Bottom-left, shows current chapter name
- Mini-map: Bottom-right, shows room layout with X markers

## WB_PauseMenu
- Overlay: Semi-transparent dark background
- Buttons: Resume, Save Game, Load Game, Options, Quit to Main Menu
- Save slot list: Shows 5 manual slots + 1 auto-save with timestamps

## WB_SaveLoad
- Slot grid: 6 slots (5 manual + 1 auto)
- Slot info: Chapter name, playtime, date, thumbnail
- Buttons: Save, Load, Delete, Cancel
- Overwrite confirmation: "Overwrite existing save?"

## WB_WeaponForge (Julia's Shop)
- Material inventory: Grid showing all materials with quantities
- Recipe list: Shows forgeable weapons with required materials
- Result preview: 3D model of weapon to be forged
- Buttons: Forge, Cancel, Material Details
- Message: "Weapon Forged!" or "Missing Materials"

## WB_CompanionStatus
- Companion portrait: 3D model or 2D artwork
- Companion name: Text
- Level: Number with XP bar
- Health: Green bar
- Mode selector: Auto / Command / Guard buttons
- Evolution button: Shows when Evo Crystals available
- Active abilities: Icons for current companion abilities

## WB_ComboCounter
- Display: "COMBO x3" with timing ring
- Colors: Green (stage 1), Yellow (stage 2), Red (stage 3)
- Animation: Pulse on successful combo continuation
- Fade out: After combo window expires

## Input Mapping Context (IMC_Default)
| Action | Keyboard | Gamepad (XInput) |
|--------|----------|------------------|
| Move | WASD | Left Stick |
| Look | Mouse | Right Stick |
| Jump | Space | A / Cross |
| Light Attack | J | X / Square |
| Heavy Attack | K | Y / Triangle |
| Dodge | Shift + Dir | B / Circle + Dir |
| Guard (Hold) | Left Shift | L1 / LB |
| Guard Release | Left Shift (release) | L1 / LB (release) |
| Special | Q | LT / L2 |
| Interact | E / L | A / Cross |
| Menu | Esc / Enter | Start / Options |
| Map | M | Select / Touchpad |
| Camera Mode | V | R3 / Rstick click |