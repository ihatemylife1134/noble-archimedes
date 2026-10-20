// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Engine/GameInstance.h"
#include "NobleArchimedesSaveGame.h"
#include "NobleArchimedesGameInstance.generated.h"

UCLASS()
class NOBLEARCHIMEDES_API UNobleArchimedesGameInstance : public UGameInstance
{
	GENERATED_BODY()

public:
	UNobleArchimedesGameInstance();

	//=============================================================================
	// SAVE/LOAD
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "SaveLoad")
	void SaveGame(int32 SlotIndex);

	UFUNCTION(BlueprintCallable, Category = "SaveLoad")
	void LoadGame(int32 SlotIndex);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "SaveLoad")
	bool HasSaveGame(int32 SlotIndex) const;

	UFUNCTION(BlueprintCallable, Category = "SaveLoad")
	void DeleteSaveGame(int32 SlotIndex);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "SaveLoad")
	TArray<FString> GetSaveSlotNames() const;

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "SaveLoad")
	UNobleArchimedesSaveGame* GetCurrentSaveGame() const { return CurrentSaveGame; }

	/** Apply a save that was loaded while the destination level was opening. */
	UFUNCTION(BlueprintCallable, Category = "SaveLoad")
	void ApplyPendingLoad();

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "SaveLoad")
	bool HasPendingLoad() const { return bPendingLoad; }

	//=============================================================================
	// SAVE SLOTS
	//=============================================================================

	UPROPERTY()
	int32 MaxSaveSlots = 5;

	UPROPERTY()
	int32 AutoSaveSlot = 5; // Slot 5 is auto-save (0-indexed: 0-4 manual, 5 auto)

private:
	UPROPERTY()
	UNobleArchimedesSaveGame* CurrentSaveGame = nullptr;

	bool bPendingLoad = false;

	void ApplySaveGameToPlayer(class AHectorCharacter* Player);
	TMap<FName, int32> InventoryArrayToMap(const TArray<FInventoryItem>& Items) const;
	TArray<FInventoryItem> InventoryMapToArray(const TMap<FName, int32>& Items) const;

	FString GetSaveSlotName(int32 SlotIndex) const;
	FString GetSaveDirectory() const;
};