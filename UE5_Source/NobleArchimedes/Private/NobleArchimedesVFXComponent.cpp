// Fill out your copyright notice in the Description page of Project Settings.

#include "NobleArchimedesVFXComponent.h"
#include "NiagaraFunctionLibrary.h"
#include "NiagaraSystem.h"
#include "NiagaraComponent.h"

UNobleArchimedesVFXComponent::UNobleArchimedesVFXComponent()
{
	PrimaryComponentTick.bCanEverTick = false;

	// Create a persistent Niagara component for ambient/looping VFX
	PersistentNiagaraComponent = CreateDefaultSubobject<UNiagaraComponent>(TEXT("PersistentNiagaraComponent"));
	PersistentNiagaraComponent->bAutoActivate = false;
}

void UNobleArchimedesVFXComponent::BeginPlay()
{
	Super::BeginPlay();
}

// Helper: spawn a Niagara system at a location and apply the global VFX scale
static UNiagaraComponent* SpawnNiagaraSystemScaled(UWorld* World, UNiagaraSystem* System, const FVector& Location, float VFXScale)
{
	if (!System || !World)
	{
		return nullptr;
	}

	UNiagaraComponent* NiagaraComponent = UNiagaraFunctionLibrary::SpawnSystemAtLocation(
		World,
		System,
		Location,
		FRotator::ZeroRotator
	);

	if (NiagaraComponent)
	{
		NiagaraComponent->SetVariableFloat(FName(TEXT("VFXScale")), VFXScale);
	}

	return NiagaraComponent;
}

//=============================================================================
// COMBAT VFX
//=============================================================================

void UNobleArchimedesVFXComponent::PlayWeaponTrail(EWeaponType WeaponType, FVector StartLocation, FVector EndLocation)
{
	UNiagaraSystem* TrailSystem = nullptr;
	switch (WeaponType)
	{
		case EWeaponType::Sword:      TrailSystem = NS_WeaponTrail_Sword; break;
		case EWeaponType::Axe:        TrailSystem = NS_WeaponTrail_Axe; break;
		case EWeaponType::Spear:      TrailSystem = NS_WeaponTrail_Spear; break;
		case EWeaponType::Knuckles:   TrailSystem = NS_WeaponTrail_Knuckles; break;
		case EWeaponType::Special:    TrailSystem = NS_WeaponTrail_Special; break;
		case EWeaponType::None:
		default:                      break;
	}

	if (TrailSystem && GetWorld())
	{
		UNiagaraComponent* Trail = UNiagaraFunctionLibrary::SpawnSystemAtLocation(
			GetWorld(),
			TrailSystem,
			StartLocation,
			FRotator::ZeroRotator
		);
		if (Trail)
		{
			Trail->SetVariableFloat(FName(TEXT("VFXScale")), VFXScale);
		}
	}
}

void UNobleArchimedesVFXComponent::PlayWeaponTrailEnd(EWeaponType WeaponType, FVector Location)
{
	UNiagaraSystem* TrailSystem = nullptr;
	switch (WeaponType)
	{
		case EWeaponType::Sword:      TrailSystem = NS_WeaponTrail_Sword; break;
		case EWeaponType::Axe:        TrailSystem = NS_WeaponTrail_Axe; break;
		case EWeaponType::Spear:      TrailSystem = NS_WeaponTrail_Spear; break;
		case EWeaponType::Knuckles:   TrailSystem = NS_WeaponTrail_Knuckles; break;
		case EWeaponType::Special:    TrailSystem = NS_WeaponTrail_Special; break;
		case EWeaponType::None:
		default:                      break;
	}

	if (TrailSystem && GetWorld())
	{
		UNiagaraComponent* TrailEnd = UNiagaraFunctionLibrary::SpawnSystemAtLocation(
			GetWorld(),
			TrailSystem,
			Location,
			FRotator::ZeroRotator
		);
		if (TrailEnd)
		{
			TrailEnd->SetVariableFloat(FName(TEXT("VFXScale")), VFXScale);
		}
	}
}

void UNobleArchimedesVFXComponent::PlayHitSpark(FVector Location, EDamageType DamageType)
{
	UNiagaraSystem* SparkSystem = nullptr;
	switch (DamageType)
	{
		case EDamageType::Fire:  SparkSystem = NS_HitSpark_Fire; break;
		case EDamageType::Ice:   SparkSystem = NS_HitSpark_Ice; break;
		case EDamageType::Light: SparkSystem = NS_HitSpark_Light; break;
		case EDamageType::Dark:  SparkSystem = NS_HitSpark_Dark; break;
		default:                 SparkSystem = NS_HitSpark_Fire; break;
	}

	if (SparkSystem && GetWorld())
	{
		UNiagaraComponent* Spark = UNiagaraFunctionLibrary::SpawnSystemAtLocation(
			GetWorld(),
			SparkSystem,
			Location,
			FRotator::ZeroRotator
		);
		if (Spark)
		{
			Spark->SetVariableFloat(FName(TEXT("VFXScale")), VFXScale);
		}
	}
}

void UNobleArchimedesVFXComponent::PlayHitBlood(FVector Location)
{
	if (NS_HitBlood && GetWorld())
	{
		UNiagaraComponent* Blood = UNiagaraFunctionLibrary::SpawnSystemAtLocation(
			GetWorld(),
			NS_HitBlood,
			Location,
			FRotator::ZeroRotator
		);
		if (Blood)
		{
			Blood->SetVariableFloat(FName(TEXT("VFXScale")), VFXScale);
		}
	}
}

void UNobleArchimedesVFXComponent::PlayQuickStepTrail(FVector StartLocation, FVector EndLocation)
{
	if (NS_QuickStepTrail && GetWorld())
	{
		UNiagaraComponent* Trail = UNiagaraFunctionLibrary::SpawnSystemAtLocation(
			GetWorld(),
			NS_QuickStepTrail,
			StartLocation,
			FRotator::ZeroRotator
		);
		if (Trail)
		{
			Trail->SetVariableFloat(FName(TEXT("VFXScale")), VFXScale);
		}
	}
}

void UNobleArchimedesVFXComponent::PlayPerfectGuardFlash(FVector Location)
{
	if (NS_PerfectGuardFlash && GetWorld())
	{
		UNiagaraComponent* Flash = UNiagaraFunctionLibrary::SpawnSystemAtLocation(
			GetWorld(),
			NS_PerfectGuardFlash,
			Location,
			FRotator::ZeroRotator
		);
		if (Flash)
		{
			Flash->SetVariableFloat(FName(TEXT("VFXScale")), VFXScale);
		}
	}
}

void UNobleArchimedesVFXComponent::PlayGuardBlockFlash(FVector Location)
{
	if (NS_GuardBlockFlash && GetWorld())
	{
		UNiagaraComponent* Flash = UNiagaraFunctionLibrary::SpawnSystemAtLocation(
			GetWorld(),
			NS_GuardBlockFlash,
			Location,
			FRotator::ZeroRotator
		);
		if (Flash)
		{
			Flash->SetVariableFloat(FName(TEXT("VFXScale")), VFXScale);
		}
	}
}

//=============================================================================
// INNOCENT DEVIL VFX
//=============================================================================

void UNobleArchimedesVFXComponent::PlayInnocentDevilSummon(FVector Location, EInnocentDevilType Type)
{
	UNiagaraSystem* SummonSystem = nullptr;
	switch (Type)
	{
		case EInnocentDevilType::Fairy:   SummonSystem = NS_InnocentDevilSummon_Fairy; break;
		case EInnocentDevilType::Griffin: SummonSystem = NS_InnocentDevilSummon_Griffin; break;
		case EInnocentDevilType::Salamander: SummonSystem = NS_InnocentDevilSummon_Salamander; break;
		case EInnocentDevilType::Ogre:    SummonSystem = NS_InnocentDevilSummon_Ogre; break;
		case EInnocentDevilType::Skeleton: SummonSystem = NS_InnocentDevilSummon_Skeleton; break;
		case EInnocentDevilType::Witch:   SummonSystem = NS_InnocentDevilSummon_Witch; break;
		case EInnocentDevilType::Pumpkin: SummonSystem = NS_InnocentDevilSummon_Pumpkin; break;
		case EInnocentDevilType::None:
		default:                          break;
	}

	if (SummonSystem && GetWorld())
	{
		UNiagaraComponent* Summon = UNiagaraFunctionLibrary::SpawnSystemAtLocation(
			GetWorld(),
			SummonSystem,
			Location,
			FRotator::ZeroRotator
		);
		if (Summon)
		{
			Summon->SetVariableFloat(FName(TEXT("VFXScale")), VFXScale);
		}
	}
}

void UNobleArchimedesVFXComponent::PlayInnocentDevilEvolve(FVector Location, EInnocentDevilType Type)
{
	if (NS_InnocentDevilEvolve && GetWorld())
	{
		UNiagaraComponent* Evolve = UNiagaraFunctionLibrary::SpawnSystemAtLocation(
			GetWorld(),
			NS_InnocentDevilEvolve,
			Location,
			FRotator::ZeroRotator
		);
		if (Evolve)
		{
			Evolve->SetVariableFloat(FName(TEXT("VFXScale")), VFXScale);
		}
	}
}

void UNobleArchimedesVFXComponent::PlayInnocentDevilAttack(FVector Location, EInnocentDevilType Type)
{
	UNiagaraSystem* AttackSystem = nullptr;
	switch (Type)
	{
		case EInnocentDevilType::Fire:   AttackSystem = NS_InnocentDevilAttack_Fire; break;
		case EInnocentDevilType::Ice:    AttackSystem = NS_InnocentDevilAttack_Ice; break;
		case EInnocentDevilType::Light:  AttackSystem = NS_InnocentDevilAttack_Light; break;
		case EInnocentDevilType::Dark:   AttackSystem = NS_InnocentDevilAttack_Dark; break;
		default:                         AttackSystem = NS_InnocentDevilAttack_Fire; break;
	}

	if (AttackSystem && GetWorld())
	{
		UNiagaraComponent* Attack = UNiagaraFunctionLibrary::SpawnSystemAtLocation(
			GetWorld(),
			AttackSystem,
			Location,
			FRotator::ZeroRotator
		);
		if (Attack)
		{
			Attack->SetVariableFloat(FName(TEXT("VFXScale")), VFXScale);
		}
	}
}

//=============================================================================
// ITEM VFX
//=============================================================================

void UNobleArchimedesVFXComponent::PlayItemPickup(FVector Location)
{
	if (NS_ItemPickup && GetWorld())
	{
		UNiagaraComponent* Pickup = UNiagaraFunctionLibrary::SpawnSystemAtLocation(
			GetWorld(),
			NS_ItemPickup,
			Location,
			FRotator::ZeroRotator
		);
		if (Pickup)
		{
			Pickup->SetVariableFloat(FName(TEXT("VFXScale")), VFXScale);
		}
	}
}

void UNobleArchimedesVFXComponent::PlayCandleBreak(FVector Location)
{
	if (NS_CandleBreak && GetWorld())
	{
		UNiagaraComponent* Candle = UNiagaraFunctionLibrary::SpawnSystemAtLocation(
			GetWorld(),
			NS_CandleBreak,
			Location,
			FRotator::ZeroRotator
		);
		if (Candle)
		{
			Candle->SetVariableFloat(FName(TEXT("VFXScale")), VFXScale);
		}
	}
}

void UNobleArchimedesVFXComponent::PlaySaveRoomHeal(FVector Location)
{
	if (NS_SaveRoomHeal && GetWorld())
	{
		UNiagaraComponent* Heal = UNiagaraFunctionLibrary::SpawnSystemAtLocation(
			GetWorld(),
			NS_SaveRoomHeal,
			Location,
			FRotator::ZeroRotator
		);
		if (Heal)
		{
			Heal->SetVariableFloat(FName(TEXT("VFXScale")), VFXScale);
		}
	}
}

//=============================================================================
// AMBIENT VFX
//=============================================================================

void UNobleArchimedesVFXComponent::PlayDustMotes(FVector Location)
{
	if (NS_DustMotes_Castle && GetWorld())
	{
		UNiagaraComponent* Dust = UNiagaraFunctionLibrary::SpawnSystemAtLocation(
			GetWorld(),
			NS_DustMotes_Castle,
			Location,
			FRotator::ZeroRotator
		);
		if (Dust)
		{
			Dust->SetVariableFloat(FName(TEXT("VFXScale")), VFXScale);
		}
	}
}

void UNobleArchimedesVFXComponent::PlayLeaves(FVector Location)
{
	if (NS_Leaves_Forest && GetWorld())
	{
		UNiagaraComponent* Leaves = UNiagaraFunctionLibrary::SpawnSystemAtLocation(
			GetWorld(),
			NS_Leaves_Forest,
			Location,
			FRotator::ZeroRotator
		);
		if (Leaves)
		{
			Leaves->SetVariableFloat(FName(TEXT("VFXScale")), VFXScale);
		}
	}
}

void UNobleArchimedesVFXComponent::PlaySteam(FVector Location)
{
	if (NS_Steam_MachineTower && GetWorld())
	{
		UNiagaraComponent* Steam = UNiagaraFunctionLibrary::SpawnSystemAtLocation(
			GetWorld(),
			NS_Steam_MachineTower,
			Location,
			FRotator::ZeroRotator
		);
		if (Steam)
		{
			Steam->SetVariableFloat(FName(TEXT("VFXScale")), VFXScale);
		}
	}
}

//=============================================================================
// SETTINGS
//=============================================================================

void UNobleArchimedesVFXComponent::SetVFXScale(float Scale)
{
	VFXScale = FMath::Clamp(Scale, 0.0f, 2.0f);
}
