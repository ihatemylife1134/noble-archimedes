// Fill out your copyright notice in the Description page of Project Settings.

#include "NobleArchimedesInnocentDevilComponent.h"
#include "HectorCharacter.h"
#include "InnocentDevilActor.h"
#include "Engine/World.h"
#include "TimerManager.h"

UNobleArchimedesInnocentDevilComponent::UNobleArchimedesInnocentDevilComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
}

void UNobleArchimedesInnocentDevilComponent::BeginPlay()
{
	Super::BeginPlay();

	// Initialize default Innocent Devils (locked by default)
	FInnocentDevilData Fairy;
	Fairy.DevilName = "Fairy";
	Fairy.DevilType = EInnocentDevilType::Fairy;
	Fairy.Level = 1;
	Fairy.Health = 50;
	Fairy.MaxHealth = 50;
	Fairy.Attack = 8;
	Fairy.bIsUnlocked = true; // Acquired in Chapter 1.
	Fairy.EvolutionCrystalColor = EEvolutionCrystalType::Light;
	InnocentDevils.Add(Fairy);

	FInnocentDevilData Griffin;
	Griffin.DevilName = "Griffin";
	Griffin.DevilType = EInnocentDevilType::Griffin;
	Griffin.Level = 1;
	Griffin.Health = 80;
	Griffin.MaxHealth = 80;
	Griffin.Attack = 12;
	Griffin.bIsUnlocked = false;
	Griffin.EvolutionCrystalColor = EEvolutionCrystalType::Fire;
	InnocentDevils.Add(Griffin);

	FInnocentDevilData Salamander;
	Salamander.DevilName = "Salamander";
	Salamander.DevilType = EInnocentDevilType::Salamander;
	Salamander.Level = 1;
	Salamander.Health = 70;
	Salamander.MaxHealth = 70;
	Salamander.Attack = 10;
	Salamander.bIsUnlocked = false;
	Salamander.EvolutionCrystalColor = EEvolutionCrystalType::Fire;
	InnocentDevils.Add(Salamander);

	FInnocentDevilData Ogre;
	Ogre.DevilName = "Ogre";
	Ogre.DevilType = EInnocentDevilType::Ogre;
	Ogre.Level = 1;
	Ogre.Health = 120;
	Ogre.MaxHealth = 120;
	Ogre.Attack = 15;
	Ogre.bIsUnlocked = false;
	Ogre.EvolutionCrystalColor = EEvolutionCrystalType::Slash;
	InnocentDevils.Add(Ogre);

	FInnocentDevilData SkeletonDevil;
	SkeletonDevil.DevilName = "Skeleton Devil";
	SkeletonDevil.DevilType = EInnocentDevilType::Skeleton;
	SkeletonDevil.Level = 1;
	SkeletonDevil.Health = 60;
	SkeletonDevil.MaxHealth = 60;
	SkeletonDevil.Attack = 9;
	SkeletonDevil.bIsUnlocked = false;
	SkeletonDevil.EvolutionCrystalColor = EEvolutionCrystalType::Dark;
	InnocentDevils.Add(SkeletonDevil);

	FInnocentDevilData WitchDevil;
	WitchDevil.DevilName = "Witch Devil";
	WitchDevil.DevilType = EInnocentDevilType::Witch;
	WitchDevil.Level = 1;
	WitchDevil.Health = 55;
	WitchDevil.MaxHealth = 55;
	WitchDevil.Attack = 11;
	WitchDevil.bIsUnlocked = false;
	WitchDevil.EvolutionCrystalColor = EEvolutionCrystalType::Magic;
	InnocentDevils.Add(WitchDevil);

	FInnocentDevilData Pumpkin;
	Pumpkin.DevilName = "Pumpkin";
	Pumpkin.DevilType = EInnocentDevilType::Pumpkin;
	Pumpkin.Level = 1;
	Pumpkin.Health = 100;
	Pumpkin.MaxHealth = 100;
	Pumpkin.Attack = 20;
	Pumpkin.bIsUnlocked = false;
	Pumpkin.EvolutionCrystalColor = EEvolutionCrystalType::Special;
	InnocentDevils.Add(Pumpkin);
}

void UNobleArchimedesInnocentDevilComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	UpdateInnocentDevilAI(DeltaTime);
}

void UNobleArchimedesInnocentDevilComponent::SummonInnocentDevil(EInnocentDevilType Type)
{
	// Find Innocent Devil data. Only devils unlocked through progression can
	// be summoned.
	for (auto& Data : InnocentDevils)
	{
		if (Data.DevilType == Type)
		{
			if (!Data.bIsUnlocked)
			{
				UE_LOG(LogTemp, Warning, TEXT("SummonInnocentDevil: %s is not unlocked yet."), *Data.DevilName.ToString());
				return;
			}

			ActiveInnocentDevil = Type;
			SpawnInnocentDevilActor(Type);
			return;
		}
	}
}

void UNobleArchimedesInnocentDevilComponent::DismissInnocentDevil(EInnocentDevilType Type)
{
	if (ActiveInnocentDevil == Type)
	{
		if (ActiveDevilActor)
		{
			ActiveDevilActor->Destroy();
			ActiveDevilActor = nullptr;
		}
		ActiveInnocentDevil = EInnocentDevilType::None;
	}
}

void UNobleArchimedesInnocentDevilComponent::SetMode(EInnocentDevilMode NewMode)
{
	CurrentMode = NewMode;
	if (ActiveDevilActor)
	{
		ActiveDevilActor->SetDevilMode(NewMode);
	}
}

void UNobleArchimedesInnocentDevilComponent::EvolveInnocentDevil(EInnocentDevilType Type, EEvolutionCrystalType CrystalColor)
{
	for (auto& Data : InnocentDevils)
	{
		if (Data.DevilType == Type)
		{
			// Reject the wrong crystal family instead of silently evolving.
			if (CrystalColor != EEvolutionCrystalType::None
				&& Data.EvolutionCrystalColor != EEvolutionCrystalType::None
				&& Data.EvolutionCrystalColor != CrystalColor)
			{
				return;
			}

			if (!Data.bIsEvolved)
			{
				Data.bIsEvolved = true;
				Data.Level += 5;
				Data.MaxHealth += 50;
				Data.Health = Data.MaxHealth;
				Data.Attack += 10;
			}
			return;
		}
	}
}

TArray<FInnocentDevilData> UNobleArchimedesInnocentDevilComponent::GetInnocentDevils() const
{
	return InnocentDevils;
}

void UNobleArchimedesInnocentDevilComponent::SetInnocentDevils(const TArray<FInnocentDevilData>& NewDevils)
{
	// Preserve the built-in roster if a save has no devil entries.
	if (NewDevils.Num() > 0)
	{
		InnocentDevils = NewDevils;
	}
}

bool UNobleArchimedesInnocentDevilComponent::HasInnocentDevil(EInnocentDevilType Type) const
{
	for (const auto& Data : InnocentDevils)
	{
		if (Data.DevilType == Type && Data.bIsUnlocked)
		{
			return true;
		}
	}
	return false;
}

void UNobleArchimedesInnocentDevilComponent::CommandAttack()
{
	if (ActiveInnocentDevil == EInnocentDevilType::None)
	{
		UE_LOG(LogTemp, Warning, TEXT("CommandAttack: no Innocent Devil active."));
		return;
	}

	// Set mode to Command so the devil waits for Hector's input, then trigger
	// the attack and schedule an auto-reset back to Auto mode.
	CurrentMode = EInnocentDevilMode::Command;

	UE_LOG(LogTemp, Warning, TEXT("Innocent Devil (%d) commanded to Attack!"), (int32)ActiveInnocentDevil);

	if (ActiveDevilActor)
	{
		ActiveDevilActor->SetDevilMode(EInnocentDevilMode::Command);
		ActiveDevilActor->CommandAttack();
	}

	if (GetWorld())
	{
		GetWorld()->GetTimerManager().SetTimer(CommandResetTimer, this, &UNobleArchimedesInnocentDevilComponent::ResetToAutoMode, 2.0f, false);
	}
}

void UNobleArchimedesInnocentDevilComponent::CommandGuard()
{
	if (ActiveInnocentDevil == EInnocentDevilType::None)
	{
		UE_LOG(LogTemp, Warning, TEXT("CommandGuard: no Innocent Devil active."));
		return;
	}

	CurrentMode = EInnocentDevilMode::Guard;

	UE_LOG(LogTemp, Warning, TEXT("Innocent Devil (%d) commanded to Guard!"), (int32)ActiveInnocentDevil);

	if (ActiveDevilActor)
	{
		ActiveDevilActor->SetDevilMode(EInnocentDevilMode::Guard);
		ActiveDevilActor->CommandGuard();
	}

	if (GetWorld())
	{
		GetWorld()->GetTimerManager().SetTimer(CommandResetTimer, this, &UNobleArchimedesInnocentDevilComponent::ResetToAutoMode, 2.0f, false);
	}
}

void UNobleArchimedesInnocentDevilComponent::CommandHeal()
{
	if (ActiveInnocentDevil == EInnocentDevilType::None)
	{
		UE_LOG(LogTemp, Warning, TEXT("CommandHeal: no Innocent Devil active."));
		return;
	}

	// Only Fairy and Witch Innocent Devils can heal Hector.
	FInnocentDevilData* HealerData = nullptr;
	for (auto& Data : InnocentDevils)
	{
		if (Data.DevilType == ActiveInnocentDevil)
		{
			HealerData = &Data;
			break;
		}
	}

	if (!HealerData ||
		(HealerData->DevilType != EInnocentDevilType::Fairy &&
			HealerData->DevilType != EInnocentDevilType::Witch))
	{
		UE_LOG(LogTemp, Warning, TEXT("CommandHeal: active Innocent Devil cannot heal (only Fairy/Witch)."));
		return;
	}

	if (AHectorCharacter* Hector = Cast<AHectorCharacter>(GetOwner()))
	{
		const float HealAmount = 25.0f;
		float NewHealth = FMath::Min(Hector->GetHealth() + HealAmount, Hector->GetMaxHealth());
		Hector->SetHealth(NewHealth);
		UE_LOG(LogTemp, Warning, TEXT("Innocent Devil healed Hector for %f HP."), HealAmount);
	}

	CurrentMode = EInnocentDevilMode::Command;

	if (ActiveDevilActor)
	{
		ActiveDevilActor->SetDevilMode(EInnocentDevilMode::Command);
		ActiveDevilActor->CommandHeal();
	}

	if (GetWorld())
	{
		GetWorld()->GetTimerManager().SetTimer(CommandResetTimer, this, &UNobleArchimedesInnocentDevilComponent::ResetToAutoMode, 2.0f, false);
	}
}

void UNobleArchimedesInnocentDevilComponent::UpdateInnocentDevilAI(float DeltaTime)
{
	if (ActiveInnocentDevil == EInnocentDevilType::None) return;

	if (AHectorCharacter* OwnerChar = Cast<AHectorCharacter>(GetOwner()))
	{
		// Follow Hector based on mode
		switch (CurrentMode)
		{
		case EInnocentDevilMode::Auto:
			// AI decides actions
			break;
		case EInnocentDevilMode::Command:
			// Wait for Hector's command
			break;
		case EInnocentDevilMode::Guard:
			// Stay close and block
			break;
		}
	}
}

void UNobleArchimedesInnocentDevilComponent::SpawnInnocentDevilActor(EInnocentDevilType Type)
{
	UWorld* World = GetWorld();
	AHectorCharacter* Owner = Cast<AHectorCharacter>(GetOwner());
	if (!World || !Owner)
	{
		return;
	}

	if (ActiveDevilActor)
	{
		ActiveDevilActor->Destroy();
		ActiveDevilActor = nullptr;
	}

	UClass* SpawnClass = DevilActorClass ? DevilActorClass.Get() : AInnocentDevilActor::StaticClass();
	FActorSpawnParameters SpawnParams;
	SpawnParams.Owner = Owner;
	SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

	const FVector SpawnLocation = Owner->GetActorLocation()
		+ Owner->GetActorRightVector() * 150.0f
		- Owner->GetActorForwardVector() * 100.0f;
	ActiveDevilActor = World->SpawnActor<AInnocentDevilActor>(
		SpawnClass, SpawnLocation, Owner->GetActorRotation(), SpawnParams);

	if (!ActiveDevilActor)
	{
		UE_LOG(LogTemp, Warning, TEXT("SpawnInnocentDevilActor: failed to spawn devil type %d."), (int32)Type);
		return;
	}

	for (const FInnocentDevilData& Data : InnocentDevils)
	{
		if (Data.DevilType == Type)
		{
			ActiveDevilActor->InitializeDevil(Data, Owner);
			ActiveDevilActor->SetDevilMode(CurrentMode);
			UE_LOG(LogTemp, Log, TEXT("SpawnInnocentDevilActor: summoned %s."), *Data.DevilName.ToString());
			break;
		}
	}
}

void UNobleArchimedesInnocentDevilComponent::UpdateInnocentDevilStats(FInnocentDevilData& Data)
{
	// Base level-1 stats per Innocent Devil type (matches BeginPlay defaults).
	int32 BaseHealth = 50;
	int32 BaseAttack = 8;
	switch (Data.DevilType)
	{
	case EInnocentDevilType::Fairy:   BaseHealth = 50; BaseAttack = 8;  break;
	case EInnocentDevilType::Griffin: BaseHealth = 80; BaseAttack = 12; break;
	case EInnocentDevilType::Salamander: BaseHealth = 70; BaseAttack = 10; break;
	case EInnocentDevilType::Ogre:    BaseHealth = 120; BaseAttack = 15; break;
	case EInnocentDevilType::Skeleton: BaseHealth = 60; BaseAttack = 9; break;
	case EInnocentDevilType::Witch:   BaseHealth = 55; BaseAttack = 11; break;
	case EInnocentDevilType::Pumpkin: BaseHealth = 100; BaseAttack = 20; break;
	default: BaseHealth = 50; BaseAttack = 8; break;
	}

	// Stat growth: +5 MaxHealth and +2 Attack per level beyond level 1.
	const int32 LevelBonus = FMath::Max(0, Data.Level - 1);

	// Per the guide: evolution grants +5 levels, +50 max HP, and +10 attack.
	// Level already includes the +5 levels applied in EvolveInnocentDevil, so
	// only the flat +50 HP / +10 attack evolution bonus is added here.
	Data.MaxHealth = BaseHealth + (LevelBonus * 5) + (Data.bIsEvolved ? 50 : 0);
	Data.Attack = BaseAttack + (LevelBonus * 2) + (Data.bIsEvolved ? 10 : 0);

	// Keep current HP within the new maximum.
	Data.Health = FMath::Clamp(Data.Health, 0, Data.MaxHealth);
}

void UNobleArchimedesInnocentDevilComponent::ResetToAutoMode()
{
	CurrentMode = EInnocentDevilMode::Auto;
	if (ActiveDevilActor)
	{
		ActiveDevilActor->SetDevilMode(EInnocentDevilMode::Auto);
	}
	UE_LOG(LogTemp, Warning, TEXT("Innocent Devil mode reset to Auto."));
}