// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "NobleArchimedesTypes.h"
#include "GameFramework/SaveGame.h"
#include "NobleArchimedesSaveGame.generated.h"

UCLASS()
class NOBLEARCHIMEDES_API UNobleArchimedesSaveGame : public USaveGame
{
	GENERATED_BODY()

public:
	UNobleArchimedesSaveGame();

	//=============================================================================
	// PLAYER DATA
	//=============================================================================

	UPROPERTY(SaveGame)
	FString PlayerName = "The Forgemaster";

	UPROPERTY(SaveGame)
	int32 Health = 100;

	UPROPERTY(SaveGame)
	int32 MaxHealth = 100;

	UPROPERTY(SaveGame)
	int32 Mana = 100;

	UPROPERTY(SaveGame)
	int32 MaxMana = 100;

	UPROPERTY(SaveGame)
	int32 Level = 1;

	UPROPERTY(SaveGame)
	int32 Experience = 0;

	UPROPERTY(SaveGame)
	int32 SkillPoints = 0;

	//=============================================================================
	// CHAPTER PROGRESSION
	//=============================================================================

	UPROPERTY(SaveGame)
	int32 CurrentChapter = 1;

	UPROPERTY(SaveGame)
	TArray<int32> CompletedChapters;

	UPROPERTY(SaveGame)
	FString CurrentLevelName = "Chap_01_AbandonedCastle";

	UPROPERTY(SaveGame)
	FVector PlayerLocation = FVector::ZeroVector;

	UPROPERTY(SaveGame)
	FRotator PlayerRotation = FRotator::ZeroRotator;

	//=============================================================================
	// INVENTORY & EQUIPMENT
	//=============================================================================

	UPROPERTY(SaveGame)
	TArray<FInventoryItem> InventoryItems;

	UPROPERTY(SaveGame)
	TArray<FString> EquippedWeapons;

	UPROPERTY(SaveGame)
	EWeaponType EquippedWeaponType = EWeaponType::Sword;

	//=============================================================================
	// COMPANIONS
	//=============================================================================

	UPROPERTY(SaveGame)
	TArray<FCompanionData> Companions;

	UPROPERTY(SaveGame)
	int32 ActiveCompanionIndex = 0;

	UPROPERTY(SaveGame)
	TArray<ECompanionType> UnlockedCompanions;

	//=============================================================================
	// WEAPON FORGING
	//=============================================================================

	UPROPERTY(SaveGame)
	TArray<FName> DiscoveredRecipes;

	UPROPERTY(SaveGame)
	TArray<FName> ForgedWeapons;

	//=============================================================================
	// SETTINGS
	//=============================================================================

	UPROPERTY(SaveGame)
	float MasterVolume = 1.0f;

	UPROPERTY(SaveGame)
	float SFXVolume = 1.0f;

	UPROPERTY(SaveGame)
	float MusicVolume = 0.0f;

	UPROPERTY(SaveGame)
	ECameraMode CurrentCameraMode = ECameraMode::Classic;
};