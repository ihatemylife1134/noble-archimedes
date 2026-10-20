// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "NobleArchimedesTypes.h"
#include "NobleArchimedesGameModeBase.generated.h"

class UNobleArchimedesSaveGame;
class UNobleArchimedesGameInstance;

UCLASS()
class NOBLEARCHIMEDES_API ANobleArchimedesGameModeBase : public AGameModeBase
{
	GENERATED_BODY()

public:
	ANobleArchimedesGameModeBase();

	virtual void BeginPlay() override;

	//=============================================================================
	// CHAPTER MANAGEMENT
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "GameMode")
	void StartChapter(int32 ChapterIndex);

	UFUNCTION(BlueprintCallable, Category = "GameMode")
	void CompleteChapter(int32 ChapterIndex);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "GameMode")
	int32 GetCurrentChapter() const { return CurrentChapter; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "GameMode")
	TArray<int32> GetCompletedChapters() const { return CompletedChapters; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "GameMode")
	TArray<FName> GetUnlockedWeaponRecipes() const { return UnlockedWeaponRecipes; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "GameMode")
	TArray<EInnocentDevilType> GetUnlockedInnocentDevilsFromMode() const { return UnlockedInnocentDevils; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "GameMode")
	bool IsChapterCompleted(int32 ChapterIndex) const;

	//=============================================================================
	// GAME STATE
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "GameMode")
	void SaveGameProgress();

	UFUNCTION(BlueprintCallable, Category = "GameMode")
	void LoadGameProgress(int32 SlotIndex);

	/** Push chapter/progression fields from an already-loaded save into the mode. */
	UFUNCTION(BlueprintCallable, Category = "GameMode")
	void RestoreProgressFromSave(const UNobleArchimedesSaveGame* Save);

	UFUNCTION(BlueprintCallable, Category = "GameMode")
	void AutoSave();

	//=============================================================================
	// INNOCENT DEVIL MANAGEMENT
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "GameMode")
	void UnlockInnocentDevil(EInnocentDevilType Type);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "GameMode")
	bool IsInnocentDevilUnlocked(EInnocentDevilType Type) const;

	//=============================================================================
	// WEAPON FORGING
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "GameMode")
	void UnlockWeaponRecipe(FName WeaponName);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "GameMode")
	bool IsWeaponRecipeUnlocked(FName WeaponName) const;

protected:
	UPROPERTY()
	int32 CurrentChapter = 1;

	UPROPERTY()
	TArray<int32> CompletedChapters;

	UPROPERTY()
	TArray<EInnocentDevilType> UnlockedInnocentDevils;

	UPROPERTY()
	TArray<FName> UnlockedWeaponRecipes;

	UPROPERTY()
	UNobleArchimedesSaveGame* SaveGameInstance;

	UPROPERTY()
	UNobleArchimedesGameInstance* GameInstance;

	void InitializeGameState();
	void LoadSaveData(int32 SlotIndex);
	void SaveCurrentState();
};