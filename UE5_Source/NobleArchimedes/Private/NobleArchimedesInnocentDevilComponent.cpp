// Fill out your copyright notice in the Description page of Project Settings.

#include "NobleArchimedesInnocentDevilComponent.h"
#include "HectorCharacter.h"

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
	Fairy.bIsUnlocked = false;
	InnocentDevils.Add(Fairy);

	FInnocentDevilData Griffin;
	Griffin.DevilName = "Griffin";
	Griffin.DevilType = EInnocentDevilType::Griffin;
	Griffin.Level = 1;
	Griffin.Health = 80;
	Griffin.MaxHealth = 80;
	Griffin.Attack = 12;
	Griffin.bIsUnlocked = false;
	InnocentDevils.Add(Griffin);

	FInnocentDevilData Salamander;
	Salamander.DevilName = "Salamander";
	Salamander.DevilType = EInnocentDevilType::Salamander;
	Salamander.Level = 1;
	Salamander.Health = 70;
	Salamander.MaxHealth = 70;
	Salamander.Attack = 10;
	Salamander.bIsUnlocked = false;
	InnocentDevils.Add(Salamander);

	FInnocentDevilData Ogre;
	Ogre.DevilName = "Ogre";
	Ogre.DevilType = EInnocentDevilType::Ogre;
	Ogre.Level = 1;
	Ogre.Health = 120;
	Ogre.MaxHealth = 120;
	Ogre.Attack = 15;
	Ogre.bIsUnlocked = false;
	InnocentDevils.Add(Ogre);

	FInnocentDevilData SkeletonDevil;
	SkeletonDevil.DevilName = "Skeleton Devil";
	SkeletonDevil.DevilType = EInnocentDevilType::Skeleton;
	SkeletonDevil.Level = 1;
	SkeletonDevil.Health = 60;
	SkeletonDevil.MaxHealth = 60;
	SkeletonDevil.Attack = 9;
	SkeletonDevil.bIsUnlocked = false;
	InnocentDevils.Add(SkeletonDevil);

	FInnocentDevilData WitchDevil;
	WitchDevil.DevilName = "Witch Devil";
	WitchDevil.DevilType = EInnocentDevilType::Witch;
	WitchDevil.Level = 1;
	WitchDevil.Health = 55;
	WitchDevil.MaxHealth = 55;
	WitchDevil.Attack = 11;
	WitchDevil.bIsUnlocked = false;
	InnocentDevils.Add(WitchDevil);

	FInnocentDevilData Pumpkin;
	Pumpkin.DevilName = "Pumpkin";
	Pumpkin.DevilType = EInnocentDevilType::Pumpkin;
	Pumpkin.Level = 1;
	Pumpkin.Health = 100;
	Pumpkin.MaxHealth = 100;
	Pumpkin.Attack = 20;
	Pumpkin.bIsUnlocked = false;
	InnocentDevils.Add(Pumpkin);
}

void UNobleArchimedesInnocentDevilComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	UpdateInnocentDevilAI(DeltaTime);
}

void UNobleArchimedesInnocentDevilComponent::SummonInnocentDevil(EInnocentDevilType Type)
{
	// Find Innocent Devil data and unlock it
	for (auto& Data : InnocentDevils)
	{
		if (Data.DevilType == Type)
		{
			Data.bIsUnlocked = true;
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
		ActiveInnocentDevil = EInnocentDevilType::None;
	}
}

void UNobleArchimedesInnocentDevilComponent::SetMode(EInnocentDevilMode NewMode)
{
	CurrentMode = NewMode;
}

void UNobleArchimedesInnocentDevilComponent::EvolveInnocentDevil(EInnocentDevilType Type, EInnocentDevilType CrystalColor)
{
	for (auto& Data : InnocentDevils)
	{
		if (Data.DevilType == Type)
		{
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
	// Command active Innocent Devil to attack
}

void UNobleArchimedesInnocentDevilComponent::CommandGuard()
{
	// Command active Innocent Devil to guard
}

void UNobleArchimedesInnocentDevilComponent::CommandHeal()
{
	// Command active Innocent Devil to heal Hector
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
	// Spawn Innocent Devil actor in the world
}

void UNobleArchimedesInnocentDevilComponent::UpdateInnocentDevilStats(FInnocentDevilData& Data)
{
	// Update Innocent Devil stats based on level
}