// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "NobleArchimedesTypes.h"
#include "NobleArchimedesItemSystem.generated.h"

class AHectorCharacter;

// Internal bookkeeping for the steal system. Tracks whether an enemy is in a
// stealable state, whether it has already been stolen from, and which item it
// offers when stolen from (set via SetStealable / data table).
USTRUCT()
struct FStealLockInfo
{
	GENERATED_BODY()

	bool bStealable = false;
	bool bStolenFrom = false;
	FName StealItem;
};

UCLASS()
class NOBLEARCHIMEDES_API UNobleArchimedesItemSystem : public UObject
{
	GENERATED_BODY()

public:
	UNobleArchimedesItemSystem();

	//=============================================================================
	// ITEM USAGE
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Items")
	bool UseItem(FName ItemName, AActor* Target);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Items")
	int32 GetItemQuantity(FName ItemName) const;

	UFUNCTION(BlueprintCallable, Category = "Items")
	void AddItem(FName ItemName, int32 Quantity);

	UFUNCTION(BlueprintCallable, Category = "Items")
	void RemoveItem(FName ItemName, int32 Quantity);

	//=============================================================================
	// DEATH DOLL
	//=============================================================================

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Items")
	bool HasDeathDoll() const;

	UFUNCTION(BlueprintCallable, Category = "Items")
	void SetDeathDoll(bool bHas);

	//=============================================================================
	// STEAL SYSTEM
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Items")
	bool TrySteal(AActor* Target, FName& OutStolenItem);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Items")
	bool CanSteal(AActor* Target) const;

	// Register an enemy as stealable (or clear its stealable state). StealItem
	// is the item that will be stolen when TrySteal succeeds; if it is None,
	// TrySteal falls back to a random steal-pool item.
	UFUNCTION(BlueprintCallable, Category = "Items")
	void SetStealable(AActor* Target, bool bStealable, FName StealItem);

private:
	UPROPERTY()
	TMap<FName, int32> ItemQuantities;

	UPROPERTY()
	TMap<AActor*, FStealLockInfo> StealLockState; // Per-enemy steal lock state

	float StealLockTimer = 0.0f;
};