// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "NobleArchimedesTypes.h"
#include "Room.generated.h"

UCLASS()
class NOBLEARCHIMEDES_API ARoom : public AActor
{
	GENERATED_BODY()

public:
	// Sets default values for this actor's properties
	ARoom();

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;

public:
	// Called every frame
	virtual void Tick(float DeltaTime) override;

	//=============================================================================
	// ROOM PROPERTIES
	//=============================================================================

	// Editable per placement so level designers can name rooms and flag their
	// purpose without creating a Blueprint subclass per room.
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Room")
	FName RoomName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Room")
	int32 ChapterNumber = 1;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Room")
	bool bIsSaveRoom = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Room")
	bool bIsBossArena = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Room")
	bool bIsLocked = true;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Room")
	bool bHasBeenCleared = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Room")
	TArray<TSubclassOf<class AEnemyBase>> EnemyClassesToSpawn;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Room")
	TArray<FVector> EnemySpawnLocations;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Room")
	TArray<FName> ExitRoomNames;

	//=============================================================================
	// ROOM LOCK SYSTEM (Red Bars)
	//=============================================================================

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Room")
	UBoxComponent* RoomTriggerBox;

	/**
	 * Four barriers at the room's north, south, east and west exits. They are
	 * collision-enabled only while the room is locked, so the player cannot
	 * simply walk past a living encounter.
	 */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Room")
	TArray<TObjectPtr<UStaticMeshComponent>> LockBarriers;

	UFUNCTION(BlueprintCallable, Category = "Room")
	void LockRoom();

	UFUNCTION(BlueprintCallable, Category = "Room")
	void UnlockRoom();

	UFUNCTION(BlueprintCallable, Category = "Room")
	bool IsRoomLocked() const;

	UFUNCTION(BlueprintCallable, Category = "Room")
	bool IsRoomCleared() const;

	//=============================================================================
	// ENEMY MANAGEMENT
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Room")
	void SpawnEnemies();

	UFUNCTION(BlueprintCallable, Category = "Room")
	void OnEnemyDefeated(class AEnemyBase* DefeatedEnemy);

	UFUNCTION(BlueprintCallable, Category = "Room")
	int32 GetRemainingEnemyCount() const;

private:
	int32 ActiveEnemyCount;
	TArray<class AEnemyBase*> ActiveEnemies;

	void UpdateLockBarrierTransforms();

	UFUNCTION()
	void OnPlayerEnterRoom(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
		UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

	UFUNCTION()
	void OnPlayerExitRoom(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
		UPrimitiveComponent* OtherComp, int32 OtherBodyIndex);
};
