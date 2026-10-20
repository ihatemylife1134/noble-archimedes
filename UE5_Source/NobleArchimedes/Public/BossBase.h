// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "EnemyBase.h"
#include "BossBase.generated.h"

UCLASS()
class NOBLEARCHIMEDES_API ABossBase : public AEnemyBase
{
	GENERATED_BODY()

public:
	// Sets default values for this actor's properties
	ABossBase();

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;

public:
	// Called every frame
	virtual void Tick(float DeltaTime) override;

	//=============================================================================
	// BOSS PHASES
	//=============================================================================

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Boss")
	int32 MaxBossPhases = 2;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Boss")
	TArray<float> PhaseTransitionHealthThresholds; // Health % at which to transition

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Boss")
	FString BossName;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Boss")
	bool bHasSecondPhase = false;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Boss")
	bool bHasThirdPhase = false;

	//=============================================================================
	// BOSS ACTIONS
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Boss")
	void TransitionToPhase(int32 NewPhase);

	UFUNCTION(BlueprintCallable, Category = "Boss")
	void PlayBossIntro();

	UFUNCTION(BlueprintCallable, Category = "Boss")
	void PlayBossVictory();

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Boss")
	int32 GetCurrentPhase() const { return BossPhase; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Boss")
	bool IsPhaseTransitionNeeded() const;

protected:
	void CheckPhaseTransition();
};
