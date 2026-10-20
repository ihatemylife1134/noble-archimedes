// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Kismet/GameplayStatics.h"
#include "NobleArchimedesTypes.h"
#include "NobleArchimedesLevelStreaming.generated.h"

class AMapChecker;
class ASaveRoom;
class ARoom;

UCLASS(ClassGroup = (Custom), meta = (BlueprintSpawnableComponent))
class NOBLEARCHIMEDES_API UNobleArchimedesLevelStreaming : public UActorComponent
{
	GENERATED_BODY()

public:
	UNobleArchimedesLevelStreaming();

	//=============================================================================
	// CHAPTER STREAMING
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "LevelStreaming")
	void LoadChapter(int32 ChapterIndex);

	UFUNCTION(BlueprintCallable, Category = "LevelStreaming")
	void UnloadChapter(int32 ChapterIndex);

	UFUNCTION(BlueprintCallable, Category = "LevelStreaming")
	void TransitionToChapter(int32 ChapterIndex);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "LevelStreaming")
	bool IsChapterLoaded(int32 ChapterIndex) const;

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "LevelStreaming")
	int32 GetCurrentChapterIndex() const { return CurrentChapterIndex; }

	//=============================================================================
	// ROOM & MAP INTEGRATION
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "LevelStreaming")
	AMapChecker* GetMapChecker() const;

	UFUNCTION(BlueprintCallable, Category = "LevelStreaming")
	ASaveRoom* GetSaveRoomInLevel() const;

	UFUNCTION(BlueprintCallable, Category = "LevelStreaming")
	TArray<ARoom*> GetAllRoomsInLevel() const;

	UFUNCTION(BlueprintCallable, Category = "LevelStreaming")
	void DiscoverRoom(FName RoomName);

	UFUNCTION(BlueprintCallable, Category = "LevelStreaming")
	void ClearRoom(FName RoomName);

	UFUNCTION(BlueprintCallable, Category = "LevelStreaming")
	void ActivateSaveRoom();

	//=============================================================================
	// CHAPTER LIST
	//=============================================================================

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "LevelStreaming")
	TArray<FName> ChapterLevelNames =
	{
		TEXT("Chap_01_AbandonedCastle"),
		TEXT("Chap_02_BaljhetMountains"),
		TEXT("Chap_03_GaribaldiTemple"),
		TEXT("Chap_04_MortviaAqueduct"),
		TEXT("Chap_05_ForestOfJigramunt"),
		TEXT("Chap_06_CordovaTown"),
		TEXT("Chap_07_EneomaosMachineTower"),
		TEXT("Chap_08_AiolonRuins"),
		TEXT("Chap_09_InfiniteCorridor"),
		TEXT("Chap_10_DraculasCastle")
	};

private:
	int32 CurrentChapterIndex = 0;
};