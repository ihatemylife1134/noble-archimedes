// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NobleArchimedesTypes.h"
#include "MapChecker.generated.h"

UCLASS()
class NOBLEARCHIMEDES_API AMapChecker : public AActor
{
	GENERATED_BODY()

public:
	// Sets default values for this actor's properties
	AMapChecker();

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;

public:
	//=============================================================================
	// MAP DATA
	//=============================================================================

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Map")
	int32 CurrentChapter = 1;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Map")
	TMap<FName, bool> RoomDiscoveredStatus; // Room name -> discovered

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Map")
	TMap<FName, bool> RoomClearedStatus; // Room name -> cleared

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Map")
	TArray<FName> GreenDoorRoomNames; // Rooms with green doors (Innocent Devil acquisition)

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Map")
	TMap<FName, EInnocentDevilType> GreenDoorInnocentDevils; // Room name -> devil acquired

	//=============================================================================
	// MAP ACTIONS
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Map")
	void DiscoverRoom(FName RoomName);

	UFUNCTION(BlueprintCallable, Category = "Map")
	void ClearRoom(FName RoomName);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Map")
	bool IsRoomDiscovered(FName RoomName) const;

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Map")
	bool IsRoomCleared(FName RoomName) const;

	UFUNCTION(BlueprintCallable, Category = "Map")
	void UnlockGreenDoor(FName RoomName, EInnocentDevilType DevilType);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Map")
	TArray<FName> GetDiscoveredRooms() const;

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Map")
	TArray<FName> GetClearedRooms() const;
};
