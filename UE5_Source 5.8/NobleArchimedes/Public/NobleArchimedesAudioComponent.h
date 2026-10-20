// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NobleArchimedesTypes.h"
#include "NobleArchimedesAudioComponent.generated.h"

UCLASS(ClassGroup = (Custom), meta = (BlueprintSpawnableComponent))
class NOBLEARCHIMEDES_API UNobleArchimedesAudioComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UNobleArchimedesAudioComponent();

	virtual void BeginPlay() override;

	//=============================================================================
	// COMBAT AUDIO
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Audio")
	void PlayWeaponSwing(EWeaponType WeaponType);

	UFUNCTION(BlueprintCallable, Category = "Audio")
	void PlayWeaponHit(EWeaponType WeaponType, EDamageType DamageType);

	UFUNCTION(BlueprintCallable, Category = "Audio")
	void PlayPlayerHit();

	UFUNCTION(BlueprintCallable, Category = "Audio")
	void PlayQuickStep();

	UFUNCTION(BlueprintCallable, Category = "Audio")
	void PlayGuardBlock();

	UFUNCTION(BlueprintCallable, Category = "Audio")
	void PlayPerfectGuard();

	//=============================================================================
	// INNOCENT DEVIL AUDIO
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Audio")
	void PlayInnocentDevilSummon(EInnocentDevilType Type);

	UFUNCTION(BlueprintCallable, Category = "Audio")
	void PlayInnocentDevilAttack(EInnocentDevilType Type);

	UFUNCTION(BlueprintCallable, Category = "Audio")
	void PlayInnocentDevilEvolve(EInnocentDevilType Type);

	//=============================================================================
	// ITEM AUDIO
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Audio")
	void PlayItemPickup();

	UFUNCTION(BlueprintCallable, Category = "Audio")
	void PlayItemUse(FName ItemName);

	UFUNCTION(BlueprintCallable, Category = "Audio")
	void PlayStealSuccess();

	//=============================================================================
	// UI AUDIO
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Audio")
	void PlayUIClick();

	UFUNCTION(BlueprintCallable, Category = "Audio")
	void PlayUIMenuOpen();

	UFUNCTION(BlueprintCallable, Category = "Audio")
	void PlayUISave();

	//=============================================================================
	// AMBIENT
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Audio")
	void PlayAmbient(int32 ChapterIndex);

	UFUNCTION(BlueprintCallable, Category = "Audio")
	void StopAmbient();

	//=============================================================================
	// SETTINGS
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Audio")
	void SetMasterVolume(float Volume);

	UFUNCTION(BlueprintCallable, Category = "Audio")
	void SetSFXVolume(float Volume);

	UFUNCTION(BlueprintCallable, Category = "Audio")
	void SetMusicVolume(float Volume);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Audio")
	float GetMasterVolume() const { return MasterVolume; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Audio")
	float GetSFXVolume() const { return SFXVolume; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Audio")
	float GetMusicVolume() const { return MusicVolume; }

private:
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio")
	float MasterVolume = 1.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio")
	float SFXVolume = 1.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio")
	float MusicVolume = 0.0f;

	void ApplyVolumeSettings();
};