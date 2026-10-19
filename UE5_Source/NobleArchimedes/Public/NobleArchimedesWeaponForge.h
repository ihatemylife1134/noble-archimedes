// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "NobleArchimedesTypes.h"
#include "NobleArchimedesWeaponForge.generated.h"

UCLASS()
class NOBLEARCHIMEDES_API UNobleArchimedesWeaponForge : public UObject
{
	GENERATED_BODY()

public:
	UNobleArchimedesWeaponForge();

	//=============================================================================
	// WEAPON COMBINING
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "WeaponForge")
	bool CombineWeapons(TArray<FName> Materials, FName& OutWeapon);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "WeaponForge")
	bool CanForgeWeapon(TArray<FName> Materials, FName& OutWeapon) const;

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "WeaponForge")
	TArray<FWeaponRecipe> GetAllRecipes() const { return WeaponRecipes; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "WeaponForge")
	TArray<FMaterialData> GetAllMaterials() const { return MaterialData; }

	UFUNCTION(BlueprintCallable, Category = "WeaponForge")
	void AddMaterial(FName MaterialName, int32 Quantity);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "WeaponForge")
	int32 GetMaterialQuantity(FName MaterialName) const;

private:
	UPROPERTY()
	TArray<FWeaponRecipe> WeaponRecipes;

	UPROPERTY()
	TArray<FMaterialData> MaterialData;

	UPROPERTY()
	TMap<FName, int32> MaterialQuantities;

	void InitializeRecipes();
	void InitializeMaterials();
};