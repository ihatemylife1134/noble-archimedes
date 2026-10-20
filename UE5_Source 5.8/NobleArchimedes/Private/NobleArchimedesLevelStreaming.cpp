// Fill out your copyright notice in the Description page of Project Settings.

#include "NobleArchimedesLevelStreaming.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/LevelStreaming.h"

UNobleArchimedesLevelStreaming::UNobleArchimedesLevelStreaming()
{
	PrimaryComponentTick.bCanEverTick = false;
}

void UNobleArchimedesLevelStreaming::LoadChapter(int32 ChapterIndex)
{
	if (ChapterIndex < 0 || ChapterIndex >= ChapterLevelNames.Num()) return;

	FName LevelName = ChapterLevelNames[ChapterIndex];
	UGameplayStatics::LoadStreamLevel(GetWorld(), LevelName, true, true, FLatentActionInfo());
}

void UNobleArchimedesLevelStreaming::UnloadChapter(int32 ChapterIndex)
{
	if (ChapterIndex < 0 || ChapterIndex >= ChapterLevelNames.Num()) return;

	FName LevelName = ChapterLevelNames[ChapterIndex];
	UGameplayStatics::UnloadStreamLevel(GetWorld(), LevelName, FLatentActionInfo());
}

void UNobleArchimedesLevelStreaming::TransitionToChapter(int32 ChapterIndex)
{
	if (ChapterIndex < 0 || ChapterIndex >= ChapterLevelNames.Num()) return;

	// Unload previous chapter
	if (CurrentChapterIndex >= 0 && CurrentChapterIndex < ChapterLevelNames.Num())
	{
		UnloadChapter(CurrentChapterIndex);
	}

	// Load new chapter
	LoadChapter(ChapterIndex);
	CurrentChapterIndex = ChapterIndex;
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