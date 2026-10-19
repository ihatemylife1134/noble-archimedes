// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Sound/SoundCue.h"
#include "Components/AudioComponent.h"
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
	// MUSIC
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Audio")
	void PlayMusic(int32 ChapterIndex);

	UFUNCTION(BlueprintCallable, Category = "Audio")
	void PlayCombatMusic();

	UFUNCTION(BlueprintCallable, Category = "Audio")
	void PlayBossMusic();

	UFUNCTION(BlueprintCallable, Category = "Audio")
	void PlayVictoryMusic();

	UFUNCTION(BlueprintCallable, Category = "Audio")
	void PlayGameOverMusic();

	UFUNCTION(BlueprintCallable, Category = "Audio")
	void StopMusic();

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

	//=============================================================================
	// SOUND CUE ASSETS
	// Names follow AssetNamingSpec.md: SC_ prefix, no spaces.
	// Assign these in the editor/Blueprint defaults (EditDefaultsOnly).
	//=============================================================================

	// Combat SFX
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Combat_Swing_Sword;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Combat_Swing_Axe;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Combat_Swing_Spear;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Combat_Swing_Knuckles;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Combat_Swing_Special;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Combat_Hit_Sword;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Combat_Hit_Axe;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Combat_Hit_Spear;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Combat_Hit_Knuckles;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Combat_Hit_Special;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Combat_PlayerHit;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Combat_EnemyHit;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Combat_QuickStep;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Combat_GuardBlock;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Combat_PerfectGuard;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Combat_Death;

	// Innocent Devil SFX
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_InnocentDevil_Summon_Fairy;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_InnocentDevil_Summon_Griffin;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_InnocentDevil_Summon_Salamander;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_InnocentDevil_Summon_Ogre;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_InnocentDevil_Summon_Skeleton;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_InnocentDevil_Summon_Witch;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_InnocentDevil_Summon_Pumpkin;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_InnocentDevil_Attack;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_InnocentDevil_Evolve;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_InnocentDevil_Hit;

	// Item SFX
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Item_Pickup;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Item_Potion;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Item_HighPotion;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Item_Serum;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Item_Uncurse;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Item_Steal;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Item_StealFail;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Item_Forge;

	// Environment SFX
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Env_CandleBreak;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Env_DoorOpen;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Env_DoorClose;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Env_ChestOpen;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Env_SaveRoom;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Env_Footstep_Stone;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Env_Footstep_Wood;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Env_Footstep_Metal;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Env_Footstep_Dirt;

	// UI SFX
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_UI_Click;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_UI_Hover;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_UI_MenuOpen;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_UI_MenuClose;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_UI_Save;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_UI_Load;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_UI_Error;

	// Ambient Beds (per chapter)
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Amb_Castle;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Amb_Mountains;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Amb_Temple;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Amb_Aqueduct;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Amb_Forest;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Amb_Town;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Amb_Tower;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Amb_Ruins;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Amb_Corridor;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Amb_CastleFinal;

	// Music
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Music_Chap01;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Music_Chap02;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Music_Chap03;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Music_Chap04;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Music_Chap05;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Music_Chap06;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Music_Chap07;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Music_Chap08;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Music_Chap09;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Music_Chap10;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Music_Combat;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Music_Boss;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Music_Victory;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio|SoundCues")
	USoundCue* SC_Music_GameOver;

protected:
	// Persistent audio component for music and ambient beds
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Audio", meta = (AllowPrivateAccess = "true"))
	UAudioComponent* AudioComponent;

private:
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio")
	float MasterVolume = 1.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio")
	float SFXVolume = 1.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Audio")
	float MusicVolume = 0.0f;

	void ApplyVolumeSettings();
};
