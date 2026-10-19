// Fill out your copyright notice in the Description page of Project Settings.

#include "NobleArchimedesWeaponForge.h"

UNobleArchimedesWeaponForge::UNobleArchimedesWeaponForge()
{
	InitializeRecipes();
	InitializeMaterials();
}

void UNobleArchimedesWeaponForge::InitializeRecipes()
{
	// Short Sword
	FWeaponRecipe Recipe1;
	Recipe1.WeaponName = "Short Sword";
	Recipe1.WeaponType = EWeaponType::Sword;
	Recipe1.DamageType = EDamageType::Slash;
	Recipe1.RequiredMaterials = { "Iron Shard" };
	Recipe1.ForgeLevel = 1;
	WeaponRecipes.Add(Recipe1);

	// Broad Sword
	FWeaponRecipe Recipe2;
	Recipe2.WeaponName = "Broad Sword";
	Recipe2.WeaponType = EWeaponType::Sword;
	Recipe2.DamageType = EDamageType::Slash;
	Recipe2.RequiredMaterials = { "Iron Shard", "Iron Shard", "Silver Ingot" };
	Recipe2.ForgeLevel = 2;
	WeaponRecipes.Add(Recipe2);

	// Battle Axe
	FWeaponRecipe Recipe3;
	Recipe3.WeaponName = "Battle Axe";
	Recipe3.WeaponType = EWeaponType::Axe;
	Recipe3.DamageType = EDamageType::Blunt;
	Recipe3.RequiredMaterials = { "Iron Shard", "Iron Shard", "Demon Bone" };
	Recipe3.ForgeLevel = 3;
	WeaponRecipes.Add(Recipe3);

	// Long Spear
	FWeaponRecipe Recipe4;
	Recipe4.WeaponName = "Long Spear";
	Recipe4.WeaponType = EWeaponType::Spear;
	Recipe4.DamageType = EDamageType::Slash;
	Recipe4.RequiredMaterials = { "Iron Shard", "Silver Ingot", "Dark Crystal" };
	Recipe4.ForgeLevel = 4;
	WeaponRecipes.Add(Recipe4);

	// Punch Rings
	FWeaponRecipe Recipe5;
	Recipe5.WeaponName = "Punch Rings";
	Recipe5.WeaponType = EWeaponType::Knuckles;
	Recipe5.DamageType = EDamageType::Blunt;
	Recipe5.RequiredMaterials = { "Silver Ingot", "Ghost Essence" };
	Recipe5.ForgeLevel = 2;
	WeaponRecipes.Add(Recipe5);
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
		Data.bIsRare = i >= 10; // Materials after index 10 are rare
		Data.Description = FText::FromName(MaterialNames[i]);
		MaterialData.Add(Data);
		MaterialQuantities.Add(MaterialNames[i], 0);
	}
}

bool UNobleArchimedesWeaponForge::CombineWeapons(TArray<FName> Materials, FName& OutWeapon)
{
	for (const auto& Recipe : WeaponRecipes)
	{
		TArray<FName> Needed = Recipe.RequiredMaterials;
		bool bCanForge = true;

		for (const auto& NeededMat : Needed)
		{
			int32 CountInMaterials = 0;
			for (const auto& Mat : Materials)
			{
				if (Mat == NeededMat) CountInMaterials++;
			}

			int32 CountInInventory = MaterialQuantities.Contains(NeededMat) ? MaterialQuantities[NeededMat] : 0;
			if (CountInMaterials + CountInInventory < 1)
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

bool UNobleArchimedesWeaponForge::CanForgeWeapon(TArray<FName> Materials, FName& OutWeapon) const
{
	for (const auto& Recipe : WeaponRecipes)
	{
		TArray<FName> Needed = Recipe.RequiredMaterials;
		bool bCanForge = true;

		for (const auto& NeededMat : Needed)
		{
			int32 CountInMaterials = 0;
			for (const auto& Mat : Materials)
			{
				if (Mat == NeededMat) CountInMaterials++;
			}

			int32 CountInInventory = MaterialQuantities.Contains(NeededMat) ? MaterialQuantities[NeededMat] : 0;
			if (CountInMaterials + CountInInventory < 1)
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