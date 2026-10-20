// Fill out your copyright notice in the Description page of Project Settings.

#include "NobleArchimedesLevelStreaming.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/LevelStreaming.h"
#include "Room.h"
#include "SaveRoom.h"
#include "MapChecker.h"
#include "HectorCharacter.h"
#include "NobleArchimedesGameInstance.h"
#include "TimerManager.h"
#include "EngineUtils.h"

UNobleArchimedesLevelStreaming::UNobleArchimedesLevelStreaming()
{
	PrimaryComponentTick.bCanEverTick = false;
}

void UNobleArchimedesLevelStreaming::LoadChapter(int32 ChapterIndex)
{
	if (ChapterIndex < 0 || ChapterIndex >= ChapterLevelNames.Num()) return;

	FName LevelName = ChapterLevelNames[ChapterIndex];
	UGameplayStatics::LoadStreamLevel(GetWorld(), LevelName, true, true, FLatentActionInfo());

	// Notify MapChecker that this chapter's rooms are being discovered
	if (AMapChecker* MapChecker = GetMapChecker())
	{
		// Rooms will be discovered as player enters them
	}
}

void UNobleArchimedesLevelStreaming::UnloadChapter(int32 ChapterIndex)
{
	if (ChapterIndex < 0 || ChapterIndex >= ChapterLevelNames.Num()) return;

	FName LevelName = ChapterLevelNames[ChapterIndex];
	UGameplayStatics::UnloadStreamLevel(GetWorld(), LevelName, FLatentActionInfo(), false);
}

void UNobleArchimedesLevelStreaming::TransitionToChapter(int32 ChapterIndex)
{
	if (ChapterIndex < 0 || ChapterIndex >= ChapterLevelNames.Num()) return;

	// Save current game state before transition
	if (UNobleArchimedesGameInstance* GameInstance = Cast<UNobleArchimedesGameInstance>(GetWorld()->GetGameInstance()))
	{
		GameInstance->SaveGame(5); // Auto-save on chapter transition
	}

	// Unload previous chapter
	if (CurrentChapterIndex >= 0 && CurrentChapterIndex < ChapterLevelNames.Num())
	{
		UnloadChapter(CurrentChapterIndex);
	}

	// Load new chapter
	LoadChapter(ChapterIndex);
	CurrentChapterIndex = ChapterIndex;

	// Update MapChecker chapter
	if (AMapChecker* MapChecker = GetMapChecker())
	{
		// MapChecker chapter updated via Blueprint
	}
}

bool UNobleArchimedesLevelStreaming::IsChapterLoaded(int32 ChapterIndex) const
{
	if (ChapterIndex < 0 || ChapterIndex >= ChapterLevelNames.Num()) return false;

	FName LevelName = ChapterLevelNames[ChapterIndex];
	for (ULevelStreaming* StreamingLevel : GetWorld()->GetStreamingLevels())
	{
		if (StreamingLevel && StreamingLevel->GetWorldAssetPackageName() == LevelName)
		{
			return StreamingLevel->IsLevelLoaded();
		}
	}
	return false;
}

AMapChecker* UNobleArchimedesLevelStreaming::GetMapChecker() const
{
	if (!GetWorld()) return nullptr;

	for (TActorIterator<AMapChecker> It(GetWorld()); It; ++It)
	{
		return *It;
	}
	return nullptr;
}

ASaveRoom* UNobleArchimedesLevelStreaming::GetSaveRoomInLevel() const
{
	if (!GetWorld()) return nullptr;

	for (TActorIterator<ASaveRoom> It(GetWorld()); It; ++It)
	{
		return *It;
	}
	return nullptr;
}

TArray<ARoom*> UNobleArchimedesLevelStreaming::GetAllRoomsInLevel() const
{
	TArray<ARoom*> Rooms;
	if (!GetWorld()) return Rooms;

	for (TActorIterator<ARoom> It(GetWorld()); It; ++It)
	{
		Rooms.Add(*It);
	}
	return Rooms;
}

void UNobleArchimedesLevelStreaming::DiscoverRoom(FName RoomName)
{
	if (AMapChecker* MapChecker = GetMapChecker())
	{
		MapChecker->DiscoverRoom(RoomName);
	}
}

void UNobleArchimedesLevelStreaming::ClearRoom(FName RoomName)
{
	if (AMapChecker* MapChecker = GetMapChecker())
	{
		MapChecker->ClearRoom(RoomName);
	}
}

void UNobleArchimedesLevelStreaming::ActivateSaveRoom()
{
	if (ASaveRoom* SaveRoom = GetSaveRoomInLevel())
	{
		if (AHectorCharacter* Hector = Cast<AHectorCharacter>(UGameplayStatics::GetPlayerCharacter(GetWorld(), 0)))
		{
			SaveRoom->ActivateSaveRoom(Hector);
		}
	}
}
