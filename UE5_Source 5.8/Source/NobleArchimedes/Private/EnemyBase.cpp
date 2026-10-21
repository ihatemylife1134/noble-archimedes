// Fill out your copyright notice in the Description page of Project Settings.

#include "EnemyBase.h"
#include "AnimVariableBridge.h"
#include "HectorCharacter.h"
#include "ItemDrop.h"
#include "NobleArchimedesItemSystem.h"
#include "Components/CapsuleComponent.h"
#include "Perception/AISense_Sight.h"
#include "Perception/AISense_Damage.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "TimerManager.h"
#include "Engine/World.h"

// Sets default values
AEnemyBase::AEnemyBase()
{
	PrimaryActorTick.bCanEverTick = true;

	// Set up character movement
	if (GetCharacterMovement())
	{
		GetCharacterMovement()->MaxWalkSpeed = PatrolSpeed;
		GetCharacterMovement()->bOrientRotationToMovement = true;
		// Room-spawned enemies have no AIController; allow their movement
		// component to simulate velocity set by the simple chase logic.
		GetCharacterMovement()->bRunPhysicsWithNoController = true;
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

	// Same runtime probe as Hector: a mesh in the wrong AnimationMode, or one
	// whose AnimClass never instantiated, renders the reference pose and looks
	// like a broken state machine.
	if (USkeletalMeshComponent* MeshComp = GetMesh())
	{
		UE_LOG(LogTemp, Display,
			TEXT("NA-ENEMYANIM %s mesh=%s mode=%d animClass=%s instance=%s"),
			*GetNameSafe(this),
			*GetNameSafe(MeshComp->GetSkeletalMeshAsset()),
			static_cast<int32>(MeshComp->GetAnimationMode()),
			*GetNameSafe(MeshComp->AnimClass),
			*GetNameSafe(MeshComp->GetAnimInstance()));
	}

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

	// Enemies share AB_Hector, whose locomotion transitions fire on these bools.
	// Nothing set them for enemies, so they stayed in Idle and slid around.
	if (UAnimInstance* AnimInstance = GetMesh() ? GetMesh()->GetAnimInstance() : nullptr)
	{
		const float Speed2D = GetVelocity().Size2D();
		const bool bMovingNow = Speed2D > 10.0f;
		AnimVariableBridge::SetBool(AnimInstance, TEXT("bIsMoving"), bMovingNow);
		AnimVariableBridge::SetBool(AnimInstance, TEXT("bIsRunning"), Speed2D > PatrolSpeed + 1.0f);
		AnimVariableBridge::SetBool(AnimInstance, TEXT("bIsIdle"), !bMovingNow);
	}

	UpdatePerception(DeltaTime);
	CheckAttackRange();
	UpdateStealWindow(DeltaTime);

	AHectorCharacter* Player = Cast<AHectorCharacter>(UGameplayStatics::GetPlayerCharacter(GetWorld(), 0));
	if (!Player)
	{
		return;
	}

	if (bCanSeePlayer)
	{
		FacePlayer();

		if (!bIsInAttackRange)
		{
			MoveToPlayer();
			PlayChaseAnimation();
		}
		else
		{
			if (GetCharacterMovement())
			{
				GetCharacterMovement()->StopMovementImmediately();
			}

			if (!bIsAttacking && GetWorld()->GetTimeSeconds() - LastAttackTime >= AttackCooldown)
			{
				bIsAttacking = true;
				LastAttackTime = GetWorld()->GetTimeSeconds();
				PlayAttackAnimation();
				GetWorld()->GetTimerManager().SetTimer(
					AttackTimer, this, &AEnemyBase::PerformAttack, AttackWindup, false);
			}
		}
	}
	else
	{
		if (GetCharacterMovement())
		{
			GetCharacterMovement()->StopMovementImmediately();
		}
		PlayIdleAnimation();
	}
}

void AEnemyBase::ApplyDamage(float DamageAmount, EDamageType DamageType)
{
	if (bIsDead) return;

	// Apply weakness/tolerance modifiers
	float FinalDamage = DamageAmount;

	if (Weaknesses.Contains(StaticEnum<EDamageType>()->GetValueAsString(DamageType)))
	{
		FinalDamage *= 1.5f; // Weakness bonus
	}

	if (Tolerances.Contains(StaticEnum<EDamageType>()->GetValueAsString(DamageType)))
	{
		FinalDamage *= 0.5f; // Tolerance reduction
	}

	CurrentHealth = FMath::Max(0.0f, CurrentHealth - FinalDamage);

	// A hit staggers the enemy and opens the steal window. The window closes
	// automatically after StealWindowSeconds, so stealing still requires
	// timing rather than being available permanently.
	if (CurrentHealth > 0.0f && CanBeStolen)
	{
		StartStealWindow();
	}

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
		FVector Direction = Player->GetActorLocation() - GetActorLocation();
		Direction.Z = 0.0f;
		Direction = Direction.GetSafeNormal();
		if (GetCharacterMovement())
		{
			GetCharacterMovement()->SetMovementMode(EMovementMode::MOVE_Walking);
			GetCharacterMovement()->Velocity = Direction * GetCharacterMovement()->MaxWalkSpeed;
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

	if (Player->CombatComponent)
	{
		Player->CombatComponent->CheckPerfectGuard();
	}
	Player->ApplyDamage(Damage, AttackDamageType);
}

void AEnemyBase::PerformAttack()
{
	bIsAttacking = false;
	if (bIsDead) return;

	AHectorCharacter* Player = Cast<AHectorCharacter>(UGameplayStatics::GetPlayerCharacter(GetWorld(), 0));
	if (!Player) return;

	const float Distance = FVector::Dist(GetActorLocation(), Player->GetActorLocation());
	if (Distance <= AttackRange + 60.0f)
	{
		ApplyDamageToPlayer(Player);
	}
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
		// Character capsules stop the enemy slightly before the nominal range;
		// allow a small contact tolerance so melee attacks can actually land.
		bIsInAttackRange = (DistanceToPlayer <= AttackRange + 50.0f);
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
	bIsAttacking = false;

	// Disable movement and collision
	if (GetCharacterMovement())
	{
		GetCharacterMovement()->DisableMovement();
	}
	if (GetCapsuleComponent())
	{
		GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	}

	DropLoot();

	// Play death animation (handled in Blueprint)
	// Notify room that this enemy was defeated
	OnDefeated.Broadcast(this);

	// Destroy after a short delay to allow death animation
	if (UWorld* World = GetWorld())
	{
		World->GetTimerManager().SetTimer(DeathTimer, this, &AEnemyBase::DestroySelf, 2.0f, false);
	}
}

void AEnemyBase::DropLoot()
{
	TArray<FString> Drops;
	ItemDrops.ParseIntoArray(Drops, TEXT(";"), true);
	if (Drops.Num() == 0)
	{
		return;
	}

	const FString& ChosenItem = Drops[FMath::RandRange(0, Drops.Num() - 1)];
	if (ChosenItem.IsEmpty() || ChosenItem.Equals(TEXT("None"), ESearchCase::IgnoreCase))
	{
		return;
	}

	UClass* DropClass = ItemDropClass ? ItemDropClass.Get() : AItemDrop::StaticClass();
	FActorSpawnParameters SpawnParams;
	SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	AItemDrop* Drop = GetWorld()->SpawnActor<AItemDrop>(
		DropClass,
		GetActorLocation() + FVector(0.0f, 0.0f, 60.0f),
		FRotator::ZeroRotator,
		SpawnParams);
	if (Drop)
	{
		Drop->InitializeItem(FName(*ChosenItem), false, false);
		UE_LOG(LogTemp, Log, TEXT("NobleArchimedes: %s dropped %s."), *EnemyName.ToString(), *ChosenItem);
	}
}

void AEnemyBase::DestroySelf()
{
	Destroy();
}

void AEnemyBase::OnPlayerDetected(AActor* DetectedActor)
{
}

void AEnemyBase::OnPlayerLost(AActor* LostActor)
{
}
