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

	/** Forge a specific recipe, consuming materials from the forge inventory. */
	UFUNCTION(BlueprintCallable, Category = "WeaponForge")
	bool ForgeWeaponByName(FName WeaponName, FName& OutWeapon);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "WeaponForge")
	bool CanForgeWeaponByName(FName WeaponName) const;

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "WeaponForge")
	TArray<FName> GetDiscoveredRecipes() const { return DiscoveredRecipes; }

	UFUNCTION(BlueprintCallable, Category = "WeaponForge")
	void SetDiscoveredRecipes(const TArray<FName>& NewRecipes);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "WeaponForge")
	TArray<FName> GetForgedWeapons() const { return ForgedWeapons; }

	UFUNCTION(BlueprintCallable, Category = "WeaponForge")
	void SetForgedWeapons(const TArray<FName>& NewWeapons);

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

	/** Full material map, used by save/load. */
	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "WeaponForge")
	TMap<FName, int32> GetAllMaterialQuantities() const { return MaterialQuantities; }

	UFUNCTION(BlueprintCallable, Category = "WeaponForge")
	void SetAllMaterialQuantities(const TMap<FName, int32>& NewQuantities);

private:
	UPROPERTY()
	TArray<FWeaponRecipe> WeaponRecipes;

	UPROPERTY()
	TArray<FMaterialData> MaterialData;

	UPROPERTY()
	TMap<FName, int32> MaterialQuantities;

	UPROPERTY()
	TArray<FName> DiscoveredRecipes;

	UPROPERTY()
	TArray<FName> ForgedWeapons;

	void InitializeRecipes();
	void InitializeMaterials();
	bool ConsumeRecipeMaterials(const FWeaponRecipe& Recipe);
};