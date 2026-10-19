// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NobleArchimedesTypes.h"
#include "NobleArchimedesCompanionComponent.generated.h"

class ANobleArchimedesCharacter;

UCLASS(ClassGroup = (Custom), meta = (BlueprintSpawnableComponent))
class NOBLEARCHIMEDES_API UNobleArchimedesCompanionComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UNobleArchimedesCompanionComponent();

	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	//=============================================================================
	// COMPANION MANAGEMENT
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Companion")
	void SummonCompanion(ECompanionType Type);

	UFUNCTION(BlueprintCallable, Category = "Companion")
	void DismissCompanion(ECompanionType Type);

	UFUNCTION(BlueprintCallable, Category = "Companion")
	void SetMode(ECompanionMode NewMode);

	UFUNCTION(BlueprintCallable, Category = "Companion")
	void EvolveCompanion(ECompanionType Type, ECompanionType CrystalColor);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Companion")
	TArray<FCompanionData> GetCompanions() const;

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Companion")
	ECompanionMode GetMode() const { return CurrentMode; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Companion")
	bool HasCompanion(ECompanionType Type) const;

	//=============================================================================
	// COMPANION COMBAT
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Companion")
	void CommandAttack();

	UFUNCTION(BlueprintCallable, Category = "Companion")
	void CommandGuard();

	UFUNCTION(BlueprintCallable, Category = "Companion")
	void CommandHeal();

protected:
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Companion")
	float FollowDistance = 300.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Companion")
	float FollowSpeed = 600.0f;

private:
	TArray<FCompanionData> Companions;
	ECompanionMode CurrentMode = ECompanionMode::Auto;
	ECompanionType ActiveCompanion = ECompanionType::None;

	void UpdateCompanionAI(float DeltaTime);
	void SpawnCompanionActor(ECompanionType Type);
	void UpdateCompanionStats(FCompanionData& Data);
};