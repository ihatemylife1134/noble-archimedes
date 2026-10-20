// Fill out your copyright notice in the Description page of Project Settings.

#include "InnocentDevilActor.h"
#include "HectorCharacter.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"

// Sets default values
AInnocentDevilActor::AInnocentDevilActor()
{
	PrimaryActorTick.bCanEverTick = true;
	bIsSummoned = false;

	if (GetCharacterMovement())
	{
		GetCharacterMovement()->MaxWalkSpeed = 400.0f;
		GetCharacterMovement()->bOrientRotationToMovement = true;
	}
}

void AInnocentDevilActor::BeginPlay()
{
	Super::BeginPlay();

	// Innocent Devil starts unsummoned
	SetActorHiddenInGame(true);
	SetActorEnableCollision(false);
}

void AInnocentDevilActor::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	if (!bIsSummoned || !OwnerHector) return;

	UpdateDevilAI(DeltaTime);
}

void AInnocentDevilActor::InitializeDevil(const FInnocentDevilData& NewDevilData, class AHectorCharacter* NewOwner)
{
	DevilData = NewDevilData;
	OwnerHector = NewOwner;
	bIsSummoned = true;

	SetActorHiddenInGame(false);
	SetActorEnableCollision(true);
}

void AInnocentDevilActor::SetDevilMode(EInnocentDevilMode NewMode)
{
	DevilMode = NewMode;
}

void AInnocentDevilActor::CommandAttack()
{
	DevilMode = EInnocentDevilMode::Command;
	AttackTarget();
}

void AInnocentDevilActor::CommandGuard()
{
	DevilMode = EInnocentDevilMode::Guard;
	GuardOwner();
}

void AInnocentDevilActor::CommandHeal()
{
	if (DevilData.DevilType == EInnocentDevilType::Fairy || DevilData.DevilType == EInnocentDevilType::Witch)
	{
		if (OwnerHector)
		{
			float NewHealth = FMath::Min(OwnerHector->GetHealth() + 25.0f, OwnerHector->GetMaxHealth());
			OwnerHector->SetHealth(NewHealth);
		}
	}
}

void AInnocentDevilActor::EvolveDevil()
{
	DevilData.bIsEvolved = true;
	DevilData.MaxHealth += 50;
	DevilData.Health = DevilData.MaxHealth;
	DevilData.Attack += 10;
}

void AInnocentDevilActor::UpdateDevilAI(float DeltaTime)
{
	DevilAIUpdateTimer += DeltaTime;
	if (DevilAIUpdateTimer < DevilAIUpdateInterval) return;
	DevilAIUpdateTimer = 0.0f;

	switch (DevilMode)
	{
	case EInnocentDevilMode::Auto:
		FollowOwner();
		break;
	case EInnocentDevilMode::Command:
		AttackTarget();
		break;
	case EInnocentDevilMode::Guard:
		GuardOwner();
		break;
	}
}

void AInnocentDevilActor::FollowOwner()
{
	if (OwnerHector)
	{
		float DistanceToOwner = FVector::Dist(GetActorLocation(), OwnerHector->GetActorLocation());
		if (DistanceToOwner > 300.0f)
		{
			if (AController* MyController = GetController())
			{
				MyController->MoveToLocation(OwnerHector->GetActorLocation());
			}
		}
	}
}

void AInnocentDevilActor::AttackTarget()
{
	// Attack logic would target nearby enemies
	// Implemented in Blueprint with specific attack montages per devil type
}

void AInnocentDevilActor::GuardOwner()
{
	// Guard logic would position between owner and nearest threat
	// Implemented in Blueprint
}

void AInnocentDevilActor::HealOwner()
{
	CommandHeal();
}
