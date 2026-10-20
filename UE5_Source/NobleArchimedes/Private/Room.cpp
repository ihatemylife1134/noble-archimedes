// Fill out your copyright notice in the Description page of Project Settings.

#include "Room.h"
#include "EnemyBase.h"
#include "HectorCharacter.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Kismet/GameplayStatics.h"
#include "EngineUtils.h"

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

	// Lock barrier mesh (visual "red bars")
	LockBarrierMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("LockBarrierMesh"));
	LockBarrierMesh->SetupAttachment(RootComponent);
	LockBarrierMesh->SetVisibility(true);

	ActiveEnemyCount = 0;
}

void ARoom::BeginPlay()
{
	Super::BeginPlay();

	// Bind overlap events
	RoomTriggerBox->OnComponentBeginOverlap.AddDynamic(this, &ARoom::OnPlayerEnterRoom);
	RoomTriggerBox->OnComponentEndOverlap.AddDynamic(this, &ARoom::OnPlayerExitRoom);

	// If room is locked, spawn enemies and keep locked
	if (bIsLocked && !bHasBeenCleared)
	{
		SpawnEnemies();
	}
	else if (bHasBeenCleared)
	{
		UnlockRoom();
	}

	// Save rooms are always unlocked
	if (bIsSaveRoom)
	{
		bIsLocked = false;
		LockBarrierMesh->SetVisibility(false);
	}
}

void ARoom::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
}

void ARoom::LockRoom()
{
	bIsLocked = true;
	LockBarrierMesh->SetVisibility(true);
}

void ARoom::UnlockRoom()
{
	bIsLocked = false;
	bHasBeenCleared = true;
	LockBarrierMesh->SetVisibility(false);
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
		// If room is locked and has enemies, ensure enemies are active
		if (bIsLocked && !bHasBeenCleared)
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
