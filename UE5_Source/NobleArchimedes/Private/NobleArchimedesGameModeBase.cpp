// Fill out your copyright notice in the Description page of Project Settings.

#include "NobleArchimedesGameModeBase.h"
#include "NobleArchimedesSaveGame.h"
#include "NobleArchimedesGameInstance.h"
#include "Kismet/GameplayStatics.h"

ANobleArchimedesGameModeBase::ANobleArchimedesGameModeBase()
{
	PrimaryActorTick.bCanEverTick = false;
}

void ANobleArchimedesGameModeBase::BeginPlay()
{
	Super::BeginPlay();

	GameInstance = Cast<UNobleArchimedesGameInstance>(GetGameInstance());
	SaveGameInstance = Cast<UNobleArchimedesSaveGame>(UGameplayStatics::CreateSaveGameObject(UNobleArchimedesSaveGame::StaticClass()));

	InitializeGameState();
}

void ANobleArchimedesGameModeBase::InitializeGameState()
{
	CurrentChapter = 1;
	CompletedChapters.Empty();
	UnlockedInnocentDevils.Empty();
	UnlockedWeaponRecipes.Empty();

	// Always unlocked: Short Sword
	UnlockedWeaponRecipes.Add("Short Sword");

	// Load existing save if available
	if (GameInstance && GameInstance->HasSaveGame(0))
	{
		LoadSaveData(0);
	}
}

void ANobleArchimedesGameModeBase::StartChapter(int32 ChapterIndex)
{
	CurrentChapter = ChapterIndex;

	if (GameInstance)
	{
		GameInstance->SaveGame(0);
	}
}

void ANobleArchimedesGameModeBase::CompleteChapter(int32 ChapterIndex)
{
	if (!CompletedChapters.Contains(ChapterIndex))
	{
		CompletedChapters.Add(ChapterIndex);
	}

	if (GameInstance)
	{
		GameInstance->SaveGame(0);
	}
}

bool ANobleArchimedesGameModeBase::IsChapterCompleted(int32 ChapterIndex) const
{
	return CompletedChapters.Contains(ChapterIndex);
}

void ANobleArchimedesGameModeBase::SaveGameProgress()
{
	if (GameInstance)
	{
		GameInstance->SaveGame(0);
	}
}

void ANobleArchimedesGameModeBase::LoadGameProgress(int32 SlotIndex)
{
	if (GameInstance)
	{
		GameInstance->LoadGame(SlotIndex);

		if (GameInstance->GetCurrentSaveGame())
		{
			CurrentChapter = GameInstance->GetCurrentSaveGame()->CurrentChapter;
			CompletedChapters = GameInstance->GetCurrentSaveGame()->CompletedChapters;
			UnlockedInnocentDevils = GameInstance->GetCurrentSaveGame()->UnlockedInnocentDevils;
			UnlockedWeaponRecipes = GameInstance->GetCurrentSaveGame()->ForgedWeapons;
		}
	}
}

void ANobleArchimedesGameModeBase::AutoSave()
{
	if (GameInstance)
	{
		GameInstance->SaveGame(GameInstance->AutoSaveSlot);
	}
}

void UNobleArchimedesGameModeBase::UnlockInnocentDevil(EInnocentDevilType Type)
{
	if (!UnlockedInnocentDevils.Contains(Type))
	{
		UnlockedInnocentDevils.Add(Type);

		if (GameInstance)
		{
			GameInstance->SaveGame(0);
		}
	}
}

bool UNobleArchimedesGameModeBase::IsInnocentDevilUnlocked(EInnocentDevilType Type) const
{
	return UnlockedInnocentDevils.Contains(Type);
}

void UNobleArchimedesGameModeBase::UnlockWeaponRecipe(FName WeaponName)
{
	if (!UnlockedWeaponRecipes.Contains(WeaponName))
	{
		UnlockedWeaponRecipes.Add(WeaponName);

		if (GameInstance)
		{
			GameInstance->SaveGame(0);
		}
	}
}

bool UNobleArchimedesGameModeBase::IsWeaponRecipeUnlocked(FName WeaponName) const
{
	return UnlockedWeaponRecipes.Contains(WeaponName);
}

void UNobleArchimedesGameModeBase::LoadSaveData(int32 SlotIndex)
{
	if (GameInstance && GameInstance->GetCurrentSaveGame())
	{
		CurrentChapter = GameInstance->GetCurrentSaveGame()->CurrentChapter;
		CompletedChapters = GameInstance->GetCurrentSaveGame()->CompletedChapters;
		UnlockedInnocentDevils = GameInstance->GetCurrentSaveGame()->UnlockedInnocentDevils;
		UnlockedWeaponRecipes = GameInstance->GetCurrentSaveGame()->ForgedWeapons;
	}
}

void UNobleArchimedesGameModeBase::SaveCurrentState()
{
	if (GameInstance && GameInstance->GetCurrentSaveGame())
	{
		GameInstance->GetCurrentSaveGame()->CurrentChapter = CurrentChapter;
		GameInstance->GetCurrentSaveGame()->CompletedChapters = CompletedChapters;
		GameInstance->GetCurrentSaveGame()->UnlockedInnocentDevils = UnlockedInnocentDevils;
		GameInstance->GetCurrentSaveGame()->ForgedWeapons = UnlockedWeaponRecipes;

		GameInstance->SaveGame(0);
	}
}