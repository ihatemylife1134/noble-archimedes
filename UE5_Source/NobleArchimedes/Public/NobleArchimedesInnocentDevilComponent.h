// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NobleArchimedesTypes.h"
#include "NobleArchimedesInnocentDevilComponent.generated.h"

class AInnocentDevilActor;

UCLASS(ClassGroup = (Custom), meta = (BlueprintSpawnableComponent))
class NOBLEARCHIMEDES_API UNobleArchimedesInnocentDevilComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UNobleArchimedesInnocentDevilComponent();

	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	//=============================================================================
	// INNOCENT DEVIL MANAGEMENT
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Innocent Devil")
	void SummonInnocentDevil(EInnocentDevilType Type);

	UFUNCTION(BlueprintCallable, Category = "Innocent Devil")
	void DismissInnocentDevil(EInnocentDevilType Type);

	UFUNCTION(BlueprintCallable, Category = "Innocent Devil")
	void SetMode(EInnocentDevilMode NewMode);

	UFUNCTION(BlueprintCallable, Category = "Innocent Devil")
	void EvolveInnocentDevil(EInnocentDevilType Type, EEvolutionCrystalType CrystalColor);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Innocent Devil")
	TArray<FInnocentDevilData> GetInnocentDevils() const;

	/** Restore the full devil roster from a save game. */
	UFUNCTION(BlueprintCallable, Category = "Innocent Devil")
	void SetInnocentDevils(const TArray<FInnocentDevilData>& NewDevils);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Innocent Devil")
	EInnocentDevilType GetActiveInnocentDevilType() const { return ActiveInnocentDevil; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Innocent Devil")
	EInnocentDevilMode GetMode() const { return CurrentMode; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Innocent Devil")
	bool HasInnocentDevil(EInnocentDevilType Type) const;

	//=============================================================================
	// INNOCENT DEVIL COMBAT
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Innocent Devil")
	void CommandAttack();

	UFUNCTION(BlueprintCallable, Category = "Innocent Devil")
	void CommandGuard();

	UFUNCTION(BlueprintCallable, Category = "Innocent Devil")
	void CommandHeal();

protected:
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Innocent Devil")
	float FollowDistance = 300.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Innocent Devil")
	float FollowSpeed = 600.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Innocent Devil")
	TSubclassOf<AInnocentDevilActor> DevilActorClass;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Innocent Devil")
	TObjectPtr<AInnocentDevilActor> ActiveDevilActor;

private:
	UPROPERTY()
	TArray<FInnocentDevilData> InnocentDevils;
	EInnocentDevilMode CurrentMode = EInnocentDevilMode::Auto;
	EInnocentDevilType ActiveInnocentDevil = EInnocentDevilType::None;

	// Timer used to auto-reset the active devil's mode back to Auto after a
	// command (Attack / Guard / Heal) has been issued.
	FTimerHandle CommandResetTimer;

	void UpdateInnocentDevilAI(float DeltaTime);
	void SpawnInnocentDevilActor(EInnocentDevilType Type);
	void UpdateInnocentDevilStats(FInnocentDevilData& Data);

	// Called by CommandResetTimer to return the active devil to Auto mode.
	void ResetToAutoMode();
};