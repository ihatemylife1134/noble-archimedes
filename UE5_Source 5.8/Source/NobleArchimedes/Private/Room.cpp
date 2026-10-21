// Fill out your copyright notice in the Description page of Project Settings.

#include "Room.h"
#include "EnemyBase.h"
#include "HectorCharacter.h"
#include "Components/BoxComponent.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Kismet/GameplayStatics.h"
#include "EngineUtils.h"
#include "UObject/ConstructorHelpers.h"

// Sets default values
ARoom::ARoom()
{
	PrimaryActorTick.bCanEverTick = false;

	// Root component
	RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("RootComponent"));

	// Trigger box for detecting player entry
	RoomTriggerBox = CreateDefaultSubobject<UBoxComponent>(TEXT("RoomTriggerBox"));
	RoomTriggerBox->SetupAttachment(RootComponent);
	RoomTriggerBox->SetBoxExtent(FVector(500.0f, 500.0f, 500.0f));
	RoomTriggerBox->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	RoomTriggerBox->SetCollisionResponseToAllChannels(ECollisionResponse::ECR_Ignore);
	RoomTriggerBox->SetCollisionResponseToChannel(ECollisionChannel::ECC_Pawn, ECollisionResponse::ECR_Overlap);

	// Lock barriers on all four exits. The cube is only a placeholder shape;
	// the art pass assigns a glowing material after content generation.
	static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeMesh(
		TEXT("/Engine/BasicShapes/Cube.Cube"));

	for (int32 BarrierIndex = 0; BarrierIndex < 4; ++BarrierIndex)
	{
		UStaticMeshComponent* Barrier = CreateDefaultSubobject<UStaticMeshComponent>(
			*FString::Printf(TEXT("LockBarrier_%d"), BarrierIndex));
		Barrier->SetupAttachment(RootComponent);
		if (CubeMesh.Succeeded())
		{
			Barrier->SetStaticMesh(CubeMesh.Object);
		}
		Barrier->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Barrier->SetCollisionProfileName(TEXT("BlockAll"));
		Barrier->SetCollisionResponseToChannel(ECollisionChannel::ECC_Camera, ECollisionResponse::ECR_Ignore);
		Barrier->SetVisibility(false);
		Barrier->SetHiddenInGame(true);
		Barrier->SetCanEverAffectNavigation(false);
		LockBarriers.Add(Barrier);
	}

	ActiveEnemyCount = 0;
}

void ARoom::BeginPlay()
{
	Super::BeginPlay();

	// Bind overlap events
	RoomTriggerBox->OnComponentBeginOverlap.AddDynamic(this, &ARoom::OnPlayerEnterRoom);
	RoomTriggerBox->OnComponentEndOverlap.AddDynamic(this, &ARoom::OnPlayerExitRoom);

	// Enemies spawn when the player first enters the room, not at level start.
	if (bHasBeenCleared || bIsSaveRoom)
	{
		UnlockRoom();
	}
	else if (bIsLocked)
	{
		LockRoom();
	}

	// The player may already be standing inside the room at level start (the
	// Chapter 1 entrance hall does this). Overlap events never fire for an actor
	// that begins play already overlapping, and the pawn is usually spawned
	// after the room's BeginPlay, so a single check here is unreliable. Poll
	// briefly instead, then stop as soon as the encounter is populated.
	if (bIsLocked && !bIsSaveRoom && !bHasBeenCleared && RoomTriggerBox)
	{
		GetWorldTimerManager().SetTimer(
			EncounterCheckHandle, this, &ARoom::CheckPlayerPresence, 0.2f, true, 0.2f);
	}
}

void ARoom::CheckPlayerPresence()
{
	if (bHasBeenCleared || ActiveEnemies.Num() > 0)
	{
		GetWorldTimerManager().ClearTimer(EncounterCheckHandle);
		return;
	}

	if (RoomTriggerBox)
	{
		if (AHectorCharacter* Player = Cast<AHectorCharacter>(
			UGameplayStatics::GetPlayerCharacter(this, 0)))
		{
			const FVector Delta = Player->GetActorLocation() - RoomTriggerBox->GetComponentLocation();
			const FVector Extent = RoomTriggerBox->GetScaledBoxExtent();

			// Two metres of vertical slack so standing on a raised or sunken
			// floor still registers.
			const bool bInside =
				FMath::Abs(Delta.X) <= Extent.X &&
				FMath::Abs(Delta.Y) <= Extent.Y &&
				Delta.Z <= Extent.Z + 200.0f &&
				Delta.Z >= -Extent.Z - 200.0f;

			if (bInside)
			{
				SpawnEnemies();
				GetWorldTimerManager().ClearTimer(EncounterCheckHandle);
			}
		}
	}
}


void ARoom::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
}

void ARoom::LockRoom()
{
	bIsLocked = true;
	UpdateLockBarrierTransforms();

	for (UStaticMeshComponent* Barrier : LockBarriers)
	{
		if (!Barrier)
		{
			continue;
		}
		Barrier->SetVisibility(true);
		Barrier->SetHiddenInGame(false);
		Barrier->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
	}
}

void ARoom::UnlockRoom()
{
	bIsLocked = false;
	bHasBeenCleared = true;

	for (UStaticMeshComponent* Barrier : LockBarriers)
	{
		if (!Barrier)
		{
			continue;
		}
		Barrier->SetVisibility(false);
		Barrier->SetHiddenInGame(true);
		Barrier->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	}
}

void ARoom::UpdateLockBarrierTransforms()
{
	if (!RoomTriggerBox || LockBarriers.Num() < 4)
	{
		return;
	}

	// The content pipeline sizes the trigger box to the room footprint. Use
	// that footprint so the barriers sit exactly on the room boundary.
	FVector Extent = RoomTriggerBox->GetUnscaledBoxExtent();
	Extent.X = FMath::Max(Extent.X, 500.0f);
	Extent.Y = FMath::Max(Extent.Y, 500.0f);

	const float BarrierHeight = 600.0f;
	const float BarrierThickness = 12.0f;
	const float CenterZ = BarrierHeight * 0.5f;

	// North / south barriers span the X axis.
	LockBarriers[0]->SetRelativeLocation(FVector(0.0f, Extent.Y, CenterZ));
	LockBarriers[0]->SetRelativeScale3D(FVector(
		(Extent.X * 2.0f) / 100.0f, BarrierThickness / 100.0f, BarrierHeight / 100.0f));

	LockBarriers[1]->SetRelativeLocation(FVector(0.0f, -Extent.Y, CenterZ));
	LockBarriers[1]->SetRelativeScale3D(FVector(
		(Extent.X * 2.0f) / 100.0f, BarrierThickness / 100.0f, BarrierHeight / 100.0f));

	// East / west barriers span the Y axis.
	LockBarriers[2]->SetRelativeLocation(FVector(Extent.X, 0.0f, CenterZ));
	LockBarriers[2]->SetRelativeScale3D(FVector(
		BarrierThickness / 100.0f, (Extent.Y * 2.0f) / 100.0f, BarrierHeight / 100.0f));

	LockBarriers[3]->SetRelativeLocation(FVector(-Extent.X, 0.0f, CenterZ));
	LockBarriers[3]->SetRelativeScale3D(FVector(
		BarrierThickness / 100.0f, (Extent.Y * 2.0f) / 100.0f, BarrierHeight / 100.0f));
}

bool ARoom::IsRoomLocked() const
{
	return bIsLocked;
}

bool ARoom::IsRoomCleared() const
{
	return bHasBeenCleared;
}

void ARoom::SpawnEnemies()
{
	if (!GetWorld()) return;

	// Guard against double-spawning when BeginPlay and the overlap event both
	// try to populate the room.
	if (ActiveEnemies.Num() > 0)
	{
		return;
	}

	ActiveEnemyCount = EnemyClassesToSpawn.Num();
	ActiveEnemies.Empty();

	for (int32 i = 0; i < EnemyClassesToSpawn.Num(); i++)
	{
		if (EnemyClassesToSpawn[i])
		{
			FVector SpawnLocation = EnemySpawnLocations.IsValidIndex(i) ? EnemySpawnLocations[i] : GetActorLocation();
			FRotator SpawnRotation = FRotator::ZeroRotator;

			FActorSpawnParameters SpawnParams;
			SpawnParams.Owner = this;

			AEnemyBase* NewEnemy = GetWorld()->SpawnActor<AEnemyBase>(EnemyClassesToSpawn[i], SpawnLocation, SpawnRotation, SpawnParams);
			if (NewEnemy)
			{
				ActiveEnemies.Add(NewEnemy);
				NewEnemy->OnDefeated.AddDynamic(this, &ARoom::OnEnemyDefeated);
			}
		}
	}
}

void ARoom::OnEnemyDefeated(class AEnemyBase* DefeatedEnemy)
{
	if (!DefeatedEnemy) return;

	ActiveEnemies.Remove(DefeatedEnemy);
	ActiveEnemyCount = ActiveEnemies.Num();

	// If all enemies defeated, unlock the room
	if (ActiveEnemyCount <= 0 && bIsLocked && !bIsSaveRoom)
	{
		UnlockRoom();
	}
}

int32 ARoom::GetRemainingEnemyCount() const
{
	return ActiveEnemyCount;
}

void ARoom::OnPlayerEnterRoom(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
	UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (AHectorCharacter* Hector = Cast<AHectorCharacter>(OtherActor))
	{
		// If room is locked and has enemies, ensure enemies are active.
		if (bIsLocked && !bHasBeenCleared && ActiveEnemies.Num() == 0)
		{
			SpawnEnemies();
		}
	}
}

void ARoom::OnPlayerExitRoom(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
	UPrimitiveComponent* OtherComp, int32 OtherBodyIndex)
{
	// Enemies will respawn when player leaves and re-enters (per spec)
	// Handled by re-spawning on next entry if room was cleared
}
