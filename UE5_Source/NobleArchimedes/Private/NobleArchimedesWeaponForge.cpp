// Fill out your copyright notice in the Description page of Project Settings.

#include "NobleArchimedesWeaponForge.h"

UNobleArchimedesWeaponForge::UNobleArchimedesWeaponForge()
{
	InitializeRecipes();
	InitializeMaterials();
}

void UNobleArchimedesWeaponForge::InitializeRecipes()
{
	// All 19 recipes from WeaponRecipeTable_Complete.csv / WeaponSpec.md
	// Format: RequiredMaterials uses duplicates for quantity (e.g. 2x Iron Shard = {"Iron Shard", "Iron Shard"})

	//--- Swords ---
	FWeaponRecipe Recipe1;
	Recipe1.WeaponName = "Short Sword";
	Recipe1.WeaponType = EWeaponType::Sword;
	Recipe1.DamageType = EDamageType::Slash;
	Recipe1.RequiredMaterials = { "Iron Shard" };
	Recipe1.ForgeLevel = 1;
	WeaponRecipes.Add(Recipe1);

	FWeaponRecipe Recipe2;
	Recipe2.WeaponName = "Iron Sword";
	Recipe2.WeaponType = EWeaponType::Sword;
	Recipe2.DamageType = EDamageType::Slash;
	Recipe2.RequiredMaterials = { "Iron Shard", "Iron Shard" };
	Recipe2.ForgeLevel = 2;
	WeaponRecipes.Add(Recipe2);

	FWeaponRecipe Recipe3;
	Recipe3.WeaponName = "Broad Sword";
	Recipe3.WeaponType = EWeaponType::Sword;
	Recipe3.DamageType = EDamageType::Slash;
	Recipe3.RequiredMaterials = { "Iron Shard", "Iron Shard", "Silver Ingot" };
	Recipe3.ForgeLevel = 2;
	WeaponRecipes.Add(Recipe3);

	FWeaponRecipe Recipe4;
	Recipe4.WeaponName = "Long Sword";
	Recipe4.WeaponType = EWeaponType::Sword;
	Recipe4.DamageType = EDamageType::Slash;
	Recipe4.RequiredMaterials = { "Silver Ingot", "Silver Ingot", "Dark Crystal" };
	Recipe4.ForgeLevel = 3;
	WeaponRecipes.Add(Recipe4);

	FWeaponRecipe Recipe5;
	Recipe5.WeaponName = "Great Sword";
	Recipe5.WeaponType = EWeaponType::Sword;
	Recipe5.DamageType = EDamageType::Curse;
	Recipe5.RequiredMaterials = { "Silver Ingot", "Dark Crystal", "Phoenix Feather" };
	Recipe5.ForgeLevel = 4;
	WeaponRecipes.Add(Recipe5);

	FWeaponRecipe Recipe6;
	Recipe6.WeaponName = "Executioner Sword";
	Recipe6.WeaponType = EWeaponType::Sword;
	Recipe6.DamageType = EDamageType::Curse;
	Recipe6.RequiredMaterials = { "Dark Crystal", "Phoenix Feather", "Dragon Scale" };
	Recipe6.ForgeLevel = 5;
	WeaponRecipes.Add(Recipe6);

	//--- Axes ---
	FWeaponRecipe Recipe7;
	Recipe7.WeaponName = "Battle Axe";
	Recipe7.WeaponType = EWeaponType::Axe;
	Recipe7.DamageType = EDamageType::Blunt;
	Recipe7.RequiredMaterials = { "Iron Shard", "Iron Shard", "Demon Bone" };
	Recipe7.ForgeLevel = 3;
	WeaponRecipes.Add(Recipe7);

	FWeaponRecipe Recipe8;
	Recipe8.WeaponName = "Great Axe";
	Recipe8.WeaponType = EWeaponType::Axe;
	Recipe8.DamageType = EDamageType::Dark;
	Recipe8.RequiredMaterials = { "Iron Shard", "Silver Ingot", "Demon Bone", "Ghost Essence" };
	Recipe8.ForgeLevel = 4;
	WeaponRecipes.Add(Recipe8);

	FWeaponRecipe Recipe9;
	Recipe9.WeaponName = "Executioner Axe";
	Recipe9.WeaponType = EWeaponType::Axe;
	Recipe9.DamageType = EDamageType::Stone;
	Recipe9.RequiredMaterials = { "Silver Ingot", "Demon Bone", "Dark Crystal", "Wizard's Orb" };
	Recipe9.ForgeLevel = 5;
	WeaponRecipes.Add(Recipe9);

	//--- Spears ---
	FWeaponRecipe Recipe10;
	Recipe10.WeaponName = "Long Spear";
	Recipe10.WeaponType = EWeaponType::Spear;
	Recipe10.DamageType = EDamageType::Slash;
	Recipe10.RequiredMaterials = { "Iron Shard", "Silver Ingot", "Dark Crystal" };
	Recipe10.ForgeLevel = 4;
	WeaponRecipes.Add(Recipe10);

	FWeaponRecipe Recipe11;
	Recipe11.WeaponName = "Halberd";
	Recipe11.WeaponType = EWeaponType::Spear;
	Recipe11.DamageType = EDamageType::Slash;
	Recipe11.RequiredMaterials = { "Silver Ingot", "Dark Crystal", "Dragon Scale" };
	Recipe11.ForgeLevel = 5;
	WeaponRecipes.Add(Recipe11);

	FWeaponRecipe Recipe12;
	Recipe12.WeaponName = "Pike";
	Recipe12.WeaponType = EWeaponType::Spear;
	Recipe12.DamageType = EDamageType::Paralyze;
	Recipe12.RequiredMaterials = { "Dark Crystal", "Dragon Scale", "Demon Bone" };
	Recipe12.ForgeLevel = 6;
	WeaponRecipes.Add(Recipe12);

	//--- Knuckles ---
	FWeaponRecipe Recipe13;
	Recipe13.WeaponName = "Punch Rings";
	Recipe13.WeaponType = EWeaponType::Knuckles;
	Recipe13.DamageType = EDamageType::Blunt;
	Recipe13.RequiredMaterials = { "Silver Ingot", "Ghost Essence" };
	Recipe13.ForgeLevel = 2;
	WeaponRecipes.Add(Recipe13);

	FWeaponRecipe Recipe14;
	Recipe14.WeaponName = "Claws";
	Recipe14.WeaponType = EWeaponType::Knuckles;
	Recipe14.DamageType = EDamageType::Poison;
	Recipe14.RequiredMaterials = { "Silver Ingot", "Ghost Essence", "Dark Crystal" };
	Recipe14.ForgeLevel = 3;
	WeaponRecipes.Add(Recipe14);

	FWeaponRecipe Recipe15;
	Recipe15.WeaponName = "Brass Knuckles";
	Recipe15.WeaponType = EWeaponType::Knuckles;
	Recipe15.DamageType = EDamageType::Poison;
	Recipe15.RequiredMaterials = { "Silver Ingot", "Ghost Essence", "Dark Crystal", "Phoenix Feather" };
	Recipe15.ForgeLevel = 4;
	WeaponRecipes.Add(Recipe15);

	FWeaponRecipe Recipe16;
	Recipe16.WeaponName = "Katar";
	Recipe16.WeaponType = EWeaponType::Knuckles;
	Recipe16.DamageType = EDamageType::Poison;
	Recipe16.RequiredMaterials = { "Ghost Essence", "Dark Crystal", "Phoenix Feather", "Dragon Scale" };
	Recipe16.ForgeLevel = 5;
	WeaponRecipes.Add(Recipe16);

	//--- Special ---
	FWeaponRecipe Recipe17;
	Recipe17.WeaponName = "Shuriken";
	Recipe17.WeaponType = EWeaponType::Special;
	Recipe17.DamageType = EDamageType::Magic;
	Recipe17.RequiredMaterials = { "Iron Shard", "Holy Water" };
	Recipe17.ForgeLevel = 2;
	WeaponRecipes.Add(Recipe17);

	FWeaponRecipe Recipe18;
	Recipe18.WeaponName = "Bomb";
	Recipe18.WeaponType = EWeaponType::Special;
	Recipe18.DamageType = EDamageType::Fire;
	Recipe18.RequiredMaterials = { "Iron Shard", "Phoenix Feather", "Demon Bone" };
	Recipe18.ForgeLevel = 3;
	WeaponRecipes.Add(Recipe18);

	FWeaponRecipe Recipe19;
	Recipe19.WeaponName = "Gatling Gun";
	Recipe19.WeaponType = EWeaponType::Special;
	Recipe19.DamageType = EDamageType::Slash;
	Recipe19.RequiredMaterials = { "Mithril Ore", "Adamantite", "Orichalcum", "Wizard's Orb" };
	Recipe19.ForgeLevel = 5;
	WeaponRecipes.Add(Recipe19);

	// All recipes are discoverable in this private recreation. The forge menu
	// lists every recipe so players can work toward the full weapon set.
	DiscoveredRecipes.Empty();
	for (const FWeaponRecipe& Recipe : WeaponRecipes)
	{
		DiscoveredRecipes.AddUnique(Recipe.WeaponName);
	}
}

void UNobleArchimedesWeaponForge::InitializeMaterials()
{
	TArray<FName> MaterialNames = {
		"Iron Shard", "Silver Ingot", "Dark Crystal", "Holy Water", "Phoenix Feather",
		"Dragon Scale", "Demon Bone", "Ghost Essence", "Wizard's Orb", "Mithril Ore",
		"Adamantite", "Orichalcum", "Phoenix Down", "Unicorn Horn", "Dragon Heart",
		"Demon Soul", "Angel Feather", "Vampire Fang", "Werewolf Claw", "Golem Core",
		"Fairy Dust", "Witch Broom", "Zombie Brain", "Ghoul Eye", "Harpy Feather",
		"Basilisk Scale", "Medusa Hair", "Cerberus Fang", "Hydra Blood", "Chimera Horn",
		"Griffin Feather", "Sphinx Eye", "Minotaur Horn", "Cyclops Eye", "Troll Skin",
		"Ogre Club", "Giant Toe", "Leviathan Scale", "Kraken Tentacle", "Sea Serpent Fang"
	};

	TArray<FLinearColor> Colors = {
		FLinearColor(0.7f, 0.7f, 0.7f),   // Iron Shard - Gray
		FLinearColor(0.9f, 0.8f, 0.7f),   // Silver Ingot - Silver
		FLinearColor(0.2f, 0.2f, 0.8f),   // Dark Crystal - Dark Blue
		FLinearColor(0.8f, 0.9f, 1.0f),   // Holy Water - Light Blue
		FLinearColor(1.0f, 0.5f, 0.0f),   // Phoenix Feather - Orange
		FLinearColor(0.2f, 0.5f, 0.2f),   // Dragon Scale - Green
		FLinearColor(0.4f, 0.2f, 0.1f),   // Demon Bone - Brown
		FLinearColor(0.5f, 0.5f, 0.5f),   // Ghost Essence - Gray
		FLinearColor(0.8f, 0.8f, 0.2f),   // Wizard's Orb - Yellow
		FLinearColor(0.6f, 0.6f, 0.6f),   // Mithril Ore - Light Gray
		FLinearColor(0.3f, 0.3f, 0.3f),   // Adamantite - Dark Gray
		FLinearColor(1.0f, 0.8f, 0.2f),   // Orichalcum - Gold
		FLinearColor(1.0f, 0.3f, 0.3f),   // Phoenix Down - Red
		FLinearColor(1.0f, 1.0f, 1.0f),   // Unicorn Horn - White
		FLinearColor(0.8f, 0.0f, 0.0f),   // Dragon Heart - Dark Red
		FLinearColor(0.5f, 0.0f, 0.5f),   // Demon Soul - Purple
		FLinearColor(1.0f, 1.0f, 0.8f),   // Angel Feather - Light Yellow
		FLinearColor(0.3f, 0.3f, 0.3f),   // Vampire Fang - Dark Gray
		FLinearColor(0.6f, 0.4f, 0.2f),   // Werewolf Claw - Brown
		FLinearColor(0.2f, 0.2f, 0.2f),   // Golem Core - Stone
		FLinearColor(1.0f, 1.0f, 0.5f),   // Fairy Dust - Light Yellow
		FLinearColor(0.3f, 0.2f, 0.1f),   // Witch Broom - Brown
		FLinearColor(0.1f, 0.1f, 0.1f),   // Zombie Brain - Dark
		FLinearColor(0.2f, 0.1f, 0.1f),   // Ghoul Eye - Dark Red
		FLinearColor(0.8f, 0.8f, 0.2f),   // Harpy Feather - Yellow
		FLinearColor(0.2f, 0.5f, 0.2f),   // Basilisk Scale - Green
		FLinearColor(0.4f, 0.2f, 0.4f),   // Medusa Hair - Purple
		FLinearColor(0.6f, 0.2f, 0.2f),   // Cerberus Fang - Red
		FLinearColor(0.3f, 0.6f, 0.3f),   // Hydra Blood - Green
		FLinearColor(0.7f, 0.4f, 0.2f),   // Chimera Horn - Brown
		FLinearColor(0.9f, 0.7f, 0.3f),   // Griffin Feather - Gold
		FLinearColor(0.4f, 0.4f, 0.1f),   // Sphinx Eye - Olive
		FLinearColor(0.5f, 0.3f, 0.2f),   // Minotaur Horn - Brown
		FLinearColor(0.2f, 0.2f, 0.2f),   // Cyclops Eye - Gray
		FLinearColor(0.3f, 0.1f, 0.1f),   // Troll Skin - Dark
		FLinearColor(0.4f, 0.3f, 0.2f),   // Ogre Club - Wood
		FLinearColor(0.8f, 0.8f, 0.8f),   // Giant Toe - Light Gray
		FLinearColor(0.2f, 0.4f, 0.8f),   // Leviathan Scale - Blue
		FLinearColor(0.1f, 0.2f, 0.4f),   // Kraken Tentacle - Dark Blue
		FLinearColor(0.3f, 0.1f, 0.5f)    // Sea Serpent Fang - Purple
	};

	for (int32 i = 0; i < MaterialNames.Num(); i++)
	{
		FMaterialData Data;
		Data.MaterialName = MaterialNames[i];
		Data.MaterialColor = Colors.IsValidIndex(i) ? Colors[i] : FLinearColor::White;
		Data.bIsRare = i >= 5; // Materials 6-40 (indices 5-39) are rare per MaterialSpec.md
		Data.Description = FText::FromName(MaterialNames[i]);
		MaterialData.Add(Data);
		MaterialQuantities.Add(MaterialNames[i], 0);
	}
}

bool UNobleArchimedesWeaponForge::CombineWeapons(TArray<FName> Materials, FName& OutWeapon)
{
	for (const auto& Recipe : WeaponRecipes)
	{
		// Count required materials per type from recipe
		TMap<FName, int32> RequiredCounts;
		for (const auto& Mat : Recipe.RequiredMaterials)
		{
			RequiredCounts.Emplace(Mat, RequiredCounts.Contains(Mat) ? RequiredCounts[Mat] + 1 : 1);
		}

		// Count available materials (from materials array + inventory)
		TMap<FName, int32> AvailableCounts;
		for (const auto& Mat : Materials)
		{
			AvailableCounts.Emplace(Mat, AvailableCounts.Contains(Mat) ? AvailableCounts[Mat] + 1 : 1);
		}
		for (const auto& Pair : MaterialQuantities)
		{
			AvailableCounts.Emplace(Pair.Key, AvailableCounts.Contains(Pair.Key) ? AvailableCounts[Pair.Key] + Pair.Value : Pair.Value);
		}

		// Check if we have enough of each required material
		bool bCanForge = true;
		for (const auto& Pair : RequiredCounts)
		{
			int32 Have = AvailableCounts.Contains(Pair.Key) ? AvailableCounts[Pair.Key] : 0;
			if (Have < Pair.Value)
			{
				bCanForge = false;
				break;
			}
		}

		if (bCanForge)
		{
			// Consume materials: first from the provided materials array, then from inventory
			TMap<FName, int32> RemainingToConsume = RequiredCounts;

			// Consume from the provided materials array
			for (int32 i = Materials.Num() - 1; i >= 0 && RemainingToConsume.Num() > 0; --i)
			{
				const FName& Mat = Materials[i];
				if (RemainingToConsume.Contains(Mat) && RemainingToConsume[Mat] > 0)
				{
					RemainingToConsume[Mat]--;
					if (RemainingToConsume[Mat] <= 0)
					{
						RemainingToConsume.Remove(Mat);
					}
				}
			}

			// Consume any remainder from inventory
			for (auto& Pair : RemainingToConsume)
			{
				if (MaterialQuantities.Contains(Pair.Key))
				{
					int32 NewQty = FMath::Max(0, MaterialQuantities[Pair.Key] - Pair.Value);
					MaterialQuantities[Pair.Key] = NewQty;
				}
			}

			OutWeapon = Recipe.WeaponName;
			return true;
		}
	}

	return false;
}

bool UNobleArchimedesWeaponForge::CanForgeWeapon(TArray<FName> Materials, FName& OutWeapon) const
{
	for (const auto& Recipe : WeaponRecipes)
	{
		// Count required materials per type from recipe
		TMap<FName, int32> RequiredCounts;
		for (const auto& Mat : Recipe.RequiredMaterials)
		{
			RequiredCounts.Emplace(Mat, RequiredCounts.Contains(Mat) ? RequiredCounts[Mat] + 1 : 1);
		}

		// Count available materials (from materials array + inventory)
		TMap<FName, int32> AvailableCounts;
		for (const auto& Mat : Materials)
		{
			AvailableCounts.Emplace(Mat, AvailableCounts.Contains(Mat) ? AvailableCounts[Mat] + 1 : 1);
		}
		for (const auto& Pair : MaterialQuantities)
		{
			AvailableCounts.Emplace(Pair.Key, AvailableCounts.Contains(Pair.Key) ? AvailableCounts[Pair.Key] + Pair.Value : Pair.Value);
		}

		// Check if we have enough of each required material
		bool bCanForge = true;
		for (const auto& Pair : RequiredCounts)
		{
			int32 Have = AvailableCounts.Contains(Pair.Key) ? AvailableCounts[Pair.Key] : 0;
			if (Have < Pair.Value)
			{
				bCanForge = false;
				break;
			}
		}

		if (bCanForge)
		{
			OutWeapon = Recipe.WeaponName;
			return true;
		}
	}

	return false;
}

void UNobleArchimedesWeaponForge::AddMaterial(FName MaterialName, int32 Quantity)
{
	if (MaterialQuantities.Contains(MaterialName))
	{
		MaterialQuantities[MaterialName] += Quantity;
	}
}

int32 UNobleArchimedesWeaponForge::GetMaterialQuantity(FName MaterialName) const
{
	return MaterialQuantities.Contains(MaterialName) ? MaterialQuantities[MaterialName] : 0;
}

bool UNobleArchimedesWeaponForge::CanForgeWeaponByName(FName WeaponName) const
{
	for (const FWeaponRecipe& Recipe : WeaponRecipes)
	{
		if (Recipe.WeaponName != WeaponName)
		{
			continue;
		}

		TMap<FName, int32> RequiredCounts;
		for (const FName& Material : Recipe.RequiredMaterials)
		{
			RequiredCounts.FindOrAdd(Material)++;
		}
		for (const auto& Pair : RequiredCounts)
		{
			if (GetMaterialQuantity(Pair.Key) < Pair.Value)
			{
				return false;
			}
		}
		return true;
	}
	return false;
}

bool UNobleArchimedesWeaponForge::ConsumeRecipeMaterials(const FWeaponRecipe& Recipe)
{
	TMap<FName, int32> RequiredCounts;
	for (const FName& Material : Recipe.RequiredMaterials)
	{
		RequiredCounts.FindOrAdd(Material)++;
	}
	for (const auto& Pair : RequiredCounts)
	{
		if (GetMaterialQuantity(Pair.Key) < Pair.Value)
		{
			return false;
		}
	}
	for (const auto& Pair : RequiredCounts)
	{
		MaterialQuantities[Pair.Key] = FMath::Max(0, MaterialQuantities[Pair.Key] - Pair.Value);
	}
	return true;
}

bool UNobleArchimedesWeaponForge::ForgeWeaponByName(FName WeaponName, FName& OutWeapon)
{
	if (!DiscoveredRecipes.Contains(WeaponName))
	{
		return false;
	}

	for (const FWeaponRecipe& Recipe : WeaponRecipes)
	{
		if (Recipe.WeaponName == WeaponName && ConsumeRecipeMaterials(Recipe))
		{
			OutWeapon = Recipe.WeaponName;
			ForgedWeapons.AddUnique(Recipe.WeaponName);
			return true;
		}
	}
	return false;
}

void UNobleArchimedesWeaponForge::SetDiscoveredRecipes(const TArray<FName>& NewRecipes)
{
	if (NewRecipes.Num() > 0)
	{
		DiscoveredRecipes = NewRecipes;
	}
}

void UNobleArchimedesWeaponForge::SetForgedWeapons(const TArray<FName>& NewWeapons)
{
	ForgedWeapons = NewWeapons;
}

void UNobleArchimedesWeaponForge::SetAllMaterialQuantities(const TMap<FName, int32>& NewQuantities)
{
	for (const auto& Pair : NewQuantities)
	{
		if (MaterialQuantities.Contains(Pair.Key))
		{
			MaterialQuantities[Pair.Key] = Pair.Value;
		}
	}
}
