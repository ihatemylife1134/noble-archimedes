#!/usr/bin/env python3
"""
Generate localization files for multiple languages.
This creates the .json localization files that UE5 can import.
"""

import json
from pathlib import Path

LOC_DIR = Path("UE5_Source/Content/Localization")

# English (base)
EN = {
    "Namespace": "NobleArchimedes",
    "Culture": "en",
    "Entries": {
        "UI.MainMenu.NewGame": "New Game",
        "UI.MainMenu.LoadGame": "Load Game",
        "UI.MainMenu.Options": "Options",
        "UI.MainMenu.Quit": "Quit",
        "UI.Pause.Resume": "Resume",
        "UI.Pause.SaveGame": "Save Game",
        "UI.Pause.LoadGame": "Load Game",
        "UI.Pause.Options": "Options",
        "UI.Pause.QuitToMain": "Quit to Main Menu",
        "UI.HUD.Health": "Health",
        "UI.HUD.Mana": "Mana",
        "UI.HUD.Combo": "Combo",
        "UI.HUD.Chapter": "Chapter",
        "UI.InnocentDevil.Auto": "Auto",
        "UI.InnocentDevil.Command": "Command",
        "UI.InnocentDevil.Guard": "Guard",
        "UI.InnocentDevil.Summon": "Summon Innocent Devil",
        "UI.InnocentDevil.Evolve": "Evolve",
        "UI.Forge.Title": "Weapon Forge",
        "UI.Forge.Combine": "Combine Materials",
        "UI.Forge.MissingMaterials": "Missing Materials",
        "UI.Forge.Success": "Weapon Forged!",
        "UI.Save.SaveSlot": "Save Slot {0}",
        "UI.Save.Empty": "Empty",
        "UI.Save.AutoSave": "Auto-Save",
        "UI.Save.Overwrite": "Overwrite existing save?",
        "UI.Settings.Graphics": "Graphics",
        "UI.Settings.Audio": "Audio",
        "UI.Settings.Controls": "Controls",
        "UI.Settings.Language": "Language",
        "UI.Settings.VSync": "V-Sync",
        "UI.Settings.Fullscreen": "Fullscreen",
        "UI.Settings.Resolution": "Resolution",
        "Chat.ItemPickup": "{0} obtained!",
        "Chat.InnocentDevilSummoned": "{0} summoned!",
        "Chat.InnocentDevilEvolved": "{0} evolved!",
        "Chat.SaveComplete": "Game saved.",
        "Chat.LoadComplete": "Game loaded.",
        "Enemy.Name.Skeleton": "Skeleton",
        "Enemy.Name.Zombie": "Zombie",
        "Enemy.Name.Ghoul": "Ghoul",
        "Enemy.Name.Harpy": "Harpy",
        "Enemy.Name.Bat": "Bat",
        "Enemy.Name.MountainBeast": "Mountain Beast",
        "Enemy.Name.TempleGuardian": "Temple Guardian",
        "Enemy.Name.Cultist": "Cultist",
        "Enemy.Name.DarkPriest": "Dark Priest",
        "Enemy.Name.WaterCreature": "Water Creature",
        "Enemy.Name.AqueductGuard": "Aqueduct Guard",
        "Enemy.Name.ForestStalker": "Forest Stalker",
        "Enemy.Name.NatureSpirit": "Nature Spirit",
        "Enemy.Name.TownGuard": "Town Guard",
        "Enemy.Name.Citizen": "Citizen",
        "Enemy.Name.ClockworkSoldier": "Clockwork Soldier",
        "Enemy.Name.MechanicalTrap": "Mechanical Trap",
        "Enemy.Name.RuinGuardian": "Ruin Guardian",
        "Enemy.Name.AncientConstruct": "Ancient Construct",
        "Enemy.Name.CorridorPhantom": "Corridor Phantom",
        "Enemy.Name.SurrealEntity": "Surreal Entity",
        "Enemy.Name.CastleElite": "Castle Elite",
        "Enemy.Name.FinalBoss": "Final Boss",
        "Item.Name.Potion": "Potion",
        "Item.Name.HighPotion": "High Potion",
        "Item.Name.Serum": "Serum",
        "Item.Name.Uncurse": "Uncurse",
        "Item.Name.DeathDoll": "Death Doll",
        "Item.Name.IronShard": "Iron Shard",
        "Item.Name.SilverIngot": "Silver Ingot",
        "Item.Name.DarkCrystal": "Dark Crystal",
        "Item.Name.HolyWater": "Holy Water",
        "Item.Name.PhoenixFeather": "Phoenix Feather",
        "Chapter.1": "Chapter 1: Abandoned Castle",
        "Chapter.2": "Chapter 2: Baljhet Mountains",
        "Chapter.3": "Chapter 3: Garibaldi Temple",
        "Chapter.4": "Chapter 4: Mortvia Aqueduct",
        "Chapter.5": "Chapter 5: Forest of Jigramunt",
        "Chapter.6": "Chapter 6: Cordova Town",
        "Chapter.7": "Chapter 7: Eneomaos Machine Tower",
        "Chapter.8": "Chapter 8: Aiolon Ruins",
        "Chapter.9": "Chapter 9: Infinite Corridor",
        "Chapter.10": "Chapter 10: Dracula's Castle",
    }
}

# Japanese ( Castlevania: Curse of Darkness original language)
JA = {
    "Namespace": "NobleArchimedes",
    "Culture": "ja",
    "Entries": {
        "UI.MainMenu.NewGame": "新規ゲーム",
        "UI.MainMenu.LoadGame": "ロード",
        "UI.MainMenu.Options": "オプション",
        "UI.MainMenu.Quit": "終了",
        "UI.Pause.Resume": "再開",
        "UI.Pause.SaveGame": "セーブ",
        "UI.Pause.LoadGame": "ロード",
        "UI.Pause.Options": "オプション",
        "UI.Pause.QuitToMain": "タイトルへ戻る",
        "UI.HUD.Health": "HP",
        "UI.HUD.Mana": "MP",
        "UI.HUD.Combo": "コンボ",
        "UI.HUD.Chapter": "チャプター",
        "UI.InnocentDevil.Auto": "オート",
        "UI.InnocentDevil.Command": "コマンド",
        "UI.InnocentDevil.Guard": "ガード",
        "UI.InnocentDevil.Summon": "イノセントデビル召喚",
        "UI.InnocentDevil.Evolve": "進化",
        "UI.Forge.Title": "武器合成",
        "UI.Forge.Combine": "素材合成",
        "UI.Forge.MissingMaterials": "素材不足",
        "UI.Forge.Success": "武器合成完了",
        "UI.Save.SaveSlot": "セーブスロット {0}",
        "UI.Save.Empty": "空き",
        "UI.Save.AutoSave": "オートセーブ",
        "UI.Save.Overwrite": "上書きしますか？",
        "UI.Settings.Graphics": "グラフィックス",
        "UI.Settings.Audio": "オーディオ",
        "UI.Settings.Controls": "コントローラ",
        "UI.Settings.Language": "言語",
        "UI.Settings.VSync": "垂直同期",
        "UI.Settings.Fullscreen": "フルスクリーン",
        "UI.Settings.Resolution": "解像度",
        "Chat.ItemPickup": "{0} を入手！",
        "Chat.InnocentDevilSummoned": "{0} が召喚された！",
        "Chat.InnocentDevilEvolved": "{0} が進化した！",
        "Chat.SaveComplete": "セーブ完了",
        "Chat.LoadComplete": "ロード完了",
        "Enemy.Name.Skeleton": "スケルトン",
        "Enemy.Name.Zombie": "ゾンビ",
        "Enemy.Name.Ghoul": "グール",
        "Enemy.Name.Harpy": "ハーピー",
        "Enemy.Name.Bat": "コウモリ",
        "Enemy.Name.MountainBeast": "マウンテンビースト",
        "Enemy.Name.TempleGuardian": "テンプルガーディアン",
        "Enemy.Name.Cultist": "カルト教徒",
        "Enemy.Name.DarkPriest": "ダークプリースト",
        "Enemy.Name.WaterCreature": "ウォータークリーチャー",
        "Enemy.Name.AqueductGuard": "水道衛兵",
        "Enemy.Name.ForestStalker": "フォレストストーカー",
        "Enemy.Name.NatureSpirit": "ネイチャースピリット",
        "Enemy.Name.TownGuard": "タウンガード",
        "Enemy.Name.Citizen": "市民",
        "Enemy.Name.ClockworkSoldier": "クロックワークソルジャー",
        "Enemy.Name.MechanicalTrap": "メカニカルトラップ",
        "Enemy.Name.RuinGuardian": "ルーンガーディアン",
        "Enemy.Name.AncientConstruct": "エンシェントコンストラクト",
        "Enemy.Name.CorridorPhantom": "コリドーファントム",
        "Enemy.Name.SurrealEntity": "シュルレアルエンティティ",
        "Enemy.Name.CastleElite": "キャッスルエリート",
        "Enemy.Name.FinalBoss": "最終ボス",
        "Item.Name.Potion": "ポーション",
        "Item.Name.HighPotion": "ハイポーション",
        "Item.Name.Serum": "セラム",
        "Item.Name.Uncurse": "アンカース",
        "Item.Name.DeathDoll": "デスドール",
        "Item.Name.IronShard": "アイアンシャード",
        "Item.Name.SilverIngot": "シルバーインゴット",
        "Item.Name.DarkCrystal": "ダーククリスタル",
        "Item.Name.HolyWater": "ホリーウォーター",
        "Item.Name.PhoenixFeather": "フェニックスフェザー",
        "Chapter.1": "チャプター1：廃墟の城",
        "Chapter.2": "チャプター2：バルジェット山脈",
        "Chapter.3": "チャプター3：ガリバルディ寺院",
        "Chapter.4": "チャプター4：モルタリア水道橋",
        "Chapter.5": "チャプター5：森のジグラムント",
        "Chapter.6": "チャプター6：コルドヴァの町",
        "Chapter.7": "チャプター7：エネオマオス機械塔",
        "Chapter.8": "チャプター8：アイオロン遺跡",
        "Chapter.9": "チャプター9：無限の回廊",
        "Chapter.10": "チャプター10：ドラキュラの城",
    }
}

def write_locale(culture: str, data: dict):
    filepath = LOC_DIR / f"{culture}.json"
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[OK] {filepath} ({len(data['Entries'])} entries)")

def main():
    LOC_DIR.mkdir(parents=True, exist_ok=True)
    
    write_locale("en", EN)
    write_locale("ja", JA)
    
    print("\nLocalization files ready for UE5 import.")
    print("In UE5 Editor: Project Settings → Localization → Add Cultures → ja")
    print("Then import these .json files via the Localization Dashboard.")

if __name__ == "__main__":
    main()