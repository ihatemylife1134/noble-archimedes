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

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Room")
	FName RoomName;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Room")
	int32 ChapterNumber;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Room")
	bool bIsSaveRoom = false;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Room")
	bool bIsBossArena = false;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Room")
	bool bIsLocked = true;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Room")
	bool bHasBeenCleared = false;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Room")
	TArray<TSubclassOf<class AEnemyBase>> EnemyClassesToSpawn;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Room")
	TArray<FVector> EnemySpawnLocations;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Room")
	TArray<FName> ExitRoomNames;

	//=============================================================================
	// ROOM LOCK SYSTEM (Red Bars)
	//=============================================================================

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Room")
	UBoxComponent* RoomTriggerBox;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Room")
	UStaticMeshComponent* LockBarrierMesh;

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

	UFUNCTION()
	void OnPlayerEnterRoom(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
		UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

	UFUNCTION()
	void OnPlayerExitRoom(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
		UPrimitiveComponent* OtherComp, int32 OtherBodyIndex);
};
