// Fill out your copyright notice in the Description page of Project Settings.

#include "NobleArchimedesAudioComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundCue.h"

UNobleArchimedesAudioComponent::UNobleArchimedesAudioComponent()
{
	PrimaryComponentTick.bCanEverTick = false;

	// Create the persistent audio component for music and ambient beds
	AudioComponent = CreateDefaultSubobject<UAudioComponent>(TEXT("PersistentAudioComponent"));
	AudioComponent->bAutoActivate = false;
}

void UNobleArchimedesAudioComponent::BeginPlay()
{
	Super::BeginPlay();
	ApplyVolumeSettings();
}

void UNobleArchimedesAudioComponent::ApplyVolumeSettings()
{
	// Apply music/ambient volume to the persistent audio component
	if (AudioComponent)
	{
		AudioComponent->SetVolumeMultiplier(MusicVolume);
	}

	// Note: One-shot SFX/UI sounds apply their volume multiplier at playback time
	// via the VolumeMultiplier parameter of UGameplayStatics::PlaySoundAtLocation/PlaySound2D.
}

void UNobleArchimedesAudioComponent::PlayWeaponSwing(EWeaponType WeaponType)
{
	USoundCue* SoundCue = nullptr;
	switch (WeaponType)
	{
		case EWeaponType::Sword:      SoundCue = SC_Combat_Swing_Sword; break;
		case EWeaponType::Axe:        SoundCue = SC_Combat_Swing_Axe; break;
		case EWeaponType::Spear:      SoundCue = SC_Combat_Swing_Spear; break;
		case EWeaponType::Knuckles:   SoundCue = SC_Combat_Swing_Knuckles; break;
		case EWeaponType::Special:    SoundCue = SC_Combat_Swing_Special; break;
		case EWeaponType::None:
		default:                      break;
	}

	if (SoundCue && GetWorld())
	{
		UGameplayStatics::PlaySoundAtLocation(GetWorld(), SoundCue, GetOwner()->GetActorLocation(), SFXVolume);
	}
}

void UNobleArchimedesAudioComponent::PlayWeaponHit(EWeaponType WeaponType, EDamageType DamageType)
{
	// Hit audio is selected by weapon type; damage type is reserved for VFX hit sparks
	USoundCue* SoundCue = nullptr;
	switch (WeaponType)
	{
		case EWeaponType::Sword:      SoundCue = SC_Combat_Hit_Sword; break;
		case EWeaponType::Axe:        SoundCue = SC_Combat_Hit_Axe; break;
		case EWeaponType::Spear:      SoundCue = SC_Combat_Hit_Spear; break;
		case EWeaponType::Knuckles:   SoundCue = SC_Combat_Hit_Knuckles; break;
		case EWeaponType::Special:    SoundCue = SC_Combat_Hit_Special; break;
		case EWeaponType::None:
		default:                      break;
	}

	if (SoundCue && GetWorld())
	{
		UGameplayStatics::PlaySoundAtLocation(GetWorld(), SoundCue, GetOwner()->GetActorLocation(), SFXVolume);
	}
}

void UNobleArchimedesAudioComponent::PlayPlayerHit()
{
	if (SC_Combat_PlayerHit && GetWorld())
	{
		UGameplayStatics::PlaySoundAtLocation(GetWorld(), SC_Combat_PlayerHit, GetOwner()->GetActorLocation(), SFXVolume);
	}
}

void UNobleArchimedesAudioComponent::PlayQuickStep()
{
	if (SC_Combat_QuickStep && GetWorld())
	{
		UGameplayStatics::PlaySoundAtLocation(GetWorld(), SC_Combat_QuickStep, GetOwner()->GetActorLocation(), SFXVolume);
	}
}

void UNobleArchimedesAudioComponent::PlayGuardBlock()
{
	if (SC_Combat_GuardBlock && GetWorld())
	{
		UGameplayStatics::PlaySoundAtLocation(GetWorld(), SC_Combat_GuardBlock, GetOwner()->GetActorLocation(), SFXVolume);
	}
}

void UNobleArchimedesAudioComponent::PlayPerfectGuard()
{
	if (SC_Combat_PerfectGuard && GetWorld())
	{
		UGameplayStatics::PlaySoundAtLocation(GetWorld(), SC_Combat_PerfectGuard, GetOwner()->GetActorLocation(), SFXVolume);
	}
}

void UNobleArchimedesAudioComponent::PlayInnocentDevilSummon(EInnocentDevilType Type)
{
	USoundCue* SoundCue = nullptr;
	switch (Type)
	{
		case EInnocentDevilType::Fairy:   SoundCue = SC_InnocentDevil_Summon_Fairy; break;
		case EInnocentDevilType::Griffin: SoundCue = SC_InnocentDevil_Summon_Griffin; break;
		case EInnocentDevilType::Salamander: SoundCue = SC_InnocentDevil_Summon_Salamander; break;
		case EInnocentDevilType::Ogre:    SoundCue = SC_InnocentDevil_Summon_Ogre; break;
		case EInnocentDevilType::Skeleton: SoundCue = SC_InnocentDevil_Summon_Skeleton; break;
		case EInnocentDevilType::Witch:   SoundCue = SC_InnocentDevil_Summon_Witch; break;
		case EInnocentDevilType::Pumpkin: SoundCue = SC_InnocentDevil_Summon_Pumpkin; break;
		case EInnocentDevilType::None:
		default:                          break;
	}

	if (SoundCue && GetWorld())
	{
		UGameplayStatics::PlaySoundAtLocation(GetWorld(), SoundCue, GetOwner()->GetActorLocation(), SFXVolume);
	}
}

void UNobleArchimedesAudioComponent::PlayInnocentDevilAttack(EInnocentDevilType Type)
{
	if (SC_InnocentDevil_Attack && GetWorld())
	{
		UGameplayStatics::PlaySoundAtLocation(GetWorld(), SC_InnocentDevil_Attack, GetOwner()->GetActorLocation(), SFXVolume);
	}
}

void UNobleArchimedesAudioComponent::PlayInnocentDevilEvolve(EInnocentDevilType Type)
{
	if (SC_InnocentDevil_Evolve && GetWorld())
	{
		UGameplayStatics::PlaySoundAtLocation(GetWorld(), SC_InnocentDevil_Evolve, GetOwner()->GetActorLocation(), SFXVolume);
	}
}

void UNobleArchimedesAudioComponent::PlayItemPickup()
{
	if (SC_Item_Pickup && GetWorld())
	{
		UGameplayStatics::PlaySoundAtLocation(GetWorld(), SC_Item_Pickup, GetOwner()->GetActorLocation(), SFXVolume);
	}
}

void UNobleArchimedesAudioComponent::PlayItemUse(FName ItemName)
{
	USoundCue* SoundCue = nullptr;

	if (ItemName == TEXT("Potion"))           SoundCue = SC_Item_Potion;
	else if (ItemName == TEXT("HighPotion"))  SoundCue = SC_Item_HighPotion;
	else if (ItemName == TEXT("Serum"))       SoundCue = SC_Item_Serum;
	else if (ItemName == TEXT("Uncurse"))     SoundCue = SC_Item_Uncurse;
	else if (ItemName == TEXT("Forge"))       SoundCue = SC_Item_Forge;
	else                                      SoundCue = SC_Item_Pickup; // fallback

	if (SoundCue && GetWorld())
	{
		UGameplayStatics::PlaySoundAtLocation(GetWorld(), SoundCue, GetOwner()->GetActorLocation(), SFXVolume);
	}
}

void UNobleArchimedesAudioComponent::PlayStealSuccess()
{
	if (SC_Item_Steal && GetWorld())
	{
		UGameplayStatics::PlaySoundAtLocation(GetWorld(), SC_Item_Steal, GetOwner()->GetActorLocation(), SFXVolume);
	}
}

void UNobleArchimedesAudioComponent::PlayUIClick()
{
	if (SC_UI_Click && GetWorld())
	{
		UGameplayStatics::PlaySound2D(GetWorld(), SC_UI_Click, SFXVolume);
	}
}

void UNobleArchimedesAudioComponent::PlayUIMenuOpen()
{
	if (SC_UI_MenuOpen && GetWorld())
	{
		UGameplayStatics::PlaySound2D(GetWorld(), SC_UI_MenuOpen, SFXVolume);
	}
}

void UNobleArchimedesAudioComponent::PlayUISave()
{
	if (SC_UI_Save && GetWorld())
	{
		UGameplayStatics::PlaySound2D(GetWorld(), SC_UI_Save, SFXVolume);
	}
}

void UNobleArchimedesAudioComponent::PlayAmbient(int32 ChapterIndex)
{
	USoundCue* AmbientCue = nullptr;
	switch (ChapterIndex)
	{
		case 1:  AmbientCue = SC_Amb_Castle; break;
		case 2:  AmbientCue = SC_Amb_Mountains; break;
		case 3:  AmbientCue = SC_Amb_Temple; break;
		case 4:  AmbientCue = SC_Amb_Aqueduct; break;
		case 5:  AmbientCue = SC_Amb_Forest; break;
		case 6:  AmbientCue = SC_Amb_Town; break;
		case 7:  AmbientCue = SC_Amb_Tower; break;
		case 8:  AmbientCue = SC_Amb_Ruins; break;
		case 9:  AmbientCue = SC_Amb_Corridor; break;
		case 10: AmbientCue = SC_Amb_CastleFinal; break;
		default: break;
	}

	if (AmbientCue && AudioComponent)
	{
		AudioComponent->SetSound(AmbientCue);
		AudioComponent->SetVolumeMultiplier(MusicVolume);
		AudioComponent->bLooping = true;
		AudioComponent->Play();
	}
}

void UNobleArchimedesAudioComponent::StopAmbient()
{
	if (AudioComponent)
	{
		AudioComponent->Stop();
		AudioComponent->SetSound(nullptr);
	}
}

void UNobleArchimedesAudioComponent::PlayMusic(int32 ChapterIndex)
{
	USoundCue* MusicCue = nullptr;
	switch (ChapterIndex)
	{
		case 1:  MusicCue = SC_Music_Chap01; break;
		case 2:  MusicCue = SC_Music_Chap02; break;
		case 3:  MusicCue = SC_Music_Chap03; break;
		case 4:  MusicCue = SC_Music_Chap04; break;
		case 5:  MusicCue = SC_Music_Chap05; break;
		case 6:  MusicCue = SC_Music_Chap06; break;
		case 7:  MusicCue = SC_Music_Chap07; break;
		case 8:  MusicCue = SC_Music_Chap08; break;
		case 9:  MusicCue = SC_Music_Chap09; break;
		case 10: MusicCue = SC_Music_Chap10; break;
		default: break;
	}

	if (MusicCue && AudioComponent)
	{
		AudioComponent->SetSound(MusicCue);
		AudioComponent->SetVolumeMultiplier(MusicVolume);
		AudioComponent->bLooping = true;
		AudioComponent->Play();
	}
}

void UNobleArchimedesAudioComponent::PlayCombatMusic()
{
	if (SC_Music_Combat && AudioComponent)
	{
		AudioComponent->SetSound(SC_Music_Combat);
		AudioComponent->SetVolumeMultiplier(MusicVolume);
		AudioComponent->bLooping = true;
		AudioComponent->Play();
	}
}

void UNobleArchimedesAudioComponent::PlayBossMusic()
{
	if (SC_Music_Boss && AudioComponent)
	{
		AudioComponent->SetSound(SC_Music_Boss);
		AudioComponent->SetVolumeMultiplier(MusicVolume);
		AudioComponent->bLooping = true;
		AudioComponent->Play();
	}
}

void UNobleArchimedesAudioComponent::PlayVictoryMusic()
{
	if (SC_Music_Victory && AudioComponent)
	{
		AudioComponent->SetSound(SC_Music_Victory);
		AudioComponent->SetVolumeMultiplier(MusicVolume);
		AudioComponent->bLooping = false;
		AudioComponent->Play();
	}
}

void UNobleArchimedesAudioComponent::PlayGameOverMusic()
{
	if (SC_Music_GameOver && AudioComponent)
	{
		AudioComponent->SetSound(SC_Music_GameOver);
		AudioComponent->SetVolumeMultiplier(MusicVolume);
		AudioComponent->bLooping = false;
		AudioComponent->Play();
	}
}

void UNobleArchimedesAudioComponent::StopMusic()
{
	if (AudioComponent)
	{
		AudioComponent->Stop();
		AudioComponent->SetSound(nullptr);
	}
}

void UNobleArchimedesAudioComponent::SetMasterVolume(float Volume)
{
	MasterVolume = FMath::Clamp(Volume, 0.0f, 1.0f);
	ApplyVolumeSettings();
}

void UNobleArchimedesAudioComponent::SetSFXVolume(float Volume)
{
	SFXVolume = FMath::Clamp(Volume, 0.0f, 1.0f);
	ApplyVolumeSettings();
}

void UNobleArchimedesAudioComponent::SetMusicVolume(float Volume)
{
	MusicVolume = FMath::Clamp(Volume, 0.0f, 1.0f);
	ApplyVolumeSettings();
}
