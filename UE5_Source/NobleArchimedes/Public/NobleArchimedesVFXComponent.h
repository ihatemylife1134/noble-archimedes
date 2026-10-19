// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NobleArchimedesTypes.h"
#include "NobleArchimedesVFXComponent.generated.h"

UCLASS(ClassGroup = (Custom), meta = (BlueprintSpawnableComponent))
class NOBLEARCHIMEDES_API UNobleArchimedesVFXComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UNobleArchimedesVFXComponent();

	virtual void BeginPlay() override;

	//=============================================================================
	// COMBAT VFX
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "VFX")
	void PlayWeaponTrail(EWeaponType WeaponType, FVector StartLocation, FVector EndLocation);

	UFUNCTION(BlueprintCallable, Category = "VFX")
	void PlayWeaponTrailEnd(EWeaponType WeaponType, FVector Location);

	UFUNCTION(BlueprintCallable, Category = "VFX")
	void PlayHitSpark(FVector Location, EDamageType DamageType);

	UFUNCTION(BlueprintCallable, Category = "VFX")
	void PlayHitBlood(FVector Location);

	UFUNCTION(BlueprintCallable, Category = "VFX")
	void PlayQuickStepTrail(FVector StartLocation, FVector EndLocation);

	UFUNCTION(BlueprintCallable, Category = "VFX")
	void PlayPerfectGuardFlash(FVector Location);

	UFUNCTION(BlueprintCallable, Category = "VFX")
	void PlayGuardBlockFlash(FVector Location);

	//=============================================================================
	// COMPANION VFX
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "VFX")
	void PlayCompanionSummon(FVector Location, ECompanionType Type);

	UFUNCTION(BlueprintCallable, Category = "VFX")
	void PlayCompanionEvolve(FVector Location, ECompanionType Type);

	UFUNCTION(BlueprintCallable, Category = "VFX")
	void PlayCompanionAttack(FVector Location, ECompanionType Type);

	//=============================================================================
	// ITEM VFX
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "VFX")
	void PlayItemPickup(FVector Location);

	UFUNCTION(BlueprintCallable, Category = "VFX")
	void PlayCandleBreak(FVector Location);

	UFUNCTION(BlueprintCallable, Category = "VFX")
	void PlaySaveRoomHeal(FVector Location);

	//=============================================================================
	// SETTINGS
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "VFX")
	void SetVFXScale(float Scale);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "VFX")
	float GetVFXScale() const { return VFXScale; }

private:
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX")
	float VFXScale = 1.0f;
};