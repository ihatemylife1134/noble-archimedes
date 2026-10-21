// Fill out your copyright notice in the Description page of Project Settings.

#include "MapChecker.h"

// Sets default values
AMapChecker::AMapChecker()
{
	PrimaryActorTick.bCanEverTick = false;
	CurrentChapter = 1;
}

void AMapChecker::BeginPlay()
{
	Super::BeginPlay();

	// Initialize all rooms as undiscovered
	// Rooms are discovered as player enters them
}

void AMapChecker::DiscoverRoom(FName RoomName)
{
	if (!RoomDiscoveredStatus.Contains(RoomName))
	{
		RoomDiscoveredStatus.Add(RoomName, true);
	}
}

void AMapChecker::ClearRoom(FName RoomName)
{
	if (!RoomClearedStatus.Contains(RoomName))
	{
		RoomClearedStatus.Add(RoomName, true);
	}
}

bool AMapChecker::IsRoomDiscovered(FName RoomName) const
{
	return RoomDiscoveredStatus.Contains(RoomName) && RoomDiscoveredStatus[RoomName];
}

bool AMapChecker::IsRoomCleared(FName RoomName) const
{
	return RoomClearedStatus.Contains(RoomName) && RoomClearedStatus[RoomName];
}

void AMapChecker::UnlockGreenDoor(FName RoomName, EInnocentDevilType DevilType)
{
	if (!GreenDoorInnocentDevils.Contains(RoomName))
	{
		GreenDoorInnocentDevils.Add(RoomName, DevilType);
		if (!GreenDoorRoomNames.Contains(RoomName))
		{
			GreenDoorRoomNames.Add(RoomName);
		}
	}
}

TArray<FName> AMapChecker::GetDiscoveredRooms() const
{
	TArray<FName> Discovered;
	for (const auto& Pair : RoomDiscoveredStatus)
	{
		if (Pair.Value)
		{
			Discovered.Add(Pair.Key);
		}
	}
	return Discovered;
}

TArray<FName> AMapChecker::GetClearedRooms() const
{
	TArray<FName> Cleared;
	for (const auto& Pair : RoomClearedStatus)
	{
		if (Pair.Value)
		{
			Cleared.Add(Pair.Key);
		}
	}
	return Cleared;
}
