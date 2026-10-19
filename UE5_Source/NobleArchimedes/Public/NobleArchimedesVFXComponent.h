// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NiagaraSystem.h"
#include "NiagaraComponent.h"
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
	// INNOCENT DEVIL VFX
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "VFX")
	void PlayInnocentDevilSummon(FVector Location, EInnocentDevilType Type);

	UFUNCTION(BlueprintCallable, Category = "VFX")
	void PlayInnocentDevilEvolve(FVector Location, EInnocentDevilType Type);

	UFUNCTION(BlueprintCallable, Category = "VFX")
	void PlayInnocentDevilAttack(FVector Location, EInnocentDevilType Type);

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
	// AMBIENT VFX
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "VFX")
	void PlayDustMotes(FVector Location);

	UFUNCTION(BlueprintCallable, Category = "VFX")
	void PlayLeaves(FVector Location);

	UFUNCTION(BlueprintCallable, Category = "VFX")
	void PlaySteam(FVector Location);

	//=============================================================================
	// SETTINGS
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "VFX")
	void SetVFXScale(float Scale);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "VFX")
	float GetVFXScale() const { return VFXScale; }

	//=============================================================================
	// NIAGARA SYSTEM ASSETS
	// Names follow AssetNamingSpec.md: NS_ prefix, no spaces.
	// Assign these in the editor/Blueprint defaults (EditDefaultsOnly).
	//=============================================================================

	// Combat VFX
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_WeaponTrail_Sword;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_WeaponTrail_Axe;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_WeaponTrail_Spear;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_WeaponTrail_Knuckles;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_WeaponTrail_Special;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_HitSpark_Fire;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_HitSpark_Ice;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_HitSpark_Light;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_HitSpark_Dark;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_HitBlood;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_QuickStepTrail;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_PerfectGuardFlash;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_GuardBlockFlash;

	// Innocent Devil VFX
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_InnocentDevilSummon_Fairy;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_InnocentDevilSummon_Griffin;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_InnocentDevilSummon_Salamander;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_InnocentDevilSummon_Ogre;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_InnocentDevilSummon_Skeleton;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_InnocentDevilSummon_Witch;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_InnocentDevilSummon_Pumpkin;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_InnocentDevilEvolve;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_InnocentDevilAttack_Fire;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_InnocentDevilAttack_Ice;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_InnocentDevilAttack_Light;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_InnocentDevilAttack_Dark;

	// Item VFX
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_ItemPickup;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_CandleBreak;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_SaveRoomHeal;

	// Ambient VFX
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_DustMotes_Castle;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_Leaves_Forest;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX|NiagaraSystems")
	UNiagaraSystem* NS_Steam_MachineTower;

protected:
	// Persistent Niagara component for ambient/looping VFX
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VFX", meta = (AllowPrivateAccess = "true"))
	UNiagaraComponent* PersistentNiagaraComponent;

private:
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "VFX")
	float VFXScale = 1.0f;
};
