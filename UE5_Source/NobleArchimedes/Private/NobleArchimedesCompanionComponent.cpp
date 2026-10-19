// Fill out your copyright notice in the Description page of Project Settings.

#include "NobleArchimedesCompanionComponent.h"
#include "NobleArchimedesCharacter.h"
#include "GameFramework/CharacterMovementComponent.h"

UNobleArchimedesCompanionComponent::UNobleArchimedesCompanionComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
}

void UNobleArchimedesCompanionComponent::BeginPlay()
{
	Super::BeginPlay();

	// Initialize default companions (locked by default)
	FCompanionData Fairy;
	Fairy.CompanionName = "Fairy";
	Fairy.CompanionType = ECompanionType::Fairy;
	Fairy.Level = 1;
	Fairy.Health = 50;
	Fairy.MaxHealth = 50;
	Fairy.Attack = 8;
	Fairy.bIsUnlocked = false;
	Companions.Add(Fairy);

	FCompanionData Griffin;
	Griffin.CompanionName = "Griffin";
	Griffin.CompanionType = ECompanionType::Griffin;
	Griffin.Level = 1;
	Griffin.Health = 80;
	Griffin.MaxHealth = 80;
	Griffin.Attack = 12;
	Griffin.bIsUnlocked = false;
	Companions.Add(Griffin);

	FCompanionData Salamander;
	Salamander.CompanionName = "Salamander";
	Salamander.CompanionType = ECompanionType::Salamander;
	Salamander.Level = 1;
	Salamander.Health = 70;
	Salamander.MaxHealth = 70;
	Salamander.Attack = 10;
	Salamander.bIsUnlocked = false;
	Companions.Add(Salamander);

	FCompanionData Ogre;
	Ogre.CompanionName = "Ogre";
	Ogre.CompanionType = ECompanionType::Ogre;
	Ogre.Level = 1;
	Ogre.Health = 120;
	Ogre.MaxHealth = 120;
	Ogre.Attack = 15;
	Ogre.bIsUnlocked = false;
	Companions.Add(Ogre);

	FCompanionData SkeletonDevil;
	SkeletonDevil.CompanionName = "Skeleton Devil";
	SkeletonDevil.CompanionType = ECompanionType::Skeleton;
	SkeletonDevil.Level = 1;
	SkeletonDevil.Health = 60;
	SkeletonDevil.MaxHealth = 60;
	SkeletonDevil.Attack = 9;
	SkeletonDevil.bIsUnlocked = false;
	Companions.Add(SkeletonDevil);

	FCompanionData WitchDevil;
	WitchDevil.CompanionName = "Witch Devil";
	WitchDevil.CompanionType = ECompanionType::Witch;
	WitchDevil.Level = 1;
	WitchDevil.Health = 55;
	WitchDevil.MaxHealth = 55;
	WitchDevil.Attack = 11;
	WitchDevil.bIsUnlocked = false;
	Companions.Add(WitchDevil);

	FCompanionData Pumpkin;
	Pumpkin.CompanionName = "Pumpkin";
	Pumpkin.CompanionType = ECompanionType::Pumpkin;
	Pumpkin.Level = 1;
	Pumpkin.Health = 100;
	Pumpkin.MaxHealth = 100;
	Pumpkin.Attack = 20;
	Pumpkin.bIsUnlocked = false;
	Companions.Add(Pumpkin);
}

void UNobleArchimedesCompanionComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	UpdateCompanionAI(DeltaTime);
}

void UNobleArchimedesCompanionComponent::SummonCompanion(ECompanionType Type)
{
	// Find companion data and unlock it
	for (auto& Data : Companions)
	{
		if (Data.CompanionType == Type)
		{
			Data.bIsUnlocked = true;
			ActiveCompanion = Type;
			SpawnCompanionActor(Type);
			return;
		}
	}
}

void UNobleArchimedesCompanionComponent::DismissCompanion(ECompanionType Type)
{
	if (ActiveCompanion == Type)
	{
		ActiveCompanion = ECompanionType::None;
	}
}

void UNobleArchimedesCompanionComponent::SetMode(ECompanionMode NewMode)
{
	CurrentMode = NewMode;
}

void UNobleArchimedesCompanionComponent::EvolveCompanion(ECompanionType Type, ECompanionType CrystalColor)
{
	for (auto& Data : Companions)
	{
		if (Data.CompanionType == Type)
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

TArray<FCompanionData> UNobleArchimedesCompanionComponent::GetCompanions() const
{
	return Companions;
}

bool UNobleArchimedesCompanionComponent::HasCompanion(ECompanionType Type) const
{
	for (const auto& Data : Companions)
	{
		if (Data.CompanionType == Type && Data.bIsUnlocked)
		{
			return true;
		}
	}
	return false;
}

void UNobleArchimedesCompanionComponent::CommandAttack()
{
	// Command active companion to attack
}

void UNobleArchimedesCompanionComponent::CommandGuard()
{
	// Command active companion to guard
}

void UNobleArchimedesCompanionComponent::CommandHeal()
{
	// Command active companion to heal player
}

void UNobleArchimedesCompanionComponent::UpdateCompanionAI(float DeltaTime)
{
	if (ActiveCompanion == ECompanionType::None) return;

	if (ANobleArchimedesCharacter* OwnerChar = Cast<ANobleArchimedesCharacter>(GetOwner()))
	{
		// Follow owner based on mode
		switch (CurrentMode)
		{
		case ECompanionMode::Auto:
			// AI decides actions
			break;
		case ECompanionMode::Command:
			// Wait for player command
			break;
		case ECompanionMode::Guard:
			// Stay close and block
			break;
		}
	}
}

void UNobleArchimedesCompanionComponent::SpawnCompanionActor(ECompanionType Type)
{
	// Spawn companion actor in the world
	// Implementation would create an actor based on companion type
}

void UNobleArchimedesCompanionComponent::UpdateCompanionStats(FCompanionData& Data)
{
	// Update companion stats based on level
}