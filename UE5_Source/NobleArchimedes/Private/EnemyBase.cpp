// Fill out your copyright notice in the Description page of Project Settings.

#include "EnemyBase.h"
#include "HectorCharacter.h"
#include "NobleArchimedesItemSystem.h"
#include "Perception/AISense_Sight.h"
#include "Perception/AISense_Damage.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "TimerManager.h"

// Sets default values
AEnemyBase::AEnemyBase()
{
	PrimaryActorTick.bCanEverTick = true;

	// Set up character movement
	if (GetCharacterMovement())
	{
		GetCharacterMovement()->MaxWalkSpeed = PatrolSpeed;
		GetCharacterMovement()->bOrientRotationToMovement = true;
	}

	CurrentHealth = MaxHealth;
	bIsStealable = false;
	bHasBeenStolenFrom = false;
	bIsDead = false;
}

void AEnemyBase::BeginPlay()
{
	Super::BeginPlay();

	CurrentHealth = MaxHealth;
	bIsDead = false;

	// Set up perception (would be enhanced with AIPerceptionComponent in editor)
	if (GetWorld())
	{
		// Register for overlap events to detect player
		// In a full implementation, use AIPerceptionComponent
	}
}

void AEnemyBase::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	if (bIsDead) return;

	UpdatePerception(DeltaTime);
	CheckAttackRange();
	UpdateStealWindow(DeltaTime);
}

void AEnemyBase::ApplyDamage(float DamageAmount, EDamageType DamageType)
{
	if (bIsDead) return;

	// Apply weakness/tolerance modifiers
	float FinalDamage = DamageAmount;

	if (Weaknesses.Contains(DamageType.ToString()))
	{
		FinalDamage *= 1.5f; // Weakness bonus
	}

	if (Tolerances.Contains(DamageType.ToString()))
	{
		FinalDamage *= 0.5f; // Tolerance reduction
	}

	CurrentHealth = FMath::Max(0.0f, CurrentHealth - FinalDamage);

	if (CurrentHealth <= 0.0f)
	{
		Die();
	}
}

void AEnemyBase::FacePlayer()
{
	if (AHectorCharacter* Player = Cast<AHectorCharacter>(UGameplayStatics::GetPlayerCharacter(GetWorld(), 0)))
	{
		FVector Direction = Player->GetActorLocation() - GetActorLocation();
		Direction.Z = 0.0f;
		if (!Direction.IsNearlyZero())
		{
			SetActorRotation(Direction.Rotation());
		}
	}
}

void AEnemyBase::MoveToPlayer()
{
	if (GetCharacterMovement())
	{
		GetCharacterMovement()->MaxWalkSpeed = ChaseSpeed;
	}

	if (AHectorCharacter* Player = Cast<AHectorCharacter>(UGameplayStatics::GetPlayerCharacter(GetWorld(), 0)))
	{
		if (AController* Controller = GetController())
		{
			Controller->MoveToLocation(Player->GetActorLocation());
		}
	}
}

void AEnemyBase::MoveToPatrolPoint()
{
	if (GetCharacterMovement())
	{
		GetCharacterMovement()->MaxWalkSpeed = PatrolSpeed;
	}

	// Patrol logic would use patrol points array in a full implementation
	// For now, idle at current location
}

void AEnemyBase::PlayAttackAnimation()
{
	// Animation montage would be played here via Blueprint
}

void AEnemyBase::PlayChaseAnimation()
{
	// Animation montage would be played here via Blueprint
}

void AEnemyBase::PlayIdleAnimation()
{
	// Animation montage would be played here via Blueprint
}

bool AEnemyBase::CanBeStolenByPlayer() const
{
	return CanBeStolen && !bHasBeenStolenFrom && bIsStealable;
}

void AEnemyBase::StartStealWindow()
{
	bIsStealable = true;
	StealWindowTimer = StealWindowSeconds;
}

void AEnemyBase::EndStealWindow()
{
	bIsStealable = false;
	StealWindowTimer = 0.0f;
}

bool AEnemyBase::TrySteal(FName& OutStolenItem)
{
	if (!CanBeStolenByPlayer()) return false;

	if (FMath::FRand() < StealChance && !StealItem.IsNone())
	{
		OutStolenItem = StealItem;
		bHasBeenStolenFrom = true;
		bIsStealable = false;
		StealWindowTimer = 0.0f;
		return true;
	}

	return false;
}

void AEnemyBase::ApplyDamageToPlayer(class AHectorCharacter* Player)
{
	if (!Player) return;

	Player->ApplyDamage(Damage, EDamageType::Slash); // Default damage type, override per enemy
}

void AEnemyBase::UpdatePerception(float DeltaTime)
{
	LastPerceptionUpdate += DeltaTime;
	if (LastPerceptionUpdate < 0.1f) return; // 0.1s tick interval per spec
	LastPerceptionUpdate = 0.0f;

	if (AHectorCharacter* Player = Cast<AHectorCharacter>(UGameplayStatics::GetPlayerCharacter(GetWorld(), 0)))
	{
		float DistanceToPlayer = FVector::Dist(GetActorLocation(), Player->GetActorLocation());
		bCanSeePlayer = (DistanceToPlayer <= DetectionRange);
	}
	else
	{
		bCanSeePlayer = false;
	}
}

void AEnemyBase::CheckAttackRange()
{
	if (AHectorCharacter* Player = Cast<AHectorCharacter>(UGameplayStatics::GetPlayerCharacter(GetWorld(), 0)))
	{
		float DistanceToPlayer = FVector::Dist(GetActorLocation(), Player->GetActorLocation());
		bIsInAttackRange = (DistanceToPlayer <= AttackRange);
	}
	else
	{
		bIsInAttackRange = false;
	}
}

void AEnemyBase::UpdateStealWindow(float DeltaTime)
{
	if (StealWindowTimer > 0.0f)
	{
		StealWindowTimer -= DeltaTime;
		if (StealWindowTimer <= 0.0f)
		{
			EndStealWindow();
		}
	}
}

void AEnemyBase::Die()
{
	bIsDead = true;
	bIsStealable = false;

	// Disable movement and collision
	if (GetCharacterMovement())
	{
		GetCharacterMovement()->DisableMovement();
	}

	// Play death animation (handled in Blueprint)
	// Notify room that this enemy was defeated
	OnDefeated.Broadcast(this);

	// Destroy after a short delay to allow death animation
	FTimerHandle DeathTimer;
	GetWorldTimerManager().SetTimer(DeathTimer, this, &AEnemyBase::DestroySelf, 2.0f, false);
}

void AEnemyBase::DestroySelf()
{
	Destroy();
}
